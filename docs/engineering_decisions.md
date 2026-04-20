# Engineering decisions

## Why provider abstraction?

The app needs both internet-connected and offline behavior. Abstracting `EmbeddingProvider` and `AnswerProvider` enables:

- online and offline implementations with the same API,
- deterministic tests via mocks,
- future model swaps without route-level rewrites.

## Why persistent Chroma?

Using `chromadb.PersistentClient` keeps the index across restarts so the app behaves closer to production and supports offline continuity.

## Why hybrid rerank?

Pure vector similarity can miss exact entities in contracts. A lightweight lexical overlap rerank improves precision for questions around names, dates, and addresses without adding heavy dependencies.

## Why include citations in responses?

Recruiters and users need trust. Returning source file, chunk index, page number, and confidence makes outputs inspectable and debuggable.

## Why offline extractive fallback?

When internet or API quota fails, extractive responses still provide useful grounded snippets. This avoids total downtime and demonstrates resilient system design.
