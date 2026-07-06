from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models.user import User
from app.api.deps import get_current_active_user
from app.db.models.application import Application
from app.db.models.job import Job
from typing import Dict, Any

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    
    total_applications = db.query(Application).filter(Application.user_id == current_user.id).count()
    
    # Status breakdown
    statuses = db.query(Application.status, func.count(Application.id)).filter(Application.user_id == current_user.id).group_by(Application.status).all()
    status_counts = {status: count for status, count in statuses}
    
    # Calculate derived stats
    interviews = status_counts.get("Interviewing", 0) + status_counts.get("Interview", 0)
    offers = status_counts.get("Offer", 0) + status_counts.get("Accepted", 0)
    
    response_rate = 0
    if total_applications > 0:
        responded = total_applications - status_counts.get("Applied", 0) - status_counts.get("Pending", 0)
        response_rate = round((responded / total_applications) * 100, 1)
        
    return {
        "status": "success",
        "data": {
            "total_applications": total_applications,
            "interviews": interviews,
            "offers": offers,
            "response_rate": f"{response_rate}%",
            "pipeline": status_counts
        }
    }
