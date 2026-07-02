# Architecture

The AI Job Agent follows a modular, monolithic architecture designed for local deployment. It separates concerns between the client interface, API routing, persistent storage, and the local AI models.

## High-Level Components

### 1. Frontend (React + Vite)
- **State Management**: Zustand & React Query for real-time state synchronization.
- **UI Framework**: Tailwind CSS with ShadCN UI for modern, responsive aesthetics.
- **Routing**: React Router.

### 2. Backend (FastAPI)
Provides high-performance, asynchronous endpoints serving both the UI and background workers.
- **Authentication**: JWT-based session management.
- **Job Discovery**: Interfaces defining dynamic providers (LinkedIn, Greenhouse, etc.).
- **Decision Engine**: Core NLP pipelines matching job descriptions to resumes via semantic similarity and explicit skill extraction.
- **Career Memory**: Analytical tracking of applications and interactions over time.
- **Automation Agent**: `apscheduler` and Playwright scripts handling unsupervised task execution.

### 3. AI Services (Ollama & LangChain)
- All LLM queries run locally. The `AIService` singleton orchestrates prompts and JSON extraction fallbacks using Langchain wrappers around local Ollama endpoints.
- **Embeddings**: ChromaDB provides vector similarity search against parsed resumes and job descriptions using `nomic-embed-text`.

### 4. Storage Layer
- **Relational DB**: SQLite (Development/Demo) or PostgreSQL (Production) managing User, Job, Application, and Memory relational data via SQLAlchemy models.
- **Vector DB**: ChromaDB for rapid cosine-similarity lookups between candidate skills and job requirements.

## AI Pipeline Flow

1. **Ingestion**: Job + Latest Resume uploaded.
2. **Semantic Match**: ChromaDB calculates baseline similarity.
3. **ATS Analysis**: LLM simulates an ATS parsing system and grades the match.
4. **Skill Gap**: LLM evaluates explicitly missing skills.
5. **Optimization**: Resume text is rewritten highlighting relevant experience.
6. **Execution**: Browser Agent navigates to application portal and submits parameters.
