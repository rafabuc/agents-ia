# DevOps AI Platform Makefile

.PHONY: help install install-dev setup test test-cov lint format type-check clean build run-dev docker-build docker-run

# Variables
PYTHON := python3
PIP := pip
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
ISORT := isort
MYPY := mypy

# Default target
help:
	@echo "DevOps AI Platform - Available Commands:"
	@echo ""
	@echo "Setup and Installation:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  setup        Full development environment setup"
	@echo ""
	@echo "Development:"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black and isort"
	@echo "  type-check   Run type checking with mypy"
	@echo "  clean        Clean build artifacts and cache"
	@echo ""
	@echo "Build and Run:"
	@echo "  build        Build the package"
	@echo "  run-dev      Run development server"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run Docker container"
	@echo ""
	@echo "CI/CD:"
	@echo "  ci           Run full CI pipeline (lint, test, type-check)"
	@echo "  pre-commit   Run pre-commit hooks"

# Installation
install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -e ".[dev,ml,docs]"
	pre-commit install

setup: install-dev
	@echo "Setting up development environment..."
	@mkdir -p logs
	@mkdir -p data
	@mkdir -p .env
	@echo "Development environment setup complete!"

# Testing
test:
	$(PYTEST) tests/ -v

test-cov:
	$(PYTEST) tests/ -v --cov=agents --cov=orchestrator --cov=tools --cov-report=html --cov-report=term

test-unit:
	$(PYTEST) tests/unit/ -v

test-integration:
	$(PYTEST) tests/integration/ -v

# Code Quality
lint:
	$(FLAKE8) agents/ orchestrator/ tools/ rag/ tests/
	$(ISORT) --check-only agents/ orchestrator/ tools/ rag/ tests/

format:
	$(BLACK) agents/ orchestrator/ tools/ rag/ tests/
	$(ISORT) agents/ orchestrator/ tools/ rag/ tests/

type-check:
	$(MYPY) agents/ orchestrator/ tools/ rag/

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Build
build: clean
	$(PYTHON) -m build

build-wheel:
	$(PYTHON) -m build --wheel

# Development Server
run-dev:
	@echo "Starting development server..."
	uvicorn apps.ai_services.main:app --host 0.0.0.0 --port 8000 --reload

run-django:
	@echo "Starting Django development server..."
	cd apps/django_app && python manage.py runserver

# Docker
docker-build:
	@echo "Building Docker image..."
	docker build -t devops-ai-platform:latest -f docker/Dockerfile.ai-services .

docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 --env-file .env devops-ai-platform:latest

docker-compose-up:
	docker-compose -f docker/docker-compose.yml up -d

docker-compose-down:
	docker-compose -f docker/docker-compose.yml down

# CI/CD Pipeline
ci: lint type-check test

pre-commit:
	pre-commit run --all-files

# Database
db-migrate:
	cd apps/django_app && python manage.py makemigrations
	cd apps/django_app && python manage.py migrate

db-reset:
	cd apps/django_app && python manage.py flush --noinput

# Infrastructure
terraform-init:
	cd infrastructure/terraform/environments/local && terraform init

terraform-plan:
	cd infrastructure/terraform/environments/local && terraform plan

terraform-apply:
	cd infrastructure/terraform/environments/local && terraform apply

k8s-deploy:
	kubectl apply -f infrastructure/kubernetes/base/

k8s-delete:
	kubectl delete -f infrastructure/kubernetes/base/

# Monitoring
start-monitoring:
	@echo "Starting monitoring stack..."
	docker-compose -f infrastructure/monitoring/docker-compose.yml up -d

stop-monitoring:
	docker-compose -f infrastructure/monitoring/docker-compose.yml down

# Documentation
docs-serve:
	mkdocs serve

docs-build:
	mkdocs build

# Security
security-scan:
	@echo "Running security scans..."
	safety check
	bandit -r agents/ orchestrator/ tools/

# Environment Management
env-example:
	@echo "Creating .env.example file..."
	@echo "# DevOps AI Platform Environment Variables" > .env.example
	@echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env.example
	@echo "ANTHROPIC_API_KEY=your_anthropic_api_key_here" >> .env.example
	@echo "DATABASE_URL=postgresql://user:pass@localhost/devops_ai" >> .env.example
	@echo "REDIS_URL=redis://localhost:6379" >> .env.example
	@echo "AWS_ACCESS_KEY_ID=your_aws_access_key" >> .env.example
	@echo "AWS_SECRET_ACCESS_KEY=your_aws_secret_key" >> .env.example
	@echo "AWS_DEFAULT_REGION=us-west-2" >> .env.example

# Release Management
version-bump-patch:
	@echo "Bumping patch version..."
	# This would typically use a tool like bump2version

version-bump-minor:
	@echo "Bumping minor version..."
	# This would typically use a tool like bump2version

version-bump-major:
	@echo "Bumping major version..."
	# This would typically use a tool like bump2version

# Utility Commands
logs:
	tail -f logs/devops-ai.log

check-deps:
	@echo "Checking for outdated dependencies..."
	$(PIP) list --outdated

install-pre-commit-hooks:
	pre-commit install
	pre-commit install --hook-type pre-push

# Performance Testing
load-test:
	@echo "Running load tests..."
	# Add load testing command here

# Backup
backup-db:
	@echo "Backing up database..."
	# Add database backup command

# Health Checks
health-check:
	@echo "Running health checks..."
	curl -f http://localhost:8000/health || exit 1

# Development Utilities
shell:
	$(PYTHON) -c "import IPython; IPython.start_ipython()"

notebook:
	jupyter lab

# All-in-one commands
dev-setup: setup env-example install-pre-commit-hooks
	@echo "Complete development setup finished!"

full-ci: clean format lint type-check test security-scan
	@echo "Full CI pipeline completed successfully!"