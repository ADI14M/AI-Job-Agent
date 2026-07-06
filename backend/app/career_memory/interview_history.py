from sqlalchemy.orm import Session
from app.db.models.career_memory import MemoryInterview
from app.career_memory.memory_engine import MemoryEngine

class InterviewHistory:
    @staticmethod
    def log_interview(db: Session, user, company_id: int, role: str, outcome: str):
        interview = MemoryInterview(
            user_id=user.id,
            company_id=company_id,
            role=role,
            outcome=outcome
        )
        db.add(interview)
        db.commit()
        
        engine = MemoryEngine(db, user)
        engine.record_event(
            event_type="INTERVIEW",
            description=f"Interviewed for {role}. Outcome: {outcome}",
            metadata={"company_id": company_id}
        )
        return interview
