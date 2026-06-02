from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class ResumeOptimizationRequest(BaseModel):
    base_resume_id: int
    target_role: str
    provider: str = "openai"

class ResumeVersionResponse(BaseModel):
    id: int
    base_resume_id: int
    target_role: str
    optimized_data: Dict[str, Any]
    file_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
