import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models.user import User
from app.api.deps import get_current_active_user
from app.decision_engine.decision_engine import DecisionEngine

logger = logging.getLogger(__name__)
router = APIRouter()

class DecisionRequest(BaseModel):
    job_id: int
    resume_id: int

@router.post("/run")
def run_decision_engine(
    request: DecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Triggers the AI Decision Engine to evaluate a job against a resume.
    Generates ATS Score, Skill Gap, Recommendation, and potentially an Application Package.
    """
    try:
        engine = DecisionEngine(db=db, user=current_user)
        result = engine.process(job_id=request.job_id, resume_id=request.resume_id)
        return {"status": "success", "data": result}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Decision engine failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during decision processing.")
