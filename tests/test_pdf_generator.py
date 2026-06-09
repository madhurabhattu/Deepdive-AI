"""
Unit tests for utils/pdf_generator.py

Covers:
- build_pdf() creates a file at the returned path
- File size > 0 bytes
- Filepath ends with .pdf
- sanitise_filename replaces special chars
"""

import os
import pytest

from utils.report_schema import ResearchReport
from utils.pdf_generator import build_pdf, sanitise_filename


@pytest.fixture
def mock_report() -> ResearchReport:
    """Return a valid ResearchReport for testing."""
    return ResearchReport(
        topic="Quantum Computing",
        executive_summary=(
            "Quantum computing is a rapidly advancing field that leverages "
            "quantum mechanical phenomena to perform computations far beyond "
            "the capabilities of classical computers."
        ),
        key_insights=[
            "Quantum computers use qubits instead of classical bits.",
            "Superposition allows qubits to represent 0 and 1 simultaneously.",
            "Quantum entanglement enables faster information processing.",
            "Error correction remains a major research challenge.",
            "Commercial quantum advantage is expected within the next decade.",
        ],
        statistics=[
            {"label": "Market Size (2025)", "value": "$8.6 billion"},
            {"label": "CAGR 2025-2030", "value": "32.7%"},
            {"label": "Active Research Labs", "value": "200+"},
            {"label": "Qubits in Leading Systems", "value": "1,121"},
            {"label": "Investment in 2024", "value": "$1.2 billion"},
        ],
        references=[
            {
                "title": "IBM Quantum Research",
                "url": "https://www.ibm.com/quantum",
                "snippet": "IBM leads enterprise quantum computing research.",
            },
            {
                "title": "Google Quantum AI",
                "url": "https://quantumai.google/",
                "snippet": "Google achieved quantum supremacy in 2019.",
            },
            {
                "title": "Nature: Quantum Computing Review",
                "url": "https://www.nature.com/subjects/quantum-computing",
                "snippet": "A comprehensive review of quantum computing advances.",
            },
        ],
    )


class TestSanitiseFilename:
    """Tests for the filename sanitisation helper."""

    def test_replaces_special_chars(self):
        assert sanitise_filename("Hello/World:Test") == "hello_world_test"

    def test_replaces_spaces(self):
        assert sanitise_filename("Quantum Computing 101") == "quantum_computing_101"

    def test_truncates_long_names(self):
        long_topic = "a" * 200
        result = sanitise_filename(long_topic)
        assert len(result) <= 80


class TestBuildPdf:
    """Tests for PDF generation."""

    def test_file_exists_at_returned_path(self, mock_report: ResearchReport):
        filepath = build_pdf(mock_report)
        assert os.path.exists(filepath)

    def test_file_size_greater_than_zero(self, mock_report: ResearchReport):
        filepath = build_pdf(mock_report)
        assert os.path.getsize(filepath) > 0

    def test_filepath_ends_with_pdf(self, mock_report: ResearchReport):
        filepath = build_pdf(mock_report)
        assert filepath.endswith(".pdf")

    def test_filename_contains_sanitised_topic(self, mock_report: ResearchReport):
        filepath = build_pdf(mock_report)
        assert "quantum_computing" in os.path.basename(filepath)
