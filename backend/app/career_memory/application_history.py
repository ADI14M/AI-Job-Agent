from sqlalchemy.orm import Session
from app.db.models.application import Application
from app.career_memory.memory_engine import MemoryEngine

class ApplicationHistory:
    @staticmethod
    def update_status(db: Session, user, app_id: int, new_status: str):
        app = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
        if app:
            old_status = app.status
            app.status = new_status
            db.commit()
            
            # Record in Semantic Memory
            engine = MemoryEngine(db, user)
            engine.record_event(
                event_type="APPLICATION_UPDATE",
                description=f"Application status changed from {old_status} to {new_status} for Job {app.job_id}",
                metadata={"app_id": app.id, "job_id": app.job_id}
            )
        return app
