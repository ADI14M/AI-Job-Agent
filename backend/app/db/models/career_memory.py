from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class MemoryCompany(Base):
    __tablename__ = "memory_companies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, index=True, nullable=False)
    website = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    career_page = Column(String, nullable=True)
    
    # Aggregated metrics for easy querying
    average_match_score = Column(Float, default=0.0)
    jobs_seen = Column(Integer, default=0)
    jobs_applied = Column(Integer, default=0)
    interview_count = Column(Integer, default=0)
    offer_count = Column(Integer, default=0)
    rejection_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MemoryInterview(Base):
    __tablename__ = "memory_interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("memory_companies.id", ondelete="SET NULL"), nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    
    role = Column(String, nullable=False)
    rounds = Column(Integer, default=1)
    interview_type = Column(String, nullable=True) # e.g. "Technical", "Behavioral"
    questions_asked = Column(JSON, nullable=True)
    outcome = Column(String, nullable=True) # e.g. "Passed", "Rejected", "Pending"
    feedback = Column(Text, nullable=True)
    
    interview_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class MemoryRecruiter(Base):
    __tablename__ = "memory_recruiters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("memory_companies.id", ondelete="SET NULL"), nullable=True)
    
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class MemoryEvent(Base):
    """
    The ledger of all career events (e.g., "Applied to Microsoft", "Resume v12 produced interview").
    These events will be vectorized into ChromaDB.
    """
    __tablename__ = "memory_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    event_type = Column(String, index=True, nullable=False) # e.g. "APPLICATION", "INTERVIEW", "RESUME_GEN"
    description = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True) # Storing references to job_id, resume_id, etc.
    
    chroma_doc_id = Column(String, nullable=True, index=True) # Link to semantic search vector
    
    created_at = Column(DateTime, default=datetime.utcnow)
