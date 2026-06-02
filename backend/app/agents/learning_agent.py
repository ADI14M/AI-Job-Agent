import logging
from sqlalchemy.orm import Session
from app.db.models.user_preferences import UserPreferences
from app.db.models.application import Application, ApplicationStatus

logger = logging.getLogger(__name__)

class LearningAgent:
    """
    Adjusts ranking weights based on user Offer/Rejection events to learn what the market actually values.
    """
    def __init__(self, db: Session):
        self.db = db

    def train_user_preferences(self, user_id: int) -> UserPreferences:
        prefs = self.db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            self.db.add(prefs)
            
        # Very simple ML heuristic algorithm
        offers = self.db.query(Application).filter(Application.user_id == user_id, Application.status == ApplicationStatus.OFFER).count()
        rejections = self.db.query(Application).filter(Application.user_id == user_id, Application.status == ApplicationStatus.REJECTED).count()
        
        # If getting rejected a lot, heavily emphasize ATS scores to pass the first filter
        if rejections > offers * 3:
            logger.info("High rejection rate detected. Re-weighting to favor ATS scores.")
            prefs.weight_ats_score = min(0.6, prefs.weight_ats_score + 0.1)
            prefs.weight_match_score = max(0.2, prefs.weight_match_score - 0.1)
            
        # If getting offers, the current balance is working or we should optimize for salary/location matching
        elif offers > 0 and offers >= rejections:
            logger.info("High offer rate detected. Re-weighting to favor Salary and Location preferences.")
            prefs.weight_salary_score = min(0.3, prefs.weight_salary_score + 0.05)
            prefs.weight_location_score = min(0.3, prefs.weight_location_score + 0.05)
            prefs.weight_ats_score = max(0.1, prefs.weight_ats_score - 0.1)
            
        # Normalize weights to sum to ~1.0
        total = prefs.weight_match_score + prefs.weight_ats_score + prefs.weight_salary_score + prefs.weight_location_score
        prefs.weight_match_score /= total
        prefs.weight_ats_score /= total
        prefs.weight_salary_score /= total
        prefs.weight_location_score /= total
        
        self.db.commit()
        self.db.refresh(prefs)
        return prefs
