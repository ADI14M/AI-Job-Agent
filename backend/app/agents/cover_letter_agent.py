import logging
import json
from typing import Optional
from app.schemas.cover_letter import CoverLetterData
from app.core.llm_provider import LLMFactory
from app.db.models.resume import Resume
from app.db.models.job import Job

logger = logging.getLogger(__name__)

def generate_cover_letter(resume: Resume, job: Job, company_name: Optional[str] = None, provider_name: str = "openai") -> Optional[CoverLetterData]:
    llm_provider = LLMFactory.get_provider(provider_name)
    
    context = f"""
    Candidate Resume:
    {json.dumps(resume.parsed_data)}
    
    Target Job Description:
    {json.dumps(job.parsed_data)}
    """
    
    c_name = company_name or job.parsed_data.get("company", "the hiring company")
    
    prompt = f"""
    You are an expert Career Strategist and Cover Letter Writer.
    Write a tailored, professional cover letter for the candidate applying to {c_name}.
    
    {context}
    
    CRITICAL RULES:
    1. Do not hallucinate any experience. Use ONLY the facts from the Candidate Resume.
    2. Focus on aligning the candidate's existing skills with the Target Job Description requirements.
    3. Keep it to 3-4 paragraphs (Introduction, Body Paragraphs aligning skills, Call to Action).
    4. Write in a confident, professional, and enthusiastic tone.
    5. Output the final cover letter text.
    """
    
    try:
        cl_data = llm_provider.generate_structured_output(prompt, CoverLetterData)
        return cl_data
    except Exception as e:
        logger.error(f"Error generating cover letter via {provider_name}: {e}")
        return None
