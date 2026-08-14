"""Sprint 5 tests for evidence auditability and targeted supplier questions."""

import unittest

from app.agent.evidence import build_evidence_register, format_reference
from app.agent.nodes.brief import compile_brief
from app.agent.nodes.questions import generate_questions
from app.agent.state import make_initial_state


class EvidenceRegisterTests(unittest.TestCase):
    def _state_with_result(self, result: dict, retrieval: dict | None = None) -> dict:
        state = make_initial_state("Example Supplier")
        state["extracted_indicators"] = {
            "principle_6": {"e6_scope3_emissions": result}
        }
        state["retrieved_context"] = {
            "e6_scope3_emissions": retrieval or {}
        }
        return state

    def test_exact_evidence_is_linked_to_existing_page_and_chunk(self) -> None:
        evidence = "Scope 3 emissions were 1,250 tCO2e in FY2025."
        state = self._state_with_result(
            {
                "state": "disclosed",
                "value": "1,250 tCO2e",
                "evidence": evidence,
                "citation": "Page 42",
                "extraction_method": "llm",
                "confidence": 0.92,
            },
            {
                "documents": [[f"Other text. {evidence} Additional context."]],
                "metadatas": [[{"page": 42, "document_id": "doc-1"}]],
                "ids": [["chunk-42"]],
                "distances": [[0.08]],
            },
        )

        entry = build_evidence_register(state)[0]

        self.assertEqual(entry["evidence_status"], "source_matched")
        self.assertEqual(entry["evidence_excerpt"], evidence)
        self.assertEqual(
            entry["source_locations"][0],
            {
                "page": 42,
                "chunk_id": "chunk-42",
                "retrieval_rank": 1,
                "distance": 0.08,
            },
        )

    def test_trivial_pdf_formatting_differences_still_match_exact_text(self) -> None:
        evidence = '"Scope 3" disclosure: 1,250 tCO2e for FY 2025.'
        state = self._state_with_result(
            {
                "state": "disclosed",
                "value": "1,250 tCO2e",
                "evidence": evidence,
                "citation": "Page 42",
                "extraction_method": "llm",
                "confidence": 0.9,
            },
            {
                "documents": [[
                    "“Scope 3” disclo-\nsure : 1,250 tCO₂e\nfor FY 2025."
                ]],
                "metadatas": [[{"page": 42}]],
                "ids": [["chunk-formatting"]],
            },
        )

        entry = build_evidence_register(state)[0]

        self.assertEqual(entry["evidence_status"], "source_matched")
        self.assertEqual(entry["source_locations"][0]["chunk_id"], "chunk-formatting")

    def test_not_found_never_receives_evidence_or_source_location(self) -> None:
        state = self._state_with_result(
            {
                "state": "not_found",
                "value": "",
                "evidence": "Text that must not be presented as absence evidence.",
                "citation": "Principle 6, Leadership Indicator",
                "extraction_method": "llm",
                "confidence": 0.7,
            },
            {
                "documents": [["Text that must not be presented as absence evidence."]],
                "metadatas": [[{"page": 8}]],
                "ids": [["chunk-8"]],
            },
        )

        entry = build_evidence_register(state)[0]

        self.assertEqual(entry["evidence_status"], "not_found")
        self.assertIsNone(entry["evidence_excerpt"])
        self.assertEqual(entry["source_locations"], [])

    def test_extraction_error_remains_distinct_from_not_found(self) -> None:
        state = self._state_with_result(
            {
                "state": "extraction_error",
                "value": "",
                "evidence": "",
                "citation": "Principle 6, Leadership Indicator",
                "error_code": "timeout_error",
                "extraction_method": "llm",
                "confidence": 0.0,
            }
        )

        entry = build_evidence_register(state)[0]

        self.assertEqual(entry["state"], "extraction_error")
        self.assertEqual(entry["evidence_status"], "extraction_error")
        self.assertEqual(entry["error_code"], "timeout_error")
        self.assertIsNone(entry["evidence_excerpt"])

    def test_materiality_claim_keeps_only_extracted_source_evidence(self) -> None:
        evidence = "Scope 3 emissions are not material to our operations."
        state = self._state_with_result(
            {
                "state": "not_found",
                "value": "",
                "evidence": evidence,
                "citation": "Page 17",
                "scope3_has_materiality_claim": True,
                "extraction_method": "llm",
                "confidence": 0.8,
            },
            {
                "documents": [[evidence]],
                "metadatas": [[{"page": 17}]],
                "ids": [["chunk-17"]],
            },
        )

        entry = build_evidence_register(state)[0]

        self.assertEqual(entry["state"], "not_found")
        self.assertEqual(entry["evidence_status"], "source_matched")
        self.assertEqual(entry["evidence_excerpt"], evidence)

    def test_unmatched_excerpt_is_not_assigned_to_top_retrieval_result(self) -> None:
        state = self._state_with_result(
            {
                "state": "disclosed",
                "value": "1,250 tCO2e",
                "evidence": "Scope 3 emissions were 1,250 tCO2e.",
                "citation": "Page 42",
                "extraction_method": "llm",
                "confidence": 0.9,
            },
            {
                "documents": [["A related but non-matching Scope 3 passage."]],
                "metadatas": [[{"page": 9}]],
                "ids": [["chunk-9"]],
            },
        )

        entry = build_evidence_register(state)[0]

        self.assertEqual(entry["evidence_status"], "citation_only")
        self.assertEqual(entry["source_locations"], [])

    def test_compile_brief_exposes_additive_evidence_register(self) -> None:
        evidence = "Scope 3 emissions were 1,250 tCO2e."
        state = self._state_with_result(
            {
                "state": "disclosed",
                "value": "1,250 tCO2e",
                "evidence": evidence,
                "citation": "Page 42",
                "extraction_method": "llm",
                "confidence": 0.9,
            },
            {
                "documents": [[evidence]],
                "metadatas": [[{"page": 42}]],
                "ids": [["chunk-42"]],
            },
        )
        state["scope3_verdict"] = {"level": "scope3_ready"}

        brief = compile_brief(state)["brief"]

        self.assertIn("evidence_register", brief)
        self.assertEqual(brief["evidence_register"][0]["indicator_id"], "e6_scope3_emissions")
        self.assertEqual(brief["scope3_verdict"], state["scope3_verdict"])

    def test_compile_brief_preserves_raw_citations_and_adds_display_references(self) -> None:
        state = make_initial_state("Example Supplier")
        raw_reference = (
            "Not found in uploaded BRSR filing — "
            "Principle 6, Essential Indicator E-5 checked"
        )
        state["gaps"] = [
            {
                "gap_id": "G-10",
                "gap_name": "GHG emission intensity metrics absent",
                "brsr_reference": "Principle 6, Essential Indicator E-5",
                "citation": raw_reference,
            }
        ]
        state["followup_questions"] = [
            {
                "gap_id": "G-10",
                "question": "Please provide the intensity metric.",
                "citation": "",
            }
        ]

        brief = compile_brief(state)["brief"]

        self.assertEqual(brief["gaps"][0]["citation"], raw_reference)
        self.assertEqual(
            brief["gap_references"]["G-10"],
            "No qualifying disclosure identified in assessed BRSR — "
            "Principle 6, Essential Indicator E-5",
        )
        self.assertEqual(brief["question_references"]["G-10"], "—")


class SupplierQuestionTests(unittest.TestCase):
    def _base_state(self) -> dict:
        state = make_initial_state("Acme Components Ltd")
        state.update(
            {
                "scope3_verdict": {"level": "claim_only"},
                "gaps": [],
                "extracted_indicators": {"principle_6": {}},
            }
        )
        return state

    def test_scope3_question_uses_supplier_and_actual_claim_only_finding(self) -> None:
        state = self._base_state()
        state["gaps"] = [
            {
                "rank": 1,
                "gap_id": "G-01",
                "gap_name": "Scope 3 not disclosed",
                "citation": "Page 42",
            }
        ]

        question = generate_questions(state)["followup_questions"][0]

        self.assertIn("Acme Components Ltd", question["question"])
        self.assertIn("acknowledged", question["question"])
        self.assertIn("absolute tCO2e", question["question"])
        self.assertEqual(question["linked_gap_id"], "G-01")
        self.assertEqual(question["citation"], "Page 42")

    def test_scope3_extraction_error_is_never_worded_as_not_found(self) -> None:
        state = self._base_state()
        state["scope3_verdict"] = {"level": "unassessed"}
        state["extracted_indicators"]["principle_6"] = {
            "e6_scope3_emissions": {
                "state": "extraction_error",
                "error_code": "timeout_error",
            }
        }
        state["gaps"] = [
            {
                "rank": 1,
                "gap_id": "G-01",
                "gap_name": "Scope 3 not disclosed",
                "citation": "Principle 6, Leadership Indicator",
            }
        ]

        question = generate_questions(state)["followup_questions"][0]["question"]

        self.assertIn("extraction failed", question)
        self.assertNotIn("No Scope 3 disclosure was identified", question)

    def test_methodology_question_mentions_emissions_actually_found(self) -> None:
        state = self._base_state()
        state["gaps"] = [
            {
                "rank": 1,
                "gap_id": "G-02",
                "gap_name": "No GHG accounting methodology named",
                "citation": "Principle 6, Essential Indicator E-4",
            }
        ]
        state["extracted_indicators"]["principle_6"] = {
            "e6_scope1_emissions": {
                "state": "disclosed",
                "value": "800 tCO2e",
            },
            "e6_scope2_emissions": {
                "state": "not_found",
                "value": "",
            },
            "e6_ghg_methodology": {"state": "not_found"},
        }

        question = generate_questions(state)["followup_questions"][0]["question"]

        self.assertIn("Scope 1 GHG Emissions (800 tCO2e)", question)
        self.assertNotIn("Scope 2 GHG Emissions", question)

    def test_incomplete_p6_question_excludes_extraction_errors_from_missing(self) -> None:
        state = self._base_state()
        state["gaps"] = [
            {
                "rank": 1,
                "gap_id": "G-03",
                "gap_name": "Principle 6 environmental data severely incomplete",
                "citation": "Principle 6, Section C",
            }
        ]
        state["extracted_indicators"]["principle_6"] = {
            "e6_water_consumption": {"state": "not_found"},
            "e6_waste_generated": {
                "state": "extraction_error",
                "error_code": "timeout_error",
            },
        }

        question = generate_questions(state)["followup_questions"][0]["question"]

        self.assertIn("Water Consumption", question)
        self.assertNotIn("Total Waste Generated", question)
        self.assertNotIn("extraction error", question.lower())

    def test_remaining_supported_gaps_use_specific_question_templates(self) -> None:
        expected_phrases = {
            "G-05": "baseline year",
            "G-10": "intensity metric",
            "G-11": "leadership indicator",
        }

        for gap_id, expected_phrase in expected_phrases.items():
            with self.subTest(gap_id=gap_id):
                state = self._base_state()
                state["gaps"] = [
                    {
                        "rank": 1,
                        "gap_id": gap_id,
                        "gap_name": "Test gap",
                        "citation": "Principle 6",
                    }
                ]
                question = generate_questions(state)["followup_questions"][0]

                self.assertIn("Acme Components Ltd", question["question"])
                self.assertIn(expected_phrase, question["question"])
                self.assertEqual(question["linked_gap_id"], gap_id)

    def test_blank_question_reference_renders_em_dash(self) -> None:
        state = self._base_state()
        state["gaps"] = [
            {
                "rank": 1,
                "gap_id": "G-99",
                "gap_name": "Test gap",
                "citation": "",
                "brsr_reference": "",
            }
        ]

        question = generate_questions(state)["followup_questions"][0]

        self.assertEqual(question["citation"], "—")
        self.assertEqual(question["reference"], "—")


class ReferenceFormattingTests(unittest.TestCase):
    def test_absence_wording_is_replaced_without_losing_assessment_detail(self) -> None:
        reference = format_reference(
            "Not found in uploaded BRSR filing — "
            "Principle 6, Essential Indicator E-5 checked"
        )

        self.assertEqual(
            reference,
            "No qualifying disclosure identified in assessed BRSR — "
            "Principle 6, Essential Indicator E-5",
        )

    def test_reference_uses_fallback_then_em_dash(self) -> None:
        self.assertEqual(format_reference("", "Principle 6"), "Principle 6")
        self.assertEqual(format_reference(None), "—")

    def test_specific_source_reference_is_unchanged(self) -> None:
        self.assertEqual(format_reference("Page 42"), "Page 42")


if __name__ == "__main__":
    unittest.main()
