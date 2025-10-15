.PHONY: help setup dev test lint fmt clean docker/build docker/run

help:
	@echo "AI Video Generator - Make Commands"
	@echo ""
	@echo "  setup         Install dependencies and setup environment"
	@echo "  dev           Run FastAPI development server"
	@echo "  test          Run pytest test suite"
	@echo "  lint          Run ruff linter"
	@echo "  fmt           Format code with black"
	@echo "  clean         Clean up temporary files and cache"
	@echo "  docker/build  Build Docker image"
	@echo "  docker/run    Run application in Docker"

setup:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"
	cp -n .env.example .env || true
	@echo "Setup complete! Edit .env with your API keys if needed."

dev:
	uvicorn src.app.web:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	ruff check src/ tests/
	mypy src/

fmt:
	black src/ tests/
	ruff check --fix src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov build dist *.egg-info
	rm -rf data/media/* data/voiceovers/* output/*

docker/build:
	docker build -t ai-video-generator:latest .

docker/run:
	docker run -p 8000:8000 -v $(PWD)/data:/app/data -v $(PWD)/output:/app/output --env-file .env ai-video-generator:latest
