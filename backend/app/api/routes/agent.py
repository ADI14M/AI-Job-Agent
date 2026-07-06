import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from app.db.session import get_db
from app.db.models.user import User
from app.api.deps import get_current_active_user
from app.db.models.agent_state import AgentApplicationState, AgentStateEnum
from app.agent.workflow import WorkflowEngine
from app.agent.models import FormProfile
from app.agent.scheduler import scheduler_instance

logger = logging.getLogger(__name__)
router = APIRouter()

class ProcessActionRequest(BaseModel):
    agent_state_id: int
    action: str # "APPROVE", "REJECT", "RETRY"

class ScheduleRequest(BaseModel):
    interval_hours: int

@router.get("/states")
def get_agent_states(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    states = db.query(AgentApplicationState).filter(AgentApplicationState.user_id == current_user.id).order_by(AgentApplicationState.updated_at.desc()).all()
    return {"status": "success", "data": states}

@router.post("/process")
def process_agent_state(
    request: ProcessActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    state = db.query(AgentApplicationState).filter(
        AgentApplicationState.id == request.agent_state_id,
        AgentApplicationState.user_id == current_user.id
    ).first()
    
    if not state:
        raise HTTPException(status_code=404, detail="Agent state not found")

    if request.action == "APPROVE" and state.current_state == AgentStateEnum.READY_FOR_REVIEW.value:
        state.human_approved = True
        db.commit()
        # Resume processing
        engine = WorkflowEngine(db, current_user)
        from app.db.models.user_profile import UserProfile
        
        db_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not db_profile:
            # Fallback to basic user info if profile not completed
            profile = FormProfile(
                first_name=current_user.email.split('@')[0],
                last_name="User",
                email=current_user.email,
                phone="",
                location="",
                years_of_experience=0,
                work_authorization="",
                requires_sponsorship=False,
                notice_period="",
                salary_expectation="",
                linkedin_url="",
                github_url="",
                portfolio_url=""
            )
        else:
            profile = FormProfile(
                first_name=db_profile.first_name or current_user.email.split('@')[0],
                last_name=db_profile.last_name or "",
                email=db_profile.email or current_user.email,
                phone=db_profile.phone or "",
                location=db_profile.location or "",
                years_of_experience=len(db_profile.experience) if db_profile.experience else 0,
                work_authorization=db_profile.work_authorization or "",
                requires_sponsorship=db_profile.visa_required or False,
                notice_period=db_profile.notice_period or "",
                salary_expectation=db_profile.expected_salary or "",
                linkedin_url=db_profile.linkedin_url or "",
                github_url=db_profile.github_url or "",
                portfolio_url=db_profile.portfolio_url or ""
            )
        engine.process_application(state, profile)
        return {"status": "success", "message": "Application approved and processing resumed"}
        
    return {"status": "error", "message": "Invalid action or state"}

@router.post("/schedule")
def set_schedule(
    request: ScheduleRequest,
    current_user: User = Depends(get_current_active_user)
):
    scheduler_instance.start()
    scheduler_instance.schedule_hourly_planning(current_user.id)
    return {"status": "success", "message": f"Scheduled automated planning for user {current_user.id}"}
