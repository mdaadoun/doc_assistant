# Retrieval & Grounding Benchmark Report

> **Generated:** `2026-08-22T07:32:48.032212+00:00` | **Overall Status:** ✅ PASS

## 1. Executive Summary & Quality Targets

| Metric | Measured Value | Minimum Target | Evaluation Status |
| :--- | :--- | :--- | :--- |
| `retrieval_precision@5` | **1.0000** | $\ge 0.75$ | ✅ PASS |
| `honesty_filter_precision` | **0.9000** | $\ge 0.90$ | ✅ PASS |
| `p95_latency_ms` | **0.7 ms** | $\le 3000 \text{ ms}$ | ✅ PASS |
| `mean_recall@5` | **1.0000** | — | INFO |
| `mrr` (Mean Reciprocal Rank) | **0.9821** | — | INFO |
| `hit_rate@5` | **1.0000** | — | INFO |

## 2. Dataset & Cardinality Overview

- **Total Queries Evaluated:** 52
- **In-Corpus Factual Queries:** 42
- **Out-of-Corpus Refusal Queries:** 10

## 3. Latency Distribution (Milliseconds)

| Metric | Latency (ms) |
| :--- | :--- |
| Median ($p_{50}$) | 0.48 ms |
| 90th Percentile ($p_{90}$) | 0.57 ms |
| 95th Percentile ($p_{95}$) | 0.67 ms |
| 99th Percentile ($p_{99}$) | 0.90 ms |
| Mean Latency | 0.46 ms |
| Maximum Latency | 0.91 ms |

## 4. Category Breakdown

| Category | Count | Precision@5 | Recall@5 | MRR | Hit Rate | Guard Pass Rate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `cloud_infra` | 4 | 1.000 | 1.000 | 0.812 | 1.000 | 1.000 |
| `hr_policy` | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `incident_response` | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `legal` | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `out_of_corpus` | 10 | 0.000 | 1.000 | 0.000 | 0.000 | 0.100 |
| `privacy` | 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `remote_work` | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `sdlc` | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `security` | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `sla` | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| `travel` | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

## 5. Failure & Outlier Inspection

| Query ID | Category | Type | Query Text | Issue |
| :--- | :--- | :--- | :--- | :--- |
| `eval-048` | `out_of_corpus` | Out-of-Corpus | What was the closing stock price of Apple Inc on N... | Failed Refusal (Guard Passed) |
