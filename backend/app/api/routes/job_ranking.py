import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.resume import Resume
from app.db.models.job import Job
from app.api.deps import get_current_active_user
from app.schemas.job_ranking import JobRankingRequest, JobRankingResponse
from app.agents.job_ranking_agent import JobRankingAgent

logger = logging.getLogger(__name__)
router = APIRouter()
agent = JobRankingAgent()

@router.post("/", response_model=JobRankingResponse)
def rank_jobs_for_resume(
    request: JobRankingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Rank a list of jobs for a specific resume using pre-calculated match scores and ATS scores.
    """
    resume = db.query(Resume).filter(Resume.id == request.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    jobs = db.query(Job).filter(Job.id.in_(request.job_ids), Job.user_id == current_user.id).all()
    if not jobs:
        raise HTTPException(status_code=404, detail="No matching jobs found for user")
        
    # In a full implementation, we'd query the DB for the Match Reports and ATS Reports here.
    # We will use Chroma vector DB to pull semantic similarity if available
    from app.vector_db.chroma_client import ChromaClient
    from app.db.models.application_package import ApplicationPackage
    
    mock_match_scores = {}
    mock_ats_scores = {}
    
    # Try retrieving from ApplicationPackage
    for job in jobs:
        pkg = db.query(ApplicationPackage).filter(
            ApplicationPackage.job_id == job.id, 
            ApplicationPackage.user_id == current_user.id
        ).first()
        if pkg and pkg.ats_score:
            mock_match_scores[job.id] = pkg.ats_score / 100.0
            mock_ats_scores[job.id] = pkg.ats_score / 100.0
        else:
            # Simple fallback
            mock_match_scores[job.id] = 0.50
            mock_ats_scores[job.id] = 0.50
    
    ranked_results = agent.rank_jobs(
        resume=resume,
        jobs=jobs,
        match_scores=mock_match_scores,
        ats_scores=mock_ats_scores,
        preferences=request.preferences
    )
    
    return JobRankingResponse(
        resume_id=resume.id,
        ranked_jobs=ranked_results
    )
