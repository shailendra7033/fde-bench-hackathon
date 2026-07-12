# Azure Decisions and Implementation Strategy

## 1. Should we resolve these questions before coding?

Yes, but only the ones that affect architecture and deployment. We do not need to lock every detail before starting.

The best approach is:
- decide the high-impact choices now
- keep the implementation flexible for lower-impact choices

### High-impact decisions
1. Which Azure AI service will power the model layer?
2. Whether we will use Azure Container Apps directly for deployment
3. Whether we will build and test locally with a native Python workflow or a container workflow

### Lower-impact decisions (already resolved by challenge repo)
1. ~~The exact shape of the orchestration tool catalog~~ — **Resolved: tools are dynamic, provided per-request in `available_tools`**
2. ~~Whether extraction accepts uploads or URLs first~~ — **Resolved: always `image_base64` (base64-encoded PNG)**
3. ~~The exact schema details for the output payloads~~ — **Resolved: schemas are fully defined in `py/data/task{1,2,3}/output_schema.json`**

We can implement the first version with a simple abstraction layer so these details can be adjusted later without rewriting the app.

---

## 2. Azure AI Foundry vs Azure OpenAI direct

### Option A: Azure OpenAI directly

**What it is**
- direct access to Azure-hosted LLM deployments
- simplest and fastest integration path
- good fit for a hackathon API service

**Pros**
- straightforward SDK integration
- fast to implement
- lower operational complexity
- enough for triage, orchestration, and structured prompting
- easy to deploy and test from a single API service

**Cons**
- less built-in experimentation and evaluation tooling
- fewer management features than a broader platform

### Option B: Azure AI Foundry

**What it is**
- a broader AI platform experience for model management, evaluation, prompt flow, and experimentation
- useful when you want a more complete MLOps-style workflow

**Pros**
- stronger model experimentation story
- good for prompt iteration and evaluation
- useful if you want richer AI workflow management

**Cons**
- more setup overhead
- less necessary for this challenge if the judge only cares about the live API
- can slow down initial implementation

### Recommendation
For this hackathon, I recommend using Azure AI Foundry as the primary model platform.

Why:
- it gives us access to multiple model options for comparison
- it directly supports the efficiency objective because we can benchmark smaller vs larger models
- it fits the challenge’s emphasis on cost, latency, and model selection strategy
- it keeps the solution aligned with the Azure ecosystem and the Microsoft-first nature of the hackathon

We can still keep the app architecture clean so that the model layer remains swappable, but the default integration path should be through Azure AI Foundry.

---

## 3. What the hackathon judge is likely to care about

The judge is likely to test:
- whether your API is reachable
- whether it returns the right structured output
- whether it handles bad input correctly
- whether it is deployed and stable

They are not likely to care whether your model layer was wired through Foundry or directly through Azure OpenAI, as long as the endpoint works and behaves correctly.

So the practical decision is:
- use the simplest path that works well
- keep the code architecture clean enough to evolve later

---

## 4. Clarification of the orchestration question

> **This question is already answered by the challenge repo.**

The `available_tools` array is provided dynamically in every `/orchestrate` request. Each tool includes its `name`, `description`, `endpoint`, and `parameters`. The endpoint URLs are rewritten at eval time by the platform to point at its mock service.

**There is no tool catalog to build.** The orchestrator must:
1. Read the `available_tools` from the request
2. Use the LLM to plan which tools to call and in what order
3. Actually call each tool's `endpoint` via HTTP
4. Track results and constraints

A fixed catalog of generic tools (lookup, summarize, validate) would be **wrong** — it would ignore the actual tools the platform sends. The original recommendation below was written before the challenge repo was fully analyzed.

<details>
<summary>Original (superseded) recommendation</summary>

### Fixed tool catalog
A fixed catalog means:
- a small predefined set of tools or actions
- easier to test and reason about
- more reliable for the hackathon

Example:
- lookup
- summarize
- validate
- transform
- failover

### Dynamic tool registry
A dynamic registry means:
- tools are discovered or configured at runtime
- more flexible, but more complex
- more engineering overhead

### Recommendation
Use a fixed tool catalog first.

Why:
- it is faster to implement
- it reduces failure modes
- it is easier to review and test
- it is enough for the first version of the challenge

We can later expand it into a registry pattern if needed.

</details>

---

## 5. Local development without Docker Desktop

Since Docker Desktop is not available, we should not depend on it for development.

### Best option: run the app natively
Use:
- Python virtual environment
- FastAPI
- Uvicorn
- pytest

This is the simplest and most reliable local path.

### Deployment without local Docker Desktop
We can still deploy to Azure Container Apps without using Docker Desktop locally by using one of these approaches:

#### Option 1: Build remotely from source in Azure
Use Azure Container Apps build-from-source deployment.

Benefits:
- no local Docker needed
- easier for a Windows environment
- good for a hackathon workflow

#### Option 2: Use Podman as a local container engine
If container-based local testing is important, Podman can be a substitute.

Benefits:
- container-based workflow without Docker Desktop
- closer to Docker behavior

Tradeoffs:
- extra setup
- not always as smooth on Windows

### Recommendation
For this project, I recommend:
- use native Python for local development when rapid iteration is needed
- use Podman for local container-based validation when we want to mirror the Azure deployment environment more closely
- deploy to Azure Container Apps using Azure build-from-source or CI/CD

This gives us a practical workflow without Docker Desktop while still allowing container-based testing and debugging.

---

## 6. Final recommendation

### Recommended stack decision
- Use Python + FastAPI
- Use Azure AI Foundry as the primary model platform
- Use a vision-capable model (gpt-5.4-nano or gpt-4.1-mini) for document extraction — **NOT Azure AI Document Intelligence**
- Deploy to Azure Container Apps
- Use Azure Key Vault for secrets
- Use Application Insights for telemetry
- Develop locally without Docker Desktop using native Python and uvicorn

> **Note:** Azure AI Document Intelligence was originally listed here but has been removed. The challenge sends base64-encoded images directly to the `/extract` endpoint, and a vision-capable LLM handles the extraction end-to-end. Adding Document Intelligence would add latency and complexity without improving accuracy.

### Why this is the best first choice
- fastest path to a working solution
- strongest fit for the hackathon evaluation
- simpler to implement and debug
- still Azure-native and production-looking

### What we should not overcomplicate
- we do not need Azure AI Foundry to win this challenge
- we do not need Azure AI Document Intelligence — vision model handles extraction directly
- we do not need a dynamic orchestration registry — the challenge already provides tools dynamically in each request
- we do not need local Docker if native Python works well

If we later need richer AI workflow features, we can evolve the design without rewriting the core service.
