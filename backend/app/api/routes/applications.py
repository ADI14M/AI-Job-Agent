import logging
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.application import Application, ApplicationStatus
from app.api.deps import get_current_active_user
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from app.schemas.approval import ApprovalDataResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=ApplicationResponse)
def create_application(
    request: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify not already applied
    existing = db.query(Application).filter(
        Application.job_id == request.job_id,
        Application.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Application already exists for this job.")

    db_app = Application(
        user_id=current_user.id,
        job_id=request.job_id,
        resume_id=request.resume_id,
        cover_letter_id=request.cover_letter_id,
        notes=request.notes
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@router.get("/", response_model=List[ApplicationResponse])
def get_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    apps = db.query(Application).filter(Application.user_id == current_user.id).order_by(Application.created_at.desc()).all()
    return apps

@router.put("/{app_id}", response_model=ApplicationResponse)
def update_application(
    app_id: int,
    request: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    if request.status:
        app.status = request.status
        if request.status == ApplicationStatus.APPLIED and not app.applied_at:
            app.applied_at = datetime.utcnow()
            
    if request.notes is not None:
        app.notes = request.notes
        
    db.commit()
    db.refresh(app)
    return app

@router.get("/{app_id}/approval-data", response_model=ApprovalDataResponse)
def get_approval_data(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Fetch combined data for the Human Approval Workflow.
    """
    from app.db.models.job import Job
    from app.db.models.resume import Resume
    from app.db.models.cover_letter import CoverLetter
    from app.schemas.approval import ApprovalDataResponse
    
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    job = db.query(Job).filter(Job.id == app.job_id).first()
    resume = db.query(Resume).filter(Resume.id == app.resume_id).first() if app.resume_id else None
    cover_letter = db.query(CoverLetter).filter(CoverLetter.id == app.cover_letter_id).first() if app.cover_letter_id else None
    
    # Mocking Match and ATS Scores for the approval dashboard
    mock_match_score = 0.88
    mock_ats_score = 0.92
    
    return ApprovalDataResponse(
        application_id=app.id,
        job_title=job.title if job else "Unknown",
        company=job.company if job else "Unknown",
        job_description_snippet=job.raw_text[:200] + "..." if job and job.raw_text else "",
        match_score=mock_match_score,
        ats_score=mock_ats_score,
        resume_summary=resume.parsed_data.get("summary", "")[:200] + "..." if resume and resume.parsed_data else None,
        cover_letter_snippet=cover_letter.content[:200] + "..." if cover_letter else None,
        status=app.status.value
    )

