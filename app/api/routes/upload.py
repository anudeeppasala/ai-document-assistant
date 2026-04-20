from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.response_models import UploadResponse
from app.services.chunker import chunk_pages
from app.services.document_loader import DocumentLoaderError, extract_pages_from_pdf
from app.services.providers.factory import get_runtime_providers
from app.services.vector_store import reset_collection, store_chunks

router = APIRouter()
logger = get_logger(__name__)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / ".gitkeep").touch(exist_ok=True)


@router.post("/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    settings = get_settings()

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = DATA_DIR / file.filename
    logger.info("Uploading file '%s'", file.filename)

    try:
        file_bytes = await file.read()
        file_path.write_bytes(file_bytes)
        pages = extract_pages_from_pdf(str(file_path))
        extracted_text = "\n".join(page["text"] for page in pages).strip()

        if not extracted_text:
            raise HTTPException(status_code=400, detail="No text could be extracted from this PDF")

        chunks = chunk_pages(
            pages,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
        )
        if not chunks:
            raise HTTPException(status_code=400, detail="Chunking produced no usable text")

        runtime = get_runtime_providers()
        reset_collection()
        store_chunks(chunks, file.filename, embedding_provider=runtime.embedding)
        logger.info(
            "Indexed file '%s' with %s chunks in mode=%s",
            file.filename,
            len(chunks),
            runtime.mode,
        )

        return UploadResponse(
            filename=file.filename,
            message="File uploaded, indexed, and stored successfully",
            text_length=len(extracted_text),
            chunk_count=len(chunks),
            page_count=len(pages),
            preview=extracted_text[:1000],
        )
    except HTTPException:
        raise
    except DocumentLoaderError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Upload/indexing failed: {exc}") from exc
