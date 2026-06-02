import logging
import json
from typing import Optional
from app.core.llm_provider import LLMFactory
from app.db.models.resume import Resume
from app.schemas.resume import ResumeParsedData

logger = logging.getLogger(__name__)

def optimize_resume_for_role(resume: Resume, target_role: str, provider_name: str = "openai") -> Optional[ResumeParsedData]:
    llm_provider = LLMFactory.get_provider(provider_name)
    
    context = f"Base Resume Data:\n{json.dumps(resume.parsed_data)}"
    
    prompt = f"""
    You are an expert Resume Writer and Career Strategist.
    Optimize the following candidate's resume specifically for the role of: {target_role}
    
    {context}
    
    CRITICAL RULES:
    1. NEVER fabricate or invent experience, projects, achievements, or certifications.
    2. You MAY reorder sections and bullet points to highlight relevance to the target role.
    3. You MAY rewrite bullet points to incorporate relevant keywords and improve impact (using strong action verbs).
    4. You MUST retain the exact same factual history (dates, locations, companies, degrees).
    
    Return the optimized resume structured exactly according to the provided schema.
    """
    
    try:
        optimized_data = llm_provider.generate_structured_output(prompt, ResumeParsedData)
        return optimized_data
    except Exception as e:
        logger.error(f"Error optimizing resume for {target_role} via {provider_name}: {e}")
        return None
