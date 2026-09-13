from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from threading import Lock

from .retrieval import Document, Entity


@dataclass(frozen=True)
class IngestedDocument:
    id: str
    title: str
    text: str
    source_uri: str | None
    checksum: str
    ingested_at: str


class CorpusRegistry:
    def __init__(self) -> None:
        self._documents: dict[str, IngestedDocument] = {}
        self._lock = Lock()

    def upsert(
        self, title: str, text: str, source_uri: str | None = None, document_id: str | None = None
    ) -> IngestedDocument:
        checksum = sha256(text.encode("utf-8")).hexdigest()
        stable_id = document_id or f"doc-{checksum[:16]}"
        document = IngestedDocument(
            stable_id, title, text, source_uri, checksum, datetime.now(UTC).isoformat()
        )
        with self._lock:
            self._documents[stable_id] = document
        return document

    def get(self, document_id: str) -> IngestedDocument | None:
        return self._documents.get(document_id)

    def list(self) -> list[IngestedDocument]:
        return sorted(self._documents.values(), key=lambda item: item.ingested_at, reverse=True)

    def as_documents(self) -> list[Document]:
        return [Document(item.id, item.title, item.text, ()) for item in self.list()]

    def as_entities(self) -> list[Entity]:
        return []
