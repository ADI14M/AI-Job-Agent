from pydantic import BaseModel
from typing import List, Optional

class JobRankingRequest(BaseModel):
    resume_id: int
    job_ids: List[int]
    preferences: Optional[dict] = None

class JobRankResult(BaseModel):
    job_id: int
    total_score: float
    match_score: float
    ats_score: float
    salary_score: float
    location_score: float
    rank_reasoning: str

class JobRankingResponse(BaseModel):
    resume_id: int
    ranked_jobs: List[JobRankResult]
