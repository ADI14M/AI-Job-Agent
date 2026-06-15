.PHONY: start install migrate test lint

start:
	./start.sh

install:
	python3 -m venv backend/.venv && \
	source backend/.venv/bin/activate && \
	pip install -r backend/requirements.txt && \
	cd frontend && npm install

migrate:
	source backend/.venv/bin/activate && \
	cd backend && alembic upgrade head

test:
	source backend/.venv/bin/activate && \
	cd backend && pytest tests/ -v

lint:
	source backend/.venv/bin/activate && \
	cd backend && ruff check app/
