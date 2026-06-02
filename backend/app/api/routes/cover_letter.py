import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.resume import Resume
from app.db.models.job import Job
from app.db.models.cover_letter import CoverLetter
from app.agents.cover_letter_agent import generate_cover_letter
from app.schemas.cover_letter import CoverLetterRequest, CoverLetterResponse

from app.db.models.user import User
from app.api.deps import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=CoverLetterResponse)
def create_cover_letter(
    request: CoverLetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a tailored cover letter using the candidate's Resume and target Job Description.
    """
    resume = db.query(Resume).filter(Resume.id == request.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
            
    try:
        cl_data = generate_cover_letter(resume, job, request.company_name, provider_name=request.provider)
        if not cl_data:
            raise ValueError("Cover Letter Agent returned None")
            
        # Generate PDF
        from app.utils.document_generator import generate_cover_letter_pdf
        import uuid
        pdf_filename = f"cover_letter_{resume.id}_{job.id}_{uuid.uuid4().hex[:8]}.pdf"
        pdf_filepath = generate_cover_letter_pdf(cl_data.content, pdf_filename)
            
        db_cl = CoverLetter(
            resume_id=resume.id,
            job_id=job.id,
            content=cl_data.content,
            file_path=pdf_filepath
        )
        
        db.add(db_cl)
        db.commit()
        db.refresh(db_cl)
        
        return db_cl
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error during Cover Letter generation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error during Cover Letter generation")
