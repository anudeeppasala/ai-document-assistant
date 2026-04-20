import socket
from functools import lru_cache

from app.core.config import get_settings
from app.services.providers.base import RuntimeProviders
from app.services.providers.offline import LocalExtractiveAnswerProvider, LocalHashEmbeddingProvider
from app.services.providers.online import GeminiAnswerProvider, GeminiEmbeddingProvider


def _has_internet(timeout_s: float = 1.5) -> bool:
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=timeout_s).close()
        return True
    except OSError:
        return False


def get_runtime_mode() -> str:
    settings = get_settings()
    if settings.rag_mode == "ONLINE":
        return "ONLINE"
    if settings.rag_mode == "OFFLINE":
        return "OFFLINE"
    if settings.gemini_api_key and _has_internet():
        return "ONLINE"
    return "OFFLINE"


@lru_cache
def get_runtime_providers() -> RuntimeProviders:
    mode = get_runtime_mode()
    if mode == "ONLINE":
        return RuntimeProviders(
            mode=mode,
            embedding=GeminiEmbeddingProvider(),
            answer=GeminiAnswerProvider(),
        )
    return RuntimeProviders(
        mode=mode,
        embedding=LocalHashEmbeddingProvider(),
        answer=LocalExtractiveAnswerProvider(),
    )
