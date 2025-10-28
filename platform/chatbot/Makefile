.PHONY: help install dev test lint format clean docker-up docker-down migrate

help:
	@echo "FacilIAuto Chatbot - Available Commands"
	@echo "========================================"
	@echo "install       - Install dependencies"
	@echo "dev           - Run development server"
	@echo "test          - Run tests"
	@echo "test-cov      - Run tests with coverage"
	@echo "lint          - Run linters"
	@echo "format        - Format code"
	@echo "type-check    - Run type checking"
	@echo "clean         - Clean temporary files"
	@echo "docker-up     - Start Docker services"
	@echo "docker-down   - Stop Docker services"
	@echo "migrate       - Run database migrations"
	@echo "worker        - Start Celery worker"
	@echo "beat          - Start Celery beat"

install:
	poetry install
	poetry run pre-commit install
	poetry run python -m spacy download pt_core_news_lg

dev:
	poetry run uvicorn src.main:app --reload --port 8000

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=src --cov-report=html --cov-report=term

lint:
	poetry run flake8 src/ tests/
	poetry run black --check src/ tests/

format:
	poetry run black src/ tests/
	poetry run isort src/ tests/

type-check:
	poetry run mypy src/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

migrate:
	poetry run alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	poetry run alembic revision --autogenerate -m "$$msg"

worker:
	poetry run celery -A src.tasks.celery_app worker --loglevel=info

beat:
	poetry run celery -A src.tasks.celery_app beat --loglevel=info

shell:
	poetry run python

pre-commit:
	poetry run pre-commit run --all-files
