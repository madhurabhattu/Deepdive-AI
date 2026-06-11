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
    background_context: str
    core_concepts: list[dict[str, str]] = field(default_factory=list)
    key_insights: list[str] = field(default_factory=list)
    benefits_challenges_risks: list[dict[str, str]] = field(default_factory=list)
    real_world_applications: list[dict[str, str]] = field(default_factory=list)
    future_outlook: list[str] = field(default_factory=list)
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
        raise ValueError("Missing or invalid 'executive_summary' in AI response.")

    background_context = data.get("background_context")
    if not background_context or not isinstance(background_context, str):
        raise ValueError("Missing or invalid 'background_context' in AI response.")

    # ── 3. Extract and validate list fields ─────────────────────────
    # Core Concepts
    core_concepts = data.get("core_concepts", [])
    if not isinstance(core_concepts, list) or len(core_concepts) < 3:
        got = len(core_concepts) if isinstance(core_concepts, list) else "non-list"
        raise ValueError(
            f"'core_concepts' must be a list with at least 3 items (got {got})."
        )
    for idx, item in enumerate(core_concepts):
        if not isinstance(item, dict):
            raise ValueError(f"core_concepts[{idx}] must be a dict.")
        if "term" not in item or "definition" not in item:
            raise ValueError(
                f"core_concepts[{idx}] must have 'term' and 'definition' keys."
            )

    # Key Insights
    key_insights = data.get("key_insights", [])
    if not isinstance(key_insights, list) or len(key_insights) < 3:
        got = len(key_insights) if isinstance(key_insights, list) else "non-list"
        raise ValueError(
            f"'key_insights' must be a list with at least 3 items (got {got})."
        )
    key_insights = [str(i).strip() for i in key_insights if str(i).strip()]
    if len(key_insights) < 3:
        raise ValueError("'key_insights' must contain at least 3 non-empty strings.")

    # Benefits, Challenges & Risks
    benefits_challenges = data.get("benefits_challenges_risks", [])
    if not isinstance(benefits_challenges, list) or len(benefits_challenges) < 3:
        got = (
            len(benefits_challenges)
            if isinstance(benefits_challenges, list)
            else "non-list"
        )
        raise ValueError(
            f"'benefits_challenges_risks' must be a list with at least 3 "
            f"items (got {got})."
        )
    for idx, item in enumerate(benefits_challenges):
        if not isinstance(item, dict):
            raise ValueError(f"benefits_challenges_risks[{idx}] must be a dict.")
        if not all(k in item for k in ("item", "type", "description")):
            raise ValueError(
                f"benefits_challenges_risks[{idx}] must have 'item', "
                "'type', and 'description' keys."
            )

    # Real World Applications
    real_world_apps = data.get("real_world_applications", [])
    if not isinstance(real_world_apps, list) or len(real_world_apps) < 3:
        got = len(real_world_apps) if isinstance(real_world_apps, list) else "non-list"
        raise ValueError(
            f"'real_world_applications' must be a list with at least 3 "
            f"items (got {got})."
        )
    for idx, item in enumerate(real_world_apps):
        if not isinstance(item, dict):
            raise ValueError(f"real_world_applications[{idx}] must be a dict.")
        if "application" not in item or "description" not in item:
            raise ValueError(
                f"real_world_applications[{idx}] must have 'application' "
                "and 'description' keys."
            )

    # Future Outlook
    future_outlook = data.get("future_outlook", [])
    if not isinstance(future_outlook, list) or len(future_outlook) < 3:
        got = len(future_outlook) if isinstance(future_outlook, list) else "non-list"
        raise ValueError(
            f"'future_outlook' must be a list with at least 3 items (got {got})."
        )
    future_outlook = [str(i).strip() for i in future_outlook if str(i).strip()]
    if len(future_outlook) < 3:
        raise ValueError("'future_outlook' must contain at least 3 non-empty strings.")

    # Statistics
    statistics = data.get("statistics", [])
    if not isinstance(statistics, list) or len(statistics) < 3:
        got = len(statistics) if isinstance(statistics, list) else "non-list"
        raise ValueError(
            f"'statistics' must be a list with at least 3 items (got {got})."
        )
    for idx, stat in enumerate(statistics):
        if not isinstance(stat, dict):
            raise ValueError(f"statistics[{idx}] must be a dict.")
        if "label" not in stat or "value" not in stat:
            raise ValueError(f"statistics[{idx}] must have 'label' and 'value' keys.")

    # References
    references = data.get("references", [])
    if not isinstance(references, list) or len(references) < 3:
        got = len(references) if isinstance(references, list) else "non-list"
        raise ValueError(
            f"'references' must be a list with at least 3 items (got {got})."
        )
    for idx, ref in enumerate(references):
        if not isinstance(ref, dict):
            raise ValueError(f"references[{idx}] must be a dict.")
        for key in ("title", "url", "snippet"):
            if key not in ref:
                raise ValueError(f"references[{idx}] is missing required key '{key}'.")

    # ── 4. Build and return validated dataclass ─────────────────────
    return ResearchReport(
        topic=topic,
        executive_summary=executive_summary.strip(),
        background_context=background_context.strip(),
        core_concepts=core_concepts,
        key_insights=key_insights,
        benefits_challenges_risks=benefits_challenges,
        real_world_applications=real_world_apps,
        future_outlook=future_outlook,
        statistics=statistics,
        references=references,
    )
