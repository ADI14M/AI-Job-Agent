# System Architecture

## Overview
The AI-Powered Job Search and Application Platform operates in 16 phases. The backend is built with **FastAPI**, **PostgreSQL**, and **ChromaDB**. The LLM layer utilizes a **Provider Abstraction** (supporting OpenAI, Ollama, and Gemini) via Langchain's BaseChatModel interface.

## Database Models
- `users`: Core authentication.
- `resumes`, `resume_embeddings`: Raw and structured resume data with vector DB references.
- `jobs`, `job_embeddings`: Extracted Job Description data.
- `applications`, `application_history`: Tracking metrics.

## Agents Layer (`backend/app/agents/`)

### 1. `resume_agent` (Phase 1)
Parses PDF/DOCX resumes to extract detailed structured fields.

### 2. `jd_agent` (Phase 2)
Analyzes Job Descriptions and extracts requirements, keywords, and salary ranges.

### 3. `matching_agent` (Phase 3)
Calculates semantic similarity (Cosine Distance) via ChromaDB and orchestrates LLM structured evaluation to output a final 0-100 Match Score.

*(Additional agents are mapped to subsequent phases).*
