from typing import Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    session_id: str | None = None
    approved: bool | None = None


class IngestRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    text: str = Field(min_length=20, max_length=200_000)
    source_uri: str | None = Field(default=None, max_length=2000)
    document_id: str | None = Field(default=None, max_length=120)


class IngestResponse(BaseModel):
    id: str
    title: str
    checksum: str
    ingested_at: str


class DocumentSummary(BaseModel):
    id: str
    title: str
    source_uri: str | None
    checksum: str
    ingested_at: str


class Source(BaseModel):
    id: str
    title: str
    excerpt: str
    score: float
    kind: Literal["document", "entity"]


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    confidence: float
    iterations: int
    provider: str
    trace: list[str]
    session_id: str


class HealthResponse(BaseModel):
    status: str
    service: str
    provider: str


class ReadinessResponse(HealthResponse):
    warnings: list[str]
    version: str
