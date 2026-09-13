from __future__ import annotations

import re

from .models import QueryRequest


class PolicyViolation(ValueError):
    pass


def validate_request(request: QueryRequest, max_question_length: int) -> None:
    question = request.question.strip()
    if len(question) != len(request.question):
        raise PolicyViolation("question must not have leading or trailing whitespace")
    if len(question) > max_question_length:
        raise PolicyViolation("question exceeds the configured limit")
    if re.search(
        r"(?:ignore|bypass)\s+(?:(?:all|previous)\s+){1,2}(?:instructions|rules)",
        question,
        re.IGNORECASE,
    ):
        raise PolicyViolation("prompt-injection phrase rejected")


def verify_citations(answer: str, source_ids: set[str]) -> bool:
    if not source_ids:
        return False
    return any(source_id in answer for source_id in source_ids)
