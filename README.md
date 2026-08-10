# Doc Assistant — Corporate Document Assistant

> Production-grade Hybrid RAG platform with citation-grounded generation.

## Quick Start

```bash
# Install dependencies
make install

# Run linter + type checker
make lint && make typecheck

# Run tests
make test

# Start dev server
make dev

# Docker deployment
docker-compose up
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for full system topology.

## Project Layout

```
src/
├── api/            # Presentation: FastAPI routes, SSE, auth
├── retrieval/      # Core Domain: hybrid engine, RRF, reranker
├── generation/     # Core Domain: grounding, prompts, citations
├── ingestion/      # Infrastructure: parsers, recursive splitters
├── clients/        # Infrastructure: LLM, embedding, reranker adapters
├── models/         # Shared: Pydantic V2 frozen schemas
├── core/           # Shared: config, exceptions, telemetry
└── cache/          # Data: SHA-256 cache persistence
frontend/           # Presentation: React 18+ / Vite / TypeScript
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── fixtures/       # Test data fixtures
```

## Tech Stack

| Component | Tool |
|---|---|
| Backend | Python 3.11+, FastAPI |
| Vector Store | Qdrant |
| Lexical Engine | rank-bm25 |
| Re-Ranker | FlashRank / Cohere |
| Frontend | React 18+, Vite, TypeScript |
| Containerization | Docker & docker-compose |
| Dependencies | Poetry |
