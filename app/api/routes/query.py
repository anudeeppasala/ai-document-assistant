import time

from fastapi import APIRouter, HTTPException

from app.models.request_models import QueryRequest
from app.models.response_models import QueryResponse, SourceMatch
from app.services.providers.factory import get_runtime_mode
from app.services.rag_pipeline import generate_answer_from_chunks, retrieve_relevant_chunks

router = APIRouter()


@router.post("/", response_model=QueryResponse)
def query_docs(request: QueryRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    started = time.perf_counter()
    try:
        matches = retrieve_relevant_chunks(question, top_k=request.top_k)
        answer = generate_answer_from_chunks(question, matches)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Query failed: {exc}") from exc
    latency_ms = int((time.perf_counter() - started) * 1000)

    cleaned_matches: list[SourceMatch] = []
    for match in matches:
        distance = float(match["distance"])
        confidence = max(0.0, min(1.0, 1.0 - distance))
        cleaned_matches.append(
            SourceMatch(
                source_file=match["source_file"],
                chunk_index=int(match["chunk_index"]),
                page_number=int(match.get("page_number", -1)),
                distance=round(distance, 4),
                confidence=round(confidence, 4),
                text_preview=str(match["text"][:350]),
            )
        )

    return QueryResponse(
        question=question,
        answer=answer,
        match_count=len(cleaned_matches),
        latency_ms=latency_ms,
        runtime_mode=get_runtime_mode(),
        sources=cleaned_matches,
    )
