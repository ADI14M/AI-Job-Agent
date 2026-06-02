from pydantic import BaseModel
from typing import Optional

class ApprovalDataResponse(BaseModel):
    application_id: int
    job_title: str
    company: str
    job_description_snippet: str
    match_score: Optional[float]
    ats_score: Optional[float]
    resume_summary: Optional[str]
    cover_letter_snippet: Optional[str]
    status: str
