from __future__ import annotations

import json
import logging
import time
from contextvars import ContextVar
from typing import Self
from uuid import uuid4

request_id_context: ContextVar[str] = ContextVar("request_id", default="-")
logger = logging.getLogger("nexus-agent")


def new_request_id() -> str:
    request_id = uuid4().hex
    request_id_context.set(request_id)
    return request_id


def event(name: str, **fields: object) -> None:
    payload = {"event": name, "request_id": request_id_context.get(), **fields}
    logger.info(json.dumps(payload, default=str, separators=(",", ":")))


class Timer:
    def __init__(self, name: str, **fields: object):
        self.name = name
        self.fields = fields
        self.started = 0.0

    def __enter__(self) -> Self:
        self.started = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        event(
            self.name,
            duration_ms=round((time.perf_counter() - self.started) * 1000, 2),
            error=bool(exc_value),
            **self.fields,
        )
