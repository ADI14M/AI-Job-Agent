import json
from typing import Optional
from app.schemas.skill_gap import SkillGapReportData
from app.services.ai_service import ai_service
from app.utils.prompt_loader import PromptLoader
from app.core.logger import system_logger
from app.db.models.resume import Resume
from app.db.models.job import Job

def generate_skill_gap_report(resume: Resume, job: Job) -> Optional[SkillGapReportData]:
    context = f"""
    Resume Data:
    {json.dumps(resume.parsed_data)}
    
    Job Description Data:
    {json.dumps(job.parsed_data)}
    """
        
    prompt = PromptLoader.load("skill_gap.txt", context=context)
    
    try:
        report_data = ai_service.generate_structured_output(prompt, SkillGapReportData, use_fast_model=True)
        return report_data
    except Exception as e:
        system_logger.error(f"Error generating Skill Gap report via ai_service: {e}")
        return None
