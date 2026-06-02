from sqlalchemy import Column, Integer, Float, ForeignKey
from app.db.session import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # ML dynamically adjusted weights for Job Ranking Engine
    weight_match_score = Column(Float, default=0.5)
    weight_ats_score = Column(Float, default=0.3)
    weight_salary_score = Column(Float, default=0.1)
    weight_location_score = Column(Float, default=0.1)
