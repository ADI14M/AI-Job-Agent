import logging
import os
import shutil
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.agents.jd_agent import process_and_store_job
from app.db.models.job import Job, JobEmbedding
from app.schemas.job import JobResponse
from app.utils.text_extraction import extract_text
from typing import Optional
from app.db.models.user import User
from app.api.deps import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[4]
UPLOAD_DIR = BASE_DIR / "data" / "sample_jds"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def extract_text_from_url(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        logger.error(f"Failed to extract text from URL {url}: {e}")
        raise ValueError(f"Could not extract content from URL: {e}")

@router.post("/upload", response_model=JobResponse)
async def upload_job(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    apply_url: Optional[str] = Form(None),
    provider: str = Form("openai"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit a JD via File (PDF, DOCX, TXT), Raw Text, or URL.
    Parses into structured data using LLMs, generates embeddings, and saves to PostgreSQL.
    """
    jd_text = ""
    
    if file:
        if not file.filename.endswith(('.pdf', '.docx', '.doc', '.txt')):
            raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are allowed")
            
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            if file.filename.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    jd_text = f.read()
            else:
                jd_text = extract_text(file_path)
        except Exception as e:
            logger.error(f"Failed to process file {file.filename}: {e}")
            raise HTTPException(status_code=500, detail="Could not process the uploaded file.")
            
    elif raw_text:
        jd_text = raw_text
    elif apply_url:
        jd_text = extract_text_from_url(apply_url)
    else:
        raise HTTPException(status_code=400, detail="Must provide either a file, raw_text, or apply_url")
        
    try:
        parsed_data, doc_id = process_and_store_job(jd_text, provider_name=provider)
        
        db_job = Job(
            user_id=current_user.id,
            apply_url=apply_url,
            raw_text=jd_text,
            title=parsed_data.title,
            company=parsed_data.company,
            location=parsed_data.location,
            parsed_data=parsed_data.model_dump() if parsed_data else {}
        )
        db.add(db_job)
        db.flush()
        
        if doc_id and doc_id != "error_embedding":
            db_embedding = JobEmbedding(
                job_id=db_job.id,
                chroma_doc_id=doc_id
            )
            db.add(db_embedding)
            
        db.commit()
        db.refresh(db_job)
        return db_job
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error processing JD: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error during Job processing")

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
