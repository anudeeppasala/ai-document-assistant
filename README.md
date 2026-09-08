# AI Document Assistant

Document **ingest and retrieval pipeline**: load → chunk → embed → retrieve → cited answer. Packaged as a containerized API.

**In this repo:** FastAPI backend, Streamlit operator UI, Chroma, Gemini with an offline fallback, eval harness, and integration tests. This is not a deployed AWS stack.

**How I would run it in production:** objects land in S3 (or Blob Storage) → ingest job on Lambda/ECS → vectors in a managed store → stateless query API behind API Gateway. Secrets in Secrets Manager / Key Vault. Streamlit is the operator console, not the product.

## Highlights

- End-to-end pipeline (upload, index, query, citations)
- Reliability: structured logs, request IDs, readiness checks, config validation
- Quality controls: chunk tuning, top-k retrieval, rerank toggle, eval metrics
- Resilience: offline mode with deterministic local fallback
- Testability: mocked integration tests for deterministic CI behavior

## Architecture

- High-level design: [`docs/architecture.md`](docs/architecture.md)
- Engineering tradeoffs: [`docs/engineering_decisions.md`](docs/engineering_decisions.md)

## Project structure

```text
ai-document-assistant/
├── app/
│   ├── api/
│   │   ├── main.py
│   │   └── routes/
│   │       ├── health.py
│   │       ├── upload.py
│   │       └── query.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── errors.py
│   ├── models/
│   └── services/
│       ├── providers/
│       │   ├── online.py
│       │   ├── offline.py
│       │   └── factory.py
│       ├── vector_store.py
│       ├── rag_pipeline.py
│       ├── chunker.py
│       └── document_loader.py
├── frontend/streamlit_app.py
├── tests/
├── eval/sample_eval_set.json
├── scripts/
│   ├── evaluate.py
│   ├── run_online.sh
│   └── run_offline.sh
└── docker-compose.yml
```

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run API

```bash
uvicorn app.api.main:app --reload
```

### Run frontend

```bash
streamlit run frontend/streamlit_app.py
```

## Runtime modes

- `RAG_MODE=ONLINE`: Gemini embeddings and answer generation
- `RAG_MODE=OFFLINE`: local hash embeddings + extractive answer fallback
- `RAG_MODE=AUTO`: online if internet + API key are available, otherwise offline

## Environment variables

```env
GEMINI_API_KEY=...
RAG_MODE=AUTO
GEMINI_CHAT_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
CHROMA_COLLECTION_NAME=document_chunks
CHROMA_PATH=./data/chroma
CHUNK_SIZE=700
CHUNK_OVERLAP=120
TOP_K_RESULTS=10
RERANK_ENABLED=true
MAX_CONTEXT_CHUNKS=8
```

## Health endpoints

- `GET /health/`
- `GET /health/ready`

## Evaluation

Run baseline retrieval/answer metrics:

```bash
python scripts/evaluate.py
```

Current baseline format:

- retrieval recall@k
- answer keyword score
- match count per query

## Tests

```bash
pytest -q
```

## Docker

Online profile:

```bash
docker compose --profile online up --build
```

Offline profile:

```bash
docker compose --profile offline up --build
```

## Demo checklist (90 seconds)

1. Show upload + indexing summary (pages/chunks).
2. Ask a contract question and show answer + citations.
3. Show health/ready output and request latency headers.
4. Switch to offline mode and repeat query successfully.
5. Show test and eval commands in terminal.
