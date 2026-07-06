from sqlalchemy.orm import Session
from typing import Optional
from app.db.models.career_memory import MemoryCompany, MemoryEvent, MemoryInterview, MemoryRecruiter

class MemoryStore:
    @staticmethod
    def get_or_create_company(db: Session, user_id: int, name: str) -> MemoryCompany:
        company = db.query(MemoryCompany).filter(MemoryCompany.user_id == user_id, MemoryCompany.name == name).first()
        if not company:
            company = MemoryCompany(user_id=user_id, name=name)
            db.add(company)
            db.commit()
            db.refresh(company)
        return company

    @staticmethod
    def log_event(db: Session, user_id: int, event_type: str, description: str, metadata: dict = None, chroma_doc_id: str = None) -> MemoryEvent:
        event = MemoryEvent(
            user_id=user_id,
            event_type=event_type,
            description=description,
            metadata_json=metadata,
            chroma_doc_id=chroma_doc_id
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
