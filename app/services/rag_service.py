from app.services.vector_store import search_similar_chunks


def retrieve_relevant_chunks(question: str, top_k: int = 3) -> list[dict]:
    """
    Retrieve top relevant document chunks for a given question
    and format them into a cleaner response.
    """
    raw_results = search_similar_chunks(question, top_k=top_k)

    ids = raw_results.get("ids", [[]])[0]
    documents = raw_results.get("documents", [[]])[0]
    metadatas = raw_results.get("metadatas", [[]])[0]
    distances = raw_results.get("distances", [[]])[0]

    formatted_results = []

    for idx in range(len(ids)):
        formatted_results.append(
            {
                "chunk_id": ids[idx],
                "source_file": metadatas[idx].get("source_file"),
                "chunk_index": metadatas[idx].get("chunk_index"),
                "distance": distances[idx],
                "text": documents[idx],
            }
        )

    return formatted_results