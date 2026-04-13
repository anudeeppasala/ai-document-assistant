from fastapi import FastAPI
from app.api.routes import health, upload, query

app = FastAPI(title="AI Document Assistant")


@app.get("/")
def root():
    return {"message": "Welcome to AI Document Assistant"}


app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(query.router, prefix="/query", tags=["Query"])