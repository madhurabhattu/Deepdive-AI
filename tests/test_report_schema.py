"""
Unit tests for utils/report_schema.py

Covers:
- Valid full JSON → correct ResearchReport
- Missing executive_summary → ValueError
- Fewer than 3 insights → ValueError
- Malformed JSON string → ValueError
"""

import json

import pytest

from utils.report_schema import ResearchReport, parse_report

# ── Fixtures ────────────────────────────────────────────────────────

def _make_valid_data() -> dict:
    """Return a minimal valid report payload."""
    return {
        "executive_summary": "This is a comprehensive overview of quantum computing.",
        "key_insights": [
            "Quantum computers use qubits instead of classical bits.",
            "Superposition allows qubits to represent 0 and 1 simultaneously.",
            "Quantum entanglement enables faster information processing.",
        ],
        "statistics": [
            {"label": "Market Size (2025)", "value": "$8.6 billion"},
            {"label": "CAGR 2025–2030", "value": "32.7%"},
            {"label": "Active Research Labs", "value": "200+"},
        ],
        "references": [
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
    }


# ── Happy Path ──────────────────────────────────────────────────────

class TestParseReportValid:
    """Tests for valid AI responses."""

    def test_returns_research_report(self):
        raw = json.dumps(_make_valid_data())
        report = parse_report(raw, topic="Quantum Computing")

        assert isinstance(report, ResearchReport)
        assert report.topic == "Quantum Computing"

    def test_executive_summary_populated(self):
        raw = json.dumps(_make_valid_data())
        report = parse_report(raw, topic="Quantum Computing")

        assert "quantum computing" in report.executive_summary.lower()

    def test_key_insights_count(self):
        raw = json.dumps(_make_valid_data())
        report = parse_report(raw, topic="Quantum Computing")

        assert len(report.key_insights) >= 3

    def test_statistics_count(self):
        raw = json.dumps(_make_valid_data())
        report = parse_report(raw, topic="Quantum Computing")

        assert len(report.statistics) >= 3
        for stat in report.statistics:
            assert "label" in stat
            assert "value" in stat

    def test_references_count(self):
        raw = json.dumps(_make_valid_data())
        report = parse_report(raw, topic="Quantum Computing")

        assert len(report.references) >= 3
        for ref in report.references:
            assert "title" in ref
            assert "url" in ref
            assert "snippet" in ref


# ── Error Cases ─────────────────────────────────────────────────────

class TestParseReportErrors:
    """Tests for invalid AI responses."""

    def test_missing_executive_summary_raises(self):
        data = _make_valid_data()
        del data["executive_summary"]
        raw = json.dumps(data)

        with pytest.raises(ValueError, match="executive_summary"):
            parse_report(raw, topic="Test")

    def test_empty_executive_summary_raises(self):
        data = _make_valid_data()
        data["executive_summary"] = ""
        raw = json.dumps(data)

        with pytest.raises(ValueError, match="executive_summary"):
            parse_report(raw, topic="Test")

    def test_fewer_than_3_insights_raises(self):
        data = _make_valid_data()
        data["key_insights"] = ["Only one insight", "And a second"]
        raw = json.dumps(data)

        with pytest.raises(ValueError, match="key_insights"):
            parse_report(raw, topic="Test")

    def test_fewer_than_3_statistics_raises(self):
        data = _make_valid_data()
        data["statistics"] = [{"label": "A", "value": "1"}]
        raw = json.dumps(data)

        with pytest.raises(ValueError, match="statistics"):
            parse_report(raw, topic="Test")

    def test_fewer_than_3_references_raises(self):
        data = _make_valid_data()
        data["references"] = [
            {"title": "A", "url": "http://a.com", "snippet": "a"},
        ]
        raw = json.dumps(data)

        with pytest.raises(ValueError, match="references"):
            parse_report(raw, topic="Test")

    def test_malformed_json_raises(self):
        with pytest.raises(ValueError, match="invalid JSON"):
            parse_report("{not valid json!!!", topic="Test")

    def test_non_dict_json_raises(self):
        with pytest.raises(ValueError, match="JSON object"):
            parse_report('"just a string"', topic="Test")

    def test_statistic_missing_label_raises(self):
        data = _make_valid_data()
        data["statistics"][0] = {"value": "100"}  # missing label
        raw = json.dumps(data)

        with pytest.raises(ValueError, match="label"):
            parse_report(raw, topic="Test")

    def test_reference_missing_url_raises(self):
        data = _make_valid_data()
        data["references"][0] = {"title": "A", "snippet": "a"}  # missing url
        raw = json.dumps(data)

        with pytest.raises(ValueError, match="url"):
            parse_report(raw, topic="Test")
