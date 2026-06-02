import logging
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.application import Application, ApplicationStatus
from app.api.deps import get_current_active_user
from app.automation.playwright_engine import PlaywrightEngine
from app.automation.adapters import LinkedInEasyApplyAdapter, WellfoundAdapter

logger = logging.getLogger(__name__)
router = APIRouter()

engine = PlaywrightEngine(headless=False)
linkedin_adapter = LinkedInEasyApplyAdapter(engine)
wellfound_adapter = WellfoundAdapter(engine)

class AutomationApplyRequest(BaseModel):
    application_id: int
    platform: str # "linkedin" or "wellfound"
    resume_path: str
    cover_letter_path: str = None

async def run_automation_background(app_id: int, apply_url: str, resume_path: str, cover_letter_path: str, platform: str, db: Session):
    success = False
    if platform.lower() == "linkedin":
        success = await linkedin_adapter.apply_to_job(apply_url, resume_path, cover_letter_path)
    elif platform.lower() == "wellfound":
        success = await wellfound_adapter.apply_to_job(apply_url, resume_path, cover_letter_path)
        
    if success:
        logger.info(f"Successfully applied to Job for App {app_id}")
        app = db.query(Application).filter(Application.id == app_id).first()
        if app:
            app.status = ApplicationStatus.APPLIED
            db.commit()
    else:
        logger.error(f"Automation failed for App {app_id}")


@router.post("/apply")
async def apply_automated(
    request: AutomationApplyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from app.db.models.job import Job
    app = db.query(Application).filter(Application.id == request.application_id, Application.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    job = db.query(Job).filter(Job.id == app.job_id).first()
    if not job or not job.apply_url:
        raise HTTPException(status_code=400, detail="Job Apply URL is missing")
        
    # Trigger background automation
    background_tasks.add_task(
        run_automation_background,
        app_id=app.id,
        apply_url=job.apply_url,
        resume_path=request.resume_path,
        cover_letter_path=request.cover_letter_path,
        platform=request.platform,
        db=db
    )
    
    return {"status": "Automation started in background"}
