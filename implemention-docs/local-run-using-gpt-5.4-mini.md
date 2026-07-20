# Local Eval Results — gpt-5.4-mini

## Run configuration

| Field | Value |
|---|---|
| Endpoint | localhost |
| Command | `make eval` |
| Run date | 2026-07-20 |
| Models used | gpt-5.4-mini |
| Notes | Local eval run using gpt-5.4-mini model |

## Local runner summary

| Metric | Score |
|---|---|
| FDEBench Composite | 73.4 / 100 |
| Resolution (avg) | 73.6 / 100 |
| Efficiency (avg) | 56.9 / 100 |
| Robustness (avg) | 84.1 / 100 |

## Per-task summary

| Task | Tier 1 Score | Resolution | Efficiency | Robustness | Items scored | Items errored |
|---|---|---|---|---|---|---|
| Signal Triage | 73.3 | 75.4 | 50.2 | 85.1 | 25 | 0 |
| Document Extraction | 88.0 | 87.8 | 81.5 | 92.7 | 50 | 0 |
| Workflow Orchestration | 59.0 | 57.7 | 39.0 | 74.6 | 50 | 0 |

## Task 1: Signal Triage

### Resolution dimensions

| Dimension | Weight | Score | Notes |
|---|---|---|---|
| `category` | 24% | 0.791 | |
| `priority` | 24% | 0.881 | |
| `routing` | 24% | 0.779 | |
| `missing_info` | 17% | 0.456 | |
| `escalation` | 11% | 0.800 | |

### Operational metrics

| Metric | Value |
|---|---|
| Tier 1 Score | 73.3 |
| Resolution | 75.4 |
| Efficiency | 50.2 |
| Robustness | 85.1 |
| Latency (P95) | 2921 ms |
| Latency score | 0.237 |
| Model | gpt-5.4-mini |
| Cost tier score | 0.900 |
| Adversarial accuracy | 75.1 |
| API resilience | 100.0 |
| Items scored | 25 |
| Items errored | 0 |

### Probe results

| Probe | Pass/Fail | Notes |
|---|---|---|
| malformed_json | PASS | |
| empty_body | PASS | |
| missing_fields | PASS | |
| huge_payload | PASS | |
| wrong_content_type | PASS | |
| concurrent_burst | PASS | |
| slow_followup | PASS | |

## Task 2: Document Extraction

### Resolution dimensions

| Dimension | Weight | Score | Notes |
|---|---|---|---|
| `information_accuracy` | 70% | 0.893 | |
| `text_fidelity` | 30% | 0.844 | |

### Operational metrics

| Metric | Value |
|---|---|
| Tier 1 Score | 88.0 |
| Resolution | 87.8 |
| Efficiency | 81.5 |
| Robustness | 92.7 |
| Latency (P95) | 9312 ms |
| Latency score | 0.758 |
| Model | gpt-5.4-mini |
| Cost tier score | 0.900 |
| Adversarial accuracy | 87.8 |
| API resilience | 100.0 |
| Items scored | 50 |
| Items errored | 0 |

### Probe results

| Probe | Pass/Fail | Notes |
|---|---|---|
| malformed_json | PASS | |
| empty_body | PASS | |
| missing_fields | PASS | |
| huge_payload | PASS | |
| wrong_content_type | PASS | |
| concurrent_burst | PASS | |
| slow_followup | PASS | |

## Task 3: Workflow Orchestration

### Resolution dimensions

| Dimension | Weight | Score | Notes |
|---|---|---|---|
| `goal_completion` | 20% | 0.358 | |
| `tool_selection` | 15% | 0.697 | |
| `parameter_accuracy` | 5% | 0.319 | |
| `ordering_correctness` | 20% | 0.531 | |
| `constraint_compliance` | 40% | 0.696 | |

### Operational metrics

| Metric | Value |
|---|---|
| Tier 1 Score | 59.0 |
| Resolution | 57.7 |
| Efficiency | 39.0 |
| Robustness | 74.6 |
| Latency (P95) | 7359 ms |
| Latency score | 0.049 |
| Model | gpt-5.4-mini |
| Cost tier score | 0.900 |
| Adversarial accuracy | 57.7 |
| API resilience | 100.0 |
| Items scored | 50 |
| Items errored | 0 |

### Probe results

| Probe | Pass/Fail | Notes |
|---|---|---|
| malformed_json | PASS | |
| empty_body | PASS | |
| missing_fields | PASS | |
| huge_payload | PASS | |
| wrong_content_type | PASS | |
| concurrent_burst | PASS | |
| slow_followup | PASS | |

## Comparison vs gpt-5.4-nano

| Metric | gpt-5.4-nano | gpt-5.4-mini | Delta |
|---|---|---|---|
| **Composite** | 61.6 | **73.4** | **+11.8** |
| Resolution | 58.6 | **73.6** | **+15.0** |
| Efficiency | **47.0** | 56.9 | +9.9 |
| Robustness | 76.2 | **84.1** | +7.9 |

### Per-task deltas

| Task | Metric | nano | mini | Delta |
|---|---|---|---|---|
| Triage | Tier 1 | 62.5 | **73.3** | +10.8 |
| | Resolution | 58.9 | **75.4** | +16.5 |
| | P95 Latency | 3516ms | **2921ms** | -595ms |
| Extract | Tier 1 | 66.5 | **88.0** | +21.5 |
| | Resolution | 64.5 | **87.8** | +23.3 |
| | P95 Latency | 17031ms | **9312ms** | -7719ms |
| Orchestrate | Tier 1 | 55.7 | **59.0** | +3.3 |
| | Resolution | 52.5 | **57.7** | +5.2 |
| | P95 Latency | 15938ms | **7359ms** | -8579ms |

**Key insight:** gpt-5.4-mini dominates across every dimension. Task 2 sees the largest improvement (+21.5 Tier 1) with both much higher accuracy and nearly 2x faster latency. The 0.900 cost tier (vs 1.000 for nano) is a negligible trade-off given the massive resolution and latency gains.
