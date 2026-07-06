#!/bin/bash
# AI Job Agent End-to-End Demo Script
# Runs the complete platform verification automatically.

echo "========================================="
echo "AI JOB AGENT v1.0 - Demo Mode Orchestrator"
echo "========================================="

# Stop on error
set -e

# Cleanup previous runs
echo "[1/4] Cleaning up old demo data..."
rm -f backend/demo.db
rm -rf backend/demo_chroma_db
rm -rf reports
mkdir -p reports/screenshots
mkdir -p reports/architecture
mkdir -p reports/logs

# Set environment variable to indicate DEMO MODE (points DB to demo.db)
export DATABASE_URL="sqlite:///./demo.db"
export CHROMA_PATH="./demo_chroma_db"
export IS_DEMO_MODE="True"

# Start backend
echo "[2/4] Starting FastAPI backend on port 8000 (background)..."
cd backend
source .venv/bin/activate
export PYTHONPATH=.
nohup python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > ../reports/logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "[3/4] Starting React frontend on port 5173 (background)..."
cd frontend
nohup npm run dev > ../reports/logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for services to boot
echo "Waiting for backend on port 8000..."
while ! nc -z 127.0.0.1 8000; do
  sleep 1
done

echo "Waiting for frontend on port 5173..."
while ! curl -s http://localhost:5173 > /dev/null; do
  sleep 1
done
echo "Services are up!"

# Execute the core demo python script
echo "[4/4] Executing demo.py Core Engine Tests..."
set +e # Don't stop script if tests fail so we can still clean up
cd backend
source .venv/bin/activate
export PYTHONPATH=.
python ../demo.py
TEST_RESULT=$?
cd ..

# Cleanup
echo "Stopping background services..."
kill $BACKEND_PID || true
kill $FRONTEND_PID || true
# Kill any lingering node/python processes started by this script
pkill -P $BACKEND_PID || true
pkill -P $FRONTEND_PID || true

if [ $TEST_RESULT -eq 0 ]; then
    echo "========================================="
    echo "AI JOB AGENT v1.0"
    echo "Production Demonstration Complete"
    echo "System Status: READY FOR PRODUCTION"
    echo "========================================="
    exit 0
else
    echo "========================================="
    echo "Demo Execution FAILED. Check reports/logs."
    echo "========================================="
    exit 1
fi
