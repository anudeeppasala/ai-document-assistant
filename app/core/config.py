import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    """Raised when application configuration is invalid."""


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    app_env: str
    log_level: str
    rag_mode: str
    gemini_api_key: str
    gemini_chat_model: str
    gemini_embedding_model: str
    chroma_collection_name: str
    chroma_path: str
    chunk_size: int
    chunk_overlap: int
    top_k_results: int
    rerank_enabled: bool
    max_context_chunks: int


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer, got: {raw}") from exc


def _normalize_mode(mode: str) -> str:
    cleaned = mode.strip().upper()
    if cleaned not in {"ONLINE", "OFFLINE", "AUTO"}:
        raise ConfigError("RAG_MODE must be ONLINE, OFFLINE, or AUTO")
    return cleaned


@lru_cache
def get_settings() -> Settings:
    settings = Settings(
        app_name=os.getenv("APP_NAME", "AI Document Assistant"),
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        app_env=os.getenv("APP_ENV", "dev"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        rag_mode=_normalize_mode(os.getenv("RAG_MODE", "AUTO")),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_chat_model=os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash"),
        gemini_embedding_model=os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"),
        chroma_collection_name=os.getenv("CHROMA_COLLECTION_NAME", "document_chunks"),
        chroma_path=os.getenv("CHROMA_PATH", "./data/chroma"),
        chunk_size=_get_int("CHUNK_SIZE", 700),
        chunk_overlap=_get_int("CHUNK_OVERLAP", 120),
        top_k_results=_get_int("TOP_K_RESULTS", 10),
        rerank_enabled=_get_bool("RERANK_ENABLED", True),
        max_context_chunks=_get_int("MAX_CONTEXT_CHUNKS", 8),
    )

    if settings.chunk_overlap >= settings.chunk_size:
        raise ConfigError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")
    if settings.top_k_results <= 0:
        raise ConfigError("TOP_K_RESULTS must be greater than zero")
    if settings.max_context_chunks <= 0:
        raise ConfigError("MAX_CONTEXT_CHUNKS must be greater than zero")
    if settings.rag_mode == "ONLINE" and not settings.gemini_api_key:
        raise ConfigError("GEMINI_API_KEY is required when RAG_MODE=ONLINE")

    return settings
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Default avoids gemini-2.0-flash — not offered to new API keys (404). Override via .env if needed.
GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "document_chunks")
# Higher k improves recall on long leases (names may sit outside the top-3 vector hits).
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "10"))