# AI Framework

AI Framework is a production-oriented foundation for AI applications and agentic workflows. The implementation follows `AI_FRAMEWORK_SPEC.md`, with LangGraph-oriented workflow boundaries, FastAPI transport, validated configuration, structured logging, PostgreSQL/pgvector persistence, Redis coordination, and explicit safety controls.

## Architecture

Milestone 0 provides the repository bootstrap: package layout, settings, logging, a FastAPI app factory, `/health`, `/ready`, tests, and local runtime assets. Later milestones fill in persistence, LLM adapters, workflows, tools, RAG, sandboxing, and evaluations.

## Prerequisites

- Python 3.12+
- `uv`
- Docker and Docker Compose for local PostgreSQL and Redis

## Quick Start

```bash
make install
make dev
```

The API starts on `http://localhost:8000`.

## Configuration

Copy `.env.example` to `.env` for local overrides. Runtime settings are loaded through `app.config.Settings`; do not read environment variables directly from feature modules.

## Local Services

```bash
make compose-up
make compose-down
```

Compose starts the API, PostgreSQL with pgvector, and Redis.

## First API Request

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## Development Checks

```bash
make lint
make typecheck
make test
```

## Adding a Tool

Place tool implementations under `app/tools/<domain>/`. Keep descriptors, permission policy, and execution separate. Do not bypass approval or sandbox boundaries.

## Adding a Workflow

Place workflow modules under `app/workflows/`. Keep business logic out of graph wiring where practical, and add workflow tests for success, retry, failure, and approval paths.

## Langfuse Setup

Set `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and optionally `LANGFUSE_BASE_URL`. Application startup must continue when Langfuse is unavailable.

## Security Model

Secrets belong in configuration, not source. Future tool and sandbox code must enforce workspace boundaries, command timeouts, output limits, and approval gates for sensitive operations.
