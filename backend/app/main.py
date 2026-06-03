from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, resume, jobs, matching, ats, skill_gap, resume_optimizer, cover_letter, job_discovery, job_ranking, applications, automation, learning, notifications, analytics, orchestrator

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

from app.db.session import Base, engine

# Initialize Database (Auto-create tables for SQLite/Postgres)
Base.metadata.create_all(bind=engine)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(resume.router, prefix="/api/v1/resume", tags=["resume"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(job_discovery.router, prefix="/api/v1/job_discovery", tags=["job_discovery"])
app.include_router(job_ranking.router, prefix="/api/v1/job_ranking", tags=["job_ranking"])
app.include_router(matching.router, prefix="/api/v1/matching", tags=["matching"])
app.include_router(ats.router, prefix="/api/v1/ats", tags=["ats"])
app.include_router(skill_gap.router, prefix="/api/v1/skill_gap", tags=["skill_gap"])
app.include_router(resume_optimizer.router, prefix="/api/v1/resume_optimizer", tags=["resume_optimizer"])
app.include_router(cover_letter.router, prefix="/api/v1/cover_letter", tags=["cover_letter"])
app.include_router(applications.router, prefix="/api/v1/applications", tags=["applications"])
app.include_router(automation.router, prefix="/api/v1/automation", tags=["automation"])
app.include_router(learning.router, prefix="/api/v1/learning", tags=["learning"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(orchestrator.router, prefix="/api/v1/orchestrator", tags=["orchestrator"])

@app.get("/")
def root():
    return {"message": "Welcome to AI Job Agent API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
