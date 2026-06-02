from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CoverLetterData(BaseModel):
    content: str = Field(..., description="The fully generated cover letter text")

class CoverLetterRequest(BaseModel):
    resume_id: int
    job_id: int
    company_name: Optional[str] = None
    provider: str = "openai"

class CoverLetterResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int
    content: str
    file_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
