import json
import logging
import uuid
from typing import Optional
from app.schemas.resume import ResumeParsedData
from app.vector_db.chroma_client import get_resume_collection

from app.utils.text_extraction import extract_text

from app.services.ai_service import ai_service
from app.utils.prompt_loader import PromptLoader
from app.core.logger import system_logger

def parse_resume_text(text: str) -> Optional[ResumeParsedData]:
    prompt = PromptLoader.load("resume_parse.txt", text=text)
    
    try:
        parsed_data = ai_service.generate_structured_output(prompt, ResumeParsedData, use_fast_model=False)
        return parsed_data
    except Exception as e:
        system_logger.error(f"Error parsing resume via ai_service: {e}")
        return None

def process_and_store_resume(file_path: str, user_id: int):
    # 1. Extract Text robustly
    raw_text = extract_text(file_path)
    if not raw_text.strip():
        raise ValueError("Could not extract text from the provided document.")
        
    # 2. Parse into structured data using LLM Abstraction
    parsed_data = parse_resume_text(raw_text)
    if not parsed_data:
        raise ValueError("Failed to parse resume data using AI provider.")
        
    # 3. Store embeddings in ChromaDB
    try:
        document_text = f"Name: {parsed_data.name}\nSkills: {', '.join(parsed_data.skills)}\nExperience: {json.dumps([exp.model_dump() for exp in parsed_data.experience])}"
        collection = get_resume_collection()
        doc_id = f"resume_{user_id}_{uuid.uuid4()}"
        
        collection.add(
            documents=[document_text],
            metadatas=[{"user_id": user_id, "type": "resume"}],
            ids=[doc_id]
        )
    except Exception as e:
        system_logger.error(f"Failed to embed and store in ChromaDB: {e}")
        doc_id = "error_embedding"
    
    return raw_text, parsed_data, doc_id
