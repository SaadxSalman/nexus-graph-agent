import pytest

from nexus_agent.checkpoint import CheckpointStore
from nexus_agent.config import Settings
from nexus_agent.graph import NexusOrchestrator
from nexus_agent.retrieval import redact_pii, search_documents, traverse_entities


def test_local_retrieval_returns_relevant_evidence():
    results = search_documents("How does corrective retrieval rewrite a query?")
    assert results[0][0].id == "doc-crag"
    assert results[0][1] > 0.2


def test_entity_traversal_is_multi_hop_aware():
    results = traverse_entities("graph and vector retrieval")
    assert {item[0].name for item in results} >= {"Vector Index", "Graph Store"}


def test_pii_redaction():
    assert "someone@example.com" not in redact_pii("Contact someone@example.com")


@pytest.mark.asyncio
async def test_orchestrator_checkpoints_and_cites(tmp_path):
    settings = Settings(checkpoint_db=str(tmp_path / "checkpoints.db"), max_agent_iterations=2)
    orchestrator = NexusOrchestrator(settings, CheckpointStore(settings.checkpoint_db))
    response = await orchestrator.run("How does the orchestrator use graph retrieval?")
    assert response.sources
    assert response.iterations <= 2
    assert response.session_id
    assert "Evidence IDs:" in response.answer or "Sources are listed" in response.answer
