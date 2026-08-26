# AI Framework — Implementation Specification

**Document:** `AI_FRAMEWORK_SPEC.md`  
**Status:** Implementation-ready  
**Primary implementer:** OpenAI Codex CLI  
**Target:** Production-oriented modular AI application framework  
**Primary language:** Python 3.12+  
**Architecture style:** Typed, modular, async-first, observable, testable, provider-neutral where practical

---

## 0. Purpose

Build a reusable AI engineering framework for developing production AI applications and agentic software.

The framework must provide reusable infrastructure for:

- workflow and agent orchestration with LangGraph;
- LLM provider abstraction;
- tool registration and permission enforcement;
- filesystem, shell, Git, GitHub, HTTP/API, database, SSH, Docker and MCP tools;
- Retrieval-Augmented Generation (RAG);
- vector search and hybrid retrieval;
- code-aware retrieval using Tree-sitter;
- application and semantic memory;
- durable workflow state and checkpoints;
- prompt management;
- Langfuse tracing, evaluations and cost/latency observability;
- FastAPI APIs and streaming;
- PostgreSQL persistence;
- pgvector as the default vector backend;
- Redis caching and coordination;
- artifact storage abstraction;
- Docker sandbox execution;
- human approval gates for sensitive operations;
- automated tests and evaluation datasets;
- local development through Docker Compose;
- clean extension points for future agents and applications.

The goal is **not** to build one chatbot.

The goal is to create an application platform on which multiple AI workflows can be implemented safely and consistently.

---

# 1. Core architectural principles

## 1.1 Separation of responsibilities

The following concerns must remain separate:

- workflow orchestration;
- LLM access;
- tool implementation;
- tool authorization;
- retrieval;
- persistence;
- observability;
- API transport;
- sandbox execution;
- application-specific agents.

LangGraph MUST orchestrate workflows, but business logic MUST NOT be embedded unnecessarily inside the graph definition.

Langfuse MUST provide observability and evaluation. It MUST NOT determine workflow control flow.

Vector-store implementations MUST NOT contain agent logic.

Tool implementations MUST NOT depend directly on LangGraph unless a LangGraph-specific adapter is necessary.

---

## 1.2 Typed interfaces

All public framework interfaces MUST use:

- Python type hints;
- Pydantic models where runtime validation is useful;
- Protocol / ABC interfaces for replaceable components;
- structured model output rather than free-form parsing where possible.

Avoid passing arbitrary dictionaries across architectural boundaries.

---

## 1.3 Async-first

Network, database, model, vector-store and external-tool interfaces SHOULD be asynchronous.

Prefer:

```python
async def ...
```

over synchronous implementations when the underlying operation is I/O bound.

Synchronous wrappers may exist where libraries require them.

---

## 1.4 Safe by default

The framework MUST distinguish at least:

- read-only operations;
- workspace writes;
- command execution;
- remote execution;
- external mutation;
- destructive operations.

High-risk operations MUST support explicit human approval.

The default software-development runtime MUST execute commands inside an isolated workspace/container rather than directly on the host.

---

## 1.5 Observable by default

Every workflow execution SHOULD be traceable.

Important operations SHOULD emit:

- trace identifiers;
- workflow name;
- node name;
- model;
- latency;
- token usage where available;
- tool name;
- tool result status;
- retrieval query;
- retrieved document identifiers;
- error information;
- evaluation results.

Langfuse is the primary AI observability backend.

OpenTelemetry-compatible instrumentation SHOULD be supported for application metrics.

---

## 1.6 Testability

Every layer MUST be testable independently.

The project MUST contain:

- unit tests;
- integration tests;
- graph/workflow tests;
- retrieval tests;
- tool authorization tests;
- API tests;
- evaluation fixtures.

No milestone is complete merely because an example runs manually.

---

# 2. Target high-level architecture

```text
┌───────────────────────────────────────────────────────────────┐
│                         CLIENTS                               │
│                                                               │
│      Web UI        CLI        IDE        External API         │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                         FASTAPI                               │
│                                                               │
│ Auth │ Sessions │ REST │ SSE/WebSocket │ Health │ Admin      │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                         LANGGRAPH                             │
│                                                               │
│ Planner → Router → Executor → Verifier → Response             │
│    ▲                    │          │                          │
│    └──────── retry ─────┴──────────┘                          │
│                                                               │
│ State │ Checkpoints │ HITL │ Branches │ Loops │ Subgraphs     │
└──────────┬───────────────────┬──────────────────┬─────────────┘
           │                   │                  │
           ▼                   ▼                  ▼
┌────────────────┐    ┌────────────────┐   ┌───────────────────┐
│      LLM       │    │     TOOLS      │   │        RAG        │
│                │    │                │   │                   │
│ OpenAI         │    │ filesystem     │   │ embeddings        │
│ optional       │    │ shell          │   │ hybrid retrieval  │
│ other providers│    │ git            │   │ reranking         │
│ local models   │    │ GitHub         │   │ metadata filters  │
│                │    │ HTTP           │   │ pgvector          │
│                │    │ DB             │   │ Tree-sitter       │
│                │    │ SSH            │   │                   │
│                │    │ Docker         │   │                   │
│                │    │ MCP            │   │                   │
└────────────────┘    └────────────────┘   └───────────────────┘
           │                   │                  │
           └───────────────────┼──────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                          STORAGE                              │
│                                                               │
│ PostgreSQL       Redis         Artifact Store                 │
│                                                               │
│ application      cache         logs                           │
│ workflows        locks         reports                        │
│ checkpoints      coordination  binaries                       │
│ metadata                       attachments                    │
│ pgvector                                                     │
└───────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                      OBSERVABILITY                            │
│                                                               │
│                         LANGFUSE                              │
│                                                               │
│ traces │ prompts │ costs │ datasets │ evaluations │ feedback  │
│                                                               │
│ OpenTelemetry → Prometheus/Grafana optional                   │
└───────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                          RUNTIME                              │
│                                                               │
│ Docker sandbox │ Docker Compose │ workers │ future Kubernetes │
└───────────────────────────────────────────────────────────────┘
```

---

# 3. Initial technology choices

| Concern | Default |
|---|---|
| Language | Python 3.12+ |
| Package/build | `uv` + `pyproject.toml` |
| API | FastAPI |
| Validation | Pydantic v2 |
| Workflow | LangGraph |
| LLM integration | LangChain model interfaces and/or provider SDK adapters |
| Primary LLM | OpenAI |
| Tracing/evals | Langfuse |
| SQL database | PostgreSQL |
| Vector database | PostgreSQL + pgvector |
| Cache | Redis |
| ORM | SQLAlchemy 2 async |
| Migration | Alembic |
| HTTP | httpx |
| Retry | tenacity |
| Logging | structlog or stdlib structured logging |
| Code parsing | Tree-sitter |
| Container SDK | Docker SDK or controlled subprocess wrapper |
| Testing | pytest + pytest-asyncio |
| Formatting/linting | Ruff |
| Type checking | mypy or pyright |
| Local runtime | Docker Compose |
| Configuration | pydantic-settings |

Do not introduce a dedicated vector database, Kubernetes, Kafka or a graph database in V1 unless a concrete requirement requires it.

Interfaces SHOULD make future replacement possible.

---

# 4. Required repository layout

```text
ai-framework/
├── AGENTS.md
├── AI_FRAMEWORK_SPEC.md
├── README.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── Makefile
├── docker-compose.yml
├── alembic.ini
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── health.py
│   │       ├── workflows.py
│   │       ├── documents.py
│   │       └── agents.py
│   │
│   ├── core/
│   │   ├── errors.py
│   │   ├── ids.py
│   │   ├── types.py
│   │   └── lifecycle.py
│   │
│   ├── llm/
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── factory.py
│   │   └── providers/
│   │       ├── openai.py
│   │       └── mock.py
│   │
│   ├── workflows/
│   │   ├── registry.py
│   │   ├── base.py
│   │   └── engineering/
│   │       ├── graph.py
│   │       ├── state.py
│   │       ├── nodes.py
│   │       ├── routing.py
│   │       └── prompts.py
│   │
│   ├── agents/
│   │   ├── shared/
│   │   │   ├── planner.py
│   │   │   ├── verifier.py
│   │   │   └── reviewer.py
│   │   ├── software_engineer/
│   │   └── security_engineer/
│   │
│   ├── tools/
│   │   ├── base.py
│   │   ├── models.py
│   │   ├── permissions.py
│   │   ├── registry.py
│   │   ├── executor.py
│   │   ├── filesystem/
│   │   ├── shell/
│   │   ├── git/
│   │   ├── github/
│   │   ├── http/
│   │   ├── database/
│   │   ├── ssh/
│   │   ├── docker/
│   │   └── mcp/
│   │
│   ├── rag/
│   │   ├── models.py
│   │   ├── ingestion.py
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   ├── hybrid.py
│   │   ├── reranker.py
│   │   └── code/
│   │       ├── parser.py
│   │       ├── symbols.py
│   │       └── chunker.py
│   │
│   ├── vectorstores/
│   │   ├── base.py
│   │   └── pgvector.py
│   │
│   ├── memory/
│   │   ├── models.py
│   │   ├── conversation.py
│   │   └── semantic.py
│   │
│   ├── persistence/
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── repositories/
│   │   └── checkpoints.py
│   │
│   ├── cache/
│   │   └── redis.py
│   │
│   ├── artifacts/
│   │   ├── base.py
│   │   └── filesystem.py
│   │
│   ├── observability/
│   │   ├── langfuse.py
│   │   ├── logging.py
│   │   └── telemetry.py
│   │
│   ├── prompts/
│   │   ├── registry.py
│   │   └── defaults/
│   │
│   └── sandbox/
│       ├── base.py
│       ├── models.py
│       ├── docker.py
│       └── policy.py
│
├── migrations/
├── scripts/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── workflows/
│   ├── tools/
│   ├── rag/
│   ├── api/
│   └── evals/
└── docs/
    ├── architecture.md
    ├── tools.md
    ├── rag.md
    ├── workflows.md
    └── development.md
```

---

# 5. Configuration contract

All runtime configuration MUST come from environment variables or configuration objects.

Do not scatter `os.getenv()` calls throughout the codebase.

Use one validated configuration model.

```python
class Settings(BaseSettings):
    environment: str = "development"
    openai_api_key: SecretStr | None = None
    database_url: str
    redis_url: str
    langfuse_public_key: str | None = None
    langfuse_secret_key: SecretStr | None = None
    langfuse_base_url: str | None = None
    artifact_root: Path = Path("./data/artifacts")
    sandbox_enabled: bool = True
    sandbox_image: str = "ai-framework-sandbox:latest"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
```

Required `.env.example` variables:

```dotenv
APP_ENV=development

OPENAI_API_KEY=

DATABASE_URL=postgresql+asyncpg://ai:ai@postgres:5432/ai
REDIS_URL=redis://redis:6379/0

LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_BASE_URL=

ARTIFACT_ROOT=/data/artifacts

SANDBOX_ENABLED=true
SANDBOX_IMAGE=ai-framework-sandbox:latest
```

Secrets MUST NOT be committed.

---

# 6. Core data model

Stable identifiers are required for:

- user;
- session/thread;
- workflow run;
- trace;
- tool execution;
- artifact;
- document;
- chunk;
- evaluation.

Minimum persistence entities:

```text
users
sessions
workflow_runs
messages
documents
document_chunks
artifacts
tool_executions
approvals
evaluations
```

Workflow state persistence SHOULD use LangGraph-compatible checkpoint persistence where possible.

---

# 7. LLM layer

No workflow node SHOULD directly instantiate provider clients.

Use a model registry/factory.

```python
model = llm_registry.get("planner")
result = await model.ainvoke(messages)
```

Logical model roles:

```yaml
models:
  planner:
    provider: openai
    model: <configured-model>

  worker:
    provider: openai
    model: <configured-model>

  verifier:
    provider: openai
    model: <configured-model>

  embedding:
    provider: openai
    model: <configured-embedding-model>
```

Exact model names must remain configuration.

Planning, routing and verification SHOULD use structured output.

```python
class PlanStep(BaseModel):
    id: str
    description: str
    tool_category: str | None = None


class ExecutionPlan(BaseModel):
    objective: str
    steps: list[PlanStep]
    success_criteria: list[str]
```

---

# 8. LangGraph workflow contract

## 8.1 Base workflow

```text
START
  │
  ▼
normalize_request
  │
  ▼
retrieve_context
  │
  ▼
plan
  │
  ▼
route
  │
  ▼
execute
  │
  ▼
verify
  │
  ├──── success ───► finalize ───► END
  │
  ├──── retry ─────► route
  │
  └──── approval ──► human_approval ─► execute
```

## 8.2 State

```python
class EngineeringState(TypedDict):
    run_id: str
    thread_id: str
    request: str
    messages: list
    plan: dict | None
    current_step: int
    retrieved_context: list
    tool_requests: list
    tool_results: list
    artifact_ids: list[str]
    modified_files: list[str]
    verification: dict | None
    attempts: int
    max_attempts: int
    status: str
    error: str | None
```

Large blobs MUST NOT be stored in graph state.

Use artifact references.

## 8.3 Bounded loops

Every loop MUST have:

```text
max_attempts
max_tool_calls
max_execution_time
```

## 8.4 Checkpointing

Required behavior:

1. stable `thread_id`;
2. checkpoint meaningful state transitions;
3. resume paused workflows;
4. preserve approval state;
5. expose run state via API.

---

# 9. Tool framework

## 9.1 Tool descriptor

```python
class ToolPermission(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    REMOTE_EXECUTE = "remote_execute"
    EXTERNAL_WRITE = "external_write"
    DESTRUCTIVE = "destructive"


class ToolDescriptor(BaseModel):
    name: str
    description: str
    permission: ToolPermission
    timeout_seconds: int = 30
    sandbox_required: bool = False
```

## 9.2 Tool result

```python
class ToolResult(BaseModel):
    success: bool
    output: str | None = None
    error: str | None = None
    exit_code: int | None = None
    artifact_ids: list[str] = []
    metadata: dict[str, Any] = {}
```

## 9.3 Permission policy

| Permission | Default |
|---|---|
| READ | allow |
| WRITE | allow only inside workspace |
| EXECUTE | sandbox required |
| REMOTE_EXECUTE | approval |
| EXTERNAL_WRITE | approval |
| DESTRUCTIVE | approval + explicit policy |

Tool authorization MUST happen outside the LLM.

## 9.4 Required V1 tools

Filesystem:

- `read_file`
- `list_directory`
- `search_text`
- `write_file`
- `apply_patch`

Shell:

- `run_command`

Git:

- `git_status`
- `git_diff`
- `git_log`
- `git_show`
- `git_branch`

HTTP:

- controlled GET/POST;
- timeout;
- response size limit;
- optional domain policy.

Database:

- read-only SQL first;
- parameterized queries.

Docker:

- create isolated workspace;
- execute command;
- collect output;
- destroy environment.

MCP:

- create adapter interface;
- one demonstration integration is sufficient for V1.

---

# 10. Sandbox runtime

The sandbox MUST support:

```text
repository checkout
filesystem modification
build
tests
static analysis
diff generation
artifact collection
```

Protocol:

```python
class Sandbox(Protocol):

    async def create(self, spec: SandboxSpec) -> SandboxHandle:
        ...

    async def exec(
        self,
        handle: SandboxHandle,
        command: list[str],
        *,
        timeout: int,
    ) -> CommandResult:
        ...

    async def copy_in(...):
        ...

    async def copy_out(...):
        ...

    async def destroy(...):
        ...
```

Safety requirements:

- execution timeout;
- CPU/memory limits where practical;
- restricted mounts;
- workspace-only writes;
- optional network disable;
- command logging;
- cleanup.

Never execute untrusted commands as root directly on the host.

---

# 11. RAG subsystem

## 11.1 Ingestion

```text
source
  │
  ▼
loader
  │
  ▼
normalizer
  │
  ▼
chunker
  │
  ▼
metadata enrichment
  │
  ▼
embedding
  │
  ▼
PostgreSQL + pgvector
```

Initial sources:

- Markdown;
- text;
- source code;
- JSON;
- HTML text extraction.

## 11.2 Models

```python
class Document(BaseModel):
    id: str
    source: str
    content_type: str
    title: str | None
    checksum: str
    metadata: dict[str, Any]


class Chunk(BaseModel):
    id: str
    document_id: str
    text: str
    ordinal: int
    token_count: int | None
    metadata: dict[str, Any]
```

## 11.3 Metadata

Repository metadata SHOULD include:

```json
{
  "repository": "project",
  "commit": "abc123",
  "path": "src/security/verify.c",
  "language": "c",
  "symbol": "verify_signature",
  "symbol_type": "function",
  "module": "security"
}
```

---

# 12. Code-aware retrieval

Do not use only fixed-size token chunking for code.

Use Tree-sitter where supported.

```text
source file
  │
  ▼
Tree-sitter parser
  │
  ├─ module
  ├─ class
  ├─ function
  ├─ method
  ├─ struct
  └─ symbol
       │
       ▼
semantic code chunks
```

V1 languages:

- Python;
- C;
- C++;
- shell.

Other languages may fall back to text chunking.

---

# 13. Hybrid retrieval

High-level interface:

```python
results = await retriever.search(
    query,
    filters=filters,
    limit=10,
)
```

Pipeline:

```text
query
 │
 ├── vector search
 │
 ├── lexical search
 │
 └── symbol/path search
       │
       ▼
      merge
       │
       ▼
  deduplicate
       │
       ▼
    rerank
       │
       ▼
 top-k context
```

V1 reranking may use reciprocal-rank fusion or another deterministic score-fusion strategy.

The interface must allow dedicated rerankers later.

---

# 14. Vector store

```python
class VectorStore(Protocol):

    async def upsert(self, chunks: list[EmbeddedChunk]) -> None:
        ...

    async def search(
        self,
        vector: list[float],
        *,
        filters: dict | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        ...

    async def delete_document(self, document_id: str) -> None:
        ...
```

V1 backend:

```text
PostgreSQL + pgvector
```

Workflow code MUST NOT depend on pgvector-specific details.

---

# 15. Memory

Keep these separate:

### Conversation memory
- sessions;
- messages;
- summaries;
- workflow associations.

### Semantic memory
- explicitly persisted reusable knowledge.

### Workflow state
- LangGraph checkpoint state.

Do not merge all three into one generic memory abstraction.

---

# 16. Artifact system

Large data MUST be stored outside graph state.

Artifacts include:

- source archives;
- logs;
- generated patches;
- reports;
- test outputs;
- binaries;
- uploaded files.

```python
class ArtifactStore(Protocol):

    async def put(
        self,
        stream,
        *,
        name: str,
        content_type: str,
        metadata: dict | None = None,
    ) -> Artifact:
        ...

    async def get(self, artifact_id: str):
        ...

    async def delete(self, artifact_id: str) -> None:
        ...
```

V1 backend: local filesystem.

Future backend: S3/MinIO.

---

# 17. Langfuse integration

Langfuse MUST be integrated from the first functional workflow.

Trace:

```text
workflow
node
LLM generation
tool call
retrieval
evaluation
```

Trace metadata SHOULD include:

```text
run_id
thread_id
workflow
environment
application
user_id if available
repository if relevant
```

Do not trace secrets.

Typical graph invocation:

```python
await graph.ainvoke(
    state,
    config={
        "callbacks": [langfuse_handler],
        "metadata": {
            "run_id": run_id,
            "workflow": "engineering",
        },
    },
)
```

Observability failure MUST NOT crash core workflow logic.

---

# 18. Prompt management

Prompts MUST NOT be duplicated across nodes.

Provide a registry:

```python
prompt = prompt_registry.get(
    "engineering.planner",
    version="v1",
)
```

Each major prompt SHOULD have:

- identifier;
- version;
- purpose;
- structured output contract;
- tests/evaluation cases.

Keep prompts in Git initially. Allow Langfuse-managed prompts later.

---

# 19. FastAPI application

Required endpoints:

```text
GET  /health
GET  /ready

POST /v1/workflows/{workflow}/runs
GET  /v1/workflows/runs/{run_id}
POST /v1/workflows/runs/{run_id}/resume

POST /v1/documents
POST /v1/documents/{document_id}/ingest
GET  /v1/documents/{document_id}

POST /v1/search

GET  /v1/tools
```

Optional:

```text
GET /v1/workflows/runs/{run_id}/events
```

using SSE or WebSocket.

---

# 20. Workflow API behavior

Request:

```json
{
  "thread_id": "optional-existing-thread",
  "request": "Analyze this repository and identify where firmware signatures are verified.",
  "context": {
    "repository": "workspace"
  }
}
```

Response:

```json
{
  "run_id": "uuid",
  "thread_id": "uuid",
  "status": "running"
}
```

Status:

```json
{
  "run_id": "uuid",
  "status": "completed",
  "result": {},
  "artifacts": []
}
```

V1 may execute synchronously internally while preserving the run abstraction.

---

# 21. Human-in-the-loop approval

Workflow status:

```text
WAITING_FOR_APPROVAL
```

Model:

```python
class ApprovalRequest(BaseModel):
    id: str
    run_id: str
    tool_name: str
    permission: ToolPermission
    description: str
    arguments_preview: dict
    status: Literal[
        "pending",
        "approved",
        "denied",
    ]
```

Required use cases:

- remote SSH;
- GitHub mutation;
- DB writes;
- destructive filesystem action;
- other external side effects.

---

# 22. Initial engineering agent

Implement one useful end-to-end reference agent.

Capabilities:

1. receive engineering request;
2. inspect repository;
3. use hybrid retrieval and direct tools;
4. generate plan;
5. inspect files;
6. optionally modify files in sandbox;
7. run tests/checks;
8. review diff;
9. verify success criteria;
10. return result and artifacts.

Default mode SHOULD be read-only unless modification is explicitly requested.

Suggested graph:

```text
normalize
   │
retrieve_repository_context
   │
planner
   │
tool_router
   │
tool_executor
   │
result_analyzer
   │
verifier
   │
   ├─ continue → tool_router
   ├─ approval → approval
   └─ complete → finalizer
```

---

# 23. Initial security engineering agent

Create as second reference workflow after the framework base is stable.

Capabilities:

- interpret requirement;
- identify evidence;
- search source;
- inspect configuration;
- execute controlled commands;
- aggregate evidence;
- evaluate sufficiency;
- produce grounded response.

The agent MUST distinguish:

```text
observed fact
inference
missing evidence
```

It MUST NOT fabricate evidence.

---

# 24. Persistence

Use:

- SQLAlchemy 2 async;
- Alembic;
- repository/service abstractions.

Minimum tables:

```text
sessions
workflow_runs
messages
documents
document_chunks
artifacts
tool_executions
approvals
evaluations
```

Enable pgvector through migration/bootstrap.

---

# 25. Redis

Use Redis for:

- cache;
- short-lived locks;
- rate-limit support;
- optional event coordination.

Redis MUST NOT be the source of truth for durable workflow data.

---

# 26. Error model

```text
AIFrameworkError
├── ConfigurationError
├── WorkflowError
├── ToolError
│   ├── ToolPermissionError
│   ├── ToolTimeoutError
│   └── ToolExecutionError
├── RetrievalError
├── ModelError
├── SandboxError
└── PersistenceError
```

API errors MUST expose stable machine-readable codes.

---

# 27. Logging

Structured logs SHOULD include:

```text
timestamp
level
run_id
thread_id
workflow
node
tool
message
```

Never log:

- API keys;
- passwords;
- authorization headers;
- private keys.

Implement redaction where practical.

---

# 28. Evaluation framework

Evaluation fixtures:

```text
tests/evals/
```

Example:

```yaml
name: code_location_test

input:
  request: "Locate signature verification logic."

expect:
  required_tools:
    - search_text

  forbidden_tools:
    - git_push

  must_reference_source: true

  criteria:
    - "Identifies relevant file"
    - "Provides grounded explanation"
```

Build a runner that can:

```text
load dataset
run workflow
collect output
score deterministic criteria
write Langfuse scores
```

Prefer deterministic checks before LLM-as-judge.

---

# 29. Security requirements

Minimum controls:

1. secrets via config/secret manager;
2. SQL parameterization;
3. path normalization;
4. workspace boundary enforcement;
5. shell timeout;
6. output-size limits;
7. HTTP timeout;
8. optional domain restrictions;
9. tool permission enforcement;
10. human approval;
11. sandbox isolation;
12. trace/log redaction.

Tests MUST cover path traversal and tool-permission bypass.

---

# 30. Dependency policy

Before adding a dependency, evaluate:

- whether stdlib is sufficient;
- whether an existing dependency already solves it;
- maintenance quality;
- coupling introduced.

Do not add multiple libraries for the same concern without reason.

---

# 31. Coding standards

Required:

- Python 3.12+;
- Ruff;
- type hints;
- docstrings on public interfaces;
- async context managers where appropriate;
- dependency injection;
- no hidden mutable global clients;
- no wildcard imports;
- no secrets in source;
- deterministic tests.

Checks:

```bash
ruff format --check .
ruff check .
mypy app
pytest
```

or a documented equivalent type checker.

---

# 32. Testing requirements

Unit tests:

- settings;
- permission policy;
- registries;
- chunkers;
- retrieval fusion;
- routing;
- artifact paths.

Integration tests:

- PostgreSQL;
- pgvector;
- Redis;
- checkpoint persistence;
- Langfuse initialization;
- Docker sandbox;
- FastAPI.

Workflow tests:

- success;
- retry;
- retry exhaustion;
- tool failure;
- approval interruption;
- approval resume;
- empty retrieval;
- model failure.

Security tests:

- path traversal;
- unauthorized destructive tool;
- workspace escape;
- command timeout.

Tests MUST NOT require paid model calls by default.

Provide mock model and mock embeddings.

---

# 33. Docker Compose

Initial services:

```text
api
postgres
redis
```

Langfuse may be:

- external cloud;
- or self-hosted via optional profile.

Framework startup MUST NOT fail if Langfuse is unavailable.

---

# 34. Developer commands

Required Make targets:

```bash
make install
make dev
make test
make lint
make format
make typecheck
make migrate
make ingest
make compose-up
make compose-down
make clean
```

---

# 35. README requirements

README MUST cover:

1. purpose;
2. architecture;
3. prerequisites;
4. quick start;
5. configuration;
6. local services;
7. first API request;
8. first ingestion;
9. first workflow;
10. tests;
11. adding a tool;
12. adding a workflow;
13. Langfuse setup;
14. security model.

---

# 36. Codex CLI implementation protocol

Codex MUST:

1. inspect repository first;
2. read `AGENTS.md`;
3. treat this spec as architectural contract;
4. implement one milestone at a time;
5. avoid unrelated refactors;
6. run tests after each milestone;
7. report failed checks;
8. keep repository runnable;
9. avoid speculative infrastructure;
10. update docs when architecture changes.

Before each task:

```text
1. inspect current tree
2. inspect pyproject
3. inspect tests
4. identify affected modules
5. implement smallest coherent change
6. format
7. lint
8. type-check
9. test
10. inspect diff
```

Do not fake production implementations merely to satisfy tests.

---

# 37. Recommended root AGENTS.md

```markdown
# AI Framework repository instructions

Read `AI_FRAMEWORK_SPEC.md` before making architectural changes.

## Implementation rules

- Implement the specification incrementally.
- Keep modules loosely coupled.
- Prefer typed interfaces and Pydantic schemas.
- Use async APIs for I/O-bound code.
- Do not bypass tool permission checks.
- Never execute untrusted commands directly on the host when sandbox execution is required.
- Keep Langfuse observability separate from workflow logic.
- PostgreSQL + pgvector is the default persistence/vector backend.
- Do not introduce additional infrastructure unless required by the spec or current task.
- Add or update tests for behavioral changes.
- Run formatting, linting and relevant tests before considering a task complete.

## Standard checks

```bash
ruff format --check .
ruff check .
mypy app
pytest
```
```

---

# 38. Implementation milestones

## Milestone 0 — Repository bootstrap

Deliver:

- package structure;
- `pyproject.toml`;
- settings;
- FastAPI skeleton;
- `/health`;
- structured logging;
- pytest;
- Ruff;
- type checking;
- `.env.example`;
- Dockerfile;
- Docker Compose with PostgreSQL and Redis;
- initial README.

Acceptance:

```bash
make lint
make typecheck
make test
```

pass.

---

## Milestone 1 — Persistence

Deliver:

- async SQLAlchemy;
- Alembic;
- core tables;
- pgvector extension;
- repositories;
- integration tests.

Acceptance:

- clean database migrates;
- workflow run can be created/read;
- pgvector is available.

---

## Milestone 2 — LLM abstraction

Deliver:

- model protocol;
- registry;
- OpenAI adapter;
- mock model;
- structured output example;
- role-to-model configuration.

Acceptance:

- workflow requests logical model role;
- tests run with mocks;
- live smoke test is opt-in.

---

## Milestone 3 — Langfuse

Deliver:

- centralized client/callback;
- graceful disable;
- metadata helpers;
- tracing in minimal graph.

Acceptance:

- graph works without credentials;
- graph works with tracing;
- tracing failure does not fail business logic.

---

## Milestone 4 — LangGraph foundation

Deliver:

- workflow registry;
- state;
- planner/executor/verifier graph;
- checkpoint persistence;
- bounded retry;
- workflow tests.

Acceptance:

```text
success
retry then success
retry exhaustion
model failure
resume from checkpoint
```

---

## Milestone 5 — Tool framework

Deliver:

- descriptors;
- registry;
- normalized results;
- permission service;
- filesystem read tools;
- search;
- workspace-safe write;
- shell interface;
- audit persistence.

Acceptance:

- read tools work;
- unauthorized tool is rejected;
- workspace escape is rejected;
- tool calls are traced.

---

## Milestone 6 — Docker sandbox

Deliver:

- sandbox protocol;
- Docker implementation;
- workspace mount;
- timeout;
- resource limits;
- result model;
- cleanup.

Acceptance:

- execute simple command;
- create artifact;
- timeout works;
- host path escape denied;
- cleanup verified.

---

## Milestone 7 — RAG baseline

Deliver:

- documents;
- chunks;
- embeddings;
- pgvector store;
- ingestion;
- semantic search;
- metadata filtering;
- APIs.

Acceptance:

- ingest Markdown;
- retrieve expected chunk;
- delete/re-ingest;
- metadata filtering works.

---

## Milestone 8 — Hybrid retrieval

Deliver:

- PostgreSQL lexical/full-text search;
- vector search integration;
- exact path/symbol search;
- deduplication;
- reciprocal-rank fusion or equivalent;
- retrieval tests.

Acceptance:

- exact function names rank highly;
- semantic queries find conceptually relevant code;
- metadata filters are preserved;
- deterministic ranking test exists.

---

## Milestone 9 — Tree-sitter code intelligence

Deliver:

- parser abstraction;
- Python parser;
- C parser;
- C++ parser;
- shell parser;
- symbol extraction;
- semantic code chunking.

Acceptance:

- functions/classes/structs are extracted;
- chunk metadata includes symbol/path/language;
- malformed files fail gracefully;
- unsupported language falls back to text chunking.

---

## Milestone 10 — Engineering agent

Deliver:

- repository analysis workflow;
- planning;
- direct code search;
- RAG retrieval;
- file inspection;
- verification;
- result generation.

Read-only mode first.

Acceptance:

Given a test repository, the agent can:

1. locate a relevant implementation;
2. cite/identify files and symbols;
3. explain reasoning grounded in retrieved source;
4. avoid modifying files.

---

## Milestone 11 — Modification workflow

Deliver:

- sandbox checkout;
- patch generation;
- apply patch;
- run tests;
- collect diff;
- review node;
- verifier.

Acceptance:

On fixture repository:

```text
request
  ↓
modify
  ↓
tests
  ↓
review
  ↓
verified diff
```

The workflow MUST not write outside sandbox/workspace.

---

## Milestone 12 — Human approval

Deliver:

- approval persistence;
- graph interruption;
- API endpoints to approve/deny;
- resume logic.

Acceptance:

- external-write tool pauses;
- approval resumes;
- denial terminates or reroutes safely;
- approval survives process restart.

---

## Milestone 13 — Additional tools

Implement production-quality adapters for selected tools:

- GitHub;
- SSH;
- HTTP;
- read-only SQL;
- MCP.

Acceptance:

- each tool has permission category;
- timeouts;
- normalized result;
- tracing;
- tests using mocks/fixtures.

---

## Milestone 14 — Security engineering workflow

Deliver:

- requirement interpreter;
- evidence planner;
- source/config retrieval;
- controlled command use;
- evidence aggregator;
- evidence sufficiency verifier;
- report response.

Acceptance:

- clearly marks facts/inferences/missing evidence;
- does not invent command output;
- retries when evidence is insufficient;
- stores evidence references.

---

## Milestone 15 — Evaluation pipeline

Deliver:

- dataset loader;
- deterministic scorer;
- workflow runner;
- Langfuse evaluation integration;
- report output.

Acceptance:

```bash
make eval
```

runs local evaluation fixtures.

---

## Milestone 16 — Streaming/events

Deliver:

- workflow event model;
- SSE or WebSocket endpoint;
- node/tool status events;
- client disconnect handling.

Acceptance:

User can observe:

```text
planning
retrieving
executing tool
verifying
completed
```

without exposing chain-of-thought.

---

## Milestone 17 — Authentication and authorization

Deliver basic pluggable application authentication.

Do not tightly bind framework internals to one identity provider.

Support:

- authenticated user;
- roles/scopes;
- workflow ownership;
- approval authorization.

Acceptance:

- one user cannot access another user's workflow run;
- authorization tests exist.

---

## Milestone 18 — Artifact backend abstraction validation

Deliver:

- filesystem backend complete;
- S3/MinIO-compatible backend optional;
- backend selected through config.

Acceptance:

Application behavior is independent of backend.

---

## Milestone 19 — Operational telemetry

Add:

- OpenTelemetry instrumentation;
- Prometheus-compatible metrics;
- optional Grafana setup.

Minimum metrics:

```text
workflow_runs_total
workflow_failures_total
workflow_duration_seconds
tool_calls_total
tool_failures_total
retrieval_duration_seconds
llm_requests_total
```

Acceptance:

Metrics endpoint/exporter documented and testable.

---

## Milestone 20 — Production hardening

Perform:

- dependency audit;
- configuration review;
- load testing;
- concurrency testing;
- sandbox threat review;
- tracing privacy review;
- database index review;
- timeout review;
- failure-mode testing.

Deliver:

```text
docs/production.md
docs/security.md
docs/operations.md
```

---

# 39. Non-goals for V1

Do NOT make these mandatory for V1:

- Kubernetes;
- Kafka;
- graph database;
- custom model training;
- distributed multi-region deployment;
- autonomous Git push;
- autonomous production DB writes;
- unrestricted SSH;
- arbitrary host shell execution;
- browser automation;
- complex multi-agent social simulation.

Design extension points, but do not build speculative complexity.

---

# 40. Definition of Done for framework V1

V1 is complete when all of the following are true:

- FastAPI service runs locally;
- PostgreSQL migrations succeed;
- pgvector retrieval works;
- Redis integration works;
- LangGraph workflows persist checkpoints;
- Langfuse traces functional workflows;
- LLM registry supports mock + OpenAI;
- tools have permission metadata;
- shell execution is sandboxed;
- repository code can be ingested;
- Tree-sitter code chunks are generated;
- hybrid retrieval works;
- engineering agent can analyze a repository;
- engineering agent can safely modify a fixture repository in sandbox;
- workflow can pause for approval and resume;
- evaluation runner works;
- tests run without paid model calls;
- README supports fresh-machine setup;
- core security tests pass.

---

# 41. Codex CLI execution strategy

The recommended workflow is to give Codex one milestone at a time.

Example initial command:

```bash
codex
```

Then instruct:

```text
Read AGENTS.md and AI_FRAMEWORK_SPEC.md.

Implement Milestone 0 only.

Before changing files, inspect the repository.

Follow the architecture and coding standards in the spec.

Do not implement later milestones yet.

When finished:
1. run formatting,
2. run linting,
3. run type checks,
4. run tests,
5. summarize changed files,
6. report any unresolved issues.
```

For the next iteration:

```text
Read AGENTS.md and AI_FRAMEWORK_SPEC.md.

Review the current implementation and verify Milestone 0 acceptance criteria.

Then implement Milestone 1 only.

Do not redesign components that already satisfy the spec unless required.

Run all relevant checks when complete.
```

Continue in this way milestone by milestone.

---

# 42. Codex implementation guardrails

Codex MUST NOT:

- silently weaken tests;
- remove security checks to make tests pass;
- bypass the permission service;
- execute arbitrary commands on the host when sandboxing is required;
- hard-code API keys;
- hard-code production model names;
- couple workflows directly to pgvector;
- embed Langfuse logic into routing decisions;
- put large files into graph state;
- create unbounded workflow loops;
- automatically perform destructive or external-write actions.

When uncertain, prefer the safer and more modular implementation.

---

# 43. Recommended first implementation sequence

Use this exact sequence unless a blocking dependency requires a small adjustment:

```text
0  Bootstrap
1  Persistence
2  LLM abstraction
3  Langfuse
4  LangGraph
5  Tools
6  Sandbox
7  RAG
8  Hybrid retrieval
9  Tree-sitter
10 Engineering analysis agent
11 Engineering modification agent
12 Human approval
13 External tools/MCP
14 Security engineering agent
15 Evaluations
16 Streaming
17 Authentication
18 Artifact backend
19 Telemetry
20 Production hardening
```

---

# 44. Future extensions

Possible later modules:

```text
app/agents/
├── devops_engineer/
├── cloud_engineer/
├── test_engineer/
├── code_reviewer/
├── documentation_agent/
├── research_agent/
└── data_engineer/
```

Potential future infrastructure:

- Qdrant;
- Milvus;
- Pinecone;
- Neo4j;
- Temporal;
- Kubernetes;
- Vault;
- Keycloak;
- S3/MinIO;
- vLLM;
- local embedding models;
- dedicated rerankers.

These should be added only after a concrete need appears.

---

# 45. Architectural decision rule

When implementing any new feature, ask:

```text
Is this workflow logic?
→ LangGraph/workflows

Is this an action?
→ tools

Is this authorization?
→ tool permission/security layer

Is this knowledge retrieval?
→ RAG/retriever/vector store

Is this durable application data?
→ PostgreSQL

Is this short-lived coordination/cache?
→ Redis

Is this a large file/result?
→ artifact store

Is this model access?
→ LLM registry

Is this tracing/evaluation?
→ Langfuse/observability

Is this isolated code execution?
→ sandbox

Is this transport/API?
→ FastAPI
```

Do not mix these layers without a documented architectural reason.

---

# 46. Final implementation objective

The completed framework should enable applications such as:

```text
User request
   │
   ▼
FastAPI / CLI
   │
   ▼
LangGraph workflow
   │
   ├── LLM planner
   ├── RAG retrieval
   ├── tool execution
   ├── sandbox
   ├── verification
   ├── human approval
   └── final response
   │
   ▼
PostgreSQL / pgvector / Redis / artifacts
   │
   ▼
Langfuse traces + evaluations
```

The framework should make adding a new AI application primarily a matter of defining:

1. state;
2. nodes;
3. routing;
4. prompts;
5. allowed tools;
6. retrieval sources;
7. success criteria.

The reusable infrastructure should remain unchanged for most new applications.

---

# 47. Immediate task for Codex

The first Codex task is:

```text
Read AGENTS.md and AI_FRAMEWORK_SPEC.md.

Implement Milestone 0 — Repository bootstrap.

Do not implement later milestones.

Create the initial Python project, FastAPI application, configuration layer,
logging, test infrastructure, Docker development setup, Makefile commands,
and README quick-start.

Run all Milestone 0 acceptance checks before stopping.
```

After Milestone 0 is complete and validated, proceed to Milestone 1 in a separate implementation step.
