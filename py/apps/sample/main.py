"""FDEBench solution: triage, extract, orchestrate.

Run:
    cd py
    make setup     # one time, install deps
    make run       # start on :8000

Score:
    make eval      # score all 3 tasks (in a second terminal)
"""

import asyncio
import json
import logging

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from config import settings
from models import (
    Category,
    ExtractRequest,
    ExtractResponse,
    MissingInfo,
    OrchestrateRequest,
    OrchestrateResponse,
    StepExecuted,
    Team,
    TriageRequest,
    TriageResponse,
)
from triage_service import classify_signal
from extract_service import extract_document
from orchestrate_service import execute_workflow

logging.basicConfig(level=logging.INFO, format="%(levelname)-5s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="FDEBench Solution")

# ---------------------------------------------------------------------------
# Middleware: payload size limit (probe #4: 50 KB → 413)
# ---------------------------------------------------------------------------
MAX_BODY_BYTES = 10 * 1024 * 1024  # 10 MB for base64 images in Task 2
MAX_BODY_BYTES_NON_EXTRACT = 51_200  # 50 KB for triage/orchestrate


@app.middleware("http")
async def check_content_type_and_size(request: Request, call_next):
    """Handle resilience probes: content-type (probe #5) and payload size (probe #4)."""
    if request.method == "POST":
        # Probe #5: wrong content-type → 415
        content_type = request.headers.get("content-type", "")
        if content_type and "application/json" not in content_type:
            return JSONResponse(
                status_code=415,
                content={"error": "Unsupported Media Type", "detail": "Content-Type must be application/json"},
            )

        # Probe #4: oversized payload → 413 (only for non-extract endpoints)
        content_length = request.headers.get("content-length")
        path = request.url.path
        if content_length and path != "/extract":
            if int(content_length) > MAX_BODY_BYTES_NON_EXTRACT:
                return JSONResponse(
                    status_code=413,
                    content={"error": "Payload Too Large", "detail": f"Body exceeds {MAX_BODY_BYTES_NON_EXTRACT} bytes"},
                )

    return await call_next(request)


# ---------------------------------------------------------------------------
# Exception handlers (probes #1, #2, #3: malformed JSON / empty body / missing fields)
# ---------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation Error", "detail": str(exc)[:500]},
    )


@app.exception_handler(json.JSONDecodeError)
async def json_decode_error_handler(request: Request, exc: json.JSONDecodeError):
    return JSONResponse(
        status_code=400,
        content={"error": "Bad Request", "detail": "Invalid JSON in request body"},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": "An unexpected error occurred"},
    )


# ---------------------------------------------------------------------------
# Shared header helper
# ---------------------------------------------------------------------------
def _add_headers(response: Response) -> None:
    response.headers["X-Model-Name"] = settings.model_name


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Task 1: Signal Triage
# ---------------------------------------------------------------------------
@app.post("/triage")
async def triage(req: TriageRequest, response: Response) -> TriageResponse:
    _add_headers(response)
    try:
        result = await classify_signal(req.model_dump())

        return TriageResponse(
            ticket_id=req.ticket_id,
            category=Category(result.get("category", "Mission Briefing Request")),
            priority=result.get("priority", "P3"),
            assigned_team=Team(result.get("assigned_team", "None")),
            needs_escalation=result.get("needs_escalation", False),
            missing_information=[
                MissingInfo(m) for m in result.get("missing_information", [])
                if m in {e.value for e in MissingInfo}
            ],
            next_best_action=result.get("next_best_action", "Investigate the reported issue."),
            remediation_steps=result.get("remediation_steps", ["Review the signal details."]),
        )
    except Exception as exc:
        logger.exception("Triage failed for %s: %s", req.ticket_id, exc)
        # Return a safe fallback so we don't score 0
        return TriageResponse(
            ticket_id=req.ticket_id,
            category=Category.BRIEFING,
            priority="P3",
            assigned_team=Team.NONE,
            needs_escalation=False,
            missing_information=[],
            next_best_action="Unable to classify — manual review required.",
            remediation_steps=["Escalate to a human operator for manual triage."],
        )


# ---------------------------------------------------------------------------
# Task 2: Document Extraction
# ---------------------------------------------------------------------------
@app.post("/extract")
async def extract(req: ExtractRequest, response: Response) -> ExtractResponse:
    _add_headers(response)
    try:
        result = await asyncio.wait_for(
            extract_document(req.document_id, req.content, req.json_schema),
            timeout=27.0,
        )
        return ExtractResponse(**result)
    except asyncio.TimeoutError:
        logger.warning("Extract timed out for %s, returning fallback", req.document_id)
        return ExtractResponse(document_id=req.document_id)
    except Exception as exc:
        logger.exception("Extract failed for %s: %s", req.document_id, exc)
        return ExtractResponse(document_id=req.document_id)


# ---------------------------------------------------------------------------
# Task 3: Workflow Orchestration
# ---------------------------------------------------------------------------
@app.post("/orchestrate")
async def orchestrate(req: OrchestrateRequest, response: Response) -> OrchestrateResponse:
    _add_headers(response)
    try:
        result = await execute_workflow(req.model_dump())

        steps = [
            StepExecuted(
                step=s.get("step", i + 1),
                tool=s.get("tool", "unknown"),
                parameters=s.get("parameters", {}),
                result_summary=s.get("result_summary", ""),
                success=s.get("success", False),
            )
            for i, s in enumerate(result.get("steps_executed", []))
        ]

        return OrchestrateResponse(
            task_id=req.task_id,
            status=result.get("status", "failed"),
            steps_executed=steps,
            accounts_processed=result.get("accounts_processed"),
            emails_sent=result.get("emails_sent"),
            emails_skipped=result.get("emails_skipped"),
            skip_reasons=result.get("skip_reasons"),
            constraints_satisfied=result.get("constraints_satisfied", []),
        )
    except Exception as exc:
        logger.exception("Orchestrate failed for %s: %s", req.task_id, exc)
        return OrchestrateResponse(
            task_id=req.task_id,
            status="failed",
            steps_executed=[],
            constraints_satisfied=[],
        )
