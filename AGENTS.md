# Repository Guidelines

## Project Structure & Module Organization

This repository implements the contract in `AI_FRAMEWORK_SPEC.md`. Treat the spec as authoritative for architecture and milestones. Runtime source code lives under `app/`, tests under `tests/`, migrations under `migrations/`, helper scripts under `scripts/`, and contributor documentation under `docs/`.

Expected major modules include `app/api/` for FastAPI routes, `app/workflows/` for LangGraph workflows, `app/tools/` for tool descriptors and permission enforcement, `app/rag/` and `app/vectorstores/` for retrieval, `app/persistence/` for database access, and `app/observability/` for Langfuse and telemetry integration.

## Build, Test, and Development Commands

Use `uv` and the Makefile for local development:

- `make install`: install project dependencies.
- `make dev`: run the local development server.
- `make test`: run the test suite.
- `make lint`: run Ruff lint checks.
- `make format`: format code with Ruff.
- `make typecheck`: run `mypy app`.
- `make compose-up` / `make compose-down`: manage local services.

The Makefile keeps `uv` caches inside the repository for sandbox-friendly execution.

## Coding Style & Naming Conventions

Use Python 3.12+, type hints on public interfaces, and Pydantic models where runtime validation is useful. Prefer async APIs for I/O-bound work. Keep modules loosely coupled and avoid hidden mutable global clients, wildcard imports, and secrets in source. Use `snake_case` for modules, functions, and variables; `PascalCase` for classes and Pydantic models.

## Testing Guidelines

Use deterministic tests that do not require paid model calls by default. Provide mocks for models and embeddings. Place tests by behavior and layer, for example `tests/unit/`, `tests/integration/`, `tests/workflows/`, `tests/tools/`, `tests/rag/`, and `tests/api/`. Cover permission policy, registries, retrieval, workflow retry paths, approval flows, sandbox safety, and API behavior.

## Commit & Pull Request Guidelines

The current history uses short imperative-style messages such as `Initial commit` and `Add files via upload`. Keep future commits concise and action-oriented. Pull requests should summarize the change, identify affected modules, link related issues when available, and list checks run, such as `ruff check .`, `mypy app`, and `pytest`.

## Agent-Specific Instructions

Read `AI_FRAMEWORK_SPEC.md` before architectural changes. Implement one milestone at a time, avoid unrelated refactors, preserve tool permission boundaries, and do not add infrastructure outside the current task unless the spec requires it.
