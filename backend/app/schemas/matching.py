from pydantic import BaseModel, Field
from typing import List

class MatchScoreDetails(BaseModel):
    skill_match_score: float = Field(..., description="Score out of 40")
    experience_match_score: float = Field(..., description="Score out of 20")
    education_match_score: float = Field(..., description="Score out of 10")
    keyword_match_score: float = Field(..., description="Score out of 15")
    semantic_similarity_score: float = Field(..., description="Score out of 15")

class MatchingResponse(BaseModel):
    resume_id: int
    job_id: int
    final_match_score: float = Field(..., description="Total score out of 100")
    score_breakdown: MatchScoreDetails
    
    missing_skills: List[str] = Field(default_factory=list, description="Skills present in JD but missing in Resume")
    strength_areas: List[str] = Field(default_factory=list, description="Areas where the candidate exceeds or perfectly matches requirements")
    weak_areas: List[str] = Field(default_factory=list, description="Areas requiring improvement for this specific role")
    keyword_coverage: float = Field(..., description="Percentage of JD keywords found in the Resume")
    ats_readiness: str = Field(..., description="High, Medium, or Low based on keyword density and formatting match")
    education_match: bool = Field(..., description="Does the candidate meet the education requirements?")
    experience_match: bool = Field(..., description="Does the candidate meet the experience requirements?")

class MatchingRequest(BaseModel):
    resume_id: int
    job_id: int
    provider: str = "openai"
