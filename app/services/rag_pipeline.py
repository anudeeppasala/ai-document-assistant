from typing import Optional

from app.core.config import get_settings
from app.core.errors import QueryError
from app.services.providers.factory import get_runtime_providers
from app.services.vector_store import search_similar_chunks


def _keyword_score(question: str, text: str) -> float:
    question_terms = {term for term in question.lower().split() if len(term) > 2}
    if not question_terms:
        return 0.0
    text_terms = set(text.lower().split())
    overlap = question_terms.intersection(text_terms)
    return len(overlap) / len(question_terms)


def retrieve_relevant_chunks(question: str, top_k: Optional[int] = None) -> list[dict]:
    settings = get_settings()
    runtime = get_runtime_providers()
    k = top_k or settings.top_k_results

    query_embedding = runtime.embedding.embed(question)
    raw_results = search_similar_chunks(query_embedding=query_embedding, top_k=k)

    ids = raw_results.get("ids", [[]])[0]
    documents = raw_results.get("documents", [[]])[0]
    metadatas = raw_results.get("metadatas", [[]])[0]
    distances = raw_results.get("distances", [[]])[0]

    formatted_results: list[dict] = []
    for idx in range(len(ids)):
        metadata = metadatas[idx] or {}
        formatted_results.append(
            {
                "chunk_id": ids[idx],
                "source_file": metadata.get("source_file", "unknown"),
                "chunk_index": metadata.get("chunk_index", -1),
                "page_number": metadata.get("page_number", -1),
                "start_char": metadata.get("start_char", -1),
                "end_char": metadata.get("end_char", -1),
                "distance": float(distances[idx]),
                "text": documents[idx],
            }
        )

    if settings.rerank_enabled:
        for row in formatted_results:
            lexical = _keyword_score(question, row["text"])
            row["hybrid_score"] = (1.0 - row["distance"]) + lexical
        formatted_results.sort(key=lambda row: row["hybrid_score"], reverse=True)

    return formatted_results


def generate_answer_from_chunks(question: str, matches: list[dict]) -> str:
    settings = get_settings()
    runtime = get_runtime_providers()

    if not matches:
        return (
            "No indexed passages matched this question. "
            "Upload a PDF first, then try again."
        )

    selected = matches[: settings.max_context_chunks]
    blocks: list[str] = []
    for m in selected:
        src = m.get("source_file", "unknown")
        idx = m.get("chunk_index", -1)
        page = m.get("page_number", -1)
        body = m.get("text", "")
        blocks.append(f"[source={src} chunk={idx} page={page}]\n{body}")
    context = "\n\n---\n\n".join(blocks)

    prompt = (
        "You are a document QA assistant. Use only the context below.\n"
        "- Give the most precise answer possible.\n"
        "- If data is missing, say exactly what is missing.\n"
        "- End with a short citations list using source, chunk, and page.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    )

    try:
        answer = runtime.answer.answer(question=question, context=context, prompt=prompt)
        return answer.strip()
    except Exception as exc:
        raise QueryError(f"Answer generation failed: {exc}") from exc
