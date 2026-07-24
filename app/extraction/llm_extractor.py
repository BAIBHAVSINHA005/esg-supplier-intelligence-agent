"""LLM-backed extraction of ESG indicators from retrieved document context."""

import json
import logging
from typing import Any

from openai import OpenAI
from pydantic import ValidationError

from app.extraction.prompts import SYSTEM_PROMPT, build_extraction_prompt
from app.extraction.schemas import (
    ExtractionResponse,
    IndicatorExtractionResult,
    make_error_result,
)


logger = logging.getLogger(__name__)


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
        self.client = client or OpenAI()

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
            A validated ``IndicatorExtractionResult`` on success. On an OpenAI,
            JSON parsing, or schema validation failure, returns the standard
            pipeline-compatible error result dictionary.
        """
        prompt = build_extraction_prompt(
            indicator_id=indicator_id,
            indicator_name=indicator_name,
            indicator_description=indicator_description,
            context=context,
        )

        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=SYSTEM_PROMPT,
                input=prompt,
            )
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
        except Exception:
            logger.exception("OpenAI extraction failed for indicator %s", indicator_id)

        return make_error_result(indicator_id=indicator_id, citation=citation)

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
