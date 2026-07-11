# app/extraction/pdf_parser.py

import fitz  # PyMuPDF
from typing import Optional


def extract_text_from_bytes(pdf_bytes: bytes) -> tuple[str, list[dict], int]:
    """
    Open a PDF from bytes and extract full text plus page-level chunks.

    Returns:
        full_text   — complete document text, all pages joined
        chunks      — list of dicts: {text, page, section, is_table}
        num_pages   — total number of pages in the PDF
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    num_pages = len(doc)

    full_text_parts = []
    chunks = []

    for page_num, page in enumerate(doc):
        page_text = page.get_text("text")
        full_text_parts.append(page_text)

        # Split page text into paragraphs for chunking
        # Minimum 50 chars — filters out page numbers, headers, single words
        paragraphs = [
            p.strip()
            for p in page_text.split("\n\n")
            if len(p.strip()) > 50
        ]
        for para in paragraphs:
            chunks.append({
                "text": para,
                "page": page_num + 1,
                "section": None,    # Labelled by section_detector
                "is_table": False   # Table detection is a future enhancement
            })

    doc.close()
    full_text = "\n".join(full_text_parts)
    return full_text, chunks, num_pages


def chars_per_page(full_text: str, num_pages: int) -> float:
    """
    Calculate average extractable characters per page.
    Used to detect scanned/image PDFs.
    A normal text-heavy PDF has 2,000–5,000 chars/page.
    A scanned PDF typically produces fewer than 200.
    """
    if num_pages == 0:
        return 0.0
    return len(full_text) / num_pages


def is_machine_readable(avg_chars_per_page: float, threshold: int = 200) -> bool:
    """
    Returns True if the document appears to contain extractable text.
    200 chars/page is a conservative threshold — adjust down if real BRSRs
    trigger false failures during testing.
    """
    return avg_chars_per_page >= threshold