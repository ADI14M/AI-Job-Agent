from app.services.ai_service import ai_service
from app.decision_engine.models import CoverLetterData
from app.core.logger import system_logger

class CoverLetterGenerator:
    @staticmethod
    def generate(resume_text: str, job_text: str) -> str:
        prompt = f"""
        You are an expert Cover Letter Writer.
        Generate a professional, human-sounding cover letter for the following job using the candidate's resume.
        CRITICAL RULES:
        - Make it company and role specific.
        - Do not use generic paragraphs.
        - Emphasize how the candidate's specific background aligns with the job's core requirements.
        
        Return ONLY the cover letter content.

        <JOB_DESCRIPTION>
        {job_text}
        </JOB_DESCRIPTION>

        <RESUME>
        {resume_text}
        </RESUME>
        """
        system_logger.info("Running Cover Letter Generator...")
        result = ai_service.generate_structured_output(prompt, CoverLetterData)
        
        if not result:
            system_logger.error("Cover Letter Generator failed to generate structured output.")
            return "Failed to generate cover letter."
        return result.content
