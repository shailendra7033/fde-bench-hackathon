# Azure Architecture Design for FDEBench API Service

## 1. Objective

Build and deploy a production-style API service on Azure that exposes four endpoints:
- GET /health
- POST /triage
- POST /extract
- POST /orchestrate

The system must be accurate, resilient, observable, and deployment-ready for the FDEBench evaluation.

---

## 2. System Overview

The solution will be implemented as a Python FastAPI application deployed to Azure Container Apps.

The application will follow a layered design:
- API layer: request handling, validation, routing, HTTP error responses
- Service layer: business logic for triage, extraction, and orchestration
- Integration layer: Azure OpenAI (text + vision), telemetry, and secrets access

This separation ensures the app is testable, maintainable, and easy for judges to review.

---

## 3. Azure Component Design

### 3.1 Azure Container Apps
The FastAPI app will run as a container in Azure Container Apps.

Responsibilities:
- receive inbound HTTP traffic
- expose the health and task endpoints
- scale based on traffic demand
- perform health and readiness probes

Why this is suitable:
- low operational overhead
- good fit for stateless API workloads
- simple deployment story for a hackathon submission

### 3.2 Azure Container Registry
The container image will be stored in Azure Container Registry.

Responsibilities:
- host the application image
- support CI/CD-style deployment updates

### 3.3 Azure Key Vault
Secrets and configuration values will be stored in Azure Key Vault.

Responsibilities:
- store model API keys
- store connection strings and any sensitive deployment values

### 3.4 Azure OpenAI (via Azure AI Foundry)
Azure AI Foundry will be used as the model platform, giving access to multiple model deployments for comparison and optimization.

Primary model target: gpt-5.4-nano (Nano tier, 100% cost score) — selected based on Foundry benchmark comparison (see submission-methodology.md). Fallback: gpt-4.1-mini (Mini tier, 90%) if nano lacks vision support for Task 2.

Responsibilities:
- triage classification and judgment
- urgency and escalation reasoning
- orchestration planning and tool selection
- document extraction via vision capability

Design note:
- the application depends on an abstraction layer rather than directly coupling to Azure OpenAI internals
- this allows model swapping for per-task optimization
- must implement custom retry-with-backoff that honors Retry-After headers (SDK does not do this for AOAI throttling)

### 3.5 Azure AI Document Intelligence — NOT USED

> **Decision: Do not use Document Intelligence for this challenge.**
>
> The challenge sends base64-encoded PNG images directly to the `/extract` endpoint. A vision-capable model handles extraction end-to-end. Adding Document Intelligence would:
> - add unnecessary latency (extra network hop + processing time)
> - add infrastructure complexity (extra Azure resource, credentials, retry logic)
> - not improve accuracy — the vision model already reads the image and the dynamic `json_schema`
> - hurt the efficiency score without a proportional resolution gain
>
> If a future iteration shows the vision model struggling on specific document types (e.g., deeply nested tables in handwritten scans), Document Intelligence could be re-evaluated as a preprocessing step.

### 3.6 Application Insights
Application Insights will provide telemetry for:
- request traces
- latency measurements
- error logging
- dependency timing for AI and document services

### 3.7 Managed Identity
Managed identity will be used wherever possible for Azure authentication.

Benefits:
- no hardcoded secrets in source code
- simpler Azure deployment model
- better production posture

---

## 4. Request Flow

### 4.1 Health Endpoint
Flow:
1. Client calls GET /health
2. FastAPI returns service status
3. Azure health probes can be used for liveness and readiness

### 4.2 Triage Endpoint
Flow:
1. Client submits a signal payload to POST /triage
2. FastAPI validates the request body
3. The request is routed to the triage service
4. The triage service builds the input prompt and calls the LLM adapter
5. The response is normalized into a constrained schema
6. The API returns a structured JSON result and observability headers

### 4.3 Extraction Endpoint
Flow:
1. Client submits a document payload to POST /extract
2. The payload contains: document_id, content (base64-encoded PNG), content_format ("image_base64"), json_schema (varies per document)
3. The extraction service decodes the base64 content
4. The service sends the image to a vision-capable model along with the json_schema describing expected fields
5. The response is parsed and normalized into the schema-defined structure
6. The service returns document_id + all extracted fields matching the json_schema
7. Returns null for fields that cannot be extracted (never hallucinate)

### 4.4 Orchestration Endpoint
Flow:
1. Client submits a workflow request to POST /orchestrate
2. The payload contains: task_id, goal, available_tools (with endpoints), constraints, mock_service_url
3. The orchestration service plans the execution using the model
4. The service ACTUALLY calls each tool endpoint via HTTP (real calls, not simulated)
5. Tool responses are validated and state is tracked across steps
6. On tool failure, the service handles errors gracefully (retry, skip, partial)
7. The service returns: task_id, status, steps_executed, constraints_satisfied, and any task-specific counters

---

## 5. Service Structure

The repository should be structured as follows:

```text
app/
  api/
    routes.py
    dependencies.py
    exceptions.py
  core/
    config.py
    logging.py
    security.py
    telemetry.py
  schemas/
    common.py
    triage.py
    extract.py
    orchestrate.py
  services/
    triage_service.py
    extract_service.py
    orchestrate_service.py
  integrations/
    llm_client.py
  prompts/
    triage_prompt.txt
    orchestrate_prompt.txt
  tests/
    test_triage.py
    test_extract.py
    test_orchestrate.py
  Dockerfile
  requirements.txt
  README.md
```

This structure ensures clear separation between transport, business logic, integrations, and tests.

---

## 6. Failure Handling and Resilience Design

The service must explicitly handle the seven benchmark probes.

### 6.1 Expected behaviors
- Malformed JSON -> return 400
- Empty body -> return 400 or 422
- Missing required fields -> return 400 or 422, or use safe defaults where allowed
- Oversized payload -> return 413
- Wrong content type -> return 415
- Concurrent burst -> maintain stability and return valid responses for the majority of requests
- Cold start -> the app should recover and serve a valid response after idle time

### 6.2 Implementation strategy
- enforce a request body size limit
- validate content type before parsing JSON
- use Pydantic models for strict validation
- catch JSON decode errors and return structured error responses
- set timeouts on model calls
- add retry logic only where it is safe and useful
- use structured error payloads with:
  - error_code
  - message
  - details
  - request_id
- ensure the app does not crash on invalid input

### 6.3 Operational resilience
- use health checks for readiness and liveness
- log requests with correlation IDs
- expose latency and model metadata headers
- fail gracefully rather than returning raw server traces

---

## 7. Observability and Response Headers

Every response should include enough metadata for production monitoring and benchmark compliance.

Recommended headers:
- X-Request-Id
- X-Model-Name
- X-Latency-Ms
- X-Token-Count

These help with both debugging and trust in the API.

---

## 8. Model Strategy

The model decision should be made with accuracy, cost, and latency in mind.

### 8.1 Principles
- use the smallest model that still performs well for the task
- use stronger models only for complex or ambiguous cases
- keep model usage behind an abstraction layer

### 8.2 Recommended approach (with exact scoring data)

The efficiency scoring uses the X-Model-Name header to determine cost tier:
- Nano tier (100%): gpt-5-nano, gpt-4.1-nano, phi-4
- Mini tier (90%): gpt-4.1-mini, gpt-4o-mini, gpt-5-mini
- Standard tier (75%): gpt-4.1, gpt-4o, o4-mini
- Full tier (50%): o3, gpt-5-pro
- Premium tier (30%): o1, claude-opus

Per-task latency thresholds (P95):
- Triage: best ≤ 1,500ms, worst ≥ 4,200ms
- Extract: best ≤ 7,100ms, worst ≥ 19,000ms
- Orchestrate: best ≤ 1,500ms, worst ≥ 8,000ms

### 8.3 Recommended model per task

| Task | Primary model | Tier | Cost score | Reasoning |
|---|---|---|---|---|
| Triage | gpt-5.4-nano | Nano | 100% | Higher quality index (0.64 vs 0.59) and faster throughput (177 vs 125 tok/s) than gpt-4.1-mini. Nano tier = best cost score |
| Extract | gpt-5.4-nano (if vision-capable) or gpt-4.1-mini (fallback) | Nano / Mini | 100% / 90% | Vision capability must be confirmed. If nano lacks vision, fall back to gpt-4.1-mini which is confirmed vision-capable |
| Orchestrate | gpt-5.4-nano | Nano | 100% | Better reasoning quality for constraint compliance (40% of T3 resolution). Faster throughput helps meet 1,500ms threshold |

### 8.4 Upgrade path
If Mini-tier accuracy is insufficient on a specific task:
- Upgrade to Standard (gpt-4.1) for that task only
- Accept the cost score drop from 90% → 75%
- Only do this if it produces a measurable resolution improvement that outweighs the 15% cost penalty

### 8.5 AOAI retry strategy (critical)
- The OpenAI SDK does NOT honor Azure OpenAI Retry-After headers by default
- We must wrap AOAI calls in custom retry logic that reads the Retry-After header
- Per-attempt timeout should be ~25-30s so two retries fit inside the platform's 60s deadline
- A 429 that can't be recovered from scores 0 on all dimensions for that item


---

## 9. Deployment Flow

The deployment lifecycle should be:

1. develop locally
2. run unit and integration tests
3. build the Docker image
4. push the image to Azure Container Registry
5. deploy to Azure Container Apps
6. configure environment variables from Azure Key Vault
7. enable Application Insights
8. verify application health and endpoint behavior

### Deployment sequence
```text
Local development -> Docker build -> ACR push -> Container Apps deploy -> Key Vault secrets -> health checks -> smoke tests
```

---

## 10. Security and Configuration

Security should be designed in from the start.

Recommended controls:
- managed identity for Azure resource access
- no secrets in repository files
- environment variables for runtime config
- separate dev/prod configuration paths
- restricted CORS and ingress policy where applicable

---

## 11. Final Design Position

This architecture is suitable because it balances:
- Azure-native deployment
- strong API contract design
- robust fault handling
- low-friction implementation
- clear engineering review quality

It is practical enough for a hackathon while still looking production-ready.
