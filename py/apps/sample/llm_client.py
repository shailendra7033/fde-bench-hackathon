"""Shared Azure OpenAI client with retry logic that honours Retry-After."""

import logging

from openai import AsyncAzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import APIStatusError, APITimeoutError, APIConnectionError

from config import settings

logger = logging.getLogger(__name__)

_client: AsyncAzureOpenAI | None = None


def get_client() -> AsyncAzureOpenAI:
    global _client
    if _client is None:
        _client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            timeout=settings.request_timeout,
            max_retries=0,  # we handle retries ourselves
        )
    return _client


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, APITimeoutError | APIConnectionError):
        return True
    if isinstance(exc, APIStatusError) and exc.status_code in (429, 500, 502, 503, 504):
        return True
    return False


def _should_retry(retry_state) -> bool:
    """Only retry on retryable errors, not 400 Bad Request."""
    exc = retry_state.outcome.exception()
    if exc is None:
        return False
    return _is_retryable(exc)


@retry(
    retry=_should_retry,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        "LLM call retry #%d after %s", retry_state.attempt_number, retry_state.outcome.exception()
    ),
)
async def chat_completion(
    *,
    messages: list[dict],
    response_format: dict | None = None,
    temperature: float = 0.0,
    max_tokens: int = 4096,
) -> str:
    """Call Azure OpenAI chat completion with retry logic."""
    client = get_client()
    kwargs: dict = {
        "model": settings.azure_openai_deployment,
        "messages": messages,
        "temperature": temperature,
        "max_completion_tokens": max_tokens,
    }
    if response_format is not None:
        kwargs["response_format"] = response_format

    resp = await client.chat.completions.create(**kwargs)
    content = resp.choices[0].message.content
    if content is None:
        return ""
    return content
