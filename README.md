# AI Document Assistant

AI Document Assistant is a Python-based RAG application that ingests PDF documents, indexes them for semantic search, and answers user questions using grounded document context.

## Features

- FastAPI backend with modular project structure
- PDF upload and validation
- PDF text extraction using `pypdf`
- Text chunking with overlap
- Embedding generation using Gemini
- Vector storage with ChromaDB
- Semantic retrieval over indexed document chunks
- Grounded answer generation using retrieved context only
- Swagger/OpenAPI docs via FastAPI

## Architecture

The application follows a Retrieval-Augmented Generation (RAG) workflow:

1. User uploads a PDF
2. Backend extracts text from the document
3. Text is split into overlapping chunks
4. Chunks are converted into embeddings
5. Embeddings are stored in ChromaDB
6. User submits a question
7. Question is embedded and matched against stored chunks
8. Relevant chunks are passed to Gemini
9. The model generates a grounded answer using only retrieved context

## Tech Stack

- Python
- FastAPI
- Uvicorn
- PyPDF
- ChromaDB
- Google Gemini API
- Pydantic
- Python-dotenv
- Pytest

## Project Structure

```bash
ai-document-assistant/
│── app/
│   │── api/
│   │   │── routes/
│   │   │   ├── upload.py
│   │   │   ├── query.py
│   │   │   └── health.py
│   │   └── main.py
│   │
│   │── core/
│   │   └── config.py
│   │
│   │── services/
│   │   ├── document_loader.py
│   │   ├── chunker.py
│   │   ├── embedding_service.py
│   │   ├── vector_store.py
│   │   └── rag_service.py
│   │
│   │── models/
│   │   └── request_models.py
│
│── tests/
│── data/
│── requirements.txt
│── .env
│── .gitignore
│── README.md