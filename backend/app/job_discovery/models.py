from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class DiscoveredJob(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary: Optional[str] = None
    experience: Optional[str] = None
    description: str
    skills: List[str] = []
    url: str
    source: str
    posted_date: Optional[str] = None
    company_logo: Optional[str] = None
    remote: bool = False
