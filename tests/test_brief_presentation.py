"""Sprint 4 regression coverage for business-intelligence presentation."""

import unittest

from app.agent.nodes.brief import compile_brief
from app.agent.nodes.confidence import assess_confidence
from app.agent.state import make_initial_state


class BriefPresentationTests(unittest.TestCase):
    """Verify additive narratives reuse upstream pipeline outputs."""

    def _brief_state(self, scope3_level: str) -> dict:
        state = make_initial_state("Example Supplier")
        state.update(
            {
                "confidence_level": "medium",
                "confidence_directive": "Manually verify uncertain fields.",
                "confidence_explanation": (
                    "Overall confidence is Medium because extraction coverage was 75%."
                ),
                "scope3_verdict": {"level": scope3_level},
                "completeness_results": [
                    {
                        "essential_total": 8,
                        "essential_disclosed": 5,
                        "essential_partial": 1,
                    }
                ],
                "gaps": [
                    {
                        "gap_id": "G-01",
                        "severity": "critical",
                    }
                ],
                "recommended_actions": [
                    {
                        "action": "Request a complete Scope 3 inventory.",
                    }
                ],
                "followup_questions": [
                    {
                        "rank": 1,
                        "linked_gap_id": "G-01",
                        "question": "Please provide a quantified Scope 3 inventory.",
                    }
                ],
            }
        )
        return state

    def test_adds_executive_summary_without_changing_existing_sections(self) -> None:
        state = self._brief_state("claim_only")

        brief = compile_brief(state)["brief"]

        self.assertEqual(brief["scope3_verdict"], state["scope3_verdict"])
        self.assertEqual(brief["gaps"], state["gaps"])
        self.assertEqual(brief["recommended_actions"], state["recommended_actions"])
        self.assertEqual(brief["followup_questions"], state["followup_questions"])
        self.assertIn("Example Supplier", brief["executive_summary"])
        self.assertIn("6 of 8 essential indicators", brief["executive_summary"])
        self.assertIn("targeted follow-up", brief["executive_summary"])
        self.assertNotIn(
            "Request a complete Scope 3 inventory", brief["executive_summary"]
        )
        self.assertNotIn(
            state["followup_questions"][0]["question"], brief["executive_summary"]
        )
        self.assertNotIn(
            state["recommended_actions"][0]["action"],
            brief["scope3_assessment_narrative"],
        )
        self.assertNotIn("\n", brief["executive_summary"])
        self.assertLessEqual(len(brief["executive_summary"].split()), 90)

    def test_scope3_business_states_have_distinct_narratives(self) -> None:
        expected_phrases = {
            "disclosed": "preliminary input",
            "claim_only": "cannot be aggregated",
            "not_found": "does not indicate zero",
            "extraction_error": "No conclusion about disclosure",
        }

        for level, phrase in expected_phrases.items():
            with self.subTest(level=level):
                brief = compile_brief(self._brief_state(level))["brief"]
                self.assertIn(phrase, brief["scope3_assessment_narrative"])

    def test_native_scope3_states_are_supported(self) -> None:
        for level in ("scope3_ready", "partial", "materiality_claim", "unassessed"):
            with self.subTest(level=level):
                narrative = compile_brief(self._brief_state(level))["brief"][
                    "scope3_assessment_narrative"
                ]
                self.assertNotIn("not available in a recognized", narrative)

    def test_confidence_explanation_comes_from_existing_decision_rationale(self) -> None:
        state = make_initial_state("Example Supplier")
        state.update(
            {
                "is_machine_readable": True,
                "brsr_section_found": True,
                "extraction_confidence_score": 0.9,
                "extracted_indicators": {
                    "principle_6": {
                        "indicator": {
                            "state": "disclosed",
                            "extraction_method": "llm",
                            "uncertain": False,
                        }
                    }
                },
                "completeness_results": [
                    {
                        "essential_total": 10,
                        "essential_disclosed": 9,
                        "essential_partial": 0,
                    }
                ],
            }
        )

        confidence = assess_confidence(state)

        self.assertEqual(confidence["confidence_level"], "high")
        self.assertIn("document quality scored 0.90", confidence["confidence_explanation"])
        self.assertIn(
            "essential-indicator coverage was 90%",
            confidence["confidence_explanation"],
        )

    def test_medium_confidence_explanation_uses_decision_signals(self) -> None:
        state = make_initial_state("Example Supplier")
        state.update(
            {
                "is_machine_readable": True,
                "brsr_section_found": True,
                "extraction_confidence_score": 0.7,
                "extracted_indicators": {
                    "principle_6": {
                        "indicator": {
                            "state": "disclosed",
                            "extraction_method": "llm",
                            "uncertain": False,
                        }
                    }
                },
                "completeness_results": [
                    {
                        "essential_total": 10,
                        "essential_disclosed": 7,
                        "essential_partial": 0,
                    }
                ],
            }
        )

        confidence = assess_confidence(state)

        self.assertEqual(confidence["confidence_level"], "medium")
        self.assertIn(
            "essential-indicator coverage was 70%",
            confidence["confidence_explanation"],
        )
        self.assertIn(
            "combined quality and coverage signals do not support High confidence",
            confidence["confidence_explanation"],
        )

    def test_low_confidence_explanation_distinguishes_extraction_failure(self) -> None:
        state = make_initial_state("Example Supplier")
        state.update(
            {
                "is_machine_readable": True,
                "brsr_section_found": True,
                "extraction_errors": [
                    {
                        "indicator_id": "e6_scope3_emissions",
                        "error_code": "timeout_error",
                    }
                ],
            }
        )

        confidence = assess_confidence(state)

        self.assertEqual(confidence["confidence_level"], "low")
        self.assertIn("could not be extracted", confidence["confidence_explanation"])


if __name__ == "__main__":
    unittest.main()
