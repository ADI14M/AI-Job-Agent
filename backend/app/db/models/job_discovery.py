from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from datetime import datetime
from app.db.session import Base

class JobDiscovery(Base):
    __tablename__ = "job_discovery"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, index=True, nullable=False)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    hash = Column(String, unique=True, index=True, nullable=False)
    raw_json = Column(JSON, nullable=False)
    normalized_json = Column(JSON, nullable=False)
    embedding_status = Column(String, default="pending")  # pending, completed, failed
    match_score = Column(Float, nullable=True)
    application_status = Column(String, default="unseen")  # unseen, viewed, applied, rejected
