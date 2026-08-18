# Session 9.3: SSE Streaming Answer Display with Real-Time Rendering

**Date:** 2026-08-18

*Implements real-time Server-Sent Events (SSE) streaming answer display and stateful rendering under `frontend/src/components/ResponseView.tsx`. Features real-time token concatenation, animated blinking streaming cursor indicator, grounded vs ungrounded/refusal badge indicators, confidence score percentage badges with S_min threshold styling, message citation pills with interactive drawer selection dispatch, FinOps telemetry execution summary, automatic smooth scrolling anchor refs, accessible screen reader live-regions (`role="log"`, `aria-live="polite"`), and backend Python contract verification in `src/core/frontend.py` and `tests/unit/test_streaming_response_view.py`.*

---

### 1. 🎓 Concepts Introduced
- **Real-Time Token Stream Concatenation:** Incrementally appending incoming token deltas from SSE event streams to active assistant message representations in React state without full list replacements or layout thrashing.
- **Visual Streaming Affordance (Blinking Cursor):** Conditional rendering of an animated monospace cursor (`▌`) while a message is in the `isStreaming: true` lifecycle state, terminated on `done` or `error` events.
- **Groundedness & Confidence Threshold Badging:** Translating backend confidence scores and grounding flags into semantic badges (`badge-success` for scores ≥ 0.35, `badge-warning` for lower scores or ungrounded refusals).
- **Interactive Citation Pills:** Message-level clickable source badges (`📄 file_name (p. page_number)`) enabling users to directly focus and highlight corresponding excerpts in the sidebar `CitationDrawer`.
- **Auto-Scrolling Anchors:** Utilizing React `useRef` and `useEffect` hooks to smoothly auto-scroll the conversation viewport to bottom as new token deltas stream in.
- **Accessible Live-Regions:** Semantic ARIA configurations (`role="log"`, `aria-live="polite"`, `aria-atomic="false"`) allowing screen readers to announce streaming content politely without interrupting active navigation.
- **Automated Component Auditing:** Backend Python test utilities in `src/core/frontend.py` asserting props contract integrity, DOM element IDs, auto-scroll mechanisms, streaming cursor presence, and badge thresholds.

---

### 2. 🧠 Architecture Decisions (ADR)

#### Decision A: Component-Level Token Concatenation in App State
- **Option 1 (Buffer in isolated leaf component):** Localizes rendering state but makes global conversation history, citations, and export persistence difficult to coordinate.
- **Option 2 (Selected — Functional State Updates in Parent `App`):** `streamChat` callbacks update the target message using `setMessages(prev => prev.map(...))`, ensuring the complete conversation history remains the single source of truth for citations, drawers, and follow-ups.

#### Decision B: Smooth Ref-Based Scrolling vs Scroll Event Listeners
- **Option 1 (Continuous container `scrollTop` manipulation):** Can cause jitter, layout recalculations on every token, and conflicts if the user scrolls up to read earlier history.
- **Option 2 (Selected — Hidden DOM Anchor with `scrollIntoView`):** Attaches a ref to a trailing empty anchor element `<div ref={messagesEndRef} />` and triggers smooth scrolling via `useEffect` keyed on message and streaming state changes.

#### Decision C: Screen Reader Politeness (`aria-live="polite"` vs `"assertive"`)
- **Option 1 (`aria-live="assertive"`):** Interrupts screen reader speech synthesis on every incoming token, creating an unusable assistive experience.
- **Option 2 (Selected — `aria-live="polite"` with `role="log"`):** Queues announcements naturally so assistive technology reads the answer upon turn completion.

---

### 3. 🛠️ Implementation & Code

**Updated files in `frontend/`:**
- `src/components/ResponseView.tsx`: Complete streaming response view component with `ResponseViewProps`, real-time token rendering, animated cursor, grounded badges, citation pills, FinOps metrics, and empty state.
- `src/App.tsx`: Wired `onSelectCitation` from `ResponseView` into `CitationDrawer` selection state.
- `src/index.css`: Added styles and keyframe animations for `.streaming-cursor`, `.message-citations`, `.citation-pill`, `.finops-bar`, `.empty-state-card`, and responsive adjustments.

**Updated Python validation & test modules:**
- `src/core/frontend.py`: Added `REQUIRED_RESPONSE_VIEW_PROPS`, `REQUIRED_RESPONSE_VIEW_IDS`, and `validate_response_view_component()` to audit component structure, contract, and streaming compliance.
- `tests/unit/test_streaming_response_view.py`: Comprehensive test suite verifying component presence, props interface, streaming cursor, confidence threshold styling, citations display, FinOps metrics, and ARIA attributes.
- `tests/unit/test_runner.py`: Parameterized test runner suite incorporating `test_streaming_response_view.py`.

---

### 4. 📌 Session Checklist & Deliverables
1. [x] **ResponseView component implemented** (`frontend/src/components/ResponseView.tsx`)
2. [x] **Real-time token delta rendering & blinking cursor** (`streaming-cursor` with CSS keyframe animation)
3. [x] **Grounded & confidence score badge indicators** (color-coded based on `S_min >= 0.35` threshold)
4. [x] **Interactive message citation pills** (clickable doc and page reference chips)
5. [x] **FinOps execution metrics footer** (tokens, USD cost, latency, cache hit tag)
6. [x] **Auto-scroll to bottom ref anchor** (`useEffect` smooth scrolling)
7. [x] **Accessible ARIA live regions and unique DOM IDs** (`response-view`, `streaming-cursor`, `empty-state-prompt`, `role="log"`)
8. [x] **Backend component validator** (`validate_response_view_component` in `src/core/frontend.py`)
9. [x] **Unit tests passing** (`tests/unit/test_streaming_response_view.py`, `make test`, `make typecheck`)
