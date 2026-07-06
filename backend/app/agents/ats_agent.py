import json
from typing import Optional
from app.schemas.ats import ATSReportData
from app.services.ai_service import ai_service
from app.utils.prompt_loader import PromptLoader
from app.core.logger import system_logger
from app.db.models.resume import Resume
from app.db.models.job import Job

def generate_ats_report(resume: Resume, job: Optional[Job] = None) -> Optional[ATSReportData]:
    context = f"Resume Structured Data:\n{json.dumps(resume.parsed_data)}"
    if job:
        context += f"\n\nTarget Job Description Data:\n{json.dumps(job.parsed_data)}"
        
    prompt = PromptLoader.load("ats_score.txt", context=context)
    
    try:
        report_data = ai_service.generate_structured_output(prompt, ATSReportData, use_fast_model=True)
        return report_data
    except Exception as e:
        system_logger.error(f"Error generating ATS report via ai_service: {e}")
        return None
