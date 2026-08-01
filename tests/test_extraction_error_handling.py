"""Focused regression coverage for extraction-error handling."""

import unittest
from types import SimpleNamespace
from unittest.mock import call, patch

import httpx
from openai import RateLimitError

from app.agent.nodes.analysis import analysis_layer
from app.agent.nodes.confidence import assess_confidence
from app.agent.state import make_initial_state
from app.extraction.llm_extractor import LLMExtractor
from app.extraction.schemas import make_error_result
from app.schemas.loader import get_indicators, load_schema


def _p6_results(climate_target_state: str) -> dict:
    """Build otherwise-disclosed Principle 6 results for deterministic tests."""
    indicators = get_indicators(load_schema("brsr_v2023"), "principle_6")
    results = {
        indicator_id: {
            "indicator_id": indicator_id,
            "state": "disclosed",
            "value": "Disclosed value",
            "evidence": "Disclosed in the uploaded BRSR filing.",
            "citation": "Page 1",
            "extraction_method": "llm",
            "confidence": 0.9,
            "uncertain": False,
        }
        for indicator_id in indicators
    }
    results["e6_climate_target"] = {
        **results["e6_climate_target"],
        "state": climate_target_state,
    }
    if climate_target_state == "extraction_error":
        results["e6_climate_target"].update(
            {
                "error_code": "rate_limit_error",
                "error_message": "Request limit reached.",
            }
        )
    return results


class ExtractionErrorHandlingTests(unittest.TestCase):
    """Verify failures are never interpreted as absent disclosures."""

    def _analysis_state(self, climate_target_state: str) -> dict:
        state = make_initial_state("Test Supplier")
        state.update(
            {
                "extracted_indicators": {
                    "principle_6": _p6_results(climate_target_state),
                },
                "extraction_errors": [],
            }
        )
        return state

    def test_genuine_not_found_produces_climate_target_gap(self) -> None:
        """A successful absence assessment must preserve the existing G-05 gap."""
        result = analysis_layer(self._analysis_state("not_found"))

        self.assertIn("G-05", {gap["gap_id"] for gap in result["gaps"]})

    def test_extraction_error_suppresses_climate_target_gap(self) -> None:
        """An extraction failure is unassessed, not evidence of a missing target."""
        result = analysis_layer(self._analysis_state("extraction_error"))

        self.assertNotIn("G-05", {gap["gap_id"] for gap in result["gaps"]})
        self.assertEqual(result["completeness_results"][0]["state"], "unassessed")

    def test_extraction_error_forces_low_confidence_and_hitl(self) -> None:
        """Any extraction failure requires manual review of the assessment."""
        state = self._analysis_state("extraction_error")
        analysis = analysis_layer(state)
        state.update(analysis)
        state["extraction_errors"] = [
            {
                "indicator_id": "e6_climate_target",
                "error_code": "rate_limit_error",
            }
        ]

        result = assess_confidence(state)

        self.assertEqual(result["confidence_level"], "low")
        self.assertTrue(result["hitl_flag"])

    def test_error_result_is_not_a_not_found_result(self) -> None:
        """Extractor fallbacks must retain a distinct, structured failure state."""
        result = make_error_result(
            "e6_climate_target",
            error_code="timeout_error",
            error_message="Request timed out.",
        )

        self.assertEqual(result["state"], "extraction_error")
        self.assertEqual(result["error_code"], "timeout_error")

    def test_rate_limit_error_retries_and_returns_successful_result(self) -> None:
        """A Retry-After delay is buffered before a successful retry."""
        response = _rate_limit_error(retry_after="5")
        client = _FakeClient(
            [
                response,
                _response_with_result("e6_climate_target"),
            ]
        )
        extractor = LLMExtractor(client=client)

        with patch("app.extraction.llm_extractor.time.sleep") as sleep:
            result = _extract_climate_target(extractor)

        self.assertEqual(result.indicator_id, "e6_climate_target")
        self.assertEqual(client.responses.calls, 2)
        sleep.assert_called_once_with(6.0)

    def test_rate_limit_error_returns_extraction_error_after_three_attempts(self) -> None:
        """Message-provided waits are buffered before retries are exhausted."""
        client = _FakeClient(
            [
                _rate_limit_error(message="Please try again in 7 seconds."),
            ]
            * 3
        )
        extractor = LLMExtractor(client=client)

        with patch("app.extraction.llm_extractor.time.sleep") as sleep:
            result = _extract_climate_target(extractor)

        self.assertEqual(result["state"], "extraction_error")
        self.assertEqual(result["error_code"], "rate_limit_error")
        self.assertEqual(client.responses.calls, 3)
        self.assertEqual(sleep.call_args_list, [call(8.0), call(8.0)])

    def test_rate_limit_error_uses_exponential_backoff_without_server_delay(self) -> None:
        """Fallback delays are exponential only when the server gives no delay."""
        error = _rate_limit_error(message="Rate limit reached")

        self.assertEqual(LLMExtractor._rate_limit_retry_delay(error, 1), 1.0)
        self.assertEqual(LLMExtractor._rate_limit_retry_delay(error, 2), 2.0)


class _FakeResponses:
    """Minimal Responses API fake that returns or raises queued outcomes."""

    def __init__(self, outcomes: list[object]) -> None:
        self._outcomes = outcomes
        self.calls = 0

    def create(self, **_kwargs: object) -> object:
        outcome = self._outcomes[self.calls]
        self.calls += 1
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class _FakeClient:
    """Minimal OpenAI client fake for retry tests."""

    def __init__(self, outcomes: list[object]) -> None:
        self.responses = _FakeResponses(outcomes)


def _rate_limit_error(
    retry_after: str | None = None,
    message: str = "Rate limit reached",
) -> RateLimitError:
    """Create an SDK-compatible 429 exception with optional server guidance."""
    request = httpx.Request("POST", "https://api.openai.com/v1/responses")
    headers = {"Retry-After": retry_after} if retry_after is not None else {}
    response = httpx.Response(
        429,
        headers=headers,
        request=request,
    )
    return RateLimitError(message, response=response, body={})


def _response_with_result(indicator_id: str) -> SimpleNamespace:
    """Return a minimal valid Responses API payload."""
    return SimpleNamespace(
        output_text=(
            '{"result":{"indicator_id":"'
            f'{indicator_id}","state":"disclosed","value":"2035",'
            '"evidence":"Target disclosed.","citation":"Page 1",'
            '"confidence":0.9}}'
        )
    )


def _extract_climate_target(extractor: LLMExtractor):
    """Run a stable extraction request shared by retry tests."""
    return extractor.extract(
        indicator_id="e6_climate_target",
        indicator_name="Climate Target",
        indicator_description="Emissions reduction target.",
        context="Target context.",
    )


if __name__ == "__main__":
    unittest.main()
