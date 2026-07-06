import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.db.session import get_db
from app.db.models.user import User
from app.api.deps import get_current_active_user
from app.career_memory.analytics import CareerAnalytics
from app.career_memory.memory_engine import MemoryEngine
from app.career_memory.models import AnalyticsReport, MemorySearchResult

logger = logging.getLogger(__name__)
router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    limit: int = 5

@router.get("/analytics", response_model=AnalyticsReport)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Fetches the user's aggregated career memory analytics.
    """
    try:
        report = CareerAnalytics.generate_report(db, current_user.id)
        return report
    except Exception as e:
        logger.error(f"Failed to generate analytics report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/search", response_model=List[MemorySearchResult])
def search_memory(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Perform semantic search on the user's career ledger.
    """
    try:
        engine = MemoryEngine(db, current_user)
        results = engine.search_memory(request.query, request.limit)
        return results
    except Exception as e:
        logger.error(f"Failed to search career memory: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
