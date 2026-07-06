import asyncio
from app.db.session import engine, Base
from app.db.models.job_discovery import JobDiscovery
from app.db.models.application_package import ApplicationPackage
from app.db.models.career_memory import MemoryCompany, MemoryInterview, MemoryRecruiter, MemoryEvent
from app.db.models.agent_state import AgentApplicationState
from app.db.models.user_profile import UserProfile

async def init_db() -> None:
    """
    Asynchronously wrapper to initialize the database tables.
    Runs the synchronous SQLAlchemy metadata.create_all within a thread
    to prevent blocking, satisfying the start.sh script's asyncio.run() call.
    """
    await asyncio.to_thread(Base.metadata.create_all, engine)
