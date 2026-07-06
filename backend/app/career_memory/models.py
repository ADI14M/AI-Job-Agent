from pydantic import BaseModel, Field
from typing import List, Optional, Any

class MemorySearchResult(BaseModel):
    id: str
    event_type: str
    description: str
    metadata: dict
    similarity: float

class AnalyticsReport(BaseModel):
    application_success_rate: float
    interview_rate: float
    offer_rate: float
    average_ats_score: float
    top_performing_resume_id: Optional[int]
    most_common_missing_skills: List[str]
    most_targeted_companies: List[str]
    most_targeted_roles: List[str]
    monthly_statistics: dict
