from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base
import enum

class AgentStateEnum(str, enum.Enum):
    DISCOVERED = "DISCOVERED"
    MATCHED = "MATCHED"
    ANALYZED = "ANALYZED"
    PACKAGE_READY = "PACKAGE_READY"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    SUBMITTED = "SUBMITTED"
    ASSESSMENT = "ASSESSMENT"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    FAILED = "FAILED"

class AgentApplicationState(Base):
    """
    Tracks the active state of an AI application process for a specific job.
    """
    __tablename__ = "agent_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    
    current_state = Column(String, default=AgentStateEnum.DISCOVERED.value, nullable=False)
    
    # Metadata for execution
    provider = Column(String, nullable=True) # e.g. "LinkedIn", "Greenhouse"
    application_package_id = Column(Integer, ForeignKey("application_packages.id", ondelete="SET NULL"), nullable=True)
    
    requires_human_review = Column(Boolean, default=False)
    human_approved = Column(Boolean, default=False)
    
    # Error Handling & Retries
    retry_count = Column(Integer, default=0)
    last_error = Column(String, nullable=True)
    screenshot_path = Column(String, nullable=True)
    
    logs = Column(JSON, nullable=True, default=list) # Array of execution log strings
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
