#!/usr/bin/env bash
set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║        AI Job Agent  —  Local Mode       ║"
echo "║     Apple M5 · 24GB · Fully Offline      ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── 1. Ollama ────────────────────────────────────────────────
echo "[1/6] Checking Ollama..."
if ! command -v ollama &>/dev/null; then
  echo ""
  echo "  ✗ Ollama not found. Install it first:"
  echo "    brew install ollama"
  echo "    or: https://ollama.com/download"
  echo ""
  exit 1
fi

if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "  Starting Ollama server..."
  ollama serve > /tmp/ollama.log 2>&1 &
  OLLAMA_PID=$!
  echo "  Waiting for Ollama to be ready..."
  for i in {1..10}; do
    sleep 1
    curl -s http://localhost:11434/api/tags >/dev/null 2>&1 && break
  done
  echo "  ✓ Ollama started (pid $OLLAMA_PID)"
else
  echo "  ✓ Ollama already running"
fi

# ── 2. Pull required models ──────────────────────────────────
echo ""
echo "[2/6] Checking local models..."

MODELS=("qwen2.5:7b" "llama3.2:3b" "nomic-embed-text")
for model in "${MODELS[@]}"; do
  if ollama list 2>/dev/null | grep -q "^${model}"; then
    echo "  ✓ $model — ready"
  else
    echo "  ↓ Pulling $model (first time only)..."
    ollama pull "$model"
    echo "  ✓ $model — ready"
  fi
done

# ── 3. Python venv ───────────────────────────────────────────
echo ""
echo "[3/6] Python environment..."
if [ ! -d "backend/.venv" ]; then
  echo "  Creating virtual environment..."
  python3 -m venv backend/.venv
  source backend/.venv/bin/activate
  pip install --upgrade pip -q
  pip install -r backend/requirements.txt -q
  echo "  ✓ Virtual environment created"
else
  source backend/.venv/bin/activate
  echo "  ✓ Virtual environment ready"
fi

# ── 4. Database ──────────────────────────────────────────────
echo ""
echo "[4/6] Database..."
cd backend
python -c "
import asyncio
from app.database import init_db
asyncio.run(init_db())
print('  ✓ Database ready')
"
cd ..

# ── 5. ChromaDB vector check ─────────────────────────────────
echo ""
echo "[5/6] ChromaDB vectors..."
if [ -d "chroma_db" ] && [ "$(ls -A chroma_db 2>/dev/null)" ]; then
  echo ""
  echo "  ⚠️  WARNING: chroma_db/ contains existing vectors."
  echo "  If these were created with OpenAI embeddings (1536-dim),"
  echo "  they are incompatible with nomic-embed-text (768-dim)."
  echo ""
  read -p "  Clear old vectors and start fresh? [y/N]: " confirm
  if [[ "$confirm" =~ ^[Yy]$ ]]; then
    rm -rf chroma_db/
    echo "  ✓ Cleared. Vectors will be rebuilt on first use."
  else
    echo "  ⚠  Keeping existing vectors. Vector search may return errors."
  fi
else
  echo "  ✓ No existing vectors — clean start"
fi

# ── 6. Frontend ──────────────────────────────────────────────
echo ""
echo "[6/6] Frontend..."
if [ ! -d "frontend/node_modules" ]; then
  echo "  Installing dependencies..."
  cd frontend && npm install -q && cd ..
fi
echo "  ✓ Frontend ready"

# ── Launch ───────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════"
echo "  ✓ Everything ready. Launching..."
echo ""
echo "  Backend  →  http://localhost:8000"
echo "  API Docs →  http://localhost:8000/docs"
echo "  Frontend →  http://localhost:5173"
echo ""
echo "  LLM      →  qwen2.5:7b (local, M5 Metal, 16GB optimised)"
echo "  Embed    →  nomic-embed-text (local)"
echo "  DB       →  SQLite (jobagent.db)"
echo "  Vectors  →  ChromaDB (./chroma_db)"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "══════════════════════════════════════════════"
echo ""

honcho start
