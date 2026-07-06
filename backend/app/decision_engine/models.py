from pydantic import BaseModel, Field
from typing import List, Optional

class ATSEvaluation(BaseModel):
    overall_score: int = Field(..., description="0 to 100")
    formatting_score: int = Field(..., description="0 to 100")
    keywords_score: int = Field(..., description="0 to 100")
    experience_score: int = Field(..., description="0 to 100")
    projects_score: int = Field(..., description="0 to 100")
    skills_score: int = Field(..., description="0 to 100")
    education_score: int = Field(..., description="0 to 100")
    achievements_score: int = Field(..., description="0 to 100")
    deductions: List[str] = Field(..., description="List of reasons for lost points")

class SkillGap(BaseModel):
    existing_skills: List[str]
    missing_skills: List[str]
    recommended_learning_path: List[str]
    estimated_learning_time: str

class CoverLetterData(BaseModel):
    content: str = Field(..., description="The complete text of the generated cover letter")

class ResumeOptimizationData(BaseModel):
    optimized_content: str = Field(..., description="The optimized markdown version of the resume. NEVER invent experience.")

class DecisionResult(BaseModel):
    recommendation: str = Field(..., description="Must be exactly 'Apply', 'Maybe', or 'Skip'")
    overall_score: int = Field(..., description="0-100 score indicating fit")
    reasoning: str
    pros: List[str]
    cons: List[str]
    missing_skills: List[str]
    estimated_interview_probability: str
    estimated_resume_strength: str
    estimated_skill_match: str
