from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .config import Settings


@dataclass(frozen=True)
class GenerationRequest:
    question: str
    context: str
    source_ids: tuple[str, ...]


@dataclass(frozen=True)
class GenerationResult:
    text: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int


class TextGenerator(ABC):
    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        raise NotImplementedError


class LocalGenerator(TextGenerator):
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        first_line = (
            request.context.splitlines()[0] if request.context else "No evidence was retrieved."
        )
        citation = ", ".join(request.source_ids[:3]) or "none"
        text = (
            f"Grounded response for: {request.question}\n\n"
            f"{first_line}\n\n"
            f"Evidence IDs: {citation}. The response is limited to retrieved evidence."
        )
        return GenerationResult(
            text, "local", "local-grounded", len(request.context) // 4, len(text) // 4
        )


class OpenAIGenerator(TextGenerator):
    def __init__(self, settings: Settings):
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key, timeout=settings.request_timeout_seconds
        )
        self.model = settings.model_name

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "Answer only from the supplied evidence. Cite source IDs.",
                },
                {
                    "role": "user",
                    "content": f"Question: {request.question}\nEvidence:\n{request.context}",
                },
            ],
        )
        usage = response.usage
        text = response.choices[0].message.content or "No answer returned."
        return GenerationResult(
            text,
            "openai",
            self.model,
            usage.prompt_tokens if usage else 0,
            usage.completion_tokens if usage else 0,
        )


def build_generator(settings: Settings) -> TextGenerator:
    if settings.model_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when MODEL_PROVIDER=openai")
        return OpenAIGenerator(settings)
    return LocalGenerator()
