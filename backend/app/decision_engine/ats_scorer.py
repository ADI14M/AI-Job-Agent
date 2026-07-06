import json
from app.services.ai_service import ai_service
from app.decision_engine.models import ATSEvaluation
from app.core.logger import system_logger

class ATSScorer:
    @staticmethod
    def score(resume_text: str, job_text: str) -> ATSEvaluation:
        prompt = f"""
        You are an expert ATS (Applicant Tracking System) simulator.
        Evaluate the following resume against the given job description.
        You must score the resume on a scale of 0-100 for the following categories:
        formatting, keywords, experience, projects, skills, education, achievements.
        Also provide an overall score (0-100) and a list of deductions (reasons for lost points).

        <JOB_DESCRIPTION>
        {job_text}
        </JOB_DESCRIPTION>

        <RESUME>
        {resume_text}
        </RESUME>
        """
        system_logger.info("Running ATS Scorer...")
        result = ai_service.generate_structured_output(prompt, ATSEvaluation)
        
        if not result:
            system_logger.error("ATS Scorer failed to generate structured output.")
            return ATSEvaluation(
                overall_score=0, formatting_score=0, keywords_score=0, 
                experience_score=0, projects_score=0, skills_score=0, 
                education_score=0, achievements_score=0, deductions=["Parsing failed"]
            )
        return result
