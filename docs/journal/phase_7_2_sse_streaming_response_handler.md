# Architectural Journal — Phase 7.2: SSE Streaming Response Handler

> **Phase:** 7.2 | **Date:** 2026-08-13 | **Status:** Completed

---

## 🎯 Objective
Implement `SSEResponseHandler` and `format_sse_event` in `src/generation/sse.py` to convert `AsyncGenerator` token streams from `GroundedGenerator` into W3C-compliant Server-Sent Events (SSE) stream frames. Define immutable Pydantic V2 payload schemas in `src/models/chat.py` for structured metadata, token delta, completion, and error streaming events.

---

## 💡 Architectural Choices

### 1. W3C-Compliant SSE Frame Formatter (`format_sse_event`)
- **Context:** Server-Sent Events require formatted text streams (`text/event-stream`) adhering to W3C spec (`event: <name>\n`, `id: <id>\n`, `retry: <ms>\n`, `data: <content>\n\n`).
- **Decision:** Implemented `format_sse_event` accepting `event`, `data` (primitive strings, dicts, lists, or Pydantic `BaseModel` instances), `event_id`, and `retry`.
- **Rationale:** Handles multi-line string splitting (`splitlines()`) prefixed with `data: ` and serializes Pydantic models automatically via `.model_dump_json()`.

### 2. Immutable Pydantic V2 SSE Payload Schemas
- **Context:** Streaming event payloads require standardized, type-safe structures across client API boundaries.
- **Decision:** Defined `SSEMetaDataPayload`, `SSETokenPayload`, `SSEDonePayload`, and `SSEErrorPayload` inheriting from `BaseDomainModel` (`frozen=True`, `extra="forbid"`).
- **Rationale:** Ensures strict typing and seamless JSON serialization for metadata (citations, confidence scores), token deltas, stream completion, and exception handling.

### 3. Structured RAG Streaming Lifecycle Sequence
- **Context:** Web clients and API consumers need initial metadata (citations, confidence scores, conversation session IDs) before token generation begins, as well as clear completion or error signals.
- **Decision:** `SSEResponseHandler.stream_generator` yields events in explicit order: `metadata` event frame -> sequence of `token` delta event frames -> `done` completion frame.
- **Rationale:** Allows client applications to render citations and UI metadata drawers immediately while streaming answer tokens progressively.

### 4. Mid-Stream Exception Catching and Error Framing
- **Context:** Exceptions during async generator token iteration could break client HTTP connections abruptly without diagnostic feedback.
- **Decision:** Wrapped token stream iteration in `stream_generator` with a try-except block that yields an `event: error` frame containing error message and code before concluding with `event: done`.
- **Rationale:** Guarantees graceful client connection termination and structured error reporting during streaming runtime failures.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Structured JSON Payloads** | Minor JSON serialization overhead per token delta event frame. | Use compact Pydantic V2 Rust-backed `model_dump_json()` serialization for low latency. |
| **Initial Metadata Event Emission** | Emits citations before text generation completes. | Citations are extracted during retrieval prior to generation, enabling instant UI drawer populating. |
| **Multi-line Data Frame Splitting** | Requires splitting token strings across newline boundaries. | `format_sse_event` splits lines efficiently using `splitlines()` and prefixes each line with `data: `. |

---

## 🛠️ Implementation & Code

### Key Flows
```text
SSEResponseHandler.stream_generator(token_stream, conversation_id, confidence_score, grounded, citations)
  ├── 1. Format citations list -> Construct SSEMetaDataPayload
  ├── 2. Yield format_frame(event="metadata", data=meta_payload)
  ├── 3. Iterate async for token in token_stream:
  │        ├── Construct SSETokenPayload(delta=token)
  │        └── Yield format_frame(event="token", data=token_payload)
  ├── 4. On Exception -> Catch error -> Construct SSEErrorPayload -> Yield format_frame(event="error", data=err_payload)
  └── 5. Construct SSEDonePayload(status="completed", finish_reason="stop") -> Yield format_frame(event="done", data=done_payload)
```

---

## 🔬 Verification Summary
- Executed unit test suite: **10 passed** in `test_sse_handler.py` (**250 passed** across entire project suite).
- Registered SSEResponseHandler test suite in `tests/unit/test_runner.py`.
- Static type checking: **0 errors** under `mypy src tests/unit/test_sse_handler.py` strict checks.
