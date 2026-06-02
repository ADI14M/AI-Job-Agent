import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.resume import Resume
from app.db.models.job import Job
from app.agents.matching_agent import evaluate_match
from app.schemas.matching import MatchingResponse, MatchingRequest

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=MatchingResponse)
def match_resume_to_job(
    request: MatchingRequest,
    db: Session = Depends(get_db)
):
    """
    Evaluate a specific Resume against a specific Job Description.
    Calculates semantic similarity and uses an LLM to evaluate Skills, Experience, Education, and Keywords.
    """
    resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    try:
        match_result = evaluate_match(resume, job, provider_name=request.provider)
        if not match_result:
            raise ValueError("Matching agent returned None")
            
        return match_result
        
    except ValueError as ve:
        logger.warning(f"Validation error during matching: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error during matching: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during matching process")
