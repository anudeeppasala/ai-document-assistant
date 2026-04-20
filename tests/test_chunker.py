import pytest

from app.services.chunker import chunk_pages, chunk_text


def test_chunk_text_returns_chunks():
    text = "a" * 1200
    chunks = chunk_text(text, chunk_size=500, overlap=100)
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)


def test_chunk_text_empty_input():
    assert chunk_text("") == []


def test_chunk_pages_returns_metadata():
    pages = [{"page_number": 1, "text": "abc " * 300}]
    chunks = chunk_pages(pages, chunk_size=100, overlap=20)
    assert len(chunks) >= 1
    assert all("page_number" in chunk for chunk in chunks)
    assert all("start_char" in chunk for chunk in chunks)


def test_chunk_pages_validates_overlap():
    with pytest.raises(ValueError):
        chunk_pages([{"page_number": 1, "text": "hello"}], chunk_size=50, overlap=50)
