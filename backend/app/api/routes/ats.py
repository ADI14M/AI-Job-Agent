import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.resume import Resume
from app.db.models.job import Job
from app.db.models.ats import ATSReport
from app.agents.ats_agent import generate_ats_report
from app.schemas.ats import ATSResponse, ATSRequest

from app.db.models.user import User
from app.api.deps import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=ATSResponse)
def create_ats_report(
    request: ATSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate an ATS Analysis Report for a Resume, optionally tailored to a specific Job Description.
    """
    resume = db.query(Resume).filter(Resume.id == request.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    job = None
    if request.job_id:
        job = db.query(Job).filter(Job.id == request.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
            
    try:
        report_data = generate_ats_report(resume, job, provider_name=request.provider)
        if not report_data:
            raise ValueError("ATS Agent returned None")
            
        db_report = ATSReport(
            resume_id=resume.id,
            job_id=job.id if job else None,
            overall_score=report_data.overall_score,
            breakdown=report_data.breakdown.model_dump(),
            recommendations=[r.model_dump() for r in report_data.recommendations]
        )
        
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        return db_report
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error during ATS generation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error during ATS report generation")
