# Be a Microsoft FDE for a Day

The FDE Hackathon. Watch the intro first, then read the rest.

[<img src="https://img.youtube.com/vi/Lp6fq74zYBY/hqdefault.jpg" width="480" alt="Intro video">](https://youtu.be/Lp6fq74zYBY)

## Overview

You're deploying an AI-powered API that solves three business problems, scored by [FDEBench](docs/challenge/README.md).

The tasks are modeled on real customer engagements — noisy inputs, messy documents, multi-step workflows with constraints. Your solution needs to work, not just pass tests. FDEBench scores accuracy, latency, cost, resilience, and code quality. Judges also read your repo.

Have fun with it. Ship something you'd be proud to run in one of our top customer's business process.

| Task | Endpoint | What you're solving |
|------|----------|---------------------|
| Signal Triage | `POST /triage` | Classify and route noisy mission signals — 42% misroute rate today, 3+ hour delay |
| Document Extraction | `POST /extract` | Extract structured data from document images (receipts, invoices, forms, financial statements) |
| Workflow Orchestration | `POST /orchestrate` | Execute multi-step business workflows with real tool calls, constraints, and failure handling |

## Getting Started

1. **Read the challenge spec** → [docs/challenge/](docs/challenge/). Start here for the task contracts, the business context behind each endpoint, and how FDEBench scores your solution.
2. **Open the task briefs** → [docs/challenge/task1/](docs/challenge/task1/), [docs/challenge/task2/](docs/challenge/task2/), [docs/challenge/task3/](docs/challenge/task3/). Each folder describes one scored endpoint plus supporting context.
4. **Explore the data contracts** → [py/data/](py/data/). Schemas for all three tasks plus sample data for Task 1.
5. **Test locally** → [docs/eval/](docs/eval/). The eval harness shows the same Tier 1-style breakdown the challenge expects: per-task Resolution, Efficiency, Robustness, probes, and item counts.
6. **Deploy and submit** → [docs/submission/](docs/submission/). Push your code, deploy your API, submit at **[aka.ms/fde/hackathon](https://aka.ms/fde/hackaton)**.

## Start Here in 30 Minutes

1. Read [docs/challenge/README.md](docs/challenge/README.md) — the scoring formula and what you're building.
2. Pick a task folder — [task1/](docs/challenge/task1/), [task2/](docs/challenge/task2/), [task3/](docs/challenge/task3/) — and read the README + support docs.
3. Look at the data and schemas in [py/data/](py/data/).
4. Set up and run:

```bash
cd py
make setup   # install deps (once)
make run     # start the sample app on :8000 (terminal 1)
make eval    # score all 3 tasks (terminal 2)
```

That gives you the full local FDEBench breakdown — resolution, efficiency, robustness, probes, the works.

You can also score individual tasks: `make eval-triage`, `make eval-extract`, `make eval-orchestrate`.

## Repository Structure

```
├── docs/
│   ├── challenge/       # Task specs, scoring rubric, FDEBench framework
│   ├── data/            # Public datasets + JSON schemas (task1/, task2/, task3/)
│   ├── eval/            # Eval harness documentation
│   └── submission/      # Submission format and checklist
├── py/                  # Python workspace (uv)
│   ├── common/libs/     # Provided: FastAPI helpers, Pydantic models, fdebenchkit
│   ├── libs/            # Your libraries
│   └── apps/            # Your applications + eval harness
├── ts/                  # TypeScript workspace (pnpm)
│   ├── libs/            # Your libraries
│   └── apps/            # Your applications
└── infra/               # Infrastructure as Code (Pulumi + Azure)
    └── app/             # Your Pulumi program
```

## Development Environment

Work locally or in any cloud-hosted environment. A [devcontainer](.devcontainer/) is included if you want a pre-configured setup, but it's optional.

Requirements: Python 3.12+, Node.js 22+, [uv](https://docs.astral.sh/uv/), [pnpm](https://pnpm.io/)

```bash
# Python — install dependencies and fix namespace packages
cd py && make setup

# TypeScript (optional)
cd ts && pnpm install

# Pre-commit hooks (optional)
uvx pre-commit install
```

> **macOS note:** If you see `ModuleNotFoundError: No module named 'ms'` after a fresh `uv sync`, run `make setup` — it fixes a macOS quirk where hidden-file flags prevent Python from loading namespace packages.

## Rules

- **Five submission** per person. Make it count.
- Any language, any framework, any AI model.
- AI coding assistants (Copilot, Cursor, Claude) are encouraged.
- Must be deployed and callable via HTTPS.
- Documentation is required: `docs/architecture.md`, `docs/methodology.md`, `docs/evals.md`.

## How You're Scored — FDEBench

FDEBench is a two-tier benchmark. Tier 1 drives the public leaderboard. Tier 2 informs finalist selection.

### Tier 1 — Deterministic (Public Leaderboard)

Your deployed API is called with ~1,000 hidden instances **per task**. Scoring is fully deterministic — no LLM judges, no variance.

```
tier1_k = 0.50 x Resolution + 0.20 x Efficiency + 0.30 x Robustness
fdebench = mean(tier1_task1, tier1_task2, tier1_task3)
```

| Dimension | Weight | What it measures |
|-----------|--------|------------------|
| **Resolution** | 50% | Did you produce the right answer for the task-specific business outcome? |
| **Efficiency** | 20% | Did you do it fast enough and cheaply enough to be operationally usable? |
| **Robustness** | 30% | Does your API survive adversarial cases, malformed input, concurrency, and cold starts? |

Per-task Tier 1 scores are averaged into a composite **FDEBench** score (0-100).

For the scoring code, look at [py/common/libs/fdebenchkit/](py/common/libs/fdebenchkit/).

### Tier 2 — LLM Judge

Judges only (not public). Four agents read your repository and score engineering quality. These scores help judges differentiate finalists with similar Tier 1 scores.

| Agent | Weight | Focus |
|-------|--------|-------|
| Code Quality | 25% | Structure, types, error handling, testing, readability |
| Architecture Design | 30% | AI pipeline, decomposition, API design, tradeoff reasoning |
| AI Problem Solving | 25% | Prompt engineering, evaluation methodology, model/cost awareness |
| Engineering Maturity | 20% | Deployment readiness, config/secrets, observability, security |

Full scoring details: [docs/challenge/README.md](docs/challenge/README.md)

## Before You Submit

- `GET /health` returns HTTP 200
- `POST /triage` returns valid JSON per the output schema
- `POST /extract` returns valid JSON per the output schema
- `POST /orchestrate` returns valid JSON per the output schema
- `docs/architecture.md`, `docs/methodology.md`, `docs/evals.md` — substantive, not placeholder
- Deployed via HTTPS, handles 10+ concurrent requests, responds in under 30s
- Public GitHub repository with README explaining how to install, run, and test

See [docs/submission/](docs/submission/) for the full checklist, then submit at **[aka.ms/fde/hackathon](https://aka.ms/fde/hackaton)**.

## License

[MIT](LICENSE)
