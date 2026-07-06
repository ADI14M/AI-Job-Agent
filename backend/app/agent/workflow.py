from sqlalchemy.orm import Session
from app.db.models.agent_state import AgentApplicationState, AgentStateEnum
from app.agent.state_machine import StateMachine
from app.agent.application_executor import ApplicationExecutor
from app.agent.models import FormProfile
from app.career_memory.memory_engine import MemoryEngine
from app.agent.notification_service import NotificationService
from app.core.logger import system_logger

class WorkflowEngine:
    def __init__(self, db: Session, user):
        self.db = db
        self.user = user
        self.memory = MemoryEngine(db, user)

    def process_application(self, agent_state: AgentApplicationState, profile: FormProfile):
        system_logger.info(f"Processing application state for Job {agent_state.job_id}")
        
        # State: DISCOVERED -> MATCHED
        if agent_state.current_state == AgentStateEnum.DISCOVERED.value:
            StateMachine.transition(self.db, agent_state, AgentStateEnum.MATCHED, "Job matched to user profile")
            
        # State: MATCHED -> ANALYZED
        if agent_state.current_state == AgentStateEnum.MATCHED.value:
            # Here we would normally trigger the Decision Engine
            StateMachine.transition(self.db, agent_state, AgentStateEnum.ANALYZED, "Job analyzed by Decision Engine")

        # State: ANALYZED -> PACKAGE_READY
        if agent_state.current_state == AgentStateEnum.ANALYZED.value:
            # Here we would normally generate documents
            StateMachine.transition(self.db, agent_state, AgentStateEnum.PACKAGE_READY, "Application package generated")
            self.memory.record_event("PACKAGE_READY", f"Application package generated for Job {agent_state.job_id}")

        # State: PACKAGE_READY -> READY_FOR_REVIEW or SUBMITTED
        if agent_state.current_state == AgentStateEnum.PACKAGE_READY.value:
            if agent_state.requires_human_review and not agent_state.human_approved:
                StateMachine.transition(self.db, agent_state, AgentStateEnum.READY_FOR_REVIEW, "Awaiting human review")
                NotificationService.notify(self.db, self.user.id, "Application ready for review.", "WARNING")
                return # Stop processing until human approves
            
            # Execute actual automation
            provider = agent_state.provider or "Generic"
            executor_class = ApplicationExecutor.get_executor(provider)
            # In real system, we fetch job URL from DB
            job_url = "https://example.com/job" 
            executor = executor_class(self.user.id, profile, job_url)
            
            result = executor.execute(dry_run=True)
            
            if result.success:
                StateMachine.transition(self.db, agent_state, AgentStateEnum.SUBMITTED, "Application successfully submitted")
                self.memory.record_event("SUBMITTED", f"Successfully applied to Job {agent_state.job_id}")
                NotificationService.notify(self.db, self.user.id, f"Successfully applied to {provider} job.", "SUCCESS")
            else:
                agent_state.last_error = result.error_message
                agent_state.screenshot_path = result.screenshot_path
                StateMachine.transition(self.db, agent_state, AgentStateEnum.FAILED, f"Failed: {result.error_message}")
                self.memory.record_event("FAILED", f"Application failed for Job {agent_state.job_id}")
                NotificationService.notify(self.db, self.user.id, f"Failed to apply to {provider} job.", "ERROR")
