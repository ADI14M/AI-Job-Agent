from pydantic import BaseModel

class LearningResponse(BaseModel):
    user_id: int
    weight_match_score: float
    weight_ats_score: float
    weight_salary_score: float
    weight_location_score: float
    status: str
