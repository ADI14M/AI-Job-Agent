@echo off
echo === AI Job Agent Starting ===

if not exist "backend\.venv" (
    echo [1/5] Creating Python virtual environment...
    python -m venv backend\.venv
    call backend\.venv\Scripts\activate
    pip install --upgrade pip
    pip install -r backend\requirements.txt
) else (
    call backend\.venv\Scripts\activate
)

echo [2/5] Initialising database...
cd backend
python -c "import asyncio; from app.database import init_db; asyncio.run(init_db()); print('Database ready.')"
cd ..

if not exist "frontend\node_modules" (
    echo [3/5] Installing frontend dependencies...
    cd frontend && npm install && cd ..
) else (
    echo [3/5] Frontend dependencies already installed.
)

pip show honcho >nul 2>&1 || pip install honcho

echo [4/5] Starting backend and frontend...
echo.
echo   Backend  -^>  http://localhost:8000
echo   API Docs -^>  http://localhost:8000/docs
echo   Frontend -^>  http://localhost:5173
echo.
honcho start
