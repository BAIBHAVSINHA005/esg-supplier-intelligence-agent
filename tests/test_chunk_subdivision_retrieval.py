"""Regression coverage for size-bounded pre-embedding chunk subdivision."""

import json
import math
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.agent.evidence import build_evidence_register
from app.agent.nodes.retrieve import INDICATOR_QUERIES
from app.extraction.llm_extractor import LLMExtractor
from app.extraction.schemas import to_pipeline_dict
from app.rag.chunker import (
    CHUNK_OVERLAP_TOKENS,
    MAX_CHUNK_TOKENS,
    enhance_chunks,
)
from app.rag.retriever import index_chunks, retrieve_chunks


class _InMemoryVectorCollection:
    """Small Chroma-shaped test double with document-scoped vector ranking."""

    def __init__(self) -> None:
        self.records = []

    def add(self, *, ids, documents, metadatas, embeddings) -> None:
        self.records.append(
            {
                "id": ids[0],
                "document": documents[0],
                "metadata": metadatas[0],
                "embedding": embeddings[0],
            }
        )

    def query(self, *, query_embeddings, n_results, where) -> dict:
        query_embedding = query_embeddings[0]
        candidates = [
            record
            for record in self.records
            if record["metadata"].get("document_id") == where.get("document_id")
        ]
        ranked = sorted(
            candidates,
            key=lambda record: math.dist(record["embedding"], query_embedding),
        )[:n_results]
        return {
            "ids": [[record["id"] for record in ranked]],
            "documents": [[record["document"] for record in ranked]],
            "metadatas": [[record["metadata"] for record in ranked]],
            "distances": [[
                math.dist(record["embedding"], query_embedding)
                for record in ranked
            ]],
        }


def _test_embedding(text: str) -> list[float]:
    """Represent the production waste query terms for deterministic ranking."""
    normalized = " ".join(text.lower().replace("-", " ").split())
    return [
        float("total waste generated" in normalized),
        float("hazardous waste" in normalized),
        float("non hazardous waste" in normalized),
        float("waste management" in normalized),
        float("waste disposed" in normalized),
    ]


def _birla_embedding(text: str) -> list[float]:
    """Represent exact BRSR row labels separately from adjacent waste totals."""
    normalized = " ".join(text.lower().replace("-", " ").split())
    return [
        float("total scope 3 emissions" in normalized),
        float("total waste generated" in normalized),
        float(
            "waste recovered" in normalized
            or "recovery operations" in normalized
            or "waste disposed" in normalized
        ),
    ]


class _WasteExtractionClient:
    def __init__(self, expected_context: str, evidence: str) -> None:
        self.expected_context = expected_context
        self.evidence = evidence
        self.responses = self

    def create(self, **kwargs):
        if self.expected_context not in kwargs["input"]:
            raise AssertionError("Retrieved waste context was not supplied to extraction")
        return SimpleNamespace(
            output_text=json.dumps(
                {
                    "result": {
                        "indicator_id": "e6_waste_generated",
                        "state": "disclosed",
                        "value": "31,223.96 MT",
                        "evidence": self.evidence,
                        "citation": "Page 112",
                        "confidence": 0.95,
                    }
                }
            )
        )


class ChunkSubdivisionTests(unittest.TestCase):
    def _reliance_page_chunk(self) -> dict:
        prefix = " ".join(f"preface{index}" for index in range(235))
        table = (
            "Provide details related to waste management by the entity. "
            "Parameter FY 2025-26 FY 2024-25 Total Waste generated in metric tonnes. "
            "Plastic waste 3,850. E-waste 171. Other Hazardous waste 1,12,702. "
            "Other Non-hazardous waste generated 8,75,982. "
            "Total A+B+C+D+E+F+G+H 9,93,787 7,60,123. "
            "Waste disposed by nature of disposal method."
        )
        suffix = " ".join(f"suffix{index}" for index in range(300))
        return {
            "chunk_id": "reliance-page-37",
            "text": f"{prefix}\n{table}\n{suffix}",
            "page": 37,
            "section": "Principle 6",
            "is_table": False,
        }

    def test_oversized_chunk_is_bounded_with_small_overlap(self) -> None:
        enhanced = enhance_chunks([self._reliance_page_chunk()])

        self.assertGreater(len(enhanced), 1)
        self.assertTrue(
            all(len(chunk["text"].split()) <= MAX_CHUNK_TOKENS for chunk in enhanced)
        )
        for previous, current in zip(enhanced, enhanced[1:]):
            previous_tokens = previous["text"].split()
            current_tokens = current["text"].split()
            self.assertEqual(
                previous_tokens[-CHUNK_OVERLAP_TOKENS:],
                current_tokens[:CHUNK_OVERLAP_TOKENS],
            )

    def test_late_waste_total_is_retrieved_in_production_top_five(self) -> None:
        collection = _InMemoryVectorCollection()
        document_id = "reliance-regression"
        chunks = [self._reliance_page_chunk()]
        chunks.extend(
            {
                "chunk_id": f"distractor-{index}",
                "text": (
                    "Circular economy initiatives and general environmental "
                    f"management narrative {index}."
                ),
                "page": index + 1,
            }
            for index in range(8)
        )
        enhanced = enhance_chunks(
            chunks,
            source_filename="Reliance-BRSR-2025-26.pdf",
            assessment_id="assessment-reliance",
            document_id=document_id,
        )

        with (
            patch("app.rag.retriever.get_collection", return_value=collection),
            patch("app.rag.retriever.get_embedding", side_effect=_test_embedding),
        ):
            index_chunks(enhanced, document_id)
            results = retrieve_chunks(
                INDICATOR_QUERIES["e6_waste_generated"], document_id
            )

        self.assertEqual(len(results["documents"][0]), 5)
        target_index = next(
            index
            for index, text in enumerate(results["documents"][0])
            if "9,93,787" in text
        )
        target_metadata = results["metadatas"][0][target_index]
        self.assertEqual(target_metadata["page"], 37)
        self.assertEqual(
            target_metadata["source_filename"], "Reliance-BRSR-2025-26.pdf"
        )
        self.assertEqual(target_metadata["assessment_id"], "assessment-reliance")
        self.assertEqual(target_metadata["document_id"], document_id)

    def test_small_chunk_keeps_existing_id_and_fields(self) -> None:
        original = {
            "chunk_id": "existing-id",
            "text": "Short source paragraph.",
            "page": 4,
            "section": "Principle 6",
            "is_table": True,
        }

        enhanced = enhance_chunks([original])

        self.assertEqual(len(enhanced), 1)
        self.assertEqual(enhanced[0]["chunk_id"], "existing-id")
        self.assertEqual(enhanced[0]["text"], original["text"])
        self.assertEqual(enhanced[0]["section"], "Principle 6")
        self.assertTrue(enhanced[0]["is_table"])


class BirlaRetrievalRegressionTests(unittest.TestCase):
    document_id = "birla-regression"
    scope3_text = (
        "Total Scope 3 Emissions - Break-up of the GHG. Metric tonnes of CO2 "
        "equivalent. FY 2025-26: 18,09,403.78."
    )
    generated_text = (
        "Total Waste Generated (A+B+C+D+E+F+G+H). FY 2025-26: "
        "31,223.96 MT."
    )
    recovered_text = (
        "For each category of waste generated, total waste recovered through "
        "recycling, re-using or other recovery operations. Total: 31,176.75 MT."
    )
    disposed_text = (
        "Total waste disposed by nature of disposal method. Total: 0.17 MT."
    )

    def _collection(self) -> _InMemoryVectorCollection:
        collection = _InMemoryVectorCollection()
        chunks = [
            {"chunk_id": "scope3-row", "text": self.scope3_text, "page": 115},
            {"chunk_id": "generated-row", "text": self.generated_text, "page": 112},
            {"chunk_id": "recovered-row", "text": self.recovered_text, "page": 113},
            {"chunk_id": "disposed-row", "text": self.disposed_text, "page": 113},
            {
                "chunk_id": "generic-climate",
                "text": "General climate change and value-chain narrative.",
                "page": 20,
            },
        ]
        with (
            patch("app.rag.retriever.get_collection", return_value=collection),
            patch("app.rag.retriever.get_embedding", side_effect=_birla_embedding),
        ):
            index_chunks(chunks, self.document_id)
        return collection

    def _retrieve(self, indicator_id: str) -> dict:
        collection = self._collection()
        with (
            patch("app.rag.retriever.get_collection", return_value=collection),
            patch("app.rag.retriever.get_embedding", side_effect=_birla_embedding),
        ):
            return retrieve_chunks(
                INDICATOR_QUERIES[indicator_id],
                self.document_id,
            )

    def test_scope3_exact_row_is_in_production_top_five(self) -> None:
        results = self._retrieve("e6_scope3_emissions")

        self.assertEqual(len(results["documents"][0]), 5)
        self.assertIn(self.scope3_text, results["documents"][0])

    def test_generated_waste_ranks_ahead_of_recovered_and_disposed_totals(self) -> None:
        results = self._retrieve("e6_waste_generated")
        ranked_ids = results["ids"][0]

        self.assertLess(ranked_ids.index("generated-row"), ranked_ids.index("recovered-row"))
        self.assertLess(ranked_ids.index("generated-row"), ranked_ids.index("disposed-row"))

    def test_extraction_selects_generated_total_not_recovered_total(self) -> None:
        results = self._retrieve("e6_waste_generated")
        context = "\n\n".join(results["documents"][0])
        extractor = LLMExtractor(
            client=_WasteExtractionClient(context, self.generated_text)
        )

        result = extractor.extract_indicator(
            indicator_id="e6_waste_generated",
            indicator_name="Total Waste Generated",
            indicator_description=(
                "Total waste generated including hazardous and non-hazardous waste"
            ),
            context=context,
            citation="Principle 6, Essential Indicator E-8",
        )
        pipeline_result = to_pipeline_dict(result)

        self.assertEqual(pipeline_result["value"], "31,223.96 MT")
        self.assertNotIn("31,176.75", pipeline_result["evidence"])

    def test_evidence_matches_selected_generated_waste_source(self) -> None:
        results = self._retrieve("e6_waste_generated")
        extraction_result = {
            "state": "disclosed",
            "value": "31,223.96 MT",
            "evidence": self.generated_text,
            "citation": "Page 112",
            "extraction_method": "llm",
            "confidence": 0.95,
        }
        state = {
            "extracted_indicators": {
                "principle_6": {"e6_waste_generated": extraction_result}
            },
            "retrieved_context": {"e6_waste_generated": results},
        }

        entry = build_evidence_register(state)[0]

        self.assertEqual(entry["evidence_status"], "source_matched")
        self.assertEqual(entry["source_locations"][0]["chunk_id"], "generated-row")
        self.assertEqual(entry["source_locations"][0]["page"], 112)


if __name__ == "__main__":
    unittest.main()
