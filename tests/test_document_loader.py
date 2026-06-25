"""Unit tests for Document Loader."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from utils.document_loader import extract_text_from_pdf


def test_extract_text_from_pdf_fitz_fallback(tmp_path) -> None:
    """Verifies that extract_text_from_pdf falls back to fitz and extracts page text."""
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Mocked PDF page content"
    mock_doc.__len__.return_value = 1
    mock_doc.__getitem__.return_value = mock_page

    with patch("fitz.open", return_value=mock_doc) as mock_open:
        dummy_pdf = tmp_path / "dummy.pdf"
        dummy_pdf.touch()

        # Disable pymupdf4llm mock-import to force fallback
        with patch.dict("sys.modules", {"pymupdf4llm": None}):
            pages = extract_text_from_pdf(str(dummy_pdf))

        assert len(pages) == 1
        assert pages[0]["page_number"] == 1
        assert pages[0]["text"] == "Mocked PDF page content"
        assert pages[0]["filename"] == "dummy.pdf"
        mock_open.assert_called_once_with(str(dummy_pdf))
