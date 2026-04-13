from google import genai

from app.core.config import GEMINI_API_KEY
from app.services.vector_store import search_similar_chunks

client = genai.Client(api_key=GEMINI_API_KEY)


def retrieve_relevant_chunks(question: str, top_k: int = 3) -> list[dict]:
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


def generate_answer_from_chunks(question: str, matches: list[dict]) -> str:
    if not matches:
        return "I could not find relevant information in the indexed document."

    context = "\n\n".join(
        [
            f"Chunk {match['chunk_index']} from {match['source_file']}:\n{match['text']}"
            for match in matches
        ]
    )

    prompt = f"""
You are a helpful AI document assistant.

Answer the user's question using ONLY the provided document context.
If the answer is not clearly available in the context, say:
"I could not find a clear answer in the document."

User question:
{question}

Document context:
{context}

Instructions:
- Give a concise answer.
- Do not make up facts.
- Base the answer only on the document context.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as exc:
        raise RuntimeError(f"Answer generation failed: {str(exc)}") from exc