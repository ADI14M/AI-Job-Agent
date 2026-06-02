from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JobDiscoveryRequest(BaseModel):
    query: str
    location: str
    platforms: List[str] = ["linkedin", "indeed", "glassdoor"]
    limit: int = 10

class DiscoveredJob(BaseModel):
    title: str
    company: str
    location: str
    salary: Optional[str] = None
    description: str
    apply_url: str
    platform: str

class JobDiscoveryResponse(BaseModel):
    status: str
    total_found: int
    new_jobs_added: int
    jobs: List[DiscoveredJob]
