import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.job import Job
from app.api.deps import get_current_active_user
from app.schemas.job_discovery import JobDiscoveryRequest, JobDiscoveryResponse
from app.agents.job_discovery_agent import JobDiscoveryAgent
from app.agents.jd_agent import process_and_store_job

logger = logging.getLogger(__name__)
router = APIRouter()

# Instantiate the singleton agent
agent = JobDiscoveryAgent()

@router.post("/run", response_model=JobDiscoveryResponse)
def run_job_discovery(
    request: JobDiscoveryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Run the Job Discovery Agent to find jobs across specified platforms.
    Deduplicates results and stores them automatically in the Jobs table.
    """
    discovered_jobs = agent.run_discovery(
        query=request.query, 
        location=request.location, 
        platforms=request.platforms, 
        limit=request.limit
    )
    
    new_jobs_added = 0
    
    # Simple Deduplication and insertion logic
    for dj in discovered_jobs:
        # Check if URL exists for this user
        existing = db.query(Job).filter(Job.apply_url == dj.apply_url, Job.user_id == current_user.id).first()
        if not existing:
            # Note: In production we would pass this to the LLM JD Parser asynchronously.
            # For discovery, we will store the raw scraped text directly to save tokens, 
            # or run it through `process_and_store_job` if we have full text.
            try:
                db_job = Job(
                    user_id=current_user.id,
                    apply_url=dj.apply_url,
                    raw_text=dj.description,
                    title=dj.title,
                    company=dj.company,
                    location=dj.location,
                    parsed_data={} # Parse later during Job Matching phase if needed
                )
                db.add(db_job)
                new_jobs_added += 1
            except Exception as e:
                logger.error(f"Failed to add job to DB: {e}")
                
    db.commit()
    
    return JobDiscoveryResponse(
        status="Success",
        total_found=len(discovered_jobs),
        new_jobs_added=new_jobs_added,
        jobs=discovered_jobs
    )
