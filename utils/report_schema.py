"""
DeepDive AI — Report Schema

Defines the ResearchReport dataclass and the parse_report() validator
that converts raw AI JSON into a validated Python object.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ResearchReport:
    """Canonical data model for a generated research report.

    Every research run must produce a consistent, validated instance of this
    class before rendering or exporting (Constitution §V).
    """

    topic: str
    executive_summary: str
    key_insights: list[str] = field(default_factory=list)
    statistics: list[dict[str, str]] = field(default_factory=list)
    references: list[dict[str, str]] = field(default_factory=list)


def parse_report(raw_json: str, topic: str) -> ResearchReport:
    """Parse and validate an AI-generated JSON string into a ResearchReport.

    Parameters
    ----------
    raw_json : str
        The raw JSON string returned by the AI backend.
    topic : str
        The original user-provided research topic.

    Returns
    -------
    ResearchReport
        A validated report dataclass instance.

    Raises
    ------
    ValueError
        If the JSON is malformed, missing required fields, or contains
        fewer than 3 items in insights/statistics/references.
    """
    # ── 1. Parse JSON ────────────────────────────────────────────────
    try:
        data: dict[str, Any] = json.loads(raw_json)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.error("Malformed JSON from AI: %s", exc)
        raise ValueError(f"AI returned invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("AI response must be a JSON object (dict).")

    # ── 2. Extract required scalar fields ────────────────────────────
    executive_summary = data.get("executive_summary")
    if not executive_summary or not isinstance(executive_summary, str):
        raise ValueError(
            "Missing or invalid 'executive_summary' in AI response."
        )

    # ── 3. Extract and validate list fields ─────────────────────────
    key_insights = data.get("key_insights", [])
    if not isinstance(key_insights, list) or len(key_insights) < 3:
        raise ValueError(
            f"'key_insights' must be a list with at least 3 items "
            f"(got {len(key_insights) if isinstance(key_insights, list) else 'non-list'})."
        )
    # Ensure every insight is a non-empty string
    key_insights = [str(i).strip() for i in key_insights if str(i).strip()]
    if len(key_insights) < 3:
        raise ValueError(
            "'key_insights' must contain at least 3 non-empty strings."
        )

    statistics = data.get("statistics", [])
    if not isinstance(statistics, list) or len(statistics) < 3:
        raise ValueError(
            f"'statistics' must be a list with at least 3 items "
            f"(got {len(statistics) if isinstance(statistics, list) else 'non-list'})."
        )
    # Validate each statistic has label + value
    for idx, stat in enumerate(statistics):
        if not isinstance(stat, dict):
            raise ValueError(f"statistics[{idx}] must be a dict.")
        if "label" not in stat or "value" not in stat:
            raise ValueError(
                f"statistics[{idx}] must have 'label' and 'value' keys."
            )

    references = data.get("references", [])
    if not isinstance(references, list) or len(references) < 3:
        raise ValueError(
            f"'references' must be a list with at least 3 items "
            f"(got {len(references) if isinstance(references, list) else 'non-list'})."
        )
    # Validate each reference has title, url, snippet
    for idx, ref in enumerate(references):
        if not isinstance(ref, dict):
            raise ValueError(f"references[{idx}] must be a dict.")
        for key in ("title", "url", "snippet"):
            if key not in ref:
                raise ValueError(
                    f"references[{idx}] is missing required key '{key}'."
                )

    # ── 4. Build and return validated dataclass ─────────────────────
    return ResearchReport(
        topic=topic,
        executive_summary=executive_summary.strip(),
        key_insights=key_insights,
        statistics=statistics,
        references=references,
    )
