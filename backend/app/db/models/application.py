from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base
import enum

class ApplicationStatus(str, enum.Enum):
    SAVED = "Saved"
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    ASSESSMENT = "Assessment"
    REJECTED = "Rejected"
    OFFER = "Offer"
    ACCEPTED = "Accepted"

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True) # Optimized resume version used
    cover_letter_id = Column(Integer, ForeignKey("cover_letters.id", ondelete="SET NULL"), nullable=True)
    
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.SAVED, nullable=False)
    notes = Column(String, nullable=True)
    
    applied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
