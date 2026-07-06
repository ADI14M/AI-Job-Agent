from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models.user import User
from app.api.deps import get_current_active_user
from app.job_discovery.discovery_engine import DiscoveryEngine
import logging

# Ensure providers are loaded and registered
from app.job_discovery.providers import linkedin, wellfound, greenhouse, lever, ashby

logger = logging.getLogger(__name__)
router = APIRouter()

class SearchRequest(BaseModel):
    keywords: str
    location: str
    experience: str = ""
    remote: bool = False
    salary: str = ""
    providers: List[str]

@router.post("/search")
def search_jobs(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Modular Job Discovery endpoint using the new DiscoveryEngine.
    """
    if not request.providers:
        raise HTTPException(status_code=400, detail="At least one provider must be specified.")

    engine = DiscoveryEngine(db=db, user_id=current_user.id)
    
    # Passing limit=200 for production load
    results = engine.run(
        query=request.keywords,
        location=request.location,
        providers=request.providers,
        limit=200 
    )
    
    return results
