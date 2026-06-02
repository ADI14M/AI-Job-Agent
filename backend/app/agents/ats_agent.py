import logging
import json
from typing import Optional
from app.schemas.ats import ATSReportData
from app.core.llm_provider import LLMFactory
from app.db.models.resume import Resume
from app.db.models.job import Job

logger = logging.getLogger(__name__)

def generate_ats_report(resume: Resume, job: Optional[Job] = None, provider_name: str = "openai") -> Optional[ATSReportData]:
    llm_provider = LLMFactory.get_provider(provider_name)
    
    context = f"Resume Structured Data:\n{json.dumps(resume.parsed_data)}"
    if job:
        context += f"\n\nTarget Job Description Data:\n{json.dumps(job.parsed_data)}"
        
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) Analyzer.
    Analyze the following candidate resume. If a Job Description is provided, analyze the resume in the context of that JD.
    
    {context}
    
    Calculate the following scores based on strict ATS rules:
    - formatting_score (max 20): Does the layout seem parseable? Are standard headers used?
    - length_score (max 10): Is it an appropriate length (e.g., 1-2 pages)?
    - section_completeness_score (max 20): Are Education, Experience, Skills, and Contact Info present?
    - action_verbs_score (max 20): Are strong action verbs used to start bullet points?
    - quantified_achievements_score (max 30): Are metrics and numbers used to quantify results?
    
    Provide an overall_score (sum of the above, max 100).
    Provide actionable recommendations categorized by priority (Critical, Important, Optional).
    """
    
    try:
        report_data = llm_provider.generate_structured_output(prompt, ATSReportData)
        return report_data
    except Exception as e:
        logger.error(f"Error generating ATS report via {provider_name}: {e}")
        return None
