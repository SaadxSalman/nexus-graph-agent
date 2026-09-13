from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from uuid import uuid4

from .checkpoint import CheckpointStore
from .config import Settings
from .corpus import CorpusRegistry
from .models import QueryResponse, Source
from .providers import GenerationRequest, TextGenerator
from .retrieval import (
    DOCUMENTS,
    ENTITIES,
    redact_pii,
    search_documents,
    traverse_entities,
    trim_context,
)


@dataclass
class Investigation:
    question: str
    session_id: str
    subquestions: list[str]
    sources: list[Source]
    context: str = ""
    confidence: float = 0.0
    iterations: int = 0
    trace: list[str] | None = None


class NexusOrchestrator:
    def __init__(
        self,
        settings: Settings,
        checkpoints: CheckpointStore,
        generator: TextGenerator | None = None,
        corpus: CorpusRegistry | None = None,
    ):
        self.settings = settings
        self.checkpoints = checkpoints
        self.generator = generator
        self.corpus = corpus

    async def run(self, question: str, session_id: str | None = None) -> QueryResponse:
        session_id = session_id or str(uuid4())
        investigation = Investigation(
            question=redact_pii(question),
            session_id=session_id,
            subquestions=self._decompose(question),
            sources=[],
            trace=[],
        )
        investigation.trace.append("decomposed request into focused retrieval questions")
        for iteration in range(1, self.settings.max_agent_iterations + 1):
            investigation.iterations = iteration
            await self._retrieve(investigation)
            investigation.confidence = self._grade(investigation)
            investigation.trace.append(
                f"iteration {iteration}: graded evidence at {investigation.confidence:.2f}"
            )
            self._checkpoint(investigation)
            if investigation.confidence >= 0.62:
                break
            investigation.subquestions = self._rewrite(investigation)
            investigation.trace.append("evidence below threshold; rewrote retrieval questions")
        answer = await self._synthesize(investigation)
        investigation.trace.append("synthesized cited answer")
        return QueryResponse(
            answer=answer,
            sources=investigation.sources,
            confidence=investigation.confidence,
            iterations=investigation.iterations,
            provider=self.settings.model_provider,
            trace=investigation.trace,
            session_id=session_id,
        )

    def _decompose(self, question: str) -> list[str]:
        parts = [
            part.strip(" .?!")
            for part in re.split(r"\band\b|[,;]", question, flags=re.IGNORECASE)
            if part.strip()
        ]
        return parts[:4] or [question]

    async def _retrieve(self, investigation: Investigation) -> None:
        documents = list(DOCUMENTS) + (self.corpus.as_documents() if self.corpus else [])
        entities = list(ENTITIES) + (self.corpus.as_entities() if self.corpus else [])
        results = await asyncio.gather(
            *(
                asyncio.to_thread(search_documents, query, 5, documents)
                for query in investigation.subquestions
            )
        )
        entity_results = await asyncio.gather(
            *(
                asyncio.to_thread(traverse_entities, query, 4, entities)
                for query in investigation.subquestions
            )
        )
        sources: dict[str, Source] = {}
        for result_set in results:
            for document, score in result_set:
                sources[document.id] = Source(
                    id=document.id,
                    title=document.title,
                    excerpt=document.text,
                    score=round(score, 3),
                    kind="document",
                )
        for result_set in entity_results:
            for entity, score in result_set:
                source_id = f"entity-{entity.name.lower().replace(' ', '-')}"
                sources[source_id] = Source(
                    id=source_id,
                    title=entity.name,
                    excerpt=entity.description + " Related: " + ", ".join(entity.related),
                    score=round(score, 3),
                    kind="entity",
                )
        investigation.sources = sorted(
            sources.values(), key=lambda source: source.score, reverse=True
        )[:10]
        investigation.context = trim_context(
            (f"[{source.title}] {source.excerpt}" for source in investigation.sources),
            self.settings.max_context_chars,
        )

    def _grade(self, investigation: Investigation) -> float:
        if not investigation.sources:
            return 0.0
        question_terms = set(re.findall(r"[a-z0-9]+", investigation.question.lower()))
        evidence_terms = set(re.findall(r"[a-z0-9]+", investigation.context.lower()))
        coverage = len(question_terms & evidence_terms) / max(len(question_terms), 1)
        quality = sum(source.score for source in investigation.sources[:4]) / min(
            len(investigation.sources), 4
        )
        return min(0.98, 0.35 * coverage + 0.65 * quality)

    def _rewrite(self, investigation: Investigation) -> list[str]:
        keywords = [
            word
            for word in re.findall(r"[a-zA-Z]{4,}", investigation.question)
            if word.lower() not in {"what", "does", "with", "that", "this"}
        ]
        return [
            "retrieval architecture " + " ".join(keywords[:5]),
            "guardrails evidence " + " ".join(keywords[:4]),
        ]

    async def _synthesize(self, investigation: Investigation) -> str:
        if not investigation.sources:
            return "I could not find grounded evidence for this request. Try naming the component or decision you want investigated."
        if self.generator:
            generated = await self.generator.generate(
                GenerationRequest(
                    question=investigation.question,
                    context=investigation.context,
                    source_ids=tuple(source.id for source in investigation.sources),
                )
            )
            return generated.text
        lead = investigation.sources[0]
        supporting = "; ".join(source.title for source in investigation.sources[1:4])
        return (
            f"The grounded answer is driven by {lead.title.lower()}: {lead.excerpt} "
            f"This is cross-checked against {supporting or 'the available evidence'}. "
            f"The investigation reached {investigation.confidence:.0%} confidence after {investigation.iterations} iteration(s). "
            "Sources are listed below so the reasoning can be inspected."
        )

    def _checkpoint(self, investigation: Investigation) -> None:
        self.checkpoints.save(
            investigation.session_id,
            {
                "question": investigation.question,
                "iterations": investigation.iterations,
                "confidence": investigation.confidence,
                "trace": investigation.trace,
            },
        )
