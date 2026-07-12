"""Task 2: Document Extraction — vision model service."""

import json
import logging

from llm_client import chat_completion

logger = logging.getLogger(__name__)

EXTRACT_SYSTEM_PROMPT = """Extract structured data from document images. You receive an image and a JSON schema describing expected output fields.

RULES:
1. Read the json_schema — it defines exactly what fields to extract and their types.
2. Extract every field. Return null for fields you cannot read. NEVER hallucinate.
3. Preserve original text formatting (capitalization, punctuation).
4. Numbers: return as numbers. Parse "$1,234.56" → 1234.56, "10%" → 10.
5. Dates: extract exactly as written.
6. Tables: return as arrays of objects per schema.
7. Nested objects: follow schema nesting exactly.
8. Booleans: true/false. Arrays: all items found.

OUTPUT: JSON with document_id and all schema fields. No explanations."""


async def extract_document(document_id: str, content_b64: str, json_schema_str: str | None) -> dict:
    """Extract structured data from a document image using a vision model."""
    schema_instruction = ""
    if json_schema_str:
        schema_instruction = f"\n\nExtract fields according to this JSON schema:\n{json_schema_str}"

    user_content: list[dict] = [
        {
            "type": "text",
            "text": f"Extract all data from this document image.{schema_instruction}\n\nReturn JSON with document_id: \"{document_id}\" and all extracted fields.",
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{content_b64}"},
        },
    ]

    result = await chat_completion(
        messages=[
            {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
        max_tokens=8192,
    )

    parsed = json.loads(result)
    parsed["document_id"] = document_id
    return parsed
