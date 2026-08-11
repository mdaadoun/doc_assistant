# Architectural Journal — Phase 3.6: Differential Update Handling (Detect Changed/New/Deleted Files)

> **Phase:** 3.6 | **Date:** 2026-08-11 | **Status:** Completed

---

## 🎯 Objective
Implement differential update handling in the document ingestion pipeline to track state changes across the document corpus. Automatically detect newly added, modified, deleted, and unchanged document files using cryptographic content hashing and state manifests, bypassing re-parsing and re-chunking for unmodified files.

---

## 💡 Architectural Choices

### 1. Decoupled Differential Tracker Class
- **Context:** The ingestion pipeline requires tracking file states across repeated batch runs to prevent redundant document parsing and chunking computations.
- **Decision:** Implement `DifferentialTracker` as a dedicated service component handling state tracking, scanning, and manifest persistence independently from concrete format parsers.
- **Rationale:** Decoupling tracking logic from parsing/chunking algorithms preserves strict layer isolation and single-responsibility principles, keeping parsers focused solely on document text extraction.

### 2. SHA-256 Content Hashing over Modification Timestamps (mtime)
- **Context:** File modification timestamps (`mtime`) fluctuate when copying files across filesystems or running `git checkout`, causing false-positive modification alerts on unchanged documents.
- **Decision:** Use SHA-256 binary content digests (`compute_file_hash`) with 64KB chunked stream reads to evaluate file state equality.
- **Rationale:** Content digests guarantee exact byte-level change detection, eliminating false positives caused by timestamp drift or file touch events. Chunked streaming keeps memory overhead low even for large PDF documents.

### 3. Pydantic V2 State Manifest Persistence
- **Context:** Differential update state must persist reliably across application restarts in a human-readable, schema-validated format.
- **Decision:** Model file state metadata as Pydantic V2 schemas (`FileState`, `StateManifest`) and persist manifest records to disk as formatted JSON files via `load_manifest()` and `save_manifest()`.
- **Rationale:** Pydantic V2 ensures strict type safety, zero dynamic typed escapes, and automatic JSON validation upon reload. Human-readable JSON allows easy operational auditing and debugging.

### 4. Seamless Ingestion Facade Integration
- **Context:** Client applications and batch ingestion scripts need a unified entry point to trigger differential ingestion without manually coordinating scanner and parser steps.
- **Decision:** Integrate `DifferentialTracker` into `IngestionFacade` via `ingest_differential()`, which automatically scans target paths, purges deleted file entries, ingests only new/changed files, and updates the manifest.
- **Rationale:** Provides an elegant high-level API for callers while preserving full backwards compatibility for standard full-ingestion methods (`ingest_document`, `ingest_batch`).

---

## ⚖️ Trade-offs & Mitigations

| Architectural Choice | Trade-off | Mitigation Strategy |
| :--- | :--- | :--- |
| **Cryptographic SHA-256 Hashing** | Reading full file bytes for hashing incurs small disk I/O cost during initial scan. | Processed using 64KB chunked binary reads in local memory; scanning fast local SSD storage completes in milliseconds. |
| **JSON File Manifest Storage** | Local JSON files are ideal for thousands of documents but less suited for multi-node distributed workers. | Encapsulated manifest load/save methods inside `DifferentialTracker`, enabling seamless replacement with PostgreSQL / Redis state stores in future phases. |
| **Automatic Deleted File Purging** | `sync_delta()` immediately purges deleted file tracking records from manifest state. | Retained deleted file path lists in returned `DifferentialDelta` payloads so downstream vector store adapters can drop corresponding vector chunks. |
