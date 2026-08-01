"""LLM-backed extraction of ESG indicators from retrieved document context."""

import json
import logging
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

from openai import OpenAI, RateLimitError
from pydantic import ValidationError

from app.extraction.prompts import SYSTEM_PROMPT, build_extraction_prompt
from app.extraction.schemas import (
    ExtractionResponse,
    IndicatorExtractionResult,
    make_error_result,
)


logger = logging.getLogger(__name__)


_MAX_RATE_LIMIT_ATTEMPTS = 3
_RATE_LIMIT_BACKOFF_SECONDS = 1.0
_RATE_LIMIT_SAFETY_BUFFER_SECONDS = 1.0
_RETRY_DELAY_PATTERN = re.compile(
    r"(?:try\s+again\s+in|retry(?:ing)?\s+in|wait(?:\s+for)?)[^\d]*"
    r"(\d+(?:\.\d+)?)\s*(milliseconds?|ms|seconds?|secs?|s|minutes?|mins?|m)",
    re.IGNORECASE,
)


class LLMExtractor:
    """Extract and validate one ESG indicator at a time with an OpenAI model.

    A client is created once when the extractor is initialized and is reused for
    every extraction request made through that instance.
    """

    def __init__(
        self,
        model: str = "gpt-4.1",
        client: OpenAI | None = None,
    ) -> None:
        """Initialize the extractor with a model and reusable OpenAI client.

        Args:
            model: OpenAI model identifier used for extraction requests.
            client: Optional client injection, primarily useful for testing.
        """
        self.model = model
        # Disable SDK retries so this extractor retries only RateLimitError.
        self.client = client or OpenAI(max_retries=0)

    def extract(
        self,
        *,
        indicator_id: str,
        indicator_name: str,
        indicator_description: str,
        context: str,
        citation: str = "",
    ) -> IndicatorExtractionResult | dict[str, Any]:
        """Extract one indicator from context and validate the model response.

        Args:
            indicator_id: Unique identifier of the requested indicator.
            indicator_name: Human-readable indicator name.
            indicator_description: Definition used to assess disclosure.
            context: Retrieved document text relevant to the indicator.
            citation: Fallback citation returned if extraction fails.

        Returns:
            A validated ``IndicatorExtractionResult`` on success, including
            optional semantic flags when supplied by the model. On an OpenAI,
            JSON parsing, or schema validation failure, returns the standard
            pipeline-compatible error result dictionary.
        """
        prompt = build_extraction_prompt(
            indicator_id=indicator_id,
            indicator_name=indicator_name,
            indicator_description=indicator_description,
            context=context,
        )

        for attempt in range(1, _MAX_RATE_LIMIT_ATTEMPTS + 1):
            try:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=SYSTEM_PROMPT,
                    input=prompt,
                )
                break
            except RateLimitError as exc:
                if attempt == _MAX_RATE_LIMIT_ATTEMPTS:
                    logger.warning(
                        "OpenAI rate limit for %s after %s attempts",
                        indicator_id,
                        attempt,
                    )
                    return make_error_result(
                        indicator_id=indicator_id,
                        citation=citation,
                        error_code=self._error_code_for(exc),
                        error_message=str(exc),
                    )

                delay = self._rate_limit_retry_delay(exc, attempt)
                logger.warning(
                    "OpenAI rate limit for %s; retrying attempt %s/%s in %.1fs",
                    indicator_id,
                    attempt + 1,
                    _MAX_RATE_LIMIT_ATTEMPTS,
                    delay,
                )
                time.sleep(delay)

        try:
            json_response = self._extract_json_object(response.output_text)
            payload = json.loads(json_response)
            validated_response = ExtractionResponse.model_validate(payload)
            return validated_response.result
        except (
            json.JSONDecodeError,
            ValidationError,
            AttributeError,
            TypeError,
            ValueError,
        ) as exc:
            logger.warning(
                "LLM extraction failed for indicator %s: %s",
                indicator_id,
                exc,
            )
            return make_error_result(
                indicator_id=indicator_id,
                citation=citation,
                error_code=self._error_code_for(exc),
                error_message=str(exc),
            )
        except Exception as exc:
            logger.exception("OpenAI extraction failed for indicator %s", indicator_id)
            return make_error_result(
                indicator_id=indicator_id,
                citation=citation,
                error_code=self._error_code_for(exc),
                error_message=str(exc),
            )

    @staticmethod
    def _error_code_for(exc: Exception) -> str:
        """Return a stable error code without coupling to OpenAI exception classes."""
        if isinstance(exc, json.JSONDecodeError):
            return "json_parse_error"
        if isinstance(exc, ValidationError):
            return "schema_validation_error"

        exception_name = type(exc).__name__.lower()
        if "rate" in exception_name and "limit" in exception_name:
            return "rate_limit_error"
        if "auth" in exception_name or "permission" in exception_name:
            return "authentication_error"
        if "timeout" in exception_name:
            return "timeout_error"
        if "connection" in exception_name:
            return "connection_error"
        if isinstance(exc, (AttributeError, TypeError, ValueError)):
            return "response_processing_error"
        return "api_error"

    @staticmethod
    def _rate_limit_retry_delay(exc: RateLimitError, attempt: int) -> float:
        """Return the server-provided delay or an exponential fallback delay."""
        response = getattr(exc, "response", None)
        headers = getattr(response, "headers", {})
        delays = []

        for header_name in (
            "retry-after",
            "x-ratelimit-reset-requests",
            "x-ratelimit-reset-tokens",
        ):
            delay = LLMExtractor._parse_retry_after(
                LLMExtractor._header_value(headers, header_name)
            )
            if delay is not None:
                delays.append(delay)

        message_delay = LLMExtractor._parse_retry_delay_from_message(str(exc))
        if message_delay is not None:
            delays.append(message_delay)

        for attribute in ("retry_after", "wait_time", "retry_delay"):
            delay = LLMExtractor._parse_retry_after(getattr(exc, attribute, None))
            if delay is not None:
                delays.append(delay)

        if delays:
            return max(delays) + _RATE_LIMIT_SAFETY_BUFFER_SECONDS

        return _RATE_LIMIT_BACKOFF_SECONDS * (2 ** (attempt - 1))

    @staticmethod
    def _header_value(headers: object, header_name: str) -> object:
        """Read a response header from case-insensitive or plain mappings."""
        if not hasattr(headers, "get"):
            return None

        value = headers.get(header_name)
        if value is not None:
            return value

        if hasattr(headers, "items"):
            for key, value in headers.items():
                if str(key).lower() == header_name:
                    return value
        return None

    @staticmethod
    def _parse_retry_after(value: object) -> float | None:
        """Parse an HTTP Retry-After header as seconds from now."""
        delay = LLMExtractor._coerce_delay(value)
        if delay is not None:
            return delay

        delay = LLMExtractor._parse_duration(value)
        if delay is not None:
            return delay

        if not isinstance(value, str):
            return None

        try:
            retry_at = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None

        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())

    @staticmethod
    def _parse_retry_delay_from_message(message: str) -> float | None:
        """Extract the server's requested wait from a rate-limit message."""
        match = _RETRY_DELAY_PATTERN.search(message)
        if match is None:
            return None
        return LLMExtractor._parse_duration("".join(match.groups()))

    @staticmethod
    def _parse_duration(value: object) -> float | None:
        """Parse a compact duration such as ``6.2s`` or ``500ms``."""
        if not isinstance(value, str):
            return None

        match = re.fullmatch(
            r"\s*(\d+(?:\.\d+)?)\s*(milliseconds?|ms|seconds?|secs?|s|minutes?|mins?|m)\s*",
            value,
            re.IGNORECASE,
        )
        if match is None:
            return None

        amount = float(match.group(1))
        unit = match.group(2).lower()
        if unit in {"millisecond", "milliseconds", "ms"}:
            return amount / 1000
        if unit in {"minute", "minutes", "min", "mins", "m"}:
            return amount * 60
        return amount

    @staticmethod
    def _coerce_delay(value: object) -> float | None:
        """Return a non-negative numeric delay, if supplied."""
        try:
            delay = float(value)
        except (TypeError, ValueError):
            return None
        return delay if delay >= 0 else None

    @staticmethod
    def _extract_json_object(response_text: str) -> str:
        """Return the first complete JSON object embedded in model output.

        The Responses API output may include prose or Markdown code fences even
        when JSON-only output is requested. This scanner finds a balanced JSON
        object while correctly ignoring braces inside quoted JSON strings.

        Raises:
            ValueError: If no complete JSON object is present in ``response_text``.
        """
        if not isinstance(response_text, str):
            raise ValueError("LLM response text must be a string")

        start = response_text.find("{")
        if start == -1:
            raise ValueError("LLM response did not contain a JSON object")

        depth = 0
        in_string = False
        escaped = False

        for index in range(start, len(response_text)):
            character = response_text[index]

            if in_string:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == '"':
                    in_string = False
                continue

            if character == '"':
                in_string = True
            elif character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
                if depth == 0:
                    return response_text[start : index + 1]

        raise ValueError("LLM response contained an incomplete JSON object")

    def extract_indicator(
        self,
        *,
        indicator_id: str,
        indicator_name: str,
        indicator_description: str,
        context: str,
        citation: str = "",
    ) -> IndicatorExtractionResult | dict[str, Any]:
        """Compatibility alias for :meth:`extract` with the same contract."""
        return self.extract(
            indicator_id=indicator_id,
            indicator_name=indicator_name,
            indicator_description=indicator_description,
            context=context,
            citation=citation,
        )
