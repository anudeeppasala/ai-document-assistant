from pathlib import Path
from pypdf import PdfReader


class DocumentLoaderError(Exception):
    pass


def extract_pages_from_pdf(file_path: str) -> list[dict]:
    pdf_path = Path(file_path)
    if not pdf_path.exists():
        raise DocumentLoaderError(f"File not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        pages: list[dict] = []
        for page_idx, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            cleaned = page_text.strip()
            if cleaned:
                pages.append({"page_number": page_idx, "text": cleaned})
        return pages
    except Exception as exc:
        raise DocumentLoaderError(f"Failed to extract text from PDF: {exc}") from exc


def extract_text_from_pdf(file_path: str) -> str:
    pages = extract_pages_from_pdf(file_path)
    return "\n".join(page["text"] for page in pages).strip()