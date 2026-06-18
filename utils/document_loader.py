"""Document Loader Utility.

Extracts clean, structured text from PDF documents page by page.
Supports PyMuPDF4LLM as preferred extractor and falls back to standard PyMuPDF.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> list[dict[str, Any]]:
    """Extracts text from a PDF file page-by-page.

    Attempts to use PyMuPDF4LLM for markdown structured text. If unavailable
    or fails, falls back to PyMuPDF (fitz) standard text extraction.

    Args:
        pdf_path: Absolute path to the PDF file.

    Returns:
        List of dictionaries containing 'page_number' (1-indexed), 'text' (str),
        and 'filename' (str).
    """
    filename = os.path.basename(pdf_path)
    pages = []
    start_time = time.time()

    # Try PyMuPDF4LLM
    try:
        import fitz  # type: ignore[import-untyped]
        import pymupdf4llm  # type: ignore[import-untyped]

        logger.info("Extracting text from %s using PyMuPDF4LLM", filename)

        # Open doc to get total page count
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()

        empty_count = 0
        for page_idx in range(total_pages):
            page_num = page_idx + 1
            # Extract single page as Markdown
            md_text = pymupdf4llm.to_markdown(pdf_path, pages=[page_idx])
            md_text = md_text.strip() if md_text else ""
            if not md_text:
                empty_count += 1
                continue
            pages.append(
                {
                    "page_number": page_num,
                    "text": md_text,
                    "filename": filename,
                }
            )

        elapsed = time.time() - start_time
        logger.info(
            "Extraction statistics for %s: Total pages: %d, Extracted: %d, "
            "Empty skipped: %d, Time: %.2fs",
            filename,
            total_pages,
            len(pages),
            empty_count,
            elapsed,
        )
        return pages

    except Exception as exc:
        logger.warning(
            "PyMuPDF4LLM extraction failed or not installed: %s. "
            "Falling back to PyMuPDF (fitz)...",
            exc,
        )

    # Fallback to PyMuPDF (fitz)
    try:
        import fitz

        logger.info("Extracting text from %s using PyMuPDF (fitz) fallback", filename)
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        empty_count = 0

        for page_idx in range(total_pages):
            page_num = page_idx + 1
            page = doc[page_idx]
            text = page.get_text().strip()
            if not text:
                empty_count += 1
                continue
            pages.append(
                {
                    "page_number": page_num,
                    "text": text,
                    "filename": filename,
                }
            )

        doc.close()
        elapsed = time.time() - start_time
        logger.info(
            "Extraction statistics (fitz fallback) for %s: Total pages: %d, "
            "Extracted: %d, Empty skipped: %d, Time: %.2fs",
            filename,
            total_pages,
            len(pages),
            empty_count,
            elapsed,
        )
        return pages
    except Exception as exc:
        logger.error("Failed to extract text from PDF %s: %s", pdf_path, exc)
        raise RuntimeError(f"Failed to load PDF: {exc}") from exc


def load_pdf_document(pdf_path: str) -> list[dict[str, Any]]:
    """Loads a PDF document and extracts its contents.

    Args:
        pdf_path: Absolute path to the PDF file.

    Returns:
        List of dictionaries containing page text and metadata.
    """
    return extract_text_from_pdf(pdf_path)
