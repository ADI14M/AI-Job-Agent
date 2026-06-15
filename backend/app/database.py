import asyncio
from app.db.session import engine, Base

async def init_db() -> None:
    """
    Asynchronously wrapper to initialize the database tables.
    Runs the synchronous SQLAlchemy metadata.create_all within a thread
    to prevent blocking, satisfying the start.sh script's asyncio.run() call.
    """
    await asyncio.to_thread(Base.metadata.create_all, engine)
