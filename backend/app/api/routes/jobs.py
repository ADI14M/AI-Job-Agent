import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.agents.jd_agent import process_and_store_job
from app.db.models.job import Job, JobEmbedding
from app.schemas.job import JobResponse, JobCreate

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=JobResponse)
def create_and_parse_job(
    job_in: JobCreate,
    db: Session = Depends(get_db)
):
    """
    Submit a raw Job Description, parse it into structured data using LLMs,
    generate vector embeddings in ChromaDB, and save to PostgreSQL.
    """
    try:
        parsed_data, doc_id = process_and_store_job(job_in.raw_text, provider_name=job_in.provider)
        
        # Save to DB
        db_job = Job(
            apply_url=job_in.apply_url,
            raw_text=job_in.raw_text,
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
        logger.warning(f"Validation error during JD processing: {ve}")
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
