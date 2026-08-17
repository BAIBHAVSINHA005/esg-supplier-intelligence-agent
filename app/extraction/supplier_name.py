"""Deterministic supplier-name resolution from user input and BRSR metadata."""

import re
from pathlib import Path


_SECTION_A_PATTERN = re.compile(
    r"section\s+a\s*:\s*general\s+disclosures",
    re.IGNORECASE,
)
_SECTION_B_PATTERN = re.compile(r"section\s+b\s*:", re.IGNORECASE)
_LISTED_ENTITY_PATTERN = re.compile(
    r"^(?:\d+\s+)?name\s+of\s+(?:the\s+)?listed\s+entity\s*(?::|-)?\s*(.*)$",
    re.IGNORECASE,
)


def _filename_name(source_filename: str) -> str:
    name = Path(source_filename or "").stem.replace("_", " ").strip()
    return name.title() or "Supplier"


def _section_a_listed_entity(document_text: str) -> str:
    section_match = _SECTION_A_PATTERN.search(document_text or "")
    if not section_match:
        return ""

    section_text = document_text[section_match.end():]
    next_section = _SECTION_B_PATTERN.search(section_text)
    if next_section:
        section_text = section_text[:next_section.start()]

    lines = [re.sub(r"\s+", " ", line).strip() for line in section_text.splitlines()]
    for index, line in enumerate(lines):
        label_match = _LISTED_ENTITY_PATTERN.match(line)
        if not label_match:
            continue

        inline_value = label_match.group(1).strip(" :-")
        if inline_value:
            return inline_value

        for candidate in lines[index + 1:index + 4]:
            candidate = candidate.strip(" :-")
            if candidate and not candidate.isdigit():
                return candidate
        return ""

    return ""


def resolve_supplier_name(
    explicit_name: str,
    document_text: str,
    source_filename: str,
) -> str:
    """Resolve supplier name using explicit, Section A, then filename precedence."""
    explicit = (explicit_name or "").strip()
    if explicit:
        return explicit

    listed_entity = _section_a_listed_entity(document_text)
    if listed_entity:
        return listed_entity

    return _filename_name(source_filename)
