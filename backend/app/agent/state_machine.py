from app.db.models.agent_state import AgentStateEnum, AgentApplicationState
from app.core.logger import system_logger
from sqlalchemy.orm import Session

class StateMachine:
    @staticmethod
    def transition(db: Session, agent_state: AgentApplicationState, new_state: AgentStateEnum, log_msg: str = ""):
        old_state = agent_state.current_state
        agent_state.current_state = new_state.value
        
        if log_msg:
            current_logs = agent_state.logs or []
            current_logs.append(f"[{old_state} -> {new_state.value}] {log_msg}")
            # Ensure we don't mutate in place without SQLAlchemy noticing
            agent_state.logs = list(current_logs)
            
        system_logger.info(f"AgentState {agent_state.id} transitioned: {old_state} -> {new_state.value}")
        
        db.commit()
        db.refresh(agent_state)
        return agent_state
