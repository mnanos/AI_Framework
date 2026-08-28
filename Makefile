UV := UV_CACHE_DIR=.uv-cache UV_PYTHON_INSTALL_DIR=.uv-python uv

.PHONY: install dev test lint format typecheck migrate ingest compose-up compose-down clean

install:
	$(UV) sync --all-groups

dev:
	$(UV) run uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000

test:
	$(UV) run pytest

lint:
	$(UV) run ruff format --check .
	$(UV) run ruff check .

format:
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

typecheck:
	$(UV) run mypy app

migrate:
	@echo "Migrations are introduced in Milestone 1."

ingest:
	@echo "Document ingestion is introduced in a later milestone."

compose-up:
	docker compose up --build

compose-down:
	docker compose down

clean:
	find . -type d \( -name .pytest_cache -o -name .ruff_cache -o -name .mypy_cache -o -name .uv-cache -o -name .uv-python -o -name __pycache__ \) -prune -exec rm -rf {} +
