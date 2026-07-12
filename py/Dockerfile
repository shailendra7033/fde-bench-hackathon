FROM python:3.12-slim

WORKDIR /app

# Install dependencies directly (no uv needed in container)
RUN pip install --no-cache-dir \
    "fastapi>=0.115.0" \
    "uvicorn>=0.34.0" \
    "pydantic>=2.11.0" \
    "pydantic-settings>=2.0.0" \
    "email-validator>=2.0.0" \
    "openai>=1.60.0" \
    "httpx>=0.28.1" \
    "tenacity>=9.0.0"

# Copy the common models library and install it
COPY common/libs/models/ /tmp/models/
RUN pip install --no-cache-dir /tmp/models/ && rm -rf /tmp/models/

# Copy ONLY the application code (no .env, no __pycache__)
COPY apps/sample/main.py apps/sample/models.py apps/sample/config.py /app/
COPY apps/sample/llm_client.py apps/sample/triage_service.py /app/
COPY apps/sample/extract_service.py apps/sample/orchestrate_service.py /app/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Run with uvicorn (2 workers for concurrent burst handling)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
