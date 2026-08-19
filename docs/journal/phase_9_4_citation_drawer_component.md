# Session 9.4: Citation Drawer Component with Clickable Source Excerpts

**Date:** 2026-08-19

*Implements interactive citation drawer component and active source excerpt inspector in `frontend/src/components/CitationDrawer.tsx`. Features real-time client-side substring search filtering across documents and text excerpts, active chunk selection with dedicated inspection container, asynchronous clipboard copying with animated feedback state, relevance score and page formatting, accessible ARIA complementary roles and keyboard navigation, modular backend validator contracts in `src/core/frontend_validators.py`, and comprehensive unit tests in `tests/unit/test_citation_drawer.py`.*

---

### 1. 🎓 Concepts Introduced
- **Bidirectional Citation Focus:** Synchronizing selection state between inline message citation pills in `ResponseView` and source excerpt cards in `CitationDrawer` via shared parent state in `App`.
- **Active Source Inspector:** Dedicated expanded view displaying the full raw text excerpt of a selected chunk alongside document provenance metadata, formatted relevance score, and chunk identifiers.
- **Client-Side Substring Filtering:** Non-blocking in-memory search over retrieved citations using React `useMemo` to filter cards by document name, chunk ID, or excerpt keywords without network round-trips.
- **Asynchronous Clipboard Excerpt Copy:** Seamless copying of source text to the system clipboard via `navigator.clipboard.writeText` with temporary visual confirmation badge feedback (`Copied!`).
- **Keyboard Navigation & ARIA Semantics:** Full compliance with WCAG standards using `role="complementary"`, `role="list"`, `role="listitem"`, `aria-selected`, `tabIndex={0}`, and `Enter`/`Space` key handlers.
- **Modular Frontend Validator Architecture:** Separating React component validation contracts into `src/core/frontend_validators.py` and `src/core/frontend.py` to maintain universal guardrail file limits (<250 LOC).

---

### 2. 🧠 Architecture Decisions (ADR)

#### Decision A: Lifted Citation Selection State vs Local Drawer State
- **Option 1 (Encapsulate active selection locally inside `CitationDrawer`):** Isolates state but prevents inline citation pill clicks in the chat stream from highlighting and focusing corresponding source cards.
- **Option 2 (Selected — Root `App` State Synchronization):** Lifting `activeCitation` to `App` enables bidirectional interaction: clicking an inline citation pill in `ResponseView` opens and highlights the card in `CitationDrawer`, while clicking a card in `CitationDrawer` highlights the active reference across the application.

#### Decision B: In-Memory Search Filtering vs Server-Side Search
- **Option 1 (Debounced API endpoint queries):** Introduces unnecessary network overhead and latency for small context candidate sets ($top\_k \le 15$).
- **Option 2 (Selected — React `useMemo` In-Memory Filtering):** Executes instantaneous substring matching on cached citation models, providing zero-latency search feedback without incurring additional backend compute or network roundtrips.

#### Decision C: Inline Sidebar Inspector vs Modal Dialog
- **Option 1 (Modal Dialog Overlay):** Obscures the active conversation stream and disrupts user reading context.
- **Option 2 (Selected — Inline Active Inspector in Sidebar Drawer):** Keeps conversational answers and cited evidence side-by-side in a responsive split view.

---

### 3. 🛠️ Implementation & Code

**Updated files in `frontend/`:**
- `src/components/CitationDrawer.tsx`: Complete citation drawer component with `CitationDrawerProps`, search filter, active source inspector, clipboard copy action, page/score formatting, and accessible roles.
- `src/index.css`: Added styles for `.drawer-panel`, `.citation-search-box`, `.active-citation-inspector`, `.active-excerpt-blockquote`, `.citation-card-active`, and `.btn-action-small`.

**Updated Python validation & test modules:**
- `src/core/frontend_validators.py`: Created modular component validator containing `REQUIRED_CITATION_DRAWER_PROPS`, `REQUIRED_CITATION_DRAWER_IDS`, and `validate_citation_drawer_component()`.
- `src/core/frontend.py`: Re-exported citation drawer constants and validator functions.
- `src/core/__init__.py`: Exposed citation drawer validation utilities in core package namespace.
- `tests/unit/test_citation_drawer.py`: Comprehensive test suite verifying component presence, props interface, search filtering, active inspector, clipboard actions, and accessibility IDs.
- `tests/unit/test_runner.py`: Integrated `test_citation_drawer.py` into automated test suite runner.

---

### 4. 📌 Session Checklist & Deliverables
1. [x] **CitationDrawer component implemented** (`frontend/src/components/CitationDrawer.tsx`)
2. [x] **Active source excerpt inspector** (`#active-citation-inspector` with full text and provenance metadata)
3. [x] **Real-time search filtering** (`#citation-search-input` with `useMemo` filtering)
4. [x] **Clipboard copy action with feedback** (`#copy-excerpt-btn` with temporary `Copied!` confirmation)
5. [x] **Relevance score & page number formatting** (`Score: X.XXX`, `p. X`, and truncated chunk ID)
6. [x] **Accessible ARIA attributes and keyboard navigation** (`role="complementary"`, `role="listitem"`, `tabIndex={0}`, `Enter`/`Space`)
7. [x] **Empty and no-match search states** (`#empty-citations-state` and filter fallback messages)
8. [x] **Backend component validator** (`validate_citation_drawer_component` in `src/core/frontend_validators.py`)
9. [x] **Unit tests passing** (`tests/unit/test_citation_drawer.py`, `make test`, `make typecheck`)
