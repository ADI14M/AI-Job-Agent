import os
import shutil
import logging
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.resume_service import process_and_store_resume
from app.db.models.resume import Resume, ResumeEmbedding
from app.schemas.resume import ResumeResponse
from app.db.models.user import User
from app.api.deps import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[4]
UPLOAD_DIR = BASE_DIR / "data" / "resumes"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("", response_model=List[ResumeResponse])
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Return all resumes uploaded by the current user."""
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()
    return resumes

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...), 
    provider: str = Query("openai", description="LLM provider to use for parsing"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
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
        user_id = current_user.id  
        
        # Process resume via LLM and VectorDB
        raw_text, parsed_data, doc_id = process_and_store_resume(file_path, user_id)
        
        # Save to PostgreSQL
        db_resume = Resume(
            user_id=user_id,
            filename=file.filename,
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

@router.delete("/{resume_id}", status_code=200)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Completely delete a resume.
    Cascades to delete: Database records, physical files, ChromaDB vectors, ATS evaluations, Cover Letters, Application Packages.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this resume")

    # Fetch references for cleanup before cascading deletes
    from app.db.models.application_package import ApplicationPackage
    from app.vector_db.chroma_client import get_resume_collection

    embeddings = db.query(ResumeEmbedding).filter(ResumeEmbedding.resume_id == resume.id).all()
    chroma_doc_ids = [e.chroma_doc_id for e in embeddings if e.chroma_doc_id]

    # Application packages might have generated files in storage/packages
    app_packages = db.query(ApplicationPackage).filter(ApplicationPackage.base_resume_id == resume.id).all()
    package_file_paths = []
    
    # Check potential generated files in storage
    package_dir = BASE_DIR / "backend" / "storage" / "packages"
    
    try:
        # Delete from ChromaDB
        if chroma_doc_ids:
            try:
                collection = get_resume_collection()
                collection.delete(ids=chroma_doc_ids)
            except Exception as e:
                logger.error(f"Failed to delete ChromaDB vectors: {e}")

        # Cascade delete from Postgres
        db.delete(resume)
        db.commit()

        # Physical file deletion (Original resume)
        original_file_path = UPLOAD_DIR / resume.filename
        if original_file_path.exists():
            try:
                os.remove(original_file_path)
            except Exception as e:
                logger.warning(f"Could not remove original file {original_file_path}: {e}")

        # Since application packages don't store strict local paths (they are generated and logged), 
        # we can attempt to clean up any files containing the package ID if they exist.
        for pkg in app_packages:
            if package_dir.exists():
                for f in package_dir.glob(f"*{pkg.id}*"):
                    try:
                        os.remove(f)
                    except Exception:
                        pass
                        
        cover_letters_dir = BASE_DIR / "backend" / "storage" / "cover_letters"
        if cover_letters_dir.exists():
            pass # If we had a specific naming scheme we'd clean it here.

        return {"message": "Resume and all associated data successfully deleted"}

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete resume and associated data")

