import json
import uuid
from typing import Optional
from app.schemas.job import JobParsedData
from app.vector_db.chroma_client import get_job_collection
from app.services.ai_service import ai_service
from app.utils.prompt_loader import PromptLoader
from app.core.logger import system_logger

def parse_job_description(text: str) -> Optional[JobParsedData]:
    prompt = PromptLoader.load("jd_parse.txt", text=text)
    
    try:
        parsed_data = ai_service.generate_structured_output(prompt, JobParsedData, use_fast_model=False)
        return parsed_data
    except Exception as e:
        system_logger.error(f"Error parsing job description via ai_service: {e}")
        return None

def process_and_store_job(raw_text: str):
    if not raw_text.strip():
        raise ValueError("Cannot parse an empty job description.")
        
    parsed_data = parse_job_description(raw_text)
    if not parsed_data:
        raise ValueError("Failed to parse job description data.")
        
    try:
        document_text = (
            f"Title: {parsed_data.title}\n"
            f"Company: {parsed_data.company}\n"
            f"Required Skills: {', '.join(parsed_data.required_skills)}\n"
            f"Preferred Skills: {', '.join(parsed_data.preferred_skills)}\n"
            f"Experience: {parsed_data.experience_requirements or 'Not specified'}"
        )
        collection = get_job_collection()
        doc_id = f"job_{uuid.uuid4()}"
        
        collection.add(
            documents=[document_text],
            metadatas=[{"type": "job", "title": parsed_data.title, "company": parsed_data.company}],
            ids=[doc_id]
        )
    except Exception as e:
        system_logger.error(f"Failed to embed and store JD in ChromaDB: {e}")
        doc_id = "error_embedding"
    
    return parsed_data, doc_id
