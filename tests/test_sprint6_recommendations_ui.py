"""Sprint 6 coverage for recommendations and UI input/presentation contracts."""

import unittest
from pathlib import Path
from unittest.mock import patch

from app.agent.nodes.brief import compile_brief
from app.agent.nodes.ingest import ingest_document
from app.agent.state import make_initial_state
from app.ui.gradio_app import assess_supplier


class ProcurementRecommendationTests(unittest.TestCase):
    def test_recommendation_uses_only_existing_action_finding_and_reference(self) -> None:
        state = make_initial_state("Acme Components")
        state["gaps"] = [
            {
                "rank": 1,
                "gap_id": "G-01",
                "gap_name": "Scope 3 not disclosed",
                "severity": "critical",
                "description": "Existing gap description.",
                "citation": "Page 42",
            }
        ]
        state["recommended_actions"] = [
            {
                "rank": 1,
                "gap_id": "G-01",
                "gap_name": "Scope 3 not disclosed",
                "action": "Request the existing Scope 3 action.",
            }
        ]
        state["followup_questions"] = [
            {
                "rank": 1,
                "gap_id": "G-01",
                "linked_gap_id": "G-01",
                "basis": "Existing Scope 3 finding.",
                "question": "Existing supplier question?",
                "citation": "Page 42",
            }
        ]

        brief = compile_brief(state)["brief"]

        self.assertEqual(
            brief["procurement_recommendations"],
            [
                {
                    "rank": 1,
                    "gap_id": "G-01",
                    "gap_name": "Scope 3 not disclosed",
                    "severity": "critical",
                    "recommendation": "Request the existing Scope 3 action.",
                    "basis": "Existing Scope 3 finding.",
                    "reference": "Page 42",
                }
            ],
        )
        self.assertEqual(brief["gaps"], state["gaps"])
        self.assertEqual(brief["recommended_actions"], state["recommended_actions"])

    def test_gap_without_existing_action_does_not_create_recommendation(self) -> None:
        state = make_initial_state("Acme Components")
        state["gaps"] = [
            {
                "rank": 1,
                "gap_id": "G-99",
                "gap_name": "Unmapped finding",
                "description": "Existing finding only.",
            }
        ]

        brief = compile_brief(state)["brief"]

        self.assertEqual(brief["procurement_recommendations"], [])


class SupplierNamePropagationTests(unittest.TestCase):
    birla_section_a = """
        SECTION A: GENERAL DISCLOSURES
        I. DETAILS OF THE LISTED ENTITY
        1
        Corporate Identity Number (CIN) of the Listed Entity
        L01132WB1919PLC003334
        2
        Name of the Listed Entity
        Birla Corporation Limited
        3
        Year of incorporation
        1919
        SECTION B: MANAGEMENT AND PROCESS DISCLOSURES
    """

    def _ingest(self, supplier_name: str, text: str, filename: str) -> dict:
        state = make_initial_state(
            supplier_name,
            source_filename=filename,
            document_bytes=b"pdf",
        )
        with (
            patch(
                "app.agent.nodes.ingest.extract_text_from_bytes",
                return_value=(text, [], 1),
            ),
            patch("app.agent.nodes.ingest.enhance_chunks", return_value=[]),
        ):
            return ingest_document(state)

    def test_blank_name_uses_birla_listed_entity_from_section_a(self) -> None:
        result = self._ingest(
            "   ",
            self.birla_section_a,
            "BRSR_500335_10072026223816_MR BIRLA GROUP.pdf",
        )

        self.assertEqual(result["supplier_name"], "Birla Corporation Limited")

    def test_filename_is_used_when_section_a_name_is_unavailable(self) -> None:
        result = self._ingest("", "No Section A metadata.", "acme_components.pdf")

        self.assertEqual(result["supplier_name"], "Acme Components")

    def test_explicit_supplier_name_takes_precedence_over_section_a(self) -> None:
        result = self._ingest(
            "Analyst Supplied Name",
            self.birla_section_a,
            "birla.pdf",
        )

        self.assertEqual(result["supplier_name"], "Analyst Supplied Name")


class GradioPresentationTests(unittest.TestCase):
    @patch("app.ui.gradio_app.run_supplier_assessment")
    @patch.object(Path, "read_bytes", return_value=b"pdf")
    def test_report_keeps_provenance_in_expandable_evidence_details(
        self,
        _read_bytes,
        run_assessment,
    ) -> None:
        run_assessment.return_value = {
            "brief": {
                "header": {"supplier_name": "Acme", "confidence_level": "high"},
                "procurement_recommendations": [
                    {
                        "rank": 1,
                        "gap_id": "G-01",
                        "gap_name": "Scope 3 not disclosed",
                        "severity": "critical",
                        "recommendation": "Request the existing action.",
                        "basis": "Existing finding.",
                    }
                ],
                "gaps": [],
                "followup_questions": [],
                "evidence_register": [],
            }
        }

        report = assess_supplier("acme.pdf")

        self.assertIn("## Procurement Recommendations", report)
        self.assertIn("<details><summary><strong>Evidence Details</strong></summary>", report)
        self.assertIn("</details>", report)


if __name__ == "__main__":
    unittest.main()
