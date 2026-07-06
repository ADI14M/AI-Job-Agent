from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class ApplicationPackage(Base):
    __tablename__ = "application_packages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    base_resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    
    # Paths to generated documents
    optimized_resume_pdf = Column(String, nullable=True)
    optimized_resume_docx = Column(String, nullable=True)
    cover_letter_pdf = Column(String, nullable=True)
    cover_letter_docx = Column(String, nullable=True)
    
    # Engine output metrics
    ats_score = Column(Float, nullable=True)
    recommendation = Column(String, nullable=True) # Apply, Maybe, Skip
    decision_reasoning = Column(String, nullable=True)
    skill_gap_json = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
