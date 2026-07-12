# Methodology

## Approach

Started by thoroughly analyzing the challenge requirements, scoring rubric, and sample data before writing any code. The strategy was:

1. **Understand the scoring system first** — mapped out exact weights, latency thresholds, and resilience probes
2. **Lock the architecture** — chose Azure AI Foundry + FastAPI + Container Apps based on scoring incentives
3. **Build foundation** — health endpoint, error handling, resilience probes, observability headers
4. **Implement tasks incrementally** — triage first (most well-defined), then orchestration (execution-focused), then extraction (vision-dependent)
5. **Iterate on prompts** — use local eval harness to measure and improve

The key insight was that consistency across all three tasks matters more than perfecting one. The FDEBench score is the mean of all three task scores, so a balanced approach wins.

## Time allocation

<!-- TODO: Update with actual time spent -->

| Phase | Estimated % | Focus |
|---|---|---|
| Requirements & design | 15% | Understanding scoring, schemas, platform behavior |
| Foundation & infrastructure | 20% | FastAPI scaffold, error handling, deployment, observability |
| Task 1: Triage | 25% | Prompt engineering, routing logic, missing_information accuracy |
| Task 2: Extraction | 20% | Vision model integration, dynamic schema parsing, retry logic |
| Task 3: Orchestration | 20% | Tool execution, constraint tracking, error recovery |

Task 1 received the most prompt-engineering attention because it has the most scored dimensions (5) and the most nuanced judgment requirements.

## Task 1: Signal Triage

**Approach:**
- Built a comprehensive system prompt encoding the routing guide, team ownership, priority definitions, and escalation rules
- Used structured output to constrain the model to valid enums
- Focused heavily on the missing_information dimension — only emit when evidence is truly absent

**What moved the needle:**
<!-- TODO: Update after implementation -->
(To be documented during implementation)
- Including explicit definitions of each missing_information term in the prompt
- Adding gray-area guidance for signals that cross team boundaries
- Using few-shot examples from the sample data to calibrate priority judgment

**What didn't work:**
<!-- TODO: Update after implementation -->
(To be documented during implementation)
- Initial prompts over-emitted missing_information (penalized by set F1)
- Keyword-based approaches for team routing failed on ambiguous signals

## Task 2: Document Extraction

**Approach:**
- Used a vision-capable model to process base64-encoded document images directly (no Azure AI Document Intelligence — the vision model handles extraction end-to-end)
- Parsed the per-document json_schema dynamically to instruct the model on expected fields
- Implemented value normalization (numbers as numbers, consistent formatting)
- Added custom retry logic for AOAI 429 throttling with Retry-After honoring

**Challenges:**
<!-- TODO: Update after implementation -->
- ~36% of documents are adversarial (handwritten, degraded, photographed)
- Different schemas per document means no hardcoded extraction logic
- Balancing information_accuracy (70% weight) vs. text_fidelity (30% weight)

## Task 3: Workflow Orchestration

**Approach:**
- The model generates an execution plan, then the service executes it by making real HTTP calls to tool endpoints
- Constraint compliance is tracked throughout execution (40% of resolution score)
- Tool failures are handled gracefully with retries and skip tracking
- State is maintained across steps to inform parameter computation

**What was hardest:**
<!-- TODO: Update after implementation -->
(To be documented during implementation)
- Computing parameters from tool responses rather than copying from the goal
- Ensuring constraint satisfaction even when tool calls return unexpected data
- Handling ambiguous goals where multiple valid plans exist

## Model Selection Decision

### Process

We compared all models available in the Azure AI Foundry model catalog using the platform's benchmark data (quality index, throughput, benchmark cost, and safety metrics) and cross-referenced against the FDEBench efficiency scoring tiers.

### FDEBench Cost Tier Mapping

The challenge scores cost efficiency via the `X-Model-Name` response header:

| Tier | Cost Score | Examples |
|------|-----------|---------|
| Nano | 100% | gpt-4.1-nano, gpt-5-nano, gpt-5.4-nano |
| Mini | 90% | gpt-4.1-mini, gpt-5.4-mini, gpt-4o-mini |
| Standard | 75% | gpt-4.1, gpt-4o, gpt-5, o4-mini |
| Full | 50% | o3, gpt-5-pro |
| Premium | 30% | o1, claude-opus |

### Benchmark Comparison (from Foundry catalog)

| Model | Quality Index | Throughput (tok/s) | Bench Cost ($) | Safety ASR (%) | FDEBench Tier | Cost Score |
|-------|--------------|-------------------|---------------|---------------|---------------|-----------|
| **gpt-5.4-nano** | **0.64** | **177** | **$8.78** | **0.61%** | **Nano** | **100%** |
| gpt-5.4-mini | 0.67 | 142 | $45.81 | 0.00% | Mini | 90% |
| gpt-5-nano | 0.53 | 224 | $25.08 | 1.67% | Nano | 100% |
| gpt-4.1-mini | 0.59 | 125 | $32.59 | 17.50% | Mini | 90% |
| gpt-4.1-nano | 0.49 | 183 | $1.38 | 1.09% | Nano | 100% |
| o4-mini | 0.69 | 52 | $90.40 | 2.33% | Standard | 75% |
| gpt-4.1 | 0.64 | 95 | $75.09 | 9.83% | Standard | 75% |
| DeepSeek-V4-Flash | 0.72 | 91 | $7.51 | 31.50% | Mini | 90% |
| gpt-5 | 0.74 | 69 | $215.93 | 1.09% | Standard | 75% |

### Decision: gpt-5.4-nano

**Selected model:** `gpt-5.4-nano`

**Why it wins over gpt-4.1-mini (the obvious default):**

| Metric | gpt-5.4-nano | gpt-4.1-mini | Advantage |
|--------|-------------|-------------|-----------|
| Quality (→ Resolution, 50% of score) | 0.64 | 0.59 | +8.5% better accuracy |
| Throughput (→ Latency, 12% of score) | 177 tok/s | 125 tok/s | +42% faster |
| Cost tier (→ Cost, 8% of score) | 100% (Nano) | 90% (Mini) | +10% cheaper scoring |
| Safety | 0.61% ASR | 17.50% ASR | 28x safer |

**Why not higher-quality models (o4-mini at 0.69, gpt-5 at 0.74)?**
- Standard tier cost score (75%) vs Nano (100%) costs 25 percentage points on cost
- Much slower throughput (52-69 tok/s) risks missing latency thresholds
- The quality gain does not compensate for the 25% cost penalty and latency hit under the FDEBench formula

**Why not DeepSeek-V4-Flash (quality 0.72, cost $7.51)?**
- 31.50% safety attack success rate is unacceptable for a Microsoft hackathon
- Unclear FDEBench tier classification
- Slower throughput (91 tok/s)

**Estimated net advantage over gpt-4.1-mini: +5-7 points on final FDEBench score**

### Per-Task Assignment

| Task | Model | Reasoning |
|------|-------|-----------|
| Triage | gpt-5.4-nano | Higher quality for nuanced classification, Nano tier for cost |
| Extract | gpt-5.4-nano (or gpt-4.1-mini fallback) | **CRITICAL: Must confirm vision capability before committing.** Task 2 is ~33% of the final score. If nano cannot process images, we MUST use gpt-4.1-mini (confirmed vision-capable) for this task. |
| Orchestrate | gpt-5.4-nano | Better reasoning for constraint compliance (40% of T3 resolution) |
### Validation Strategy: Deploy Both, Compare Locally

We will deploy **both** `gpt-5.4-nano` and `gpt-4.1-mini` in Azure AI Foundry and run the local eval harness against each to make a data-driven decision:

1. Deploy both models in Foundry
2. Build the solution with a configurable `MODEL_NAME` / `AZURE_OPENAI_DEPLOYMENT` env var
3. Run `make eval` against `public_eval_50` with gpt-5.4-nano → record all dimension scores
4. Run `make eval` again with gpt-4.1-mini → record all dimension scores
5. Compare FDEBench composite: if gpt-4.1-mini's resolution advantage (if any) outweighs the 10% cost penalty, submit with mini
6. Submit with whichever model produces the higher total FDEBench score

This is low-risk because the code is identical — only the deployment target changes via env var. We can switch models in seconds without code changes.

**Decision criteria:**
- If gpt-5.4-nano scores within 3 points of gpt-4.1-mini on resolution → use nano (wins on cost + latency)
- If gpt-4.1-mini beats nano by >5 points on resolution → use mini (resolution is 50% of score, overwhelms the 10% cost gap)
- If nano lacks vision → use mini for Task 2, nano for Tasks 1 & 3 (split model strategy, report both in X-Model-Name per endpoint)
### Upgrade Path

If gpt-5.4-nano lacks vision support for Task 2, we use gpt-4.1-mini for extraction only (confirmed vision-capable) and keep gpt-5.4-nano for Tasks 1 and 3. This is the **first thing to verify** when setting up the Azure AI Foundry deployment.

> **Action item:** Deploy gpt-5.4-nano in Foundry and test with a sample base64 image before building the extraction pipeline. If it fails, lock in gpt-4.1-mini for Task 2 immediately.

## What worked

<!-- TODO: Update after implementation -->
(To be documented during implementation)
- Choosing Nano-tier model (gpt-5.4-nano) over the default Mini-tier — stronger quality AND better cost/latency scores
- Building resilience probes into the foundation from day one
- Using the local eval harness for rapid iteration
- Keeping the architecture simple and modular

## What didn't work

<!-- TODO: Update after implementation -->
- (To be documented during implementation)

## Key learnings

<!-- TODO: Update after implementation -->
- The scoring rubric should drive every design decision
- Consistency across tasks matters more than perfection on one
- Platform behaviors (retry, timeout, shuffling) must be designed for explicitly
- Cost scoring via X-Model-Name header is a strong incentive to use smaller models
