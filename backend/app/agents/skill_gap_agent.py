import logging
import json
from typing import Optional
from app.schemas.skill_gap import SkillGapReportData
from app.core.llm_provider import LLMFactory
from app.db.models.resume import Resume
from app.db.models.job import Job

logger = logging.getLogger(__name__)

def generate_skill_gap_report(resume: Resume, job: Job, provider_name: str = "openai") -> Optional[SkillGapReportData]:
    llm_provider = LLMFactory.get_provider(provider_name)
    
    context = f"""
    Resume Data:
    {json.dumps(resume.parsed_data)}
    
    Job Description Data:
    {json.dumps(job.parsed_data)}
    """
        
    prompt = f"""
    You are an expert Technical Recruiter and Career Coach.
    Compare the candidate's Resume with the target Job Description.
    
    {context}
    
    Identify all missing Skills, Technologies, Tools, and Certifications that are present in the JD but missing in the Resume.
    Classify each missing item's priority as one of: Critical, Important, Optional.
    Categorize each item as: Skill, Tool, or Certification.
    Output only the structured list.
    """
    
    try:
        report_data = llm_provider.generate_structured_output(prompt, SkillGapReportData)
        return report_data
    except Exception as e:
        logger.error(f"Error generating Skill Gap report via {provider_name}: {e}")
        return None
