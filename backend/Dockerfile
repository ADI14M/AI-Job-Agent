FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Playwright, PyMuPDF, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (optional here, might be moved to a specific agent container later)
RUN playwright install --with-deps chromium

COPY . .

# Add /app to PYTHONPATH
ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
