from google import genai

from app.core.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_embedding(text: str) -> list[float]:
    """
    Generate an embedding vector for a single text input.
    """
    try:
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
        )
        return response.embeddings[0].values

    except Exception as exc:
        raise RuntimeError(f"Embedding generation failed: {str(exc)}") from exc