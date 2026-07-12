# Evaluation Results

Use this file to record the output of the local eval harness at [py/apps/eval/run_eval.py](../py/apps/eval/run_eval.py). Fill in the numbers from your latest run, then add concise analysis.

## Run configuration

| Field | Value |
|---|---|
| Endpoint | https://fde-solution.braveglacier-ab8fc7b3.eastus2.azurecontainerapps.io |
| Command | `uv run --package eval python apps/eval/run_eval.py --endpoint https://fde-solution.braveglacier-ab8fc7b3.eastus2.azurecontainerapps.io` |
| Run date | 2026-07-12 |
| Models used | gpt-5.4-nano |
| Notes | Eval run against deployed Azure Container Apps endpoint |

## Local runner summary

These fields map directly to the top-level runner output.

| Metric | Score |
|---|---|
| FDEBench Composite | 62.3 / 100 |
| Resolution (avg) | 59.2 / 100 |
| Efficiency (avg) | 48.8 / 100 |
| Robustness (avg) | 76.4 / 100 |

## Per-task summary

These rows mirror the task summary block printed by the local runner.

| Task | Tier 1 Score | Resolution | Efficiency | Robustness | Items scored | Items errored |
|---|---|---|---|---|---|---|
| Signal Triage | 65.0 | 61.3 | 52.8 | 79.4 | 25 | 0 |
| Document Extraction | 66.0 | 63.6 | 53.6 | 78.2 | 50 | 0 |
| Workflow Orchestration | 55.8 | 52.7 | 40.0 | 71.6 | 50 | 0 |

## Task 1: Signal Triage

### Resolution dimensions

| Dimension | Weight | Score | Notes |
|---|---|---|---|
| `category` | 24% | 0.622 | Same as local — deterministic with temp=0 |
| `priority` | 24% | 0.855 | Improved from 0.842 local — override rules working well |
| `routing` | 24% | 0.627 | Same as local |
| `missing_info` | 17% | 0.314 | Improved from 0.276 local |
| `escalation` | 11% | 0.500 | Improved from 0.364 local |

### Operational metrics

| Metric | Value |
|---|---|
| Tier 1 Score | 65.0 |
| Resolution | 61.3 |
| Efficiency | 52.8 |
| Robustness | 79.4 |
| Latency (P95) | 3047 ms |
| Latency score | 0.213 |
| Model | gpt-5.4-nano |
| Cost tier score | 1.000 |
| Adversarial accuracy | 65.7 |
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

Deployed endpoint shows improvement over local run on escalation (0.500 vs 0.364) and missing_info (0.314 vs 0.276). Latency also improved (3047 ms vs 3516 ms), likely due to Azure Container Apps being closer to the Azure OpenAI endpoint (both in Azure network). Priority remains the strongest dimension at 0.855.

## Task 2: Document Extraction

### Resolution dimensions

| Dimension | Weight | Score | Notes |
|---|---|---|---|
| `information_accuracy` | 70% | 0.648 | Slightly lower than local (0.660) — minor variance |
| `text_fidelity` | 30% | 0.608 | Consistent with local (0.611) |

### Operational metrics

| Metric | Value |
|---|---|
| Tier 1 Score | 66.0 |
| Resolution | 63.6 |
| Efficiency | 53.6 |
| Robustness | 78.2 |
| Latency (P95) | 16906 ms |
| Latency score | 0.226 |
| Model | gpt-5.4-nano |
| Cost tier score | 1.000 |
| Adversarial accuracy | 63.6 |
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

Very consistent with local run. Slight decrease in information_accuracy (0.648 vs 0.660) is within expected variance for vision model outputs. Latency slightly improved (16906 ms vs 17031 ms). Overall stable and reproducible.

## Task 3: Workflow Orchestration

### Resolution dimensions

| Dimension | Weight | Score | Notes |
|---|---|---|---|
| `goal_completion` | 20% | 0.338 | Consistent with local (0.345) |
| `tool_selection` | 15% | 0.627 | Slightly improved from local (0.614) |
| `parameter_accuracy` | 5% | 0.230 | Consistent with local (0.227) |
| `ordering_correctness` | 20% | 0.529 | Consistent with local (0.536) |
| `constraint_compliance` | 40% | 0.619 | Slightly improved from local (0.613) |

### Operational metrics

| Metric | Value |
|---|---|
| Tier 1 Score | 55.8 |
| Resolution | 52.7 |
| Efficiency | 40.0 |
| Robustness | 71.6 |
| Latency (P95) | 11985 ms |
| Latency score | 0.000 |
| Model | gpt-5.4-nano |
| Cost tier score | 1.000 |
| Adversarial accuracy | 52.7 |
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

Latency improved significantly vs local (11985 ms vs 15938 ms) — Azure-internal networking between Container App and mock tool service is faster. Score still 0.000 due to threshold. Tool selection and constraint compliance slightly improved. Goal completion remains the weakest dimension — single upfront planning cannot adapt to actual tool response data.

## Cross-task takeaways

### What improved the score

- **Deployed endpoint scores higher than local** — FDEBench Composite improved from 61.6 (local) to 62.3 (deployed). Improvements concentrated in Task 1 (62.5 → 65.0) due to better escalation and missing_info scores.
- **Lower latency on Azure** — internal Azure networking reduces round-trip time for both LLM calls and tool calls. P95 latency improved across all tasks.
- **100% probe pass rate maintained** — all 7 probes pass across all 3 tasks on the deployed endpoint, confirming the resilience foundation works in production.

### Known limitations

- **Latency score still 0.000 for Task 3** — even with improved latency (11985 ms), orchestration exceeds the scoring threshold due to sequential LLM + multiple HTTP calls.
- **Goal completion (0.338)** remains the weakest dimension — requires iterative re-planning to improve.
- **Parameter accuracy (0.230)** — upfront planning can't chain tool outputs as parameters to subsequent steps.
- **Efficiency (avg 48.8)** is still the weakest scoring category — latency is the bottleneck, not cost (which is perfect at 1.000).
