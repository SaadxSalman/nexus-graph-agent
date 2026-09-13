from __future__ import annotations

from .corpus import CorpusRegistry, IngestedDocument
from .models import IngestRequest, IngestResponse


class IngestionService:
    def __init__(self, corpus: CorpusRegistry):
        self.corpus = corpus

    def ingest(self, request: IngestRequest) -> IngestResponse:
        document = self.corpus.upsert(
            request.title, request.text, request.source_uri, request.document_id
        )
        return IngestResponse(
            id=document.id,
            title=document.title,
            checksum=document.checksum,
            ingested_at=document.ingested_at,
        )

    def list_documents(self) -> list[IngestedDocument]:
        return self.corpus.list()
