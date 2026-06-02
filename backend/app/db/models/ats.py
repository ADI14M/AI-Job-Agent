from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class ATSReport(Base):
    __tablename__ = "ats_reports"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    
    # Optional job_id if the ATS score is specific to a job description
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    
    overall_score = Column(Float, nullable=False)
    
    # Store detailed analysis as JSON
    breakdown = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships can be defined if needed
    # resume = relationship("Resume")
    # job = relationship("Job")
