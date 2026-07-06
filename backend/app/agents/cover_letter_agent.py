import json
from typing import Optional
from app.schemas.cover_letter import CoverLetterData
from app.services.ai_service import ai_service
from app.utils.prompt_loader import PromptLoader
from app.core.logger import system_logger
from app.db.models.resume import Resume
from app.db.models.job import Job

def generate_cover_letter(resume: Resume, job: Job, company_name: Optional[str] = None) -> Optional[CoverLetterData]:
    context = f"""
    Candidate Resume:
    {json.dumps(resume.parsed_data)}
    
    Target Job Description:
    {json.dumps(job.parsed_data)}
    """
    
    c_name = company_name or job.parsed_data.get("company", "the hiring company")
    prompt = PromptLoader.load("cover_letter.txt", c_name=c_name, context=context)
    
    try:
        cl_data = ai_service.generate_structured_output(prompt, CoverLetterData, use_fast_model=False)
        return cl_data
    except Exception as e:
        system_logger.error(f"Error generating cover letter via ai_service: {e}")
        return None
