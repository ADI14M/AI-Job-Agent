from sqlalchemy.orm import Session
from app.db.models.agent_state import AgentApplicationState, AgentStateEnum
from app.db.models.job import Job
from app.db.models.application_package import ApplicationPackage
from app.core.logger import system_logger

class Planner:
    """
    Decides which jobs to process, priority, and if human review is needed.
    """
    @staticmethod
    def plan_next_actions(db: Session, user_id: int):
        system_logger.info("Planner evaluating next actions...")
        
        # Find jobs that have application packages but no agent state yet
        packages = db.query(ApplicationPackage).filter(
            ApplicationPackage.user_id == user_id,
            ApplicationPackage.recommendation == "Apply"
        ).all()
        
        for pkg in packages:
            existing = db.query(AgentApplicationState).filter(
                AgentApplicationState.user_id == user_id,
                AgentApplicationState.job_id == pkg.job_id
            ).first()
            
            if not existing:
                requires_review = pkg.ats_score < 75 # Require human review if ATS score is low
                
                new_state = AgentApplicationState(
                    user_id=user_id,
                    job_id=pkg.job_id,
                    provider="Generic", # In real system, extract from Job URL
                    application_package_id=pkg.id,
                    requires_human_review=requires_review,
                    current_state=AgentStateEnum.PACKAGE_READY.value
                )
                db.add(new_state)
                db.commit()
                system_logger.info(f"Planner initiated new Agent State for Job {pkg.job_id}")
