from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class FormProfile(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    location: str
    years_of_experience: int
    work_authorization: str
    requires_sponsorship: bool
    notice_period: str
    salary_expectation: str
    linkedin_url: str
    github_url: str
    portfolio_url: str

class ExecutionResult(BaseModel):
    success: bool
    final_state: str
    logs: List[str]
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None

class QAConfidence(BaseModel):
    answer: str
    confidence_score: int = Field(..., description="0-100 score indicating certainty of the answer based ONLY on the user profile")
    requires_human_review: bool = Field(..., description="True if confidence is low or information is missing")
