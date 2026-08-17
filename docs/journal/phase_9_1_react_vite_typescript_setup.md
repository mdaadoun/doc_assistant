# Session 9.1: React 18+ / Vite / TypeScript Project Initialization

**Date:** 2026-08-17

*Initializes the React 18+, Vite, and TypeScript presentation layer skeleton under `frontend/`. Sets up strict TypeScript configuration, development proxying, domain contract synchronization with backend Pydantic models, SSE stream consumption via `fetch` ReadableStream, custom HSL design system tokens in Vanilla CSS, and automated verification tooling in `src/core/frontend.py`.*

---

### 1. 🎓 Concepts Introduced
- **React 18+ / Vite Single Page Application:** Modern frontend toolchain enabling instant Hot Module Replacement (HMR) and fast ES-module based bundling.
- **Strict TypeScript Boundaries:** Strict TypeScript configuration (`strict: true`, `noUnusedLocals`, `noFallthroughCasesInSwitch`) ensuring complete type safety between frontend UI state and backend contracts.
- **Fetch-based SSE Streaming Client:** Utilizing browser `fetch()` and `ReadableStreamDefaultReader` with `TextDecoder` to handle HTTP POST SSE streams with structured JSON payloads.
- **Design System Tokens:** Vanilla CSS variable architecture utilizing calibrated HSL color spaces and responsive layout primitives without external framework overhead.
- **Frontend Structural Auditing:** Automated Python validator in `src/core/frontend.py` verifying file layout, scripts, dependencies, and contract parity.

---

### 2. 🧠 Architecture Decisions (ADR)

#### Decision A: Fetch with `ReadableStream` vs Native `EventSource`
- **Option 1 (Native `EventSource`):** Only supports HTTP `GET` requests and cannot pass JSON request bodies or custom request headers without query parameter hacks.
- **Option 2 (Selected — `fetch` with `ReadableStream`):** Allows standard `POST /api/v1/chat` request bodies containing `ChatRequest` (`query`, `conversation_id`, `top_k`) while parsing streaming SSE frames asynchronously.

#### Decision B: Vanilla CSS Custom Properties vs Tailwind / CSS Frameworks
- **Option 1 (Tailwind / External UI library):** Adds heavy dependency overhead, build complexity, and potential design drift from project constraints.
- **Option 2 (Selected — Vanilla CSS Tokens):** Zero runtime overhead, clean HSL theme tokens, predictable CSS variables, and full control over accessible micro-interactions.

#### Decision C: Automated Parity Audit via Python Core Module
- **Option 1 (Manual code inspection):** Prone to contract drift when backend Pydantic models are updated.
- **Option 2 (Selected — `validate_frontend_setup` & `test_frontend.py`):** Integrates frontend contract verification directly into backend `pytest` and `make test` test pipelines.

---

### 3. 🛠️ Implementation & Code

**New files in `frontend/`:**
- `package.json`: Configured React 18.3, Vite 5.2, TypeScript 5.4, Lucide icons, and npm scripts (`dev`, `build`, `preview`, `typecheck`).
- `tsconfig.json` & `tsconfig.node.json`: Strict mode with `moduleResolution: "bundler"` and `jsx: "react-jsx"`.
- `vite.config.ts`: Configured `@vitejs/plugin-react` and API proxy `/api -> http://127.0.0.1:8000`.
- `index.html`: Responsive HTML5 shell with semantic layout anchors.
- `src/types/index.ts`: TypeScript contracts mirrored from backend Pydantic models (`Citation`, `FinOpsMetadata`, `ChatRequest`, `ChatResponse`, `RetrievalResult`, `DebugRetrievalResponse`, `SSEEvent`).
- `src/services/api.ts`: Robust SSE reader and API client handling `streamChat` and `getDebugRetrieval`.
- `src/components/Header.tsx`: Application title, session badge, and backend connection status indicator.
- `src/components/QueryInput.tsx`: Multiline prompt input with submission handling, keyboard shortcuts, and `top_k` configuration.
- `src/components/ResponseView.tsx`: Chat stream transcript view with confidence score badges and FinOps telemetry.
- `src/components/CitationDrawer.tsx`: Interactive side drawer displaying grounded citations, page numbers, and relevance scores.
- `src/App.tsx`: Main application orchestrator managing conversation state, streaming SSE events, and active citations.
- `src/index.css`: HSL tokenized design system and responsive layout styling.

**New Python validation & test modules:**
- `src/core/frontend.py`: Project layout, package manifest, and TypeScript contract validator.
- `tests/unit/test_frontend.py`: Unit tests asserting structural completeness and model parity.
- `tests/unit/test_runner.py`: Registered `test_run_project_tests_frontend_suite`.

---

### 4. 📌 Session Checklist & Deliverables
1. [x] **React 18+ / Vite / TypeScript project initialized** (`frontend/`)
2. [x] **Strict TypeScript configuration** (`tsconfig.json`, `tsconfig.node.json`)
3. [x] **Vite configuration with dev proxy** (`vite.config.ts`)
4. [x] **TypeScript domain contracts** (`frontend/src/types/index.ts`)
5. [x] **SSE streaming API client** (`frontend/src/services/api.ts`)
6. [x] **Modular presentation components** (`Header`, `QueryInput`, `ResponseView`, `CitationDrawer`, `App`)
7. [x] **Vanilla CSS design system** (`frontend/src/index.css`)
8. [x] **Python validation module & tests** (`src/core/frontend.py`, `tests/unit/test_frontend.py`)
9. [x] **All tests and typechecks passing** (`make test`, `make typecheck`)
