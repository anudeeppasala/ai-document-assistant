from dataclasses import dataclass
from typing import Protocol


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]:
        ...


class AnswerProvider(Protocol):
    def answer(self, question: str, context: str, prompt: str) -> str:
        ...


@dataclass(frozen=True)
class RuntimeProviders:
    mode: str
    embedding: EmbeddingProvider
    answer: AnswerProvider
