from fastapi import APIRouter, HTTPException

from app.models.request_models import QueryRequest
from app.services.rag_service import retrieve_relevant_chunks

router = APIRouter()


@router.post("/")
def query_docs(request: QueryRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    matches = retrieve_relevant_chunks(question)

    return {
        "question": question,
        "match_count": len(matches),
        "matches": matches
    }