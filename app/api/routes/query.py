from fastapi import APIRouter, HTTPException

from app.models.request_models import QueryRequest
from app.services.rag_service import generate_answer_from_chunks, retrieve_relevant_chunks

router = APIRouter()


@router.post("/")
def query_docs(request: QueryRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        matches = retrieve_relevant_chunks(question)
        answer = generate_answer_from_chunks(question, matches)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Answer generation failed: {str(exc)}"
        ) from exc

    cleaned_matches = [
        {
            "source_file": match["source_file"],
            "chunk_index": match["chunk_index"],
            "distance": round(match["distance"], 4),
            "text_preview": match["text"][:300]
        }
        for match in matches
    ]

    return {
        "question": question,
        "answer": answer,
        "match_count": len(cleaned_matches),
        "sources": cleaned_matches
    }