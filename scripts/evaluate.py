from __future__ import annotations

import asyncio
import json
from pathlib import Path

from nexus_agent.checkpoint import CheckpointStore
from nexus_agent.config import Settings
from nexus_agent.graph import NexusOrchestrator


async def main() -> None:
    settings = Settings(checkpoint_db=".data/evaluation.db")
    agent = NexusOrchestrator(settings, CheckpointStore(settings.checkpoint_db))
    cases = [json.loads(line) for line in Path("evals/golden_questions.jsonl").read_text().splitlines() if line.strip()]
    passed = 0
    for case in cases:
        result = await agent.run(case["question"])
        source_text = " ".join([source.id + " " + source.title for source in result.sources])
        source_match = all(required.lower() in source_text.lower() for required in case["required_sources"])
        ok = source_match and result.confidence >= case["min_confidence"]
        passed += int(ok)
        print(f"{'PASS' if ok else 'FAIL'} {case['id']} confidence={result.confidence:.2f}")
    print(f"{passed}/{len(cases)} evaluation cases passed")
    raise SystemExit(0 if passed == len(cases) else 1)


if __name__ == "__main__":
    asyncio.run(main())
