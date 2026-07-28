"""Regression coverage for optional extraction semantic metadata."""

import unittest

from app.extraction.prompts import build_extraction_prompt
from app.extraction.schemas import ExtractionResponse, to_pipeline_dict


class ExtractionSemanticFlagsTests(unittest.TestCase):
    """Verify optional semantic metadata remains backward compatible."""

    def test_scope3_semantic_flags_are_validated_and_preserved(self) -> None:
        """Scope 3 output retains semantic flags in the pipeline representation."""
        response = ExtractionResponse.model_validate(
            {
                "result": {
                    "indicator_id": "e6_scope3_emissions",
                    "state": "disclosed",
                    "value": "1,250 tCO2e",
                    "evidence": "Scope 3 emissions were 1,250 tCO2e.",
                    "citation": "Page 12",
                    "confidence": 0.91,
                    "semantic_flags": {
                        "scope3_mentioned": True,
                        "scope3_has_absolute_number": True,
                        "scope3_has_methodology": False,
                        "scope3_is_intensity_only": False,
                        "scope3_has_materiality_claim": False,
                    },
                }
            }
        )

        pipeline_result = to_pipeline_dict(response.result)

        self.assertEqual(pipeline_result["state"], "disclosed")
        self.assertEqual(
            pipeline_result["semantic_flags"],
            {
                "scope3_mentioned": True,
                "scope3_has_absolute_number": True,
                "scope3_has_methodology": False,
                "scope3_is_intensity_only": False,
                "scope3_has_materiality_claim": False,
            },
        )

    def test_non_scope3_extraction_remains_compatible_without_semantic_flags(
        self,
    ) -> None:
        """Existing non-Scope 3 responses validate without optional metadata."""
        response = ExtractionResponse.model_validate(
            {
                "result": {
                    "indicator_id": "e6_energy_consumption",
                    "state": "disclosed",
                    "value": "200 GJ",
                    "evidence": "Total energy consumption was 200 GJ.",
                    "citation": "Page 8",
                    "confidence": 0.9,
                }
            }
        )

        pipeline_result = to_pipeline_dict(response.result)

        self.assertIsNone(response.result.semantic_flags)
        self.assertEqual(pipeline_result["value"], "200 GJ")
        self.assertIsNone(pipeline_result["semantic_flags"])

    def test_prompts_request_scope3_flags_only_for_scope3(self) -> None:
        """Prompt construction limits semantic reasoning instructions to Scope 3."""
        scope3_prompt = build_extraction_prompt(
            indicator_id="e6_scope3_emissions",
            indicator_name="Scope 3 GHG Emissions",
            indicator_description="Value-chain emissions.",
            context="Scope 3 emissions were 1,250 tCO2e.",
        )
        energy_prompt = build_extraction_prompt(
            indicator_id="e6_energy_consumption",
            indicator_name="Energy Consumption",
            indicator_description="Energy used.",
            context="Energy consumption was 200 GJ.",
        )

        self.assertIn("scope3_has_absolute_number", scope3_prompt)
        self.assertIn("Do not include semantic_flags", energy_prompt)
