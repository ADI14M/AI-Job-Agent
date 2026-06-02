import os
import shutil
import logging
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.resume_service import process_and_store_resume
from app.db.models.resume import Resume, ResumeEmbedding
from app.schemas.resume import ResumeResponse

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = "/app/data/resumes"
# Locally, it will be in the cwd, so we ensure it exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...), 
    provider: str = Query("openai", description="LLM provider to use for parsing"),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF or DOCX resume, extract its text, parse it using the chosen LLM provider,
    store embeddings in ChromaDB, and save all metadata in PostgreSQL.
    """
    if not file.filename.endswith(('.pdf', '.docx', '.doc')):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")
        
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Could not save file to disk")
        
    try:
        # Mock user ID = 1 for now until auth is implemented
        user_id = 1 
        
        # Process resume via LLM and VectorDB
        raw_text, parsed_data, doc_id = process_and_store_resume(file_path, user_id, provider_name=provider)
        
        # Save to PostgreSQL
        db_resume = Resume(
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            raw_text=raw_text,
            parsed_data=parsed_data.model_dump() if parsed_data else {}
        )
        db.add(db_resume)
        db.flush() # Flush to get db_resume.id
        
        # Save embedding reference
        if doc_id and doc_id != "error_embedding":
            db_embedding = ResumeEmbedding(
                resume_id=db_resume.id,
                chroma_doc_id=doc_id
            )
            db.add(db_embedding)
            
        db.commit()
        db.refresh(db_resume)
        
        return db_resume
        
    except ValueError as ve:
        logger.warning(f"Validation error during processing: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error processing resume: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error during resume processing")
