from app.services.ai_service import ai_service
from app.decision_engine.models import SkillGap
from app.core.logger import system_logger

class SkillGapAnalyzer:
    @staticmethod
    def analyze(resume_text: str, job_text: str) -> SkillGap:
        prompt = f"""
        Compare the provided Resume and Job Description.
        Identify existing skills the candidate has that match the job.
        Identify missing skills required by the job that the candidate lacks.
        Provide a recommended learning path and an estimated learning time to acquire the missing skills.

        <JOB_DESCRIPTION>
        {job_text}
        </JOB_DESCRIPTION>

        <RESUME>
        {resume_text}
        </RESUME>
        """
        system_logger.info("Running Skill Gap Analyzer...")
        result = ai_service.generate_structured_output(prompt, SkillGap)
        
        if not result:
            system_logger.error("Skill Gap Analyzer failed to generate structured output.")
            return SkillGap(
                existing_skills=[], missing_skills=["Analysis failed"], 
                recommended_learning_path=[], estimated_learning_time="Unknown"
            )
        return result
