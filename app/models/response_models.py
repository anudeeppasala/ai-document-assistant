from pydantic import BaseModel


class SourceMatch(BaseModel):
    source_file: str
    chunk_index: int
    page_number: int
    distance: float
    confidence: float
    text_preview: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    match_count: int
    latency_ms: int
    runtime_mode: str
    sources: list[SourceMatch]


class UploadResponse(BaseModel):
    filename: str
    message: str
    text_length: int
    chunk_count: int
    page_count: int
    preview: str
