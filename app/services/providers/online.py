from google import genai

from app.core.config import get_settings
from app.core.errors import DependencyUnavailableError


class GeminiEmbeddingProvider:
    def __init__(self):
        settings = get_settings()
        if not settings.gemini_api_key:
            raise DependencyUnavailableError("Missing GEMINI_API_KEY for online mode")
        self._model = settings.gemini_embedding_model
        self._client = genai.Client(api_key=settings.gemini_api_key)

    def embed(self, text: str) -> list[float]:
        if not text.strip():
            raise DependencyUnavailableError("Cannot embed empty text")
        try:
            response = self._client.models.embed_content(model=self._model, contents=text)
            return response.embeddings[0].values
        except Exception as exc:
            raise DependencyUnavailableError(f"Gemini embedding failed: {exc}") from exc


class GeminiAnswerProvider:
    def __init__(self):
        settings = get_settings()
        if not settings.gemini_api_key:
            raise DependencyUnavailableError("Missing GEMINI_API_KEY for online mode")
        self._model = settings.gemini_chat_model
        self._client = genai.Client(api_key=settings.gemini_api_key)

    @staticmethod
    def _response_text(response: object) -> str:
        text = getattr(response, "text", None)
        if text:
            return text
        candidates = getattr(response, "candidates", None) or []
        parts: list[str] = []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            for part in getattr(content, "parts", None) or []:
                value = getattr(part, "text", None)
                if value:
                    parts.append(value)
        return "".join(parts)

    def answer(self, question: str, context: str, prompt: str) -> str:
        del question
        del context
        try:
            response = self._client.models.generate_content(model=self._model, contents=prompt)
            text = self._response_text(response).strip()
            if not text:
                raise DependencyUnavailableError("Gemini returned empty answer")
            return text
        except Exception as exc:
            raise DependencyUnavailableError(f"Gemini answer generation failed: {exc}") from exc
