# Evaluation Results

Use this file to record the output of the local eval harness at [py/apps/eval/run_eval.py](../py/apps/eval/run_eval.py). Fill in the numbers from your latest run, then add concise analysis.

## Run configuration

| Field | Value |
|---|---|
| Endpoint | localhost |
| Command | `make eval` |
| Run date | 2026-07-12 |
| Models used | gpt-5.4-nano |
| Notes | First local eval run after increasing request_timeout to 30s |

## Local runner summary

These fields map directly to the top-level runner output.

| Metric | Score |
|---|---|
| FDEBench Composite | 61.6 / 100 |
| Resolution (avg) | 58.6 / 100 |
| Efficiency (avg) | 47.0 / 100 |
| Robustness (avg) | 76.2 / 100 |

## Per-task summary

These rows mirror the task summary block printed by the local runner.

| Task | Tier 1 Score | Resolution | Efficiency | Robustness | Items scored | Items errored |
|---|---|---|---|---|---|---|
| Signal Triage | 62.5 | 58.9 | 47.6 | 78.4 | 25 | 0 |
| Document Extraction | 66.5 | 64.5 | 53.3 | 78.7 | 50 | 0 |
| Workflow Orchestration | 55.7 | 52.5 | 40.0 | 71.5 | 50 | 0 |

## Task 1: Signal Triage

### Resolution dimensions

| Dimension | Weight | Score | Notes |
|---|---|---|---|
| `category` | 24% | 0.622 | |
| `priority` | 24% | 0.842 | |
| `routing` | 24% | 0.627 | |
| `missing_info` | 17% | 0.276 | |
| `escalation` | 11% | 0.364 | |

### Operational metrics

| Metric | Value |
|---|---|
| Tier 1 Score | 62.5 |
| Resolution | 58.9 |
| Efficiency | 47.6 |
| Robustness | 78.4 |
| Latency (P95) | 3516 ms |
| Latency score | 0.127 |
| Model | gpt-5.4-nano |
| Cost tier score | 1.000 |
| Adversarial accuracy | 64.0 |
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

### Error analysis

<!-- Which signal types failed? Where did routing, priority, or missing_info break down? -->

## Task 2: Document Extraction

### Resolution dimensions

| Dimension | Weight | Score | Notes |
|---|---|---|---|
| `information_accuracy` | 70% | 0.660 | |
| `text_fidelity` | 30% | 0.611 | |

### Operational metrics

| Metric | Value |
|---|---|
| Tier 1 Score | 66.5 |
| Resolution | 64.5 |
| Efficiency | 53.3 |
| Robustness | 78.7 |
| Latency (P95) | 17031 ms |
| Latency score | 0.222 |
| Model | gpt-5.4-nano |
| Cost tier score | 1.000 |
| Adversarial accuracy | 64.5 |
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

### Error analysis

<!-- Which document types, fields, or PDF cases failed? Where did normalization help or hurt? -->

## Task 3: Workflow Orchestration

### Resolution dimensions

| Dimension | Weight | Score | Notes |
|---|---|---|---|
| `goal_completion` | 20% | 0.345 | |
| `tool_selection` | 15% | 0.614 | |
| `parameter_accuracy` | 5% | 0.227 | |
| `ordering_correctness` | 20% | 0.536 | |
| `constraint_compliance` | 40% | 0.613 | |

### Operational metrics

| Metric | Value |
|---|---|
| Tier 1 Score | 55.7 |
| Resolution | 52.5 |
| Efficiency | 40.0 |
| Robustness | 71.5 |
| Latency (P95) | 15938 ms |
| Latency score | 0.000 |
| Model | gpt-5.4-nano |
| Cost tier score | 1.000 |
| Adversarial accuracy | 52.5 |
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

### Error analysis

<!-- Which workflow types failed? Were failures caused by tool choice, parameters, ordering, or constraint handling? -->

## Cross-task takeaways

### What improved the score

<!-- Which changes moved the needle across multiple tasks? Better prompts, validation, retries, model changes, caching, etc. -->

### Known limitations

<!-- Where does the system still break? Be concrete about likely failure modes per task and what you would fix next. -->
