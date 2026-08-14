"""Regression coverage for size-bounded pre-embedding chunk subdivision."""

import math
import unittest
from unittest.mock import patch

from app.agent.nodes.retrieve import INDICATOR_QUERIES
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


if __name__ == "__main__":
    unittest.main()
