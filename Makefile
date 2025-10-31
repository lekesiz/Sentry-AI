.PHONY: help install test run api clean lint format

help:
	@echo "Sentry-AI - Makefile Commands"
	@echo "=============================="
	@echo "install     - Install dependencies"
	@echo "test        - Run all tests"
	@echo "test-unit   - Run unit tests only"
	@echo "test-int    - Run integration tests only"
	@echo "run         - Run Sentry-AI main application"
	@echo "api         - Run API server"
	@echo "clean       - Clean up generated files"
	@echo "lint        - Run linters (flake8)"
	@echo "format      - Format code with black"
	@echo "coverage    - Run tests with coverage report"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

test-unit:
	pytest tests/test_agents.py -v -m unit

test-int:
	pytest tests/test_integration.py -v -m integration

coverage:
	pytest tests/ --cov=sentry_ai --cov-report=html --cov-report=term

run:
	python -m sentry_ai.main

api:
	python run_api.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f sentry_ai.db
	rm -f sentry_ai.log

lint:
	flake8 sentry_ai/ --max-line-length=100 --ignore=E501,W503

format:
	black sentry_ai/ tests/ --line-length=100

check:
	@echo "Running linters..."
	@make lint
	@echo "\nRunning tests..."
	@make test
	@echo "\nAll checks passed!"
