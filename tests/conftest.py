from dataclasses import dataclass
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.api.main import app


@dataclass
class _DummyEmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        value = float(len(text) % 10)
        return [value, value + 1.0, value + 2.0]


@dataclass
class _DummyAnswerProvider:
    def answer(self, question: str, context: str, prompt: str) -> str:
        del prompt
        return f"Mock answer for: {question} (ctx={len(context)})"


@dataclass
class _DummyRuntime:
    mode: str = "OFFLINE"
    embedding: _DummyEmbeddingProvider = _DummyEmbeddingProvider()
    answer: _DummyAnswerProvider = _DummyAnswerProvider()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def dummy_runtime() -> _DummyRuntime:
    return _DummyRuntime()
