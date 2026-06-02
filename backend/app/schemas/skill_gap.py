from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class GapItem(BaseModel):
    name: str = Field(description="Name of the missing skill, tool, or certification")
    priority: str = Field(description="Critical, Important, or Optional")
    category: str = Field(description="Skill, Tool, or Certification")

class SkillGapReportData(BaseModel):
    missing_items: List[GapItem]

class SkillGapResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int
    report_data: SkillGapReportData
    created_at: datetime

    class Config:
        from_attributes = True

class SkillGapRequest(BaseModel):
    resume_id: int
    job_id: int
    provider: str = "openai"
