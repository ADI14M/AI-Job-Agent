import json
from typing import Optional
from app.services.ai_service import ai_service
from app.utils.prompt_loader import PromptLoader
from app.core.logger import system_logger
from app.db.models.resume import Resume
from app.schemas.resume import ResumeParsedData

def optimize_resume_for_role(resume: Resume, target_role: str) -> Optional[ResumeParsedData]:
    context = f"Base Resume Data:\n{json.dumps(resume.parsed_data)}"
    prompt = PromptLoader.load("resume_optimize.txt", target_role=target_role, context=context)
    
    try:
        optimized_data = ai_service.generate_structured_output(prompt, ResumeParsedData, use_fast_model=False)
        return optimized_data
    except Exception as e:
        system_logger.error(f"Error optimizing resume for {target_role} via ai_service: {e}")
        return None
