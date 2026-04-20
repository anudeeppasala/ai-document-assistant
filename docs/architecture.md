# Architecture

## Data flow

1. User uploads a PDF from Streamlit.
2. FastAPI extracts per-page text from the PDF.
3. Text is chunked with overlap and metadata (`page_number`, offsets).
4. Chunks are embedded using runtime provider:
   - `ONLINE`: Gemini embedding.
   - `OFFLINE`: deterministic local hash embedding.
5. Chunks + metadata are stored in Chroma persistent collection.
6. Query flow embeds the question, retrieves top-k chunks, optionally reranks, and builds a grounded prompt.
7. Answer provider generates the final answer:
   - `ONLINE`: Gemini generation.
   - `OFFLINE`: local extractive fallback.

## Reliability features

- Request ID middleware (`X-Request-ID` and response latency headers).
- Structured logging with request correlation.
- Dedicated health and readiness endpoints.
- Config validation with early startup checks.

## Retrieval quality controls

- Configurable chunk size and overlap.
- Configurable top-k retrieval.
- Optional lexical rerank on top of vector search.
- Citation metadata propagated to UI and API response.
