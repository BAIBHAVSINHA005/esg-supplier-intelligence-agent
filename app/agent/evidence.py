"""Presentation-layer evidence traceability for the final ESG brief."""

import re
import unicodedata
from typing import Any

from app.schemas.loader import get_indicators, load_schema


def _result_items(result: dict, key: str) -> list:
    """Return the first Chroma query result list for ``key`` safely."""
    values = result.get(key) or []
    if values and isinstance(values[0], list):
        return values[0]
    return values if isinstance(values, list) else []


def _normalized_text(value: str) -> str:
    """Canonicalize trivial formatting while retaining exact textual grounding."""
    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n")
    # Remove PDF line-wrap hyphenation, but only when the hyphen crosses a line.
    text = re.sub(r"(?<=\w)[\u00ad-]\s*\n\s*(?=\w)", "", text)
    text = unicodedata.normalize("NFKC", text).replace("\u00ad", "")
    text = text.translate(
        str.maketrans(
            {
                "“": '"',
                "”": '"',
                "‘": "'",
                "’": "'",
                "–": "-",
                "—": "-",
                "−": "-",
                "•": " ",
                "▪": " ",
                "◦": " ",
            }
        )
    )
    text = re.sub(r"\s*([,;:])\s*", r"\1", text)
    text = re.sub(r"\s*-\s*", "-", text)
    text = re.sub(r"\s+([.%)])", r"\1", text)
    text = re.sub(r"([(])\s+", r"\1", text)
    text = re.sub(r"\s*/\s*", "/", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().casefold()


def format_reference(value: object, fallback: object = None) -> str:
    """Return a defensible, nonblank presentation reference."""
    reference = str(value or "").strip()
    fallback_reference = str(fallback or "").strip()
    if not reference:
        reference = fallback_reference
    if not reference:
        return "—"

    absence_phrase = re.compile(
        r"not found in uploaded brsr filing\s*(?:[—–-]\s*)?",
        re.IGNORECASE,
    )
    implies_absence = bool(absence_phrase.search(reference)) or bool(
        re.search(r"\bchecked\s*\.?$", reference, re.IGNORECASE)
    )
    if implies_absence:
        detail = absence_phrase.sub("", reference)
        detail = re.sub(r"\bchecked\b", "", detail, flags=re.IGNORECASE)
        detail = re.sub(r"\s+", " ", detail).strip(" —–-.:")
        base = "No qualifying disclosure identified in assessed BRSR"
        return f"{base} — {detail}" if detail else base

    return reference


def _matching_source_locations(evidence: str, retrieval_result: dict) -> list[dict]:
    """Locate an extracted excerpt only when it occurs in retrieved chunk text."""
    normalized_evidence = _normalized_text(evidence)
    if not normalized_evidence:
        return []

    documents = _result_items(retrieval_result, "documents")
    metadatas = _result_items(retrieval_result, "metadatas")
    chunk_ids = _result_items(retrieval_result, "ids")
    distances = _result_items(retrieval_result, "distances")
    locations = []

    for index, document in enumerate(documents):
        if normalized_evidence not in _normalized_text(str(document or "")):
            continue

        metadata = metadatas[index] if index < len(metadatas) else {}
        metadata = metadata if isinstance(metadata, dict) else {}
        location = {
            "page": metadata.get("page"),
            "chunk_id": chunk_ids[index] if index < len(chunk_ids) else None,
            "retrieval_rank": index + 1,
        }
        if index < len(distances):
            location["distance"] = distances[index]
        locations.append(location)

    return locations


def build_evidence_register(state: dict[str, Any]) -> list[dict]:
    """Build auditable evidence entries from existing extraction/retrieval metadata.

    This function does not infer evidence. Found excerpts are linked to a page and
    chunk only when the extracted text is present in that retrieved chunk. Genuine
    ``not_found`` and ``extraction_error`` results never receive synthetic evidence.
    """
    definitions = get_indicators(load_schema("brsr_v2023"), "principle_6")
    extracted = state.get("extracted_indicators", {}).get("principle_6", {})
    retrieved = state.get("retrieved_context", {})
    entries = []

    for indicator_id, result in extracted.items():
        definition = definitions.get(indicator_id, {})
        assessment_reference = definition.get("brsr_indicator_ref")
        disclosure_state = result.get("state", "not_found")
        is_materiality_claim = bool(result.get("scope3_has_materiality_claim"))
        evidence = (result.get("evidence") or "").strip()

        if disclosure_state == "extraction_error":
            evidence_excerpt = None
            source_locations = []
            evidence_status = "extraction_error"
        elif disclosure_state == "not_found" and not is_materiality_claim:
            evidence_excerpt = None
            source_locations = []
            evidence_status = "not_found"
        else:
            evidence_excerpt = evidence or None
            source_locations = _matching_source_locations(
                evidence, retrieved.get(indicator_id, {})
            )
            if source_locations:
                evidence_status = "source_matched"
            elif result.get("citation"):
                evidence_status = "citation_only"
            elif evidence_excerpt:
                evidence_status = "excerpt_unmatched"
            else:
                evidence_status = "no_source_reference"

        entries.append(
            {
                "indicator_id": indicator_id,
                "indicator_name": definition.get("name", indicator_id),
                "state": disclosure_state,
                "value": result.get("value") or None,
                "evidence_excerpt": evidence_excerpt,
                "citation": format_reference(
                    result.get("citation"), assessment_reference
                ),
                "raw_citation": result.get("citation") or None,
                "assessment_reference": assessment_reference,
                "evidence_status": evidence_status,
                "source_locations": source_locations,
                "extraction_method": result.get("extraction_method"),
                "extraction_confidence": result.get("confidence"),
                "error_code": (
                    result.get("error_code")
                    if disclosure_state == "extraction_error"
                    else None
                ),
            }
        )

    return entries
