from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db.models.application import ApplicationStatus

class ApplicationCreate(BaseModel):
    job_id: int
    resume_id: Optional[int] = None
    cover_letter_id: Optional[int] = None
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    resume_id: Optional[int]
    cover_letter_id: Optional[int]
    status: ApplicationStatus
    notes: Optional[str]
    applied_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
