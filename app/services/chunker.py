def chunk_text(text: str, chunk_size: int = 700, overlap: int = 120) -> list[str]:
    if not text.strip():
        return []

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[str] = []
    start = 0
    text_length = len(text)
    step = chunk_size - overlap

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 700,
    overlap: int = 120,
) -> list[dict]:
    """Chunk page-level text and keep provenance metadata for citations."""
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[dict] = []
    step = chunk_size - overlap

    for page in pages:
        page_number = int(page["page_number"])
        text = str(page["text"])
        if not text.strip():
            continue

        start = 0
        while start < len(text):
            end = start + chunk_size
            body = text[start:end].strip()
            if body:
                chunks.append(
                    {
                        "text": body,
                        "page_number": page_number,
                        "start_char": start,
                        "end_char": min(end, len(text)),
                    }
                )
            start += step

    return chunks