from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True) # Could be nullable if jobs are shared globally
    apply_url = Column(String, nullable=True)
    raw_text = Column(String, nullable=False)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String, nullable=True)
    parsed_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class JobEmbedding(Base):
    __tablename__ = "job_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    chroma_doc_id = Column(String, index=True, nullable=False)
