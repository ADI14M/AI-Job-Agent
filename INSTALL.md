# Installation Guide

## Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm`
- **Ollama**: Installed and running locally.
- **Playwright System Dependencies**

## 1. Local AI Setup
Install Ollama and pull the required models:
```bash
ollama run qwen2.5:7b
ollama run llama3.2:3b
ollama run nomic-embed-text
```

## 2. Backend Setup
Navigate to the backend directory and install dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### Environment Variables
Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL=sqlite:///./ai_job_agent.db
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
OLLAMA_BASE_URL=http://localhost:11434
CHAT_MODEL=qwen2.5:7b
EMBED_MODEL=nomic-embed-text
```

### Database Initialization
Apply initial migrations (or let SQLAlchemy create them on startup depending on configuration).

## 3. Frontend Setup
Navigate to the frontend directory:
```bash
cd frontend
npm install
```

## 4. Running the Application
**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```
Navigate to `http://localhost:5173` in your browser.
