# 🤖 AI Job Agent

An intelligent, full-stack platform that autonomously searches for jobs, evaluates your resume fit, tailors specific resumes and cover letters for every role, and automates job application submissions using browser automation.

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![React](https://img.shields.io/badge/React-18-cyan)

## 🌟 Key Features

- **Resume Parsing & Vectorization**: Upload your resume to have it semantically analyzed by OpenAI and stored in ChromaDB.
- **Skill Gap Analysis & ATS Scoring**: Instantly score your resume against job descriptions and highlight missing keywords.
- **AI Document Generation**: Automatically rewrite your resume bullet points and generate custom cover letters for specific roles.
- **Job Discovery Engine**: Discover relevant jobs across the web.
- **Playwright Automation**: Push a button to watch a visible browser autonomously navigate to LinkedIn/Wellfound, fill out the "Easy Apply" fields, upload your optimized documents, and submit your application.
- **Modern Dashboard**: A premium React/Tailwind/ShadCN interface to track applications, metrics, and documents.

---

## 🛠️ Technology Stack

**Backend:**
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Vector DB**: ChromaDB
- **AI/LLM**: LangChain, OpenAI API
- **Automation**: Playwright
- **Auth**: JWT / Bcrypt

**Frontend:**
- **Framework**: React 18 + Vite (TypeScript)
- **Styling**: Tailwind CSS + ShadCN UI
- **State Management**: Zustand
- **API Client**: Axios

---

## Local LLM Setup (macOS Apple Silicon)

1. Install Ollama:
   ```bash
   brew install ollama
   ```
   *or download from https://ollama.com/download*

2. Run `./start.sh` — it will pull all required models automatically.

That's it. No API keys. No accounts. Fully offline.

---

## 🚀 Getting Started

Follow these instructions to get the project running locally on your machine.

### Prerequisites

You must have the following installed on your system:
1. **Python 3.10+**
2. **Node.js (v18+)**
3. **PostgreSQL** (running locally on port `5432`)

### 1. Database Setup

Ensure PostgreSQL is running on your machine. Create a new database for the application.

If you have `psql` CLI installed, run:
```bash
psql -U postgres
CREATE DATABASE ai_job_agent;
```

### 2. Backend Setup

Open a terminal and navigate to the backend folder:

```bash
cd backend
```

**Create a Virtual Environment & Install Dependencies:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

**Install Playwright Browsers:**
```bash
playwright install chromium
```

**Set Up Environment Variables:**
Copy the template file to create your local environment config:
```bash
cp .env.example .env
```

Open `backend/.env` and configure your keys. Ensure your `DATABASE_URL` matches your local Postgres credentials and provide a valid OpenAI API key.
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_job_agent
SECRET_KEY=your_secure_random_secret_key
OPENAI_API_KEY=sk-proj-your_openai_api_key_here
CHROMA_DB_DIR=./chroma_data
```

**Start the Backend Server:**
```bash
python3 -m uvicorn app.main:app --reload
```
*Note: The backend automatically creates all necessary database tables on the first startup. The API will be available at `http://localhost:8000` and Swagger docs at `http://localhost:8000/docs`.*

### 3. Frontend Setup

Open a **new** terminal window and navigate to the frontend folder:

```bash
cd frontend
```

**Install Dependencies:**
```bash
npm install
```

**Start the Frontend Server:**
```bash
npm run dev
```

*The dashboard will now be live at `http://localhost:5173`. Open this URL in your browser to start using the AI Job Agent!*

---

## 📁 Project Structure

```text
AI-Job-Agent/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── agents/           # LLM logic for optimizations and matching
│   │   ├── api/routes/       # REST API Endpoints
│   │   ├── automation/       # Playwright browser scripts
│   │   ├── core/             # Security, config, and DB sessions
│   │   ├── db/models/        # SQLAlchemy PostgreSQL schemas
│   │   └── vector_db/        # ChromaDB setup
│   └── requirements.txt
├── frontend/                 # React Application
│   ├── src/
│   │   ├── api/              # Axios client and interceptors
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Main application views
│   │   └── store/            # Zustand global state
│   └── package.json
└── data/                     # Auto-generated storage (Resumes, DB files)
```
