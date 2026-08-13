# Architectural Journal — Phase 7.5: FinOps Metadata Collection Integration

> **Phase:** 7.5 | **Date:** 2026-08-13 | **Status:** Completed

---

## 🎯 Objective
Implement feature 7.5 to integrate FinOps telemetry and metadata collection (token counts, USD cost estimation, execution latency) across the LLM generation pipeline. Encapsulate token accounting and model cost calculations into a dedicated, modular `FinOpsCollector` service (`src/generation/finops.py`), provide robust tiktoken tokenization with offline sandboxed fallback heuristics, integrate context-managed latency tracking (`track_latency`), and update `GroundedGenerator` (`src/generation/engine.py`) to support `generate_with_finops`.

---

## 💡 Architectural Choices

### 1. Standalone Telemetry Service (`FinOpsCollector`)
- **Context:** RAG generation requires accurate tracking of prompt tokens, completion tokens, execution time, and USD cost per query to enforce operational budgeting and telemetry observability.
- **Decision:** Encapsulated token calculation and cost mapping inside a dedicated `FinOpsCollector` class rather than embedding cost math directly inside `GroundedGenerator`.
- **Rationale:** Decouples cost accounting from LLM generation logic, adhering to the Single Responsibility Principle and allowing reuse across embedding, re-ranking, and API middleware layers.

### 2. Multi-tier Tokenizer Resolution & Offline Fallback (`count_tokens`)
- **Context:** In isolated or sandboxed environments, `tiktoken` may fail to fetch model-specific BPE files (e.g. `o200k_base` over HTTPS) from external remote endpoints.
- **Decision:** Implemented a multi-tier resolution strategy in `count_tokens`: attempts model-specific tiktoken encoding first, falls back to local `cl100k_base` encoding on lookup error, and uses a word-ratio heuristic (`len(words) * 1.3`) if tokenizer loading fails completely.
- **Rationale:** Guarantees non-blocking, error-free token counting in offline, sandboxed, or network-restricted execution environments.

### 3. Model Pricing Matrix (`MODEL_PRICING`)
- **Context:** Different LLM models (`gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`, `text-embedding-3-small`) feature distinct per-token pricing for input prompts and output completions.
- **Decision:** Defined a central `MODEL_PRICING` lookup dictionary mapping model names to USD rates per 1,000 tokens, with a standard fallback rate for unknown models and explicit $0.00 cost calculation for cache hits (`is_cached=True`).
- **Rationale:** Enables instant, zero-latency USD cost calculation without external HTTP dependencies during request processing.

### 4. Seamless Generator Integration (`generate_with_finops`)
- **Context:** Downstream API endpoints and response handlers need complete response text paired directly with structured `FinOpsMetadata`.
- **Decision:** Added `generate_with_finops(query, contexts)` to `GroundedGenerator`, returning `tuple[str, FinOpsMetadata]` while measuring precise wall-clock execution time.
- **Rationale:** Simplifies generation invocation for API routes by returning the complete grounded answer alongside fully populated telemetry metrics.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Local Tiktoken vs Provider API Telemetry** | Local calculation may differ slightly (<1%) from provider-side chat formatting tokens. | Local counting provides immediate, non-blocking telemetry without waiting for async response trailers. |
| **Static Model Pricing Matrix** | Pricing table requires manual updates when provider pricing tiers change. | Centralized `MODEL_PRICING` table simplifies updates and provides fallback rates for unlisted models. |
| **Heuristic Fallback Tokenizer** | Word-ratio calculation (`1.3` tokens/word) is an approximation when offline. | Fallback executes only when network or tiktoken binary loading fails, ensuring zero request crashes. |

---

## 🛠️ Implementation & Code

### Key Flows
```text
GroundedGenerator.generate_with_finops(query, contexts)
  ├── 1. Start timer (time.perf_counter())
  ├── 2. Check if contexts list empty:
  │        ├── Calculate elapsed seconds
  │        ├── FinOpsCollector.collect(prompt_tokens=0, completion_tokens=0, execution_time_seconds=elapsed)
  │        └── Return (NO_CONTEXT_REFUSAL, finops_metadata)
  ├── 3. Format context blocks & prompt string
  ├── 4. Await generate(query, contexts) -> answer text
  ├── 5. Calculate elapsed seconds
  ├── 6. FinOpsCollector.collect(prompt_text, answer_text, execution_time_seconds, model)
  │        ├── count_tokens(prompt_text) via tiktoken / fallback
  │        ├── count_tokens(answer_text) via tiktoken / fallback
  │        ├── calculate_cost(prompt_tokens, completion_tokens, model)
  │        └── Construct FinOpsMetadata(prompt_tokens, completion_tokens, total_tokens, cost, latency, is_cached)
  └── 7. Return (answer, finops_metadata)
```

---

## 🔬 Verification Summary
- Executed unit test suite: **7 passed** in `test_finops_collector.py` (**270 passed** across entire project suite).
- Registered test suite in `tests/unit/test_runner.py`.
- Static type checking: **0 errors** under `mypy` strict mode.
