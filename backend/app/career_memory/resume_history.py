from sqlalchemy.orm import Session
from app.db.models.resume_version import ResumeVersion

class ResumeHistory:
    @staticmethod
    def get_resume_stats(db: Session, user_id: int):
        # A simple aggregation of resume performance
        resumes = db.query(ResumeVersion).filter(ResumeVersion.id > 0).all() # Just return existing resumes for now
        return resumes
