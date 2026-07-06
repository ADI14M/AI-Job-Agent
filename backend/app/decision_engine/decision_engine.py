import time
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.models.job import Job
from app.db.models.resume import Resume
from app.db.models.application_package import ApplicationPackage
from app.decision_engine.models import DecisionResult
from app.decision_engine.ats_scorer import ATSScorer
from app.decision_engine.skill_gap import SkillGapAnalyzer
from app.decision_engine.resume_optimizer import ResumeOptimizer
from app.decision_engine.cover_letter_generator import CoverLetterGenerator
from app.decision_engine.application_package import ApplicationPackageGenerator
from app.services.ai_service import ai_service
from app.core.logger import system_logger

class DecisionEngine:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def process(self, job_id: int, resume_id: int) -> dict:
        start_time = time.time()
        
        job = self.db.query(Job).filter(Job.id == job_id).first()
        resume = self.db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == self.user.id).first()
        
        if not job or not resume:
            raise ValueError("Job or Resume not found.")

        job_text = job.raw_text
        resume_text = resume.parsed_data.get("raw_text", str(resume.parsed_data))

        system_logger.info(f"Starting Decision Engine for Job {job_id} and Resume {resume_id}")

        # 1. ATS Analysis
        ats_eval = ATSScorer.score(resume_text, job_text)

        # 2. Skill Gap Analysis
        skill_gap = SkillGapAnalyzer.analyze(resume_text, job_text)

        # 3. Decision Logic (Should Apply?)
        decision_prompt = f"""
        Based on the following ATS Evaluation and Skill Gap Analysis for a candidate, 
        determine if they should apply for this job.
        
        ATS Score: {ats_eval.overall_score}/100
        Missing Skills: {', '.join(skill_gap.missing_skills)}
        
        Make a recommendation: 'Apply', 'Maybe', or 'Skip'.
        Provide reasoning, pros, cons, and estimates for interview probability, resume strength, and skill match.
        """
        decision = ai_service.generate_structured_output(decision_prompt, DecisionResult)
        
        if not decision:
            decision = DecisionResult(
                recommendation="Skip", overall_score=ats_eval.overall_score, 
                reasoning="Failed to generate decision.", pros=[], cons=[], missing_skills=[],
                estimated_interview_probability="0%", estimated_resume_strength="0%", estimated_skill_match="0%"
            )

        # 4. Resume Optimization (Only if Apply or Maybe)
        optimized_resume = ""
        cover_letter = ""
        package_files = {}
        
        if decision.recommendation in ["Apply", "Maybe"]:
            optimized_resume = ResumeOptimizer.optimize(resume_text, job_text)
            cover_letter = CoverLetterGenerator.generate(resume_text, job_text)
            
            # Generate Document Package
            summary_data = {
                "decision": decision.model_dump(),
                "ats_evaluation": ats_eval.model_dump(),
                "skill_gap": skill_gap.model_dump()
            }
            package_files = ApplicationPackageGenerator.create_package(optimized_resume, cover_letter, summary_data)

        # 5. Save to Database
        db_package = ApplicationPackage(
            user_id=self.user.id,
            job_id=job.id,
            base_resume_id=resume.id,
            optimized_resume_pdf=package_files.get("resume_pdf"),
            optimized_resume_docx=package_files.get("resume_docx"),
            cover_letter_pdf=package_files.get("cover_letter_pdf"),
            cover_letter_docx=package_files.get("cover_letter_docx"),
            ats_score=ats_eval.overall_score,
            recommendation=decision.recommendation,
            decision_reasoning=decision.reasoning,
            skill_gap_json=skill_gap.model_dump()
        )
        self.db.add(db_package)
        self.db.commit()
        self.db.refresh(db_package)

        end_time = time.time()
        system_logger.info(f"Decision Engine completed in {end_time - start_time:.2f} seconds.")

        return {
            "package_id": db_package.id,
            "decision": decision.model_dump(),
            "ats_evaluation": ats_eval.model_dump(),
            "skill_gap": skill_gap.model_dump(),
            "optimized_resume": optimized_resume,
            "cover_letter": cover_letter,
            "files": package_files
        }
