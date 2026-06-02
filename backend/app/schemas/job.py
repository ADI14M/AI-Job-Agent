from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class JobParsedData(BaseModel):
    title: str = Field(description="Job title")
    company: str = Field(description="Company offering the job")
    location: Optional[str] = Field(None, description="Job location (City, State, Country, or Remote)")
    employment_type: Optional[str] = Field(None, description="Employment type e.g., Full-time, Contract, Part-time")
    salary: Optional[str] = Field(None, description="Salary range or compensation details if mentioned")
    required_skills: List[str] = Field(default_factory=list, description="Must-have skills for the role")
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have or bonus skills")
    responsibilities: List[str] = Field(default_factory=list, description="List of key responsibilities and duties")
    experience_requirements: Optional[str] = Field(None, description="Years of experience or seniority required")
    education_requirements: Optional[str] = Field(None, description="Degrees or educational background required")
    keywords: List[str] = Field(default_factory=list, description="Important SEO or ATS keywords found in the description")

class JobCreate(BaseModel):
    raw_text: str
    apply_url: Optional[str] = None
    provider: Optional[str] = "openai"

class JobResponse(BaseModel):
    id: int
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    apply_url: Optional[str] = None
    parsed_data: Optional[JobParsedData] = None
    created_at: datetime

    class Config:
        from_attributes = True
