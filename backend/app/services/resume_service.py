import json
import logging
import uuid
from typing import Optional
from app.schemas.resume import ResumeParsedData
from app.vector_db.chroma_client import get_resume_collection
from app.core.llm_provider import LLMFactory
from app.utils.text_extraction import extract_text

logger = logging.getLogger(__name__)

def parse_resume_text(text: str, provider_name: str = "openai") -> Optional[ResumeParsedData]:
    llm_provider = LLMFactory.get_provider(provider_name)
    
    prompt = f"""
    You are an expert AI recruiter and resume parser.
    Extract the following resume text into a highly structured format.
    Ensure all skills, experiences, and education are accurately captured.
    Do NOT invent any information. If a field is missing, leave it empty or omit it.
    
    Resume Text:
    {text}
    """
    
    try:
        parsed_data = llm_provider.generate_structured_output(prompt, ResumeParsedData)
        return parsed_data
    except Exception as e:
        logger.error(f"Error parsing resume via {provider_name}: {e}")
        return None

def process_and_store_resume(file_path: str, user_id: int, provider_name: str = "openai"):
    # 1. Extract Text robustly
    raw_text = extract_text(file_path)
    if not raw_text.strip():
        raise ValueError("Could not extract text from the provided document.")
        
    # 2. Parse into structured data using LLM Abstraction
    parsed_data = parse_resume_text(raw_text, provider_name)
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
        logger.error(f"Failed to embed and store in ChromaDB: {e}")
        doc_id = "error_embedding"
    
    return raw_text, parsed_data, doc_id
