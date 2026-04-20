from google import genai

from app.core.config import GEMINI_API_KEY


class EmbeddingServiceError(Exception):
    pass


client = genai.Client(api_key=GEMINI_API_KEY)


def generate_embedding(text: str) -> list[float]:
    if not text.strip():
        raise EmbeddingServiceError("Cannot generate embedding for empty text")

    try:
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
        )
        return response.embeddings[0].values
    except Exception as exc:
        raise EmbeddingServiceError(f"Embedding generation failed: {exc}") from exc