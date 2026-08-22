# End-to-End Latency Benchmark Report (Phase 10.6)

**Timestamp:** 2026-08-22T07:32:48.092258+00:00 | **Status:** PASSED

## Executive Summary

| Latency Metric | Measured (ms) | SLA Threshold (ms) | Status |
| :--- | :--- | :--- | :--- |
| **$p_{95}$ Latency** | 0.64 ms | <= 3000.00 ms | PASS |
| **$p_{50}$ (Median)** | 0.51 ms | <= 1000.00 ms | PASS |
| **$p_{90}$ Latency** | 0.61 ms | <= 2500.00 ms | PASS |
| **$p_{99}$ Latency** | 0.75 ms | <= 5000.00 ms | PASS |
| **Mean Latency** | 0.48 ms | <= 1500.00 ms | PASS |
| **Min / Max** | 0.18 / 0.79 ms | - | INFO |
| **Std Deviation** | 0.13 ms | - | INFO |

## Domain Category P95 Breakdown

| Category | Evaluated Queries | Measured $p_{95}$ (ms) | SLA Compliance |
| :--- | :--- | :--- | :--- |
| `cloud_infra` | - | 0.53 ms | PASS |
| `hr_policy` | - | 0.58 ms | PASS |
| `incident_response` | - | 0.59 ms | PASS |
| `legal` | - | 0.53 ms | PASS |
| `out_of_corpus` | - | 0.50 ms | PASS |
| `privacy` | - | 0.62 ms | PASS |
| `remote_work` | - | 0.55 ms | PASS |
| `sdlc` | - | 0.52 ms | PASS |
| `security` | - | 0.76 ms | PASS |
| `sla` | - | 0.69 ms | PASS |
| `travel` | - | 0.58 ms | PASS |

## Query Latency Sample Audit

| Query ID | Category | Latency (ms) | Status |
| :--- | :--- | :--- | :--- |
| `eval-001` | `sla` | 0.61 ms | OK |
| `eval-002` | `security` | 0.79 ms | OK |
| `eval-003` | `sla` | 0.71 ms | OK |
| `eval-004` | `sla` | 0.64 ms | OK |
| `eval-005` | `sla` | 0.53 ms | OK |
| `eval-006` | `sla` | 0.52 ms | OK |
| `eval-007` | `security` | 0.62 ms | OK |
| `eval-008` | `security` | 0.36 ms | OK |
| `eval-009` | `security` | 0.48 ms | OK |
| `eval-010` | `security` | 0.55 ms | OK |
| *... and 42 more queries* | | | |
