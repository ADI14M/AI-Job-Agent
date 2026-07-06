from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, resume, jobs, matching, ats, skill_gap, resume_optimizer, cover_letter, job_discovery_v2, job_ranking, applications, automation, learning, notifications, analytics, orchestrator, decision, memory, agent

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

from app.db.session import Base, engine
from app.db.models import user as m_user, resume as m_resume, job as m_job, application as m_app, cover_letter as m_cl, resume_version as m_rv, skill_gap as m_sg, ats as m_ats, notification as m_notif, user_preferences as m_up

# Initialize Database (Auto-create tables for SQLite/Postgres)
Base.metadata.create_all(bind=engine)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from starlette.middleware.base import BaseHTTPMiddleware
from app.middleware import add_timing_middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=add_timing_middleware)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(resume.router, prefix="/api/v1/resume", tags=["resume"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(resume_optimizer.router, prefix="/api/v1/resume-optimizer", tags=["resume optimizer"])
app.include_router(cover_letter.router, prefix="/api/v1/cover-letter", tags=["cover letter"])
app.include_router(ats.router, prefix="/api/v1/ats", tags=["ats checker"])
app.include_router(skill_gap.router, prefix="/api/v1/skill-gap", tags=["skill gap"])
app.include_router(applications.router, prefix="/api/v1/applications", tags=["applications"])
app.include_router(decision.router, prefix="/api/v1/decision", tags=["decision engine"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["career memory"])
app.include_router(agent.router, prefix="/api/v1/agent", tags=["agent"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(matching.router, prefix="/api/v1/matching", tags=["matching"])
app.include_router(job_discovery_v2.router, prefix="/api/v1/job-discovery", tags=["job discovery"])
app.include_router(job_ranking.router, prefix="/api/v1/job-ranking", tags=["job ranking"])
app.include_router(automation.router, prefix="/api/v1/automation", tags=["automation"])
app.include_router(learning.router, prefix="/api/v1/learning", tags=["learning"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(orchestrator.router, prefix="/api/v1/orchestrator", tags=["orchestrator"])

@app.get("/")
def root():
    return {"message": "Welcome to AI Job Agent API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
