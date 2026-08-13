# Architectural Journal — Phase 7.1: Grounded LLM Generation Service

> **Phase:** 7.1 | **Date:** 2026-08-13 | **Status:** Completed

---

## 🎯 Objective
Implement `GroundedGenerator` in `src/generation/engine.py` to enforce strict context-only grounding system prompts, zero temperature sampling ($T=0.0$), and `AsyncGenerator` streaming generation. Provide fallback context refusal handling when no high-confidence retrieval context blocks are available.

---

## 💡 Architectural Choices

### 1. Decoupled AsyncOpenAI Client Dependency Injection
- **Context:** Hardcoding `AsyncOpenAI` instantiation inside the service makes offline unit testing dependent on external network connectivity or live API keys.
- **Decision:** Accepted an optional `client: AsyncOpenAI | None = None` parameter in `GroundedGenerator.__init__`.
- **Rationale:** Allows mock client injection during unit testing while falling back to settings-driven `AsyncOpenAI(api_key=...)` in runtime production environments.

### 2. Strict Context-Only System Prompt & Zero Temperature
- **Context:** Unconstrained generative models tend to hallucinate or supplement answers with unverified external training knowledge.
- **Decision:** Configured `SYSTEM_PROMPT` establishing a strict corporate assistant persona, prohibiting outside assumptions, requiring inline citation syntax `[Doc: <file_name> | Page: <page_number>]`, and setting `temperature=0.0`.
- **Rationale:** Eliminates sampling variance and forces the model to synthesize answers exclusively from provided context blocks.

### 3. Heterogeneous Context Object Formatting
- **Context:** Retrieval hits and context items can be passed as dictionaries or domain objects (`ChunkDocument`, `RetrievalResult`, custom models).
- **Decision:** Implemented `_format_context` with attribute and dictionary fallback inspection for `file_name`, `page_number`, and `text`/`content`/`excerpt`.
- **Rationale:** Ensures consistent prompt block construction across heterogeneous caller schemas without requiring rigid type conversions upstream.

### 4. Immediate Refusal Stream Short-Circuit
- **Context:** When retrieval pipelines supply empty context lists, invoking the LLM wastes latency and token costs.
- **Decision:** Checks `if not contexts` in `generate_stream` and immediately yields `NO_CONTEXT_REFUSAL` (`"I cannot answer this question based on the available documentation."`).
- **Rationale:** Prevents unnecessary LLM API calls and guarantees deterministic refusal behavior on ungrounded queries.

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Async Generator Token Streaming** | Requires upstream consumers to iterate via `async for` instead of simple string returns. | Provided a convenience `generate()` method that aggregates stream tokens into a complete answer string for non-streaming consumers. |
| **Heterogeneous Context Format Inspection** | Attribute and dictionary key lookups incur minor dynamic checks per context item. | Checked fields (`file_name`, `page_number`, `text`) cover standard domain models and dynamic dicts efficiently with negligible overhead. |
| **Strict Refusal Short-Circuit** | Immediately refuses queries with empty context without attempting fallback search. | Higher-level confidence guards handle query expansion or search retries prior to invoking generation. |

---

## 🛠️ Implementation & Code

### Key Flows
```text
GroundedGenerator.generate_stream(query, contexts)
  ├── 1. Check if not contexts -> Yield NO_CONTEXT_REFUSAL -> Return
  ├── 2. Format contexts into structured prompt blocks via _format_context()
  ├── 3. Build user prompt: "CONTEXT INFORMATION:\n{context_str}\n\nUSER QUESTION: {query}"
  ├── 4. Invoke client.chat.completions.create(
  │        model=self.model,
  │        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
  │        temperature=0.0,
  │        stream=True
  │      )
  ├── 5. Iterate async stream -> Extract chunk.choices[0].delta.content -> Yield delta
  └── 6. Catch Exception -> Log structlog error -> Raise GenerationError
```

---

## 🔬 Verification Summary
- Executed unit test suite: **7 passed** in `test_grounded_generator.py` (**239 passed** across entire project suite).
- Registered GroundedGenerator test suite in `tests/unit/test_runner.py`.
- Static type checking: **0 errors** under `mypy src` strict checks.
