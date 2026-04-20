from pathlib import Path

import chromadb

from app.core.config import get_settings
from app.services.providers.base import EmbeddingProvider

settings = get_settings()
Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=settings.chroma_path)
collection = client.get_or_create_collection(name=settings.chroma_collection_name)


def reset_collection() -> None:
    global collection
    try:
        client.delete_collection(name=settings.chroma_collection_name)
    except Exception:
        pass
    collection = client.get_or_create_collection(name=settings.chroma_collection_name)


def count_chunks() -> int:
    return int(collection.count())


def store_chunks(chunks: list[dict], source_file: str, embedding_provider: EmbeddingProvider) -> None:
    for idx, chunk in enumerate(chunks):
        text = chunk["text"]
        embedding = embedding_provider.embed(text)
        collection.add(
            ids=[f"{source_file}_chunk_{idx}"],
            embeddings=[embedding],
            documents=[text],
            metadatas=[
                {
                    "source_file": source_file,
                    "chunk_index": idx,
                    "page_number": int(chunk.get("page_number", -1)),
                    "start_char": int(chunk.get("start_char", -1)),
                    "end_char": int(chunk.get("end_char", -1)),
                }
            ],
        )


def search_similar_chunks(query_embedding: list[float], top_k: int) -> dict:
    return collection.query(query_embeddings=[query_embedding], n_results=top_k)