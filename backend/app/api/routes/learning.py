import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.api.deps import get_current_active_user
from app.agents.learning_agent import LearningAgent
from app.schemas.learning import LearningResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/train", response_model=LearningResponse)
def train_learning_engine(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Trigger the Learning Agent to dynamically re-weight the Job Ranking algorithms 
    based on the user's historical Application success/failure rates.
    """
    try:
        agent = LearningAgent(db)
        prefs = agent.train_user_preferences(current_user.id)
        
        return LearningResponse(
            user_id=current_user.id,
            weight_match_score=prefs.weight_match_score,
            weight_ats_score=prefs.weight_ats_score,
            weight_salary_score=prefs.weight_salary_score,
            weight_location_score=prefs.weight_location_score,
            status="Model Retrained Successfully"
        )
    except Exception as e:
        logger.error(f"Error training learning engine: {e}")
        raise HTTPException(status_code=500, detail="Failed to train learning engine")
