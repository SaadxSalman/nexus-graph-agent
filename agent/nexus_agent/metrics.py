from __future__ import annotations

from collections import Counter
from threading import Lock


class Metrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: Counter[str] = Counter()
        self._durations: dict[str, list[float]] = {}

    def increment(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] += value

    def observe(self, name: str, value: float) -> None:
        with self._lock:
            self._durations.setdefault(name, []).append(value)

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "counters": dict(self._counters),
                "durations": {key: values[-100:] for key, values in self._durations.items()},
            }

    def prometheus(self) -> str:
        snapshot = self.snapshot()
        lines = [f"nexus_{key} {value}" for key, value in snapshot["counters"].items()]
        return "\n".join(lines) + "\n"
