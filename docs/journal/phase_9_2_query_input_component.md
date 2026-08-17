# Session 9.2: Query Input Component with Submission Handling

**Date:** 2026-08-17

*Implements a resilient, accessible, and reactive QueryInput component under `frontend/src/components/QueryInput.tsx`. Supports keyboard submission shortcuts (Enter vs Shift+Enter), whitespace trimming and validation guards, interactive `top_k` context chunk selector dropdown, pre-configured suggestion pills for document inquiries, character counter, input clear action, loading spinner feedback, and comprehensive Python backend structural and contract verification in `src/core/frontend.py` and `tests/unit/test_query_input.py`.*

---

### 1. 🎓 Concepts Introduced
- **Keyboard Submission Ergonomics:** Handling `onKeyDown` events on multiline textareas to distinguish between atomic query submission (`Enter` without modifier) and multiline newline insertion (`Shift+Enter`), with `Escape` shortcut for clearing input buffers.
- **Synchronous Input Validation & Trimming:** Validating user query character boundaries and trimming whitespace before dispatching network requests, preventing empty or oversized payloads.
- **Configurable Context Window (Top-K Selection):** Providing interactive controls allowing end-users to select retrieval depth (3, 5, 10, or 15 chunks) passed directly to backend hybrid search and re-ranking pipelines.
- **Suggested Query Chips:** Interactive onboarding prompts representing typical corporate document search inquiries (contract obligations, compliance rules, termination clauses) to accelerate user testing and benchmark exploration.
- **Accessible ARIA and Form Semantics:** Semantic `<form role="form">` structure with distinct DOM element IDs, `aria-label` descriptions, `aria-busy` progress states, `aria-invalid` bindings, and `role="alert"` validation message containers.
- **Automated Frontend Component Auditing:** Backend Python test utilities in `src/core/frontend.py` asserting props contract integrity, DOM element IDs, submission guards, and keyboard shortcuts.

---

### 2. 🧠 Architecture Decisions (ADR)

#### Decision A: Textarea Keydown Interception vs Native Form Submission
- **Option 1 (Native Form Submission):** Multiline `<textarea>` elements insert newlines on Enter by default and do not trigger form submission without complex external event listeners.
- **Option 2 (Selected — Intercepting `onKeyDown`):** Directly inspects `e.key === "Enter" && !e.shiftKey`, prevents default newline insertion, and triggers `handleSubmit()` while preserving `Shift+Enter` for multiline text input.

#### Decision B: Synchronous Disabling During Active Stream
- **Option 1 (Allowing concurrent inputs):** Risks race conditions, out-of-order SSE responses, and confusing transcript state when a query is already streaming.
- **Option 2 (Selected — `isInteractiveDisabled`):** Locks textarea, submit button, clear button, suggestion chips, and top_k dropdown while `isLoading` is true, ensuring clean serial request execution.

#### Decision C: Suggested Query Quick-Fill vs Auto-Submit
- **Option 1 (Immediate submission on pill click):** May execute unwanted search if user accidentally clicks a suggestion or wanted to customize it first.
- **Option 2 (Selected — Quick-fill with focus):** Populates the textarea with the suggested query, focuses the input element, and allows immediate submission via Enter or manual parameter adjustment.

---

### 3. 🛠️ Implementation & Code

**Updated files in `frontend/`:**
- `src/components/QueryInput.tsx`: Complete query input component with `QueryInputProps` interface, validation guards, keyboard handlers, suggestions, top_k selector, and a11y attributes.
- `src/index.css`: Added responsive styles for `.input-action-buttons`, `.btn-clear`, `.btn-spinner`, `.input-error-msg`, `.textarea-error`, `.input-controls-bar`, `.control-label`, `.top-k-dropdown`, `.input-hints`, `.char-counter`, and `.suggested-query-btn`.

**Updated Python validation & test modules:**
- `src/core/frontend.py`: Added `REQUIRED_QUERY_INPUT_PROPS`, `REQUIRED_QUERY_INPUT_IDS`, and `validate_query_input_component()` to audit component structure, contract, and a11y compliance.
- `tests/unit/test_query_input.py`: Comprehensive test suite verifying component presence, props interface, keyboard shortcuts, submission guards, ARIA attributes, top_k options, and error handling.
- `tests/unit/test_runner.py`: Parameterized test runner suite incorporating `test_query_input.py`.

---

### 4. 📌 Session Checklist & Deliverables
1. [x] **QueryInput component implemented** (`frontend/src/components/QueryInput.tsx`)
2. [x] **Keyboard navigation & shortcuts** (`Enter` to submit, `Shift+Enter` for multiline, `Escape` to clear)
3. [x] **Whitespace trimming & validation guards** (prevent empty query submissions, max length validation)
4. [x] **Top-K chunk selector dropdown** (3, 5, 10, 15 chunks)
5. [x] **Suggested query prompt chips** (corporate document query presets)
6. [x] **Accessible ARIA attributes & unique DOM IDs** (`query-form`, `query-input`, `top-k-select`, `submit-query-btn`)
7. [x] **Vanilla CSS styling & micro-animations** (`frontend/src/index.css`)
8. [x] **Backend component validator** (`validate_query_input_component` in `src/core/frontend.py`)
9. [x] **Unit tests passing** (`tests/unit/test_query_input.py`, `make test`, `make typecheck`)
