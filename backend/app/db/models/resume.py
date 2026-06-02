from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, index=True)
    raw_text = Column(String)
    parsed_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class ResumeEmbedding(Base):
    __tablename__ = "resume_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"))
    chroma_doc_id = Column(String, index=True)
