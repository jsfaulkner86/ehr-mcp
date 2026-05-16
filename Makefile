.PHONY: help install install-dev run test lint format clean docker-build docker-run keys

# Default target
help:
	@echo ""
	@echo "  EHR-MCP — FHIR R4 MCP Server for Healthcare AI Agents"
	@echo ""
	@echo "  Usage: make <target>"
	@echo ""
	@echo "  Setup"
	@echo "    install        Install production dependencies"
	@echo "    install-dev    Install all dependencies including dev/test"
	@echo "    keys           Generate RS384 key pair for SMART-on-FHIR auth"
	@echo ""
	@echo "  Development"
	@echo "    run            Start the MCP server (stdio mode)"
	@echo "    test           Run test suite"
	@echo "    lint           Run ruff linter"
	@echo "    format         Run black formatter"
	@echo "    clean          Remove build artifacts and caches"
	@echo ""
	@echo "  Docker"
	@echo "    docker-build   Build Docker image"
	@echo "    docker-run     Run server in Docker (requires .env)"
	@echo ""

## ── Setup ────────────────────────────────────────────────────────────────────

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	@if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

.env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "  Created .env from .env.example — add your SMART-on-FHIR credentials."; \
	fi

keys:
	@mkdir -p keys
	@echo "  Generating RS384 key pair..."
	openssl genrsa -out keys/private_key.pem 2048
	openssl rsa -in keys/private_key.pem -pubout -out keys/public_key.pem
	@echo "  Keys written to keys/private_key.pem and keys/public_key.pem"
	@echo "  Register the public key with your EHR vendor (e.g. Epic FHIR sandbox)."

## ── Development ──────────────────────────────────────────────────────────────

run: .env
	python main.py

test:
	@if [ -d tests ]; then \
		python -m pytest tests/ -v; \
	else \
		echo "  No tests directory found. Run: mkdir tests"; \
	fi

lint:
	@if command -v ruff > /dev/null; then \
		ruff check ehr_mcp/ main.py; \
	else \
		echo "  ruff not installed. Run: pip install ruff"; \
	fi

format:
	@if command -v black > /dev/null; then \
		black ehr_mcp/ main.py; \
	else \
		echo "  black not installed. Run: pip install black"; \
	fi

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "  Cleaned build artifacts."

## ── Docker ───────────────────────────────────────────────────────────────────

docker-build:
	docker build -t ehr-mcp:latest .
	@echo "  Image built: ehr-mcp:latest"

docker-run: .env
	docker run --rm --env-file .env -it ehr-mcp:latest
