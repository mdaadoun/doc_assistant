# Session 9.5: Loading States, Error Handling, and Confidence Indicators

**Date:** 2026-08-19

*Implements resilient frontend feedback mechanisms in `frontend/src/components/ConfidenceIndicator.tsx`, `frontend/src/components/ErrorBanner.tsx`, `frontend/src/components/LoadingIndicator.tsx`, with full integration across `frontend/src/components/ResponseView.tsx` and `frontend/src/App.tsx`. Introduces tiered confidence score visualization (High $\ge 0.70$, Moderate $0.35 - 0.70$, Low $< 0.35$) with an accessible visual progress meter and minimum threshold marker ($S_{\min} = 0.35$), multi-phase retrieval progress tracking ('retrieving' $\to$ 'reranking' $\to$ 'generating' $\to$ 'complete') with skeleton shimmer animations, non-blocking inline error recovery with automated query replay, modular backend validator contracts in `src/core/resilience_validators.py`, and comprehensive unit tests in `tests/unit/test_loading_and_confidence.py`.*

---

### 1. 🎓 Concepts Introduced
- **Tiered Confidence Calibration:** Categorizing continuous cross-encoder relevance scores into discrete, human-interpretable tiers (High $\ge 70\%$, Moderate $35\% - 70\%$, Low $< 35\%$) paired with grounding verification badges and visual meter indicators relative to the $S_{\min} = 0.35$ gate.
- **Granular Retrieval Phase Tracking:** Communicating multi-stage RAG execution stages (`retrieving` $\to$ `reranking` $\to$ `generating` $\to$ `complete`) to the user via animated pipeline step tracks and skeleton shimmer placeholders prior to first-token arrival.
- **Non-Blocking Inline Error Recovery:** Rendering rich diagnostic failure details (error code, message, timestamp) directly inside conversation threads alongside an idempotent `Retry Query` replay action.
- **Accessible Progressbar & Alert Semantics:** Adhering strictly to WCAG accessibility standards using `role="progressbar"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, `role="alert"`, `aria-live="assertive"`, and `role="status"`.
- **Modular Resilience Validation Architecture:** Isolating React resilience contracts into `src/core/resilience_validators.py` and re-exporting through `src/core/frontend.py` to maintain universal file limits (<250 LOC).

---

### 2. 🧠 Architecture Decisions (ADR)

#### Decision A: Tiered Confidence Classification & Visual Meter vs Binary Pass/Fail
- **Option 1 (Binary Grounded/Ungrounded Toggle):** Obscures relative confidence levels within acceptable answer bounds and provides no insight into how close a query is to the refusal threshold.
- **Option 2 (Selected — 3-Tier Model with Visual Progress Bar):** Classifies scores into High ($\ge 0.70$), Moderate ($0.35 - 0.70$), and Low ($< 0.35$), visually anchored by a threshold marker at $35\%$, giving users calibrated confidence and grounding transparency.

#### Decision B: Inline Error Boundary & Query Replay vs Modal Dialog Blocking
- **Option 1 (Modal Dialog Blocking):** Interrupts conversation flow and forces the user to manually re-enter their query and configuration upon network interruption.
- **Option 2 (Selected — Inline Message Error Cards & Idempotent Replay):** Retains full conversational context and preserves query parameters (`query`, `top_k`), enabling one-click re-submission without page reloads.

#### Decision C: Granular Phase Tracking vs Indeterminate Spinner
- **Option 1 (Generic Indeterminate Spinner):** Leaves users uncertain whether latency originates from document vector retrieval, re-ranking, or token generation.
- **Option 2 (Selected — Pipeline Step Track & Skeleton Shimmer):** Visually steps through `Dual Search` $\to$ `Re-Rank & Guard` $\to$ `Grounded Stream`, improving perceived performance and debugging visibility.

---

### 3. 🛠️ Implementation & Code

**Updated & Created files in `frontend/`:**
- `src/components/ConfidenceIndicator.tsx`: Visual confidence meter, tiered score badge, grounding status, and threshold marker ($S_{\min} = 0.35$).
- `src/components/ErrorBanner.tsx`: Global alert banner with error code tags, ARIA alert semantics, dismiss action, and query retry mechanism.
- `src/components/LoadingIndicator.tsx`: Multi-phase pipeline progress tracker with skeleton shimmer and loading spinner.
- `src/types/index.ts`: Added `ConfidenceTier`, `RetrievalPhase`, and `ErrorInfo` interfaces; updated `ChatMessage` and `QueryState`.
- `src/components/ResponseView.tsx`: Integrated `ConfidenceIndicator`, in-flight `LoadingIndicator`, and inline error retry cards into message stream.
- `src/App.tsx`: Added global `ErrorBanner`, stateful `retrievalPhase` transitions, and query replay handler `handleRetry`.
- `src/index.css`: Added styling for confidence meters, skeleton shimmer pulses, pipeline tracks, and error alert cards.

**Updated Python validation & test modules:**
- `src/core/resilience_validators.py`: Created modular component validator containing `REQUIRED_CONFIDENCE_INDICATOR_PROPS`, `REQUIRED_ERROR_BANNER_PROPS`, `REQUIRED_LOADING_INDICATOR_PROPS`, and validation functions.
- `src/core/frontend.py`: Updated required frontend files, interfaces, and re-exports.
- `src/core/__init__.py`: Exposed resilience validation utilities in core package namespace.
- `tests/unit/test_loading_and_confidence.py`: Comprehensive test suite verifying confidence meters, error banners, loading indicators, retry actions, and accessibility attributes.
- `tests/unit/test_runner.py`: Integrated `test_loading_and_confidence.py` into automated test suite runner.

---

### 4. 📌 Session Checklist & Deliverables
1. [x] **ConfidenceIndicator component implemented** (`frontend/src/components/ConfidenceIndicator.tsx`)
2. [x] **Tiered confidence classification & meter bar** (High $\ge 0.70$, Moderate $0.35 - 0.70$, Low $< 0.35$, $S_{\min} = 0.35$ marker)
3. [x] **ErrorBanner component implemented** (`frontend/src/components/ErrorBanner.tsx` with retry & dismiss)
4. [x] **LoadingIndicator component implemented** (`frontend/src/components/LoadingIndicator.tsx` with pipeline steps & skeleton pulse)
5. [x] **ResponseView and App integration** (In-flight loading skeletons, inline error cards, and global retry orchestration)
6. [x] **Backend component validator** (`validate_resilience_and_confidence_components` in `src/core/resilience_validators.py`)
7. [x] **Unit tests passing** (`tests/unit/test_loading_and_confidence.py`, `make test`, `make typecheck`)
