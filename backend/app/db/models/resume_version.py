from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, index=True)
    base_resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    
    target_role = Column(String, nullable=False) # e.g. "AI Engineer"
    optimized_data = Column(JSON, nullable=False)
    file_path = Column(String, nullable=True) # If we export it to PDF later
    
    created_at = Column(DateTime, default=datetime.utcnow)
