import hashlib
import math
import re


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class LocalHashEmbeddingProvider:
    """Deterministic local embeddings for offline mode."""

    def __init__(self, dimensions: int = 256):
        self._dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        tokens = _tokenize(text)
        vector = [0.0] * self._dimensions
        if not tokens:
            return vector
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % self._dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[idx] += sign
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class LocalExtractiveAnswerProvider:
    """Simple extractive fallback for no-internet mode."""

    def answer(self, question: str, context: str, prompt: str) -> str:
        del prompt
        question_terms = [t for t in _tokenize(question) if len(t) > 2]
        if not context.strip():
            return "No context is available to answer this question."
        snippets = [s.strip() for s in re.split(r"[\n\.]+", context) if s.strip()]
        if not snippets:
            return "No extracted text was available in the selected context."

        scored: list[tuple[int, str]] = []
        for snippet in snippets:
            terms = set(_tokenize(snippet))
            score = sum(1 for term in question_terms if term in terms)
            if score:
                scored.append((score, snippet))

        if not scored:
            return (
                "I could not find a direct match in the retrieved excerpts. "
                "Try a more specific question or upload a clearer text-based PDF."
            )

        scored.sort(key=lambda item: item[0], reverse=True)
        top = [text for _, text in scored[:3]]
        return " ".join(top)
