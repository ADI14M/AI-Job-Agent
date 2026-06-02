# AI-Powered Autonomous Job Search and Application Platform

An intelligent system that automatically searches for jobs, evaluates candidate fit based on an uploaded resume, tailors resumes and cover letters for specific roles, and supports automated application submissions via browser automation.

## Project Structure

- `frontend/`: React + TypeScript frontend (Vite)
- `backend/`: FastAPI + Python backend
- `infrastructure/`: Docker and deployment configs
- `data/`: Storage for resumes, screenshots, etc.
- `docs/`: Technical documentation

## Setup

1. Copy `.env.example` to `.env` and fill in API keys.
2. Run `docker-compose up -d` to start the PostgreSQL and ChromaDB containers.
3. Install backend dependencies: `cd backend && pip install -r requirements.txt`.
4. Install frontend dependencies: `cd frontend && npm install`.

## Execution Phases
This project is built iteratively in 10 phases, starting from Resume Intelligence and expanding into fully autonomous browser actions.
