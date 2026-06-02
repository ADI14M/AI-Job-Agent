import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.resume import Resume
from app.db.models.job import Job
from app.db.models.skill_gap import SkillGapReport
from app.agents.skill_gap_agent import generate_skill_gap_report
from app.schemas.skill_gap import SkillGapResponse, SkillGapRequest

from app.db.models.user import User
from app.api.deps import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=SkillGapResponse)
def create_skill_gap_report(
    request: SkillGapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a Skill Gap Report comparing a candidate's Resume against a target Job Description.
    """
    resume = db.query(Resume).filter(Resume.id == request.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
            
    try:
        report_data = generate_skill_gap_report(resume, job, provider_name=request.provider)
        if not report_data:
            raise ValueError("Skill Gap Agent returned None")
            
        db_report = SkillGapReport(
            resume_id=resume.id,
            job_id=job.id,
            report_data=report_data.model_dump()
        )
        
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        return db_report
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error during Skill Gap generation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error during Skill Gap report generation")
