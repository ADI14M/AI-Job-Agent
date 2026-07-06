from app.services.ai_service import ai_service
from app.decision_engine.models import ResumeOptimizationData
from app.core.logger import system_logger

class ResumeOptimizer:
    @staticmethod
    def optimize(resume_text: str, job_text: str) -> str:
        prompt = f"""
        You are an expert Resume Writer.
        Optimize the following resume for the given job description.
        CRITICAL RULES:
        - NEVER invent experience.
        - NEVER invent projects.
        - NEVER invent certifications.
        - Only reorder, rewrite, improve wording, and highlight relevance.
        
        Return the optimized resume formatted cleanly in Markdown. Do not include any conversational text.

        <JOB_DESCRIPTION>
        {job_text}
        </JOB_DESCRIPTION>

        <RESUME>
        {resume_text}
        </RESUME>
        """
        system_logger.info("Running Resume Optimizer...")
        result = ai_service.generate_structured_output(prompt, ResumeOptimizationData)
        
        if not result:
            system_logger.error("Resume Optimizer failed to generate structured output.")
            return resume_text
        return result.optimized_content
