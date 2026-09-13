import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from .checkpoint import CheckpointStore
from .config import get_settings
from .graph import NexusOrchestrator
from .ingestion import IngestionService
from .metrics import Metrics
from .models import (
    DocumentSummary,
    HealthResponse,
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    ReadinessResponse,
)
from .observability import event, new_request_id
from .policy import PolicyViolation, validate_request
from .providers import build_generator
from .settings_validation import validate_settings
from .version import __version__

settings = get_settings()
checkpoints = CheckpointStore(settings.checkpoint_db)
metrics = Metrics()
from .corpus import CorpusRegistry

corpus = CorpusRegistry()
ingestion = IngestionService(corpus)
orchestrator = NexusOrchestrator(settings, checkpoints, build_generator(settings), corpus)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


logging.basicConfig(level=settings.log_level, format="%(message)s")
app = FastAPI(
    title="Nexus Graph Agent",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs" if settings.enable_docs else None,
)
app.add_middleware(
    CORSMiddleware, allow_origins=settings.allowed_origins, allow_methods=["*"], allow_headers=["*"]
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = new_request_id()
    started = time.perf_counter()
    response = await call_next(request)
    metrics.increment(f"http_{response.status_code}")
    response.headers["x-request-id"] = request_id
    event(
        "http_request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round((time.perf_counter() - started) * 1000, 2),
    )
    return response


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="nexus-agent", provider=settings.model_provider)


@app.get("/ready", response_model=ReadinessResponse)
async def ready() -> ReadinessResponse:
    return ReadinessResponse(
        status="ready",
        service="nexus-agent",
        provider=settings.model_provider,
        warnings=validate_settings(settings),
        version=__version__,
    )


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics_endpoint() -> str:
    return metrics.prometheus()


@app.post("/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    try:
        validate_request(request, settings.max_question_length)
    except PolicyViolation as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    metrics.increment("queries_total")
    return await orchestrator.run(request.question, request.session_id)


@app.post("/v1/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest) -> IngestResponse:
    metrics.increment("ingests_total")
    return ingestion.ingest(request)


@app.get("/v1/documents", response_model=list[DocumentSummary])
async def documents() -> list[DocumentSummary]:
    return [
        DocumentSummary(
            id=item.id,
            title=item.title,
            source_uri=item.source_uri,
            checksum=item.checksum,
            ingested_at=item.ingested_at,
        )
        for item in ingestion.list_documents()
    ]
