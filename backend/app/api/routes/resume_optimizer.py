import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.resume import Resume
from app.db.models.resume_version import ResumeVersion
from app.agents.resume_optimizer_agent import optimize_resume_for_role
from app.schemas.resume_optimizer import ResumeOptimizationRequest, ResumeVersionResponse

from app.db.models.user import User
from app.api.deps import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=ResumeVersionResponse)
def create_optimized_resume(
    request: ResumeOptimizationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate an optimized Resume targeted at a specific role without fabricating experience.
    """
    resume = db.query(Resume).filter(Resume.id == request.base_resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Base Resume not found")
            
    try:
        optimized_data = optimize_resume_for_role(resume, request.target_role, provider_name=request.provider)
        if not optimized_data:
            raise ValueError("Resume Optimizer Agent returned None")
            
        # Generate PDF
        from app.utils.document_generator import generate_resume_pdf
        import uuid
        pdf_filename = f"optimized_resume_{resume.id}_{uuid.uuid4().hex[:8]}.pdf"
        pdf_filepath = generate_resume_pdf(optimized_data.model_dump(), pdf_filename)
            
        db_version = ResumeVersion(
            base_resume_id=resume.id,
            target_role=request.target_role,
            optimized_data=optimized_data.model_dump(),
            file_path=pdf_filepath
        )
        
        db.add(db_version)
        db.commit()
        db.refresh(db_version)
        
        return db_version
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error during Resume Optimization: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error during Resume optimization")
