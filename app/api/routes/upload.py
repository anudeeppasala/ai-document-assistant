from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.chunker import chunk_text
from app.services.document_loader import extract_text_from_pdf

router = APIRouter()

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = DATA_DIR / file.filename

    file_bytes = await file.read()
    file_path.write_bytes(file_bytes)

    extracted_text = extract_text_from_pdf(str(file_path))

    if not extracted_text:
        raise HTTPException(status_code=400, detail="No text could be extracted from this PDF")

    chunks = chunk_text(extracted_text)

    return {
        "filename": file.filename,
        "message": "File uploaded, text extracted, and chunking completed successfully",
        "text_length": len(extracted_text),
        "chunk_count": len(chunks),
        "preview": extracted_text[:1000],
        "first_chunk_preview": chunks[0][:500] if chunks else ""
    }