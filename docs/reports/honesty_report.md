# Honesty Filter Precision Benchmark Report (Phase 10.5)

**Timestamp:** 2026-08-22T07:32:48.064908+00:00 | **Status:** PASSED

## Executive Summary

| Metric | Measured | Target Threshold | Status |
| :--- | :--- | :--- | :--- |
| `honesty_filter_precision` | 90.00% | >= 90.00% | PASS |
| `out_of_corpus_refusal_rate` | 90.00% | >= 90.00% | PASS |
| `in_corpus_pass_rate` | 100.00% | >= 90.00% | PASS |
| `false_refusal_rate` | 0.00% | <= 10.00% | PASS |

## Confusion Matrix

| Ground Truth Scope | System Refused (Low Confidence) | System Accepted (Grounded) | Total |
| :--- | :--- | :--- | :--- |
| **Out-of-Corpus** | 9 (True Refusal) | 1 (False Acceptance) | 10 |
| **In-Corpus** | 0 (False Refusal) | 42 (True Acceptance) | 42 |
| **Total** | 9 | 43 | 52 |

## Domain Category Breakdown

| Domain Category | Evaluated Queries | Accuracy / Precision |
| :--- | :--- | :--- |
| `cloud_infra` | - | 100.00% |
| `hr_policy` | - | 100.00% |
| `incident_response` | - | 100.00% |
| `legal` | - | 100.00% |
| `out_of_corpus` | - | 90.00% |
| `privacy` | - | 100.00% |
| `remote_work` | - | 100.00% |
| `sdlc` | - | 100.00% |
| `security` | - | 100.00% |
| `sla` | - | 100.00% |
| `travel` | - | 100.00% |

## Out-of-Corpus Query Refusal Audit

| Query ID | Query | Top Score | Refused? | Status |
| :--- | :--- | :--- | :--- | :--- |
| `eval-043` | What is the recipe for authentic Neapolitan pizza dough? | 0.000 | YES | CORRECT |
| `eval-044` | Who won the FIFA Men World Cup football tournament in 1998? | 0.000 | YES | CORRECT |
| `eval-045` | How do you calculate the Schwarzschild radius of a rotating ... | 0.000 | YES | CORRECT |
| `eval-046` | What are the syntax differences between React useState and V... | 0.111 | YES | CORRECT |
| `eval-047` | Can you provide medical advice for managing acute symptoms o... | 0.100 | YES | CORRECT |
| `eval-048` | What was the closing stock price of Apple Inc on NASDAQ on O... | 0.600 | NO | HALLUCINATION_RISK |
| `eval-049` | Who was the first emperor of the Qin dynasty in ancient Chin... | 0.125 | YES | CORRECT |
| `eval-050` | What are the primary tactical opening moves of the Sicilian ... | 0.125 | YES | CORRECT |
| `eval-051` | What are the biochemical synthesis pathways and chemical for... | 0.000 | YES | CORRECT |
| `eval-052` | How did the narrative arc and character storylines resolve i... | 0.091 | YES | CORRECT |
