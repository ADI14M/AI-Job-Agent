import logging
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.api.deps import get_current_active_user
from app.agents.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

async def run_orchestrator_bg(user_id: int, db: Session):
    orchestrator = AgentOrchestrator(db)
    await orchestrator.run_autonomous_loop(user_id)

@router.post("/trigger")
async def trigger_orchestrator(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Manually triggers the autonomous Agent Orchestrator loop.
    In a real production environment, this would run on a Cron schedule (Celery/APScheduler).
    """
    background_tasks.add_task(run_orchestrator_bg, current_user.id, db)
    return {"status": "Autonomous Orchestrator Loop triggered in background."}
