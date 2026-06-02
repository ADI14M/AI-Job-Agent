import json
import logging
import uuid
from typing import Optional
from app.schemas.job import JobParsedData
from app.vector_db.chroma_client import get_job_collection
from app.core.llm_provider import LLMFactory

logger = logging.getLogger(__name__)

def parse_job_description(text: str, provider_name: str = "openai") -> Optional[JobParsedData]:
    llm_provider = LLMFactory.get_provider(provider_name)
    
    prompt = f"""
    You are an expert AI Job Description analyzer.
    Extract the following job description text into a highly structured format.
    Ensure required skills, preferred skills, and experience requirements are accurately captured.
    If a field is missing or not mentioned, leave it empty or omit it. Do not guess.
    
    Job Description Text:
    {text}
    """
    
    try:
        parsed_data = llm_provider.generate_structured_output(prompt, JobParsedData)
        return parsed_data
    except Exception as e:
        logger.error(f"Error parsing job description via {provider_name}: {e}")
        return None

def process_and_store_job(raw_text: str, provider_name: str = "openai"):
    if not raw_text.strip():
        raise ValueError("Cannot parse an empty job description.")
        
    parsed_data = parse_job_description(raw_text, provider_name)
    if not parsed_data:
        raise ValueError("Failed to parse job description data.")
        
    # Prepare ChromaDB embedding text
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
        logger.error(f"Failed to embed and store JD in ChromaDB: {e}")
        doc_id = "error_embedding"
    
    return parsed_data, doc_id
