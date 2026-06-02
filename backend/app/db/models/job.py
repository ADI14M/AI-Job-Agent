from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    # The source URL for the job application if available
    apply_url = Column(String, nullable=True)
    
    # Store Raw Job Description Text
    raw_text = Column(Text, nullable=False)
    
    # Store Structured JSON parsing results
    parsed_data = Column(JSON, nullable=True)
    
    # We can promote some fields as direct columns for easier DB querying (e.g., location, salary)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    embeddings = relationship("JobEmbedding", back_populates="job", cascade="all, delete-orphan")


class JobEmbedding(Base):
    __tablename__ = "job_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    
    # ChromaDB reference ID
    chroma_doc_id = Column(String, nullable=False, unique=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    job = relationship("Job", back_populates="embeddings")
