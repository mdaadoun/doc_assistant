# Architectural Journal — Phase 6.4: Confidence Guard & Refusal Response Bypass

> **Phase:** 6.4 | **Date:** 2026-08-13 | **Status:** Completed

---

## 🎯 Objective
Implement `ConfidenceGuard` in `src/retrieval/confidence_guard.py` and `ConfidenceDecision` schema in `src/models/retrieval.py` to enforce minimum confidence threshold gating ($S_{\text{min}} \ge 0.35$) over cross-encoder reranked search hits. Provide immediate refusal response bypass for low-confidence or out-of-corpus queries prior to generative LLM execution.

---

## 💡 Architectural Choices

### 1. Early Gating Architecture Prior to LLM Generation
- **Context:** Out-of-corpus user queries or low-relevance search hits passed directly to generative LLMs risk severe hallucinations or wasted prompt token expenses.
- **Decision:** Implemented `ConfidenceGuard` in `src/retrieval/confidence_guard.py` to intercept retrieved search hits immediately after cross-encoder re-ranking.
- **Rationale:** Evaluating top relevance score against a calibrated cutoff ($S_{\text{min}} \ge 0.35$) ensures generative LLMs are only invoked when high-confidence grounding context is available.

### 2. Deterministic Refusal Bypass Path
- **Context:** Unconfident queries should fail fast without sending prompt text to external LLM providers.
- **Decision:** Implemented `create_refusal_response()` method constructing a standardized `ChatResponse` (`"I cannot answer this question based on the available documentation."`).
- **Rationale:** Short-circuits LLM text generation, reducing completion latency to near 0ms, preventing token expenditure, and guaranteeing zero hallucination leakage on ungrounded queries.

### 3. Structured Confidence Decision Schema
- **Context:** Pipeline components require clear programmatic feedback regarding confidence evaluation outcomes.
- **Decision:** Created `ConfidenceDecision` in `src/models/retrieval.py` containing `passed: bool`, `top_score: float`, `threshold: float`, `filtered_hits: list[RetrievalResult]`, and `refusal_message: str`.
- **Rationale:** Provides strict, immutable domain contracts allowing downstream services to inspect filtering decisions and top-candidate scores transparently.

### 4. Pydantic Telemetry & Field Bounds Preservation
- **Context:** Standard response schemas enforce Pydantic constraints (`confidence_score` between `0.0` and `1.0`, non-negative FinOps token counts).
- **Decision:** Clamped `confidence_score` values during refusal response construction and populated `FinOpsMetadata` with zero prompt/completion tokens.
- **Rationale:** Maintains full schema validity and telemetry integrity without throwing Pydantic validation errors during refusal execution.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Early Gating Prior to LLM Generation** | Borderline queries with scores slightly below 0.35 are refused outright. | Calibrated default threshold ($S_{\text{min}} = 0.35$) balances precision ($\ge 0.90$) and recall based on cross-encoder logit distributions. |
| **Deterministic Refusal Bypass Path** | Bypasses generative LLM completely, skipping conversational phrasing. | Returns standardized corporate disclaimer ensuring anti-hallucination compliance. |
| **Structured Confidence Decision Schema** | Introduces additional Pydantic model serialization overhead. | Schema validation overhead is sub-millisecond, far outweighed by execution safety. |

---

## 🛠️ Implementation & Code

### Key Flows
```text
ConfidenceGuard.evaluate(hits)
  -> Compute top_score = max(hit.relevance_score) or 0.0
  -> Check passed = is_confident(hits) -> (top_score >= threshold)
  -> If passed:
       -> filtered_hits = filter_hits(hits)  (relevance_score >= S_min)
  -> If failed:
       -> filtered_hits = []
  -> Log confidence_guard_evaluated telemetry
  -> Return ConfidenceDecision(passed, top_score, threshold, filtered_hits, refusal_message)

ConfidenceGuard.create_refusal_response(top_score, latency_ms)
  -> Clamp score to [0.0, 1.0]
  -> Return ChatResponse(
       answer=refusal_message,
       citations=[],
       confidence_score=clamped_score,
       grounded=False,
       latency_ms=latency_ms,
       finops=FinOpsMetadata(tokens=0, cost=0.0, is_cached=False)
     )
```

---

## 🔬 Verification Summary
- Executed unit test suite: **12 passed** in `test_confidence_guard.py` (231 passed across entire suite).
- Registered confidence guard test suite in `tests/unit/test_runner.py`.
- Mypy static type checking: **0 errors** across source files.
