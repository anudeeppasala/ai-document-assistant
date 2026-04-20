from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import health, query, upload
from app.core.config import ConfigError, get_settings
from app.core.errors import AppError
from app.core.logging import request_context_middleware, setup_logging

setup_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.middleware("http")(request_context_middleware)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    del request
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error_code": exc.code},
    )


@app.exception_handler(ConfigError)
async def config_error_handler(request: Request, exc: ConfigError):
    del request
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error_code": "invalid_config"},
    )


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.app_name}"}


app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(query.router, prefix="/query", tags=["Query"])
from fastapi import FastAPI
from app.api.routes import health, query, upload

app = FastAPI(title="AI Document Assistant", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Welcome to AI Document Assistant"}


app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(query.router, prefix="/query", tags=["Query"])