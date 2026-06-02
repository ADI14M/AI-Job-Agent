from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ATSBreakdown(BaseModel):
    formatting_score: float = Field(..., description="Score out of 20")
    length_score: float = Field(..., description="Score out of 10")
    section_completeness_score: float = Field(..., description="Score out of 20")
    action_verbs_score: float = Field(..., description="Score out of 20")
    quantified_achievements_score: float = Field(..., description="Score out of 30")

class ATSRecommendation(BaseModel):
    category: str = Field(description="e.g., Formatting, Action Verbs, Quantified Achievements")
    priority: str = Field(description="Critical, Important, Optional")
    suggestion: str = Field(description="Actionable advice")

class ATSReportData(BaseModel):
    overall_score: float = Field(..., description="Total ATS score out of 100")
    breakdown: ATSBreakdown
    recommendations: List[ATSRecommendation]

class ATSResponse(BaseModel):
    id: int
    resume_id: int
    job_id: Optional[int] = None
    overall_score: float
    breakdown: ATSBreakdown
    recommendations: List[ATSRecommendation]
    created_at: datetime

    class Config:
        from_attributes = True

class ATSRequest(BaseModel):
    resume_id: int
    job_id: Optional[int] = None
    provider: str = "openai"
