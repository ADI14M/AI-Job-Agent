import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.application import Application, ApplicationStatus
from app.api.deps import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard")
def get_analytics_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Aggregates Analytics for the Frontend Dashboard.
    """
    total_applications = db.query(Application).filter(Application.user_id == current_user.id).count()
    
    # Group by status
    status_counts = db.query(Application.status, func.count(Application.id)).filter(Application.user_id == current_user.id).group_by(Application.status).all()
    
    funnel = {
        "Saved": 0,
        "Applied": 0,
        "Interview": 0,
        "Assessment": 0,
        "Rejected": 0,
        "Offer": 0,
        "Accepted": 0
    }
    
    for status, count in status_counts:
        funnel[status.value] = count
        
    conversion_rate = (funnel["Interview"] / funnel["Applied"] * 100) if funnel["Applied"] > 0 else 0
    offer_rate = (funnel["Offer"] / funnel["Interview"] * 100) if funnel["Interview"] > 0 else 0
    
    return {
        "total_applications": total_applications,
        "funnel": funnel,
        "metrics": {
            "application_to_interview_rate": round(conversion_rate, 2),
            "interview_to_offer_rate": round(offer_rate, 2)
        }
    }
