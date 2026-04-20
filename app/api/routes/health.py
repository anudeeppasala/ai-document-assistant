from fastapi import APIRouter

from app.core.config import ConfigError, get_settings
from app.services.providers.factory import get_runtime_mode
from app.services.vector_store import count_chunks

router = APIRouter()


@router.get("/")
def health_check():
    settings = get_settings()
    return {
        "status": "ok",
        "message": "AI Document Assistant is running",
        "env": settings.app_env,
    }


@router.get("/ready")
def readiness_check():
    problems: list[str] = []
    mode = "OFFLINE"

    try:
        settings = get_settings()
        mode = get_runtime_mode()
        if mode == "ONLINE" and not settings.gemini_api_key:
            problems.append("GEMINI_API_KEY missing for online mode")
    except ConfigError as exc:
        problems.append(str(exc))

    try:
        count = count_chunks()
    except Exception as exc:
        problems.append(f"Vector store unavailable: {exc}")
        count = -1

    return {
        "status": "ok" if not problems else "degraded",
        "runtime_mode": mode,
        "indexed_chunks": count,
        "problems": problems,
    }
