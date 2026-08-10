# ==============================================================================
# Makefile — Doc Assistant: Corporate RAG Platform
# ==============================================================================

.DEFAULT_GOAL := help

.PHONY: help install clean lint format typecheck test dev run docker-build docker-run build

BIN := $(shell if [ -d ".venv/bin" ]; then echo ".venv/bin/"; else echo ""; fi)
POETRY := $(shell command -v poetry 2> /dev/null)

help:
	@echo "======================================================================"
	@echo "          Doc Assistant — Corporate RAG Platform                      "
	@echo "======================================================================"
	@echo "  make install      - Install dependencies & git hooks."
	@echo "  make clean        - Purge cache & temporary artifacts."
	@echo "  make lint         - Run Ruff linter + formatter check."
	@echo "  make typecheck    - Run Mypy strict type analysis."
	@echo "  make format       - Auto-format source code with Ruff."
	@echo "  make test         - Run full pytest suite."
	@echo "  make dev          - Start FastAPI dev server (reload)."
	@echo "  make run          - Run main module."
	@echo "  make docker-build - Build multi-stage Docker image."
	@echo "  make docker-run   - Run container locally on port 8000."
	@echo "======================================================================"

install:
	@if [ -n "$(POETRY)" ]; then poetry install && poetry run pre-commit install; else $(BIN)python -m pip install -e . && $(BIN)pre-commit install; fi

clean:
	@echo "Cleaning cache directories and temporary files..."
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	@echo "--- [1/2] Static analysis (Ruff) ---"
	@if [ -n "$(POETRY)" ]; then poetry run ruff check .; else $(BIN)ruff check .; fi
	@echo "--- [2/2] Code formatting check (Ruff Format) ---"
	@if [ -n "$(POETRY)" ]; then poetry run ruff format --check .; else $(BIN)ruff format --check .; fi

typecheck:
	@echo "--- Strict type check (Mypy) ---"
	@if [ -n "$(POETRY)" ]; then poetry run python -m mypy src/; else $(BIN)mypy src/; fi

format:
	@echo "--- Auto-formatting source code (Ruff) ---"
	@if [ -n "$(POETRY)" ]; then poetry run ruff format .; poetry run ruff check --fix .; else $(BIN)ruff format .; $(BIN)ruff check --fix .; fi

test:
	@if [ -n "$(POETRY)" ]; then poetry run python -m pytest; else $(BIN)pytest; fi

dev:
	@if [ -n "$(POETRY)" ]; then poetry run uvicorn src.main:app --reload --port 8000; else $(BIN)uvicorn src.main:app --reload --port 8000; fi

run:
	@if [ -n "$(POETRY)" ]; then poetry run python -m src.main; else $(BIN)python -m src.main; fi

build: docker-build

docker-build:
	@echo "--- Building production Docker image ---"
	docker build -t doc-assistant:latest .
	@echo "--- Final image size ---"
	@docker images doc-assistant:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

docker-run:
	@echo "--- Running container on port 8000 ---"
	docker run -p 8000:8000 doc-assistant:latest
