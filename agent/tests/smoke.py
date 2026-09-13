"""Dependency-light smoke check for environments without pytest on PATH."""

import asyncio
import tempfile
from pathlib import Path

from nexus_agent.checkpoint import CheckpointStore
from nexus_agent.config import Settings
from nexus_agent.graph import NexusOrchestrator


async def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        settings = Settings(checkpoint_db=str(Path(directory) / "checkpoints.db"))
        result = await NexusOrchestrator(settings, CheckpointStore(settings.checkpoint_db)).run(
            "How does corrective retrieval improve graph search?"
        )
        assert result.sources
        assert result.confidence > 0
        assert result.session_id
        print(f"smoke ok: {len(result.sources)} sources, confidence={result.confidence:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
