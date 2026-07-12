# Implementation Specification (from Challenge Repo)

This document captures the exact schemas, constraints, scoring rules, and platform behaviors extracted from the `be-an-fde-for-a-day-main` challenge repository. It supersedes any approximations in earlier planning docs.

---

## 1. Exact API Contracts

### 1.1 GET /health

Returns HTTP 200 with `{"status": "ok"}`.

### 1.2 POST /triage

#### Input Schema
```json
{
  "ticket_id": "SIG-XXXX",
  "subject": "string",
  "description": "string",
  "reporter": {
    "name": "string",
    "email": "string (email)",
    "department": "string"
  },
  "created_at": "ISO 8601 datetime",
  "channel": "subspace_relay | holodeck_comm | bridge_terminal | emergency_beacon",
  "attachments": ["string"]
}
```

#### Output Schema
```json
{
  "ticket_id": "must match input",
  "category": "enum (8 values)",
  "priority": "P1 | P2 | P3 | P4",
  "assigned_team": "enum (7 values)",
  "needs_escalation": "boolean",
  "missing_information": ["enum (16 values)"],
  "next_best_action": "string (single sentence)",
  "remediation_steps": ["string"]
}
```

#### Valid Categories (exact strings)
- Crew Access & Biometrics
- Hull & Structural Systems
- Communications & Navigation
- Flight Software & Instruments
- Threat Detection & Containment
- Telemetry & Data Banks
- Mission Briefing Request
- Not a Mission Signal

#### Valid Teams (exact strings)
- Crew Identity & Airlock Control
- Spacecraft Systems Engineering
- Deep Space Communications
- Mission Software Operations
- Threat Response Command
- Telemetry & Data Core
- None

#### Valid Missing Information (exact strings, 16 terms)
- affected_subsystem
- anomaly_readout
- sequence_to_reproduce
- affected_crew
- habitat_conditions
- stardate
- previous_signal_id
- crew_contact
- module_specs
- software_version
- sector_coordinates
- mission_impact
- recurrence_pattern
- sensor_log_or_capture
- biometric_method
- system_configuration

#### Priority Definitions
- P1: Red Alert — critical/life-threatening
- P2: Yellow Alert — major, no workaround
- P3: Standard Ops — impact with workaround
- P4: Routine — minor/cosmetic

### 1.3 POST /extract

#### Input Schema
```json
{
  "document_id": "DOC-OCR-XXXX",
  "content": "base64-encoded PNG bytes",
  "content_format": "image_base64",
  "json_schema": "string (JSON schema describing expected output, varies per document)"
}
```

#### Output Schema
```json
{
  "document_id": "must match input",
  // ... all fields specified in the json_schema from the request
}
```

The output fields are dynamic per document. The endpoint must read the `json_schema` from the request and return matching structured JSON.

### 1.4 POST /orchestrate

#### Input Schema
```json
{
  "task_id": "TASK-XXXX",
  "goal": "string",
  "available_tools": [
    {
      "name": "string",
      "description": "string",
      "endpoint": "string (URI — rewritten at runtime by platform)",
      "parameters": [
        {
          "name": "string",
          "type": "string",
          "description": "string",
          "required": "boolean"
        }
      ]
    }
  ],
  "constraints": ["string"],
  "mock_service_url": "string (optional, provided at runtime)"
}
```

#### Output Schema
```json
{
  "task_id": "must match input",
  "status": "completed | partial | failed",
  "steps_executed": [
    {
      "step": "integer",
      "tool": "string",
      "parameters": {},
      "result_summary": "string",
      "success": "boolean"
    }
  ],
  "accounts_processed": "integer | null",
  "emails_sent": "integer | null",
  "emails_skipped": "integer | null",
  "skip_reasons": {"reason": count} | null,
  "constraints_satisfied": ["string"]
}
```

#### Critical: Tool Execution
The benchmark checks REAL execution. You MUST actually HTTP-call the tool endpoints. Do not simulate responses. The tool URLs are rewritten at evaluation time by the platform.

---

## 2. Exact Scoring Weights

### Per-task composite
```
task_score = 0.50 × Resolution + 0.20 × Efficiency + 0.30 × Robustness
```

### Final score
```
FDEBench = mean(task1_score, task2_score, task3_score)
```

### 2.1 Resolution (50% per task)

#### Task 1 — Triage
| Dimension | Weight |
|---|---|
| Category F1 (macro, 8 classes) | 24% |
| Priority (ordinal partial credit, off-by-one = 0.67) | 24% |
| Routing F1 (macro, 7 teams) | 24% |
| Missing Info F1 (per-ticket set F1, 16 terms) | 17% |
| Escalation F1 (binary) | 11% |

#### Task 2 — Extraction
| Dimension | Weight |
|---|---|
| Information accuracy (fuzzy token F1, value normalization) | 70% |
| Text fidelity (exact character-level match) | 30% |

#### Task 3 — Orchestration
| Dimension | Weight |
|---|---|
| Goal completion (end-state match) | 20% |
| Tool selection (multiset F1) | 15% |
| Parameter accuracy (per-call parameter match) | 5% |
| Ordering correctness (dependency satisfaction) | 20% |
| Constraint compliance (outcome assertions) | 40% |

### 2.2 Efficiency (20% per task)
```
efficiency = 0.60 × latency_score + 0.40 × cost_score
```

#### Latency thresholds (P95)
| Task | Best (1.0) | Worst (0.0) |
|---|---|---|
| Triage | ≤ 1,500 ms | ≥ 4,200 ms |
| Extract | ≤ 7,100 ms | ≥ 19,000 ms |
| Orchestrate | ≤ 1,500 ms | ≥ 8,000 ms |

#### Model cost tiers (from X-Model-Name header)
| Tier | Score | Examples |
|---|---|---|
| Nano | 100% | gpt-5-nano, gpt-4.1-nano, phi-4, llama-4, qwen |
| Mini | 90% | gpt-5-mini, gpt-4.1-mini, gpt-4o-mini, claude-haiku, deepseek-r1 |
| Standard | 75% | gpt-5, gpt-4.1, gpt-4o, claude-sonnet, o4-mini |
| Full | 50% | gpt-5-pro, o3, grok-4 |
| Premium | 30% | o1, o3-pro, claude-opus, gpt-4.5 |

### 2.3 Robustness (30% per task)
```
robustness = 0.60 × adversarial_accuracy + 0.40 × api_resilience
```

#### API resilience probes
| Probe | Input | Expected |
|---|---|---|
| Malformed JSON | `{"broken` | 400 |
| Empty body | `{}` | 400 or 422 |
| Missing fields | Required fields omitted | 400/422 or valid response with defaults |
| 50 KB payload | Oversized body | 413 or clean rejection |
| Wrong content-type | `Content-Type: text/plain` | 415 or valid JSON response |
| Concurrent burst | 20 requests in 500 ms | ≥ 18 valid responses |
| Cold start | Request after 5 s idle | Valid response |

---

## 3. Platform Behavior (Critical)

1. **Eval items are shuffled per submission.** Join responses on `ticket_id` / `document_id` / `task_id`, NOT on position.
2. **Per-call timeout is 60 seconds.** Keep per-attempt timeout to ~25-30s so retries fit.
3. **Platform retries 429 and 5xx twice** with `Retry-After` honoring (capped at 10s). After 2 retries, the item scores 0.
4. **You must wrap AOAI calls in your own retry-with-backoff.** The OpenAI SDK does NOT honor AOAI throttling by default.
5. **X-Model-Name header is required** for cost scoring. Missing header = unknown cost tier.
6. **No per-dimension or per-item feedback** from the platform. Use local `run_eval.py` for debugging.
7. **T3 tool URLs are rewritten at submission time.** Never hardcode `example.invalid`.

---

## 4. Key Design Constraints Revealed

### Task 1 — Triage
- Signals are messy, vague, contradictory, or prompt-injected.
- Keywords alone will not work — the system needs judgment.
- "Quiet" signals from senior officers can be the real emergencies.
- Hull breach, atmospheric compromise, restricted zone access ALWAYS escalate.
- Gray areas exist: BioAuth panels, SubComm issues, Station Core compute all cross team boundaries.
- `missing_information` should ONLY be emitted when the evidence is truly absent. Over-emitting is penalized by set F1.

### Task 2 — Extraction
- Every document has a DIFFERENT schema — cannot hardcode field names.
- Must read the `json_schema` from the request and return matching fields.
- ~36% of documents are adversarial (photographed, scanned, handwritten, degraded).
- Return `null` for fields you cannot extract — do not hallucinate.
- Numbers should be parsed as numbers, not strings.
- Vision model required (input is an image).
- **AOAI 429 throttling** is a real concern at scale. Must implement retry with Retry-After.

### Task 3 — Orchestration
- Must ACTUALLY call tool endpoints via HTTP.
- The benchmark checks what you actually did, not what you said you'd do.
- Constraint compliance is 40% of resolution — the biggest single dimension.
- Multiple valid plans exist for most goals.
- Parameters must be computed, not copied from the goal.
- Handle tool failures gracefully — crashing is not recovery.
- Track state across steps, validate tool outputs before next call.

---

## 5. Starter Code Available

The repo ships a working stub at `py/apps/sample/`:
- `main.py` — FastAPI app with stub endpoints
- `models.py` — Pydantic models matching all schemas

The eval harness at `py/apps/eval/`:
- `run_eval.py` — scores against public_eval_50 datasets
- `mock_tool_service.py` — local mock for Task 3 tool endpoints

Infrastructure:
- `infra/app/` — Pulumi skeleton for Azure deployment (minimal)

---

## 6. Required Submission Artifacts

```
your-repo/
├── README.md
├── docs/
│   ├── architecture.md
│   ├── methodology.md
│   └── evals.md
└── ... (code, tests, infrastructure)
```

All three docs are mandatory. Missing one affects Tier 2 score.

---

## 7. Model Strategy (Revised with Exact Data)

### For Task 1 (Triage)
- Latency target: ≤ 1,500ms P95 for best score
- This is text classification — a Mini-tier model should work well
- The complexity is in the prompt, not the model size
- Recommended: gpt-4.1-mini or gpt-4o-mini (90% cost score)

### For Task 2 (Extraction)
- Latency target: ≤ 7,100ms P95 for best score
- Requires a vision-capable model
- Higher tolerance for latency means we can use a stronger model if needed
- Recommended: start with gpt-4.1-mini (vision), upgrade if accuracy is too low

### For Task 3 (Orchestration)
- Latency target: ≤ 1,500ms P95 for best score
- Multi-step planning + real HTTP tool calls add latency
- The model call should be fast; tool calls add time
- Recommended: gpt-4.1-mini for planning, real HTTP calls for execution

### Summary
Using a Mini-tier model across all tasks gives us:
- 90% cost efficiency score (vs 75% for Standard, 50% for Full)
- Better latency due to smaller model
- Still strong enough for structured classification and planning
- Can upgrade selectively if accuracy on a specific task is too low

---

## 8. Updated Architecture Decisions

Based on the challenge repo, the following decisions are now locked:

| Decision | Answer | Why |
|---|---|---|
| Extraction input format | `image_base64` | Platform always sends base64, confirmed in docs |
| Orchestration tool calls | Real HTTP calls | Scorer checks actual execution |
| Tool catalog | Dynamic from request | `available_tools` is provided per-request |
| Model tier target | Mini (gpt-4.1-mini) | Best balance of cost score + accuracy + latency |
| Retry strategy | Custom with Retry-After | Platform retries 2x then gives up; AOAI SDK doesn't honor AOAI throttling |
| Response headers | X-Model-Name required | Used for cost scoring |
| Cold start concern | Low (5s idle, not 60s) | The probe uses only 5s idle — easier than expected |

---

## 9. What Changes in Our Design

### Previous assumption → Corrected
- "extraction accepts uploads or URLs" → **always base64 inline**
- "fixed tool catalog for orchestration" → **tools come dynamically in the request**
- "cold start after 60s idle" → **probe is 5s idle (much more lenient)**
- "50KB payload → 413" → **confirmed exactly**
- "model selection is flexible" → **Mini-tier is optimal for cost/latency/accuracy balance**

### New critical requirements discovered
1. Must implement AOAI retry-with-backoff (SDK doesn't do it)
2. Per-attempt timeout should be ~25-30s (platform kills at 60s)
3. Task 3 must make real HTTP calls to tool endpoints
4. X-Model-Name header is mandatory on every response
5. The `json_schema` for Task 2 varies per document — must be parsed dynamically
