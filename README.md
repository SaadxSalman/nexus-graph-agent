# Nexus Graph Agent

Nexus Graph Agent is a production-minded reference architecture for agentic Retrieval-Augmented Generation (RAG). It treats retrieval as an active investigation loop instead of a single similarity lookup. The system decomposes a request, searches documents and entity relationships in parallel, evaluates evidence quality, rewrites weak investigations, and returns a cited answer with an inspectable trace.

This repository is intentionally runnable in two modes:

- **Local zero-key mode:** a deterministic in-memory knowledge base and grounded synthesizer make the architecture demonstrable without paid APIs, PostgreSQL, Chroma, or Ollama.
- **Service mode:** Docker Compose starts PostgreSQL with pgvector, ChromaDB, the Python agent, and the Rust edge service. Provider adapters and persistence boundaries are ready for replacing the local implementation with hosted models and production indexes.

The low-level public backend boundary is written in Rust. The agentic workflow is written in Python 3.11+ because LangGraph and the surrounding RAG ecosystem are Python-first.

## What Is Included

### Rust edge service

The Rust binary, `nexus-edge`, is the public HTTP edge:

- Serves the browser console.
- Exposes `GET /health`.
- Validates and forwards `POST /api/query` to the agent service.
- Returns normalized upstream errors as JSON.
- Adds permissive development CORS and HTTP tracing.
- Has a small attack surface and no model or database credentials.

This makes the user-facing boundary a compiled low-level service while keeping orchestration easy to evolve.

### Python agent service

The Python service in `agent/nexus_agent` owns the decision-making loop:

1. **Decompose:** split a multi-part question into focused sub-questions.
2. **Retrieve:** run local document search and entity graph traversal concurrently.
3. **Grade:** calculate evidence coverage and source quality.
4. **Correct:** rewrite the request when confidence is below the threshold.
5. **Checkpoint:** persist session state in SQLite by default.
6. **Synthesize:** produce a grounded answer with source records and trace metadata.

The implementation caps attempts with `MAX_AGENT_ITERATIONS`. Context is capped with `MAX_CONTEXT_CHARS`. Basic email and phone patterns are redacted before retrieval. Answers always expose their source list and provider name.

### MCP capability server

`agent/nexus_agent/mcp_server.py` exposes two read-only tools:

- `local_search(query)` searches the local document index.
- `entity_lookup(query)` traverses the local relationship graph.

Tools are controlled by the comma-separated `MCP_ALLOWED_TOOLS` environment variable. This allowlist is checked at invocation time. External tools should follow the same pattern and be added only with explicit permission and timeouts.

### Storage boundaries

The checked-in local implementation provides a useful deterministic fallback:

- Document retrieval: a transparent lexical hybrid-style scorer over seeded documents.
- Entity retrieval: relationship-aware traversal over a seeded graph.
- Checkpoints: SQLite.

The project includes service dependencies for the intended production path:

- PostgreSQL 16 with pgvector for relational metadata and vector search.
- ChromaDB for an operational vector collection.
- `asyncpg` and Chroma client dependencies in the agent package.

The adapters can be introduced behind the retrieval functions without changing the HTTP contract or graph state model.

## Architecture

```text
Browser console
      |
      v
Rust nexus-edge :8080
      |
      v
Python FastAPI agent :8000
      |
      v
LangGraph-compatible investigation loop
      |
      +--> document/vector retrieval
      +--> entity/graph traversal
      +--> MCP read-only tools
      +--> relevance grading and query rewrite
      +--> checkpoint store
      |
      v
Grounded response + sources + trace
```

The current orchestrator is intentionally represented by a small explicit state object and node-like methods. It is compatible with LangGraph's state-machine model and keeps the behavior understandable in zero-key mode. To enable full LangGraph checkpointing, replace the local loop with a `StateGraph` whose nodes map to `_decompose`, `_retrieve`, `_grade`, `_rewrite`, and `_synthesize`; the request and response schemas do not need to change.

## Repository Layout

```text
.
├── .env                          # local configuration and secrets; always ignored
├── .gitignore                   # ignores .env, runtime state, build output
├── Cargo.toml                   # Rust edge manifest
├── Dockerfile.edge              # multi-stage Rust image
├── docker-compose.yml            # Postgres, Chroma, agent, edge
├── .github/workflows/ci.yml      # Rust, Python, and container CI
├── .dockerignore                 # lean build context
├── Makefile                      # common developer commands
├── migrations/                   # PostgreSQL/pgvector schema and audit tables
├── deploy/k8s/                   # Kubernetes reference manifests and secret template
├── docs/                         # architecture, operations, and ADRs
├── evals/                        # golden questions for retrieval evaluation
├── scripts/                      # health and evaluation utilities
├── static/index.html             # working investigation console
├── src/main.rs                   # Rust HTTP edge
└── agent/
    ├── Dockerfile                # Python service image
    ├── pyproject.toml            # dependencies and tooling
    ├── nexus_agent/
    │   ├── api.py                # FastAPI application
    │   ├── checkpoint.py         # durable SQLite checkpoints
    │   ├── config.py             # typed environment settings
    │   ├── corpus.py             # thread-safe ingestion registry
    │   ├── graph.py              # orchestration and correction loop
    │   ├── ingestion.py          # document ingestion service
    │   ├── mcp_server.py         # allowlisted MCP tools
    │   ├── metrics.py            # counters and Prometheus output
    │   ├── models.py             # API contracts
    │   ├── observability.py      # request IDs and structured events
    │   ├── policy.py             # input and citation guardrails
    │   ├── providers.py          # local and OpenAI generation adapters
    │   └── retrieval.py           # documents, graph, guards
    └── tests/
        ├── test_agent.py         # pytest behavior suite
        ├── smoke.py              # dependency-light smoke check
        └── test_api.py           # HTTP contract tests
```

## Requirements

For local development:

- Rust stable with Cargo.
- Python 3.11 or newer.
- Docker Desktop is optional for service mode.
- PowerShell, Bash, or an equivalent shell.

Python 3.14 is supported by the local code path, but Python 3.11-3.13 is the conservative production target because the broader AI ecosystem may lag new interpreter releases.

## Configuration

The repository already contains one local configuration file used by every service:

```powershell
Get-Content .env
```

The `.env` file is gitignored. Add real API keys only there. Never paste real API keys into source files, Dockerfiles, README content, or tracked configuration. The important groups are:

| Variable | Purpose | Default |
|---|---|---|
| `MODEL_PROVIDER` | `local`, `openai`, `anthropic`, or a future adapter | `local` |
| `MODEL_NAME` | Provider model identifier | `local-grounded` |
| `OPENAI_API_KEY` | OpenAI credential, if selected | empty |
| `ANTHROPIC_API_KEY` | Anthropic credential, if selected | empty |
| `OLLAMA_BASE_URL` | Local Ollama endpoint | `http://127.0.0.1:11434` |
| `RUST_API_HOST` / `RUST_API_PORT` | Rust listener | `127.0.0.1:8080` |
| `AGENT_HOST` / `AGENT_PORT` | Python listener | `127.0.0.1:8000` |
| `AGENT_BASE_URL` | Rust-to-agent URL | `http://127.0.0.1:8000` |
| `POSTGRES_URL` | PostgreSQL connection string | local pgvector URL |
| `CHROMA_URL` | Chroma server URL | `http://localhost:8001` |
| `CHROMA_COLLECTION` | Chroma collection name | `nexus_documents` |
| `CHECKPOINT_DB` | SQLite checkpoint path | `./.data/checkpoints.db` |
| `MAX_AGENT_ITERATIONS` | Hard correction-loop cap | `3` |
| `MAX_CONTEXT_CHARS` | Context budget | `12000` |
| `REQUEST_TIMEOUT_SECONDS` | External request timeout budget | `30` |
| `MCP_ALLOWED_TOOLS` | Comma-separated MCP permission list | `local_search,entity_lookup` |

## Run Without Docker

The local provider requires no model keys or databases. Install the Python package into the active interpreter:

```powershell
python -m pip install -e ".\\agent[dev]"
```

Start the agent in one terminal:

```powershell
python -m uvicorn nexus_agent.api:app --app-dir agent --host 127.0.0.1 --port 8000
```

Start the Rust edge in another:

```powershell
cargo run
```

Open <http://127.0.0.1:8080>. The console's health indicator should turn green. Enter a question such as:

```text
How does corrective retrieval improve graph search?
```

Or call the API directly:

```powershell
$body = @{ question = "How does the orchestrator use graph retrieval?" } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8080/api/query -Method Post -ContentType "application/json" -Body $body
```

The direct agent endpoint is also available at `http://127.0.0.1:8000/v1/query`.

### Ingest a document

The local corpus is mutable at runtime. Ingested documents receive a stable checksum-based ID and participate in subsequent investigations:

```powershell
$body = @{
  title = "Internal retrieval notes"
  text = "The relevance grader compares evidence coverage and source quality before synthesis."
  source_uri = "file:///notes/retrieval.md"
} | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/v1/ingest -Method Post -ContentType "application/json" -Body $body
Invoke-RestMethod http://127.0.0.1:8000/v1/documents
```

For production, the same request should enqueue chunking and embedding work rather than keeping text in process memory. The API shape remains stable so clients do not need to know which storage adapter is active.

## Run With Docker Compose

Create `.env`, then build and start all services:

```powershell
docker compose up --build
```

Open <http://127.0.0.1:8080>. Service health endpoints:

```text
GET http://127.0.0.1:8080/health
GET http://127.0.0.1:8000/health
GET http://127.0.0.1:8000/ready
GET http://127.0.0.1:8000/metrics
```

Stop the stack while keeping named volumes:

```powershell
docker compose down
```

Delete local database volumes as well:

```powershell
docker compose down -v
```

The default zero-key provider does not require the database containers for its answer path. They are included so the reference architecture has a repeatable place to connect production persistence and vector services.

## Tests and Checks

Compile the Rust edge:

```powershell
cargo check
```

Compile Python modules without executing the app:

```powershell
python -m compileall -q agent
```

Run the behavior suite after installing the development extra:

```powershell
python -m pytest agent/tests -q
```

Run the dependency-light smoke check when a test runner is unavailable:

```powershell
$env:PYTHONPATH = "agent"
python agent/tests/smoke.py
```

The tests cover relevant document ranking, entity traversal, PII redaction, checkpoint creation, source citation, iteration limits, readiness, metrics, ingestion, document listing, and prompt-injection rejection. CI runs the same checks on every push and pull request.

The optional evaluation harness reads `evals/golden_questions.jsonl`:

```powershell
$env:PYTHONPATH = "agent"
python scripts/evaluate.py
```

## API Contract

### `POST /api/query`

The Rust edge accepts and forwards:

```json
{
  "question": "How does the grader decide whether to rewrite?",
  "session_id": "optional-stable-id",
  "approved": true
}
```

A successful response looks like:

```json
{
  "answer": "The grounded answer is driven by ...",
  "sources": [
    {
      "id": "doc-crag",
      "title": "Corrective retrieval",
      "excerpt": "...",
      "score": 0.91,
      "kind": "document"
    }
  ],
  "confidence": 0.86,
  "iterations": 1,
  "provider": "local",
  "trace": ["decomposed request ...", "iteration 1 ..."],
  "session_id": "..."
}
```

### `GET /health`

The edge returns its service name and configured agent URL. The agent returns its provider name. Health checks do not call a model and should stay cheap.

### `GET /ready`

Readiness returns the service version, provider, and configuration warnings. A warning is informational in development. Deployment systems should fail readiness when required external dependencies are unavailable.

### `GET /metrics`

Returns a small Prometheus-compatible text payload for request status codes, query count, and ingestion count. It is intentionally dependency-light; replace it with an OpenTelemetry/Prometheus exporter when operating at scale.

### `POST /v1/ingest`

Accepts `title`, `text`, optional `source_uri`, and optional `document_id`. The response includes the checksum and ingestion timestamp. Repeating the same explicit ID updates the document. In the local implementation this registry is process-local; PostgreSQL is the durable production target.

### `GET /v1/documents`

Returns document metadata without returning full document text. This is suitable for an administrative inventory view and avoids accidentally exposing corpus content in list responses.

## Provider Model

Provider selection is explicit and validated at startup:

| Provider | Behavior | Credentials |
|---|---|---|
| `local` | Deterministic grounded response for development and CI | none |
| `openai` | Async chat completion with a strict evidence-only system instruction | `OPENAI_API_KEY` |
| `anthropic` | Reserved adapter slot for the Anthropic implementation | `ANTHROPIC_API_KEY` |
| `ollama` | Reserved adapter slot for a local model endpoint | `OLLAMA_BASE_URL` |

The provider interface accepts a question, bounded context, and source IDs, and returns text plus usage metadata. This keeps token accounting and model-specific SDK imports outside the graph controller. Add retries and circuit breakers around the provider boundary rather than inside retrieval nodes.

## Ingestion and Data Lifecycle

The intended durable lifecycle is:

1. Accept an authenticated ingest request.
2. Hash and deduplicate the source document.
3. Split text into stable, ordered chunks.
4. Extract entities and relationships.
5. Generate embeddings with the configured embedding model.
6. Write document metadata, chunks, entities, and edges transactionally.
7. Upsert vectors to pgvector and optionally Chroma.
8. Emit an audit event and make the document available to retrieval.

The checked-in local registry implements steps 1, 2, and 8 so the workflow can be demonstrated without infrastructure. `migrations/001_initial.sql` defines the production tables and tenant columns. The unique `(tenant_id, checksum)` constraint makes ingestion idempotent per tenant.

## Observability and Auditability

Every HTTP response includes `x-request-id`. Structured events include request ID, event name, status, and duration. The graph trace is returned to the caller because an agentic answer should be inspectable, not an opaque string. Production deployments should add:

- OpenTelemetry spans around retrieval, grading, tool calls, and provider generation.
- Token and cost counters by tenant, model, and provider.
- Histograms for first-token latency, total latency, and retrieval latency.
- Audit rows for policy rejection, tool authorization, human approval, and source selection.
- Redaction before logs leave the process.

The audit migration is deliberately separate from the document migration so compliance retention policies can evolve independently.

## Deployment Profiles

### Single-machine development

Run the agent and Rust edge directly. Use the local provider and SQLite checkpoint store. This profile is the fastest feedback loop and needs no containers.

### Docker Compose

Use `docker compose up --build` for a complete local service graph. PostgreSQL and Chroma are included for adapter development even though local zero-key queries can run without them.

### Kubernetes reference

Apply `deploy/k8s/namespace.yaml`, create a real secret from `deploy/k8s/secret.example.yaml`, then apply `agent.yaml` and `edge.yaml`. The manifests use two replicas, readiness probes, liveness probes, and separate ConfigMap/Secret sources. They are intentionally incomplete for a specific cloud provider: add an ingress, network policies, persistent volumes, workload identity, image registry references, and resource limits before production use.

## Developer Workflow

The Make targets provide a common vocabulary across Windows, Linux, and CI environments:

```text
make install       install Python development dependencies
make check         lint, compile Python, and cargo check
make test          run the pytest suite
make smoke         run the dependency-light smoke check
make dev           run the Python service with reload
make edge          run the Rust edge
make compose-up    build and start the full Docker stack
```

On Windows PowerShell, the equivalent commands are documented above and in `scripts/healthcheck.ps1`. The repository does not commit virtual environments, build output, runtime state, or secrets.

## Evaluation Strategy

The golden set is intentionally small and readable. Each case names required evidence and a minimum confidence. A mature evaluation suite should add:

- Retrieval recall at K for documents and graph entities.
- Claim-level citation precision and recall.
- Faithfulness judgments by a separate evaluator model.
- Prompt-injection resistance cases.
- Tenant isolation tests.
- Tool authorization and approval tests.
- Latency and cost budgets.
- Regression cases for rewritten queries.

Never optimize only for a single aggregate score. A high answer score with missing citations or a policy bypass is a failed release.

## Production Hardening Checklist

Before exposing this beyond a local network:

- Replace permissive Rust CORS with the exact frontend origins.
- Put TLS and an identity-aware reverse proxy in front of both services.
- Require authenticated sessions and authorize every MCP capability.
- Move checkpoints from local SQLite to a managed PostgreSQL schema.
- Add tenant IDs to every document, entity, checkpoint, and source query.
- Replace lexical fallback retrieval with a pgvector/Chroma hybrid retriever.
- Add model provider adapters with explicit timeout, retry, and token budgets.
- Encrypt provider keys using the deployment secret manager.
- Add structured trace IDs, OpenTelemetry spans, and redacted request logs.
- Add rate limits and request body limits at the Rust edge.
- Add a human approval interrupt before any write-capable or externally visible tool.
- Treat retrieved documents as untrusted input and defend against prompt injection.
- Add a citation verifier that checks claims against selected source spans.
- Add evaluation datasets for answer faithfulness, retrieval recall, rewrite quality, and tool authorization.
- Pin container image digests and scan dependencies in CI.
- Run the Rust service as a non-root user and apply a read-only filesystem where possible.

## Extension Points

### Real model synthesis

The local synthesizer in `NexusOrchestrator._synthesize` is deliberately deterministic. Add a provider interface with a method such as `async generate(question, context)`, then select it from `MODEL_PROVIDER`. Keep the local provider as a fallback for tests and outages. The provider must receive only trimmed, redacted context and must be instructed to cite source IDs.

### PostgreSQL and pgvector

Create migrations for documents, chunks, embeddings, entities, relationships, tenants, and checkpoints. Use one transaction for ingestion metadata and an idempotent document hash. Query vector candidates with a tenant predicate before ranking. Do not use a vector score as proof of factual correctness; keep the relevance grader.

### ChromaDB

Use the configured collection for chunk embeddings and metadata filters. Chroma can be useful for rapid retrieval iteration, while PostgreSQL remains the system of record for identities, permissions, and graph relationships.

### LangGraph checkpointing

Convert `Investigation` to a TypedDict state and compile a graph with conditional edges from the grader to either synthesis or rewrite. Use a checkpointer keyed by `session_id`. Put human approval at a graph interrupt immediately before any non-read-only MCP action.

### MCP servers

Keep each MCP server narrow. Declare tool schemas, validate arguments, apply an allowlist, set network timeouts, and return structured errors. Never give a general-purpose shell tool to an untrusted agent. Separate read and write servers and require approval for writes.

## Security Notes

The local `.env` contains development defaults and is ignored by Git. Add real provider keys only to that file. The Rust service does not read model keys. The Python service redacts common PII before retrieval, trims context, caps loop iterations, and rejects the idea of unrestricted MCP access by default. These are reference controls, not a security certification; production deployments still need identity, tenant isolation, threat modeling, dependency scanning, and operational monitoring.

## License

Use the license and contribution policy appropriate for the organization deploying this reference architecture.
