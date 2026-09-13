import re
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str
    topics: tuple[str, ...]


@dataclass(frozen=True)
class Entity:
    name: str
    kind: str
    description: str
    related: tuple[str, ...]


DOCUMENTS = [
    Document(
        "doc-orchestration",
        "Orchestrator design",
        "The orchestrator decomposes a request into focused sub-questions, runs retrieval in parallel, and stops at a configured iteration limit. It records every decision in a checkpoint so a human can approve sensitive actions.",
        ("orchestration", "orchestrator", "checkpoint", "agent", "stop"),
    ),
    Document(
        "doc-crag",
        "Corrective retrieval",
        "The relevance grader scores evidence for coverage and source quality. When confidence is below the threshold, the rewrite node creates a narrower query and retrieves again. The loop stops when evidence passes or the iteration budget is exhausted.",
        ("grading", "rewrite", "retrieval"),
    ),
    Document(
        "doc-hybrid",
        "Hybrid retrieval",
        "Vector retrieval finds semantically similar passages while graph traversal follows known relationships between entities. Combining both views reduces ambiguity and makes multi-hop questions inspectable.",
        ("vector", "graph", "retrieval"),
    ),
    Document(
        "doc-guardrails",
        "Production guardrails",
        "Pre-model hooks redact common PII patterns and trim context to a character budget. Post-model checks require citations, expose the provider, and reject answers with no supporting evidence.",
        ("safety", "observability", "guardrails"),
    ),
    Document(
        "doc-mcp",
        "MCP capability boundary",
        "MCP tools are isolated by an allowlist. Local search and entity lookup are read-only capabilities; external tools must be explicitly enabled before the agent can call them.",
        ("mcp", "tools", "security"),
    ),
]

ENTITIES = [
    Entity(
        "Orchestrator",
        "component",
        "Stateful controller for decomposition, retrieval, grading, and synthesis.",
        ("Relevance Grader", "Checkpoint Store"),
    ),
    Entity(
        "Relevance Grader",
        "component",
        "Evaluates evidence coverage and determines whether to rewrite.",
        ("Orchestrator", "Vector Index"),
    ),
    Entity(
        "Vector Index",
        "store",
        "Semantic document index used for candidate retrieval.",
        ("Graph Store", "Relevance Grader"),
    ),
    Entity(
        "Graph Store",
        "store",
        "Entity and relationship view used for multi-hop traversal.",
        ("Vector Index", "MCP"),
    ),
    Entity(
        "MCP",
        "protocol",
        "Permissioned tool boundary for local and external capabilities.",
        ("Graph Store", "Guardrails"),
    ),
    Entity(
        "Guardrails",
        "control",
        "PII, context, citation, and iteration controls.",
        ("MCP", "Orchestrator"),
    ),
]


def _terms(text: str) -> set[str]:
    return {term for term in re.findall(r"[a-z0-9]+", text.lower()) if len(term) > 2}


def search_documents(
    query: str, limit: int = 5, documents: Iterable[Document] | None = None
) -> list[tuple[Document, float]]:
    terms = _terms(query)
    ranked: list[tuple[Document, float]] = []
    for document in documents or DOCUMENTS:
        haystack = _terms(f"{document.title} {document.text} {' '.join(document.topics)}")
        overlap = len(terms & haystack)
        topic_bonus = 0.15 if terms & set(document.topics) else 0
        score = min(0.99, 0.2 + (overlap / max(len(terms), 1)) * 0.7 + topic_bonus)
        if overlap or not terms:
            ranked.append((document, score))
    return sorted(ranked, key=lambda item: item[1], reverse=True)[:limit]


def traverse_entities(
    query: str, limit: int = 4, entities: Iterable[Entity] | None = None
) -> list[tuple[Entity, float]]:
    terms = _terms(query)
    ranked: list[tuple[Entity, float]] = []
    for entity in entities or ENTITIES:
        haystack = _terms(
            f"{entity.name} {entity.kind} {entity.description} {' '.join(entity.related)}"
        )
        overlap = len(terms & haystack)
        if overlap:
            ranked.append((entity, min(0.95, 0.35 + overlap / max(len(terms), 1) * 0.6)))
    return sorted(ranked, key=lambda item: item[1], reverse=True)[:limit]


def redact_pii(text: str) -> str:
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[redacted-email]", text)
    return re.sub(r"\b(?:\+?\d[\d -]{7,}\d)\b", "[redacted-phone]", text)


def trim_context(items: Iterable[str], max_chars: int) -> str:
    output = "\n".join(items)
    return output[:max_chars]
