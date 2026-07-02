# AI Job Agent

Welcome to the **AI Job Agent**, a fully autonomous, local-first recruiting and job application assistant. This project leverages the power of Local Large Language Models (LLMs) via Ollama, combined with persistent vector search (ChromaDB) and web automation (Playwright), to streamline the entire job search lifecycle.

## Overview

The AI Job Agent acts as your personal AI recruiter. It is designed to run entirely locally (with internet only used for fetching jobs and submitting forms), ensuring complete privacy for your career data and resumes.

### Key Features

- **Job Discovery Engine**: Modular architecture supporting multiple platforms (LinkedIn, Wellfound, Greenhouse, etc.).
- **Decision Engine**: Automatically analyzes job descriptions against your resume, calculates ATS match scores, performs skill gap analysis, and decides whether a job is worth applying for.
- **Resume Optimization & Cover Letters**: Automatically generates tailor-made, optimized resumes and cover letters for each high-match job.
- **Career Memory**: Persistent tracking of every job viewed, applied, or skipped, along with historical performance analytics.
- **Autonomous Application**: Playwright-based browser automation capable of parsing local ATS forms and navigating employer application portals.
- **Local AI Pipeline**: Powered by Ollama (`qwen2.5:7b`, `llama3.2:3b`) and `nomic-embed-text` for embeddings. No OpenAI API keys required.

## Tech Stack

- **Backend**: Python 3, FastAPI, SQLAlchemy, ChromaDB
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, ShadCN UI
- **AI & Automation**: LangChain, Ollama, Playwright

## Getting Started

Please see the following documents for detailed information:
- [INSTALL.md](INSTALL.md) for setup and deployment instructions.
- [DEMO.md](DEMO.md) to run the fully automated offline demonstration.
- [ARCHITECTURE.md](ARCHITECTURE.md) for deep technical insights.

## Project Layout

```text
├── backend/            # FastAPI Backend
│   ├── app/            # Core application logic
│   ├── requirements.txt
├── frontend/           # React + Vite Frontend
│   ├── src/            # UI components and logic
│   ├── package.json
├── demo.sh             # E2E Automation Demo Script
```
