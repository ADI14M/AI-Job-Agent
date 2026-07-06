import os
from app.core.logger import system_logger

class LoginManager:
    SESSION_DIR = "storage/sessions"
    
    @classmethod
    def ensure_storage(cls):
        if not os.path.exists(cls.SESSION_DIR):
            os.makedirs(cls.SESSION_DIR)
            
    @classmethod
    def get_session_path(cls, user_id: int, provider: str) -> str:
        cls.ensure_storage()
        return os.path.join(cls.SESSION_DIR, f"{user_id}_{provider}.json")
        
    @classmethod
    def save_session(cls, context, user_id: int, provider: str):
        """
        Securely extracts cookies and localStorage from the Playwright context
        and writes them to disk to bypass repeated login flows.
        """
        path = cls.get_session_path(user_id, provider)
        context.storage_state(path=path)
        system_logger.info(f"Persisted authenticated session for {provider}")
