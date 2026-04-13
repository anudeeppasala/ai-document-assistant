import chromadb

from app.services.embedding_service import generate_embedding

client = chromadb.Client()
collection = client.get_or_create_collection(name="document_chunks")


def store_chunks(chunks: list[str], source_file: str) -> None:
    """
    Generate embeddings for all chunks and store them in Chroma.
    """
    for idx, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk)

        collection.add(
            ids=[f"{source_file}_chunk_{idx}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"source_file": source_file, "chunk_index": idx}]
        )


def search_similar_chunks(question: str, top_k: int = 3) -> dict:
    """
    Search Chroma for the most relevant chunks for a user question.
    """
    question_embedding = generate_embedding(question)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    return results


def reset_collection() -> None:
    """
    Clear all stored chunk data from the collection.
    """
    global collection
    client.delete_collection(name="document_chunks")
    collection = client.get_or_create_collection(name="document_chunks")