from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ExperienceSchema(BaseModel):
    company: str = Field(description="Name of the company")
    title: str = Field(description="Job title")
    location: Optional[str] = Field(None, description="Job location")
    start_date: Optional[str] = Field(None, description="Start date (e.g. MM/YYYY)")
    end_date: Optional[str] = Field(None, description="End date (e.g. MM/YYYY or Present)")
    description: Optional[str] = Field(None, description="Detailed responsibilities and accomplishments")
    technologies: List[str] = Field(default_factory=list, description="Technologies used in this role")

class EducationSchema(BaseModel):
    institution: str = Field(description="Name of the university or institution")
    degree: str = Field(description="Degree obtained (e.g. BS in Computer Science)")
    location: Optional[str] = Field(None, description="Location of the institution")
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End date or expected graduation")
    gpa: Optional[str] = Field(None, description="GPA if mentioned")

class ProjectSchema(BaseModel):
    name: str = Field(description="Name of the project")
    description: Optional[str] = Field(None, description="Project description and accomplishments")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    link: Optional[str] = Field(None, description="URL to project if available")

class ResumeParsedData(BaseModel):
    name: str = Field(description="Full name of the candidate")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Candidate's location (City, State, Country)")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    portfolio: Optional[str] = Field(None, description="Personal website or portfolio URL")
    summary: Optional[str] = Field(None, description="Professional summary or objective statement")
    skills: List[str] = Field(default_factory=list, description="List of all skills mentioned")
    education: List[EducationSchema] = Field(default_factory=list, description="List of educational background")
    experience: List[ExperienceSchema] = Field(default_factory=list, description="List of professional experience")
    projects: List[ProjectSchema] = Field(default_factory=list, description="List of personal or professional projects")
    certifications: List[str] = Field(default_factory=list, description="List of certifications")
    achievements: List[str] = Field(default_factory=list, description="List of awards or achievements")

class ResumeResponse(BaseModel):
    id: int
    filename: str
    parsed_data: Optional[ResumeParsedData] = None
    created_at: datetime

    class Config:
        from_attributes = True
