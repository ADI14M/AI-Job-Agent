from sqlalchemy.orm import Session
from app.career_memory.memory_store import MemoryStore

class CompanyProfiles:
    @staticmethod
    def track_interaction(db: Session, user_id: int, company_name: str, interaction_type: str):
        company = MemoryStore.get_or_create_company(db, user_id, company_name)
        if interaction_type == "viewed":
            company.jobs_seen += 1
        elif interaction_type == "applied":
            company.jobs_applied += 1
        elif interaction_type == "interview":
            company.interview_count += 1
        elif interaction_type == "rejected":
            company.rejection_count += 1
        elif interaction_type == "offer":
            company.offer_count += 1
        db.commit()
        return company
