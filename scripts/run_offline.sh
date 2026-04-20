#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source venv/bin/activate

export RAG_MODE=OFFLINE
uvicorn app.api.main:app --reload
