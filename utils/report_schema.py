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


REQUIRED_FIELDS = [
    "executive_summary",
    "background_context",
    "core_concepts",
    "key_insights",
    "benefits_challenges_risks",
    "real_world_applications",
    "future_outlook",
    "statistics",
    "references",
]


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
    warnings: list[str] = field(default_factory=list)


def parse_report(raw_json: str, topic: str, strict: bool = True) -> ResearchReport:
    """Parse and validate an AI-generated JSON string into a ResearchReport.

    Parameters
    ----------
    raw_json : str
        The raw JSON string returned by the AI backend.
    topic : str
        The original user-provided research topic.
    strict : bool
        If True, run strict validations. If False, normalize/auto-correct.

    Returns
    -------
    ResearchReport
        A validated report dataclass instance.

    Raises
    ------
    ValueError
        If the JSON is malformed, missing required fields, or contains
        fewer than 3 items (under strict=True).
    """
    # Task 1: Print the complete expected schema
    logger.info("EXPECTED SCHEMA: %s", REQUIRED_FIELDS)

    # ── 1. Parse JSON ────────────────────────────────────────────────
    try:
        data: dict[str, Any] = json.loads(raw_json)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.error("Malformed JSON from AI: %s", exc)
        raise ValueError(f"AI returned invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("AI response must be a JSON object (dict).")

    # Task 2: Print parsed JSON keys
    logger.info("PARSED KEYS: %s", list(data.keys()))

    # Task 5: Log the parsed response dictionary before validation
    logger.info("Parsed response before validation: %s", data)

    warnings_list: list[str] = []

    # ── 2. Normalization Layer (Tolerant Mode) ──────────────────────
    if not strict:
        # Convert camelCase keys to snake_case
        import re

        camel_to_snake_mapping = {
            "executiveSummary": "executive_summary",
            "backgroundContext": "background_context",
            "coreConcepts": "core_concepts",
            "keyInsights": "key_insights",
            "benefitsChallengesRisks": "benefits_challenges_risks",
            "realWorldApplications": "real_world_applications",
            "futureOutlook": "future_outlook",
        }
        normalized_data = {}
        for k, v in data.items():
            new_key = camel_to_snake_mapping.get(k, k)
            if new_key == k:
                new_key = re.sub(r"(?<!^)(?=[A-Z])", "_", k).lower()
            normalized_data[new_key] = v
        data = normalized_data

    # Task 3: Show exact missing fields
    missing_fields = [field for field in REQUIRED_FIELDS if field not in data]

    # Store in streamlit session state if streamlit is imported
    try:
        import streamlit as st

        st.session_state["missing_fields"] = missing_fields
    except ImportError:
        pass

    if strict and missing_fields:
        raise ValueError(f"Missing fields: {missing_fields}")

    # ── 2.1 Tolerant Mode Padding (Only if not strict) ────────────────
    if not strict:
        # Scalar fields
        if "executive_summary" not in data or not data["executive_summary"]:
            data["executive_summary"] = (
                f"Executive summary for research topic: {topic}. "
                "The model did not generate a summary."
            )
            warnings_list.append(
                "Executive summary was missing and generated automatically."
            )
        if "background_context" not in data or not data["background_context"]:
            data["background_context"] = (
                f"Background context for research topic: {topic}. "
                "The model did not populate this background information."
            )
            warnings_list.append(
                "Background context was missing and generated automatically."
            )

        # Core Concepts
        if "core_concepts" not in data or not isinstance(data["core_concepts"], list):
            data["core_concepts"] = []

        normalized_cc = []
        for item in data["core_concepts"]:
            if isinstance(item, dict):
                normalized_cc.append(item)
            elif isinstance(item, str):
                normalized_cc.append(
                    {
                        "term": item,
                        "definition": (
                            f"Refer to main report content for details on {item}."
                        ),
                    }
                )
        data["core_concepts"] = normalized_cc

        for item in data["core_concepts"]:
            if "term" not in item or not item["term"]:
                item["term"] = "Concept term"
            if "definition" not in item or not item["definition"]:
                item["definition"] = "Definition of the concept."

        padded_cc = False
        while len(data["core_concepts"]) < 3:
            padded_cc = True
            idx = len(data["core_concepts"]) + 1
            data["core_concepts"].append(
                {
                    "term": f"Topic discussion area {idx}",
                    "definition": (
                        "Refer to the executive summary or background context "
                        "for details on this area."
                    ),
                }
            )
        if padded_cc:
            warnings_list.append(
                "Model returned fewer core_concepts than expected. "
                "Missing concepts were generated automatically."
            )

        # Key Insights
        if "key_insights" not in data or not isinstance(data["key_insights"], list):
            data["key_insights"] = []
        data["key_insights"] = [
            str(i).strip() for i in data["key_insights"] if str(i).strip()
        ]
        padded_ki = False
        while len(data["key_insights"]) < 3:
            padded_ki = True
            idx = len(data["key_insights"]) + 1
            data["key_insights"].append(
                "Key insight not generated by the model (refer to main "
                f"report text) {idx}."
            )
        if padded_ki:
            warnings_list.append(
                "Model returned fewer key insights than expected. "
                "Missing insights were generated automatically."
            )

        # Benefits, Challenges & Risks
        if "benefits_challenges_risks" not in data or not isinstance(
            data["benefits_challenges_risks"], list
        ):
            data["benefits_challenges_risks"] = []

        normalized_bcr = []
        for item in data["benefits_challenges_risks"]:
            if isinstance(item, dict):
                normalized_bcr.append(item)
            elif isinstance(item, str):
                item_lower = item.lower()
                t = "benefit"
                if (
                    "challenge" in item_lower
                    or "limitation" in item_lower
                    or "con" in item_lower
                ):
                    t = "challenge"
                elif (
                    "risk" in item_lower
                    or "threat" in item_lower
                    or "danger" in item_lower
                ):
                    t = "risk"
                normalized_bcr.append(
                    {
                        "item": item,
                        "type": t,
                        "description": f"Analysis regarding {item}.",
                    }
                )
        data["benefits_challenges_risks"] = normalized_bcr

        for item in data["benefits_challenges_risks"]:
            if "item" not in item or not item["item"]:
                item["item"] = "Additional aspect"
            if "type" not in item or not item["type"]:
                item["type"] = "benefit"
            if "description" not in item or not item["description"]:
                item["description"] = (
                    "Specific details regarding this aspect were not "
                    "populated by the AI."
                )

        types_list = ["benefit", "challenge", "risk"]
        padded_bcr = False
        while len(data["benefits_challenges_risks"]) < 3:
            padded_bcr = True
            idx = len(data["benefits_challenges_risks"]) + 1
            t_type = types_list[(idx - 1) % 3]
            data["benefits_challenges_risks"].append(
                {
                    "item": "Additional aspect",
                    "type": t_type,
                    "description": (
                        f"Specific details regarding this {t_type} aspect were not "
                        "populated by the AI."
                    ),
                }
            )
        if padded_bcr:
            warnings_list.append(
                "Model returned fewer benefits/challenges/risks than expected. "
                "Missing items were generated automatically."
            )

        # Real World Applications
        if "real_world_applications" not in data or not isinstance(
            data["real_world_applications"], list
        ):
            data["real_world_applications"] = []

        normalized_rwa = []
        for item in data["real_world_applications"]:
            if isinstance(item, dict):
                normalized_rwa.append(item)
            elif isinstance(item, str):
                normalized_rwa.append(
                    {
                        "application": item,
                        "description": f"Practical application of {item}.",
                    }
                )
        data["real_world_applications"] = normalized_rwa

        for item in data["real_world_applications"]:
            if "application" not in item or not item["application"]:
                item["application"] = "Industry adoption use case"
            if "description" not in item or not item["description"]:
                item["description"] = (
                    "Adoption details for this use case are not specified."
                )

        padded_rwa = False
        while len(data["real_world_applications"]) < 3:
            padded_rwa = True
            idx = len(data["real_world_applications"]) + 1
            data["real_world_applications"].append(
                {
                    "application": "Industry adoption use case",
                    "description": (
                        "Adoption details for this use case are not specified."
                    ),
                }
            )
        if padded_rwa:
            warnings_list.append(
                "Model returned fewer real-world applications than expected. "
                "Missing applications were generated automatically."
            )

        # Future Outlook
        if "future_outlook" not in data or not isinstance(data["future_outlook"], list):
            data["future_outlook"] = []
        data["future_outlook"] = [
            str(i).strip() for i in data["future_outlook"] if str(i).strip()
        ]
        padded_fo = False
        while len(data["future_outlook"]) < 3:
            padded_fo = True
            idx = len(data["future_outlook"]) + 1
            data["future_outlook"].append(
                "Emerging trend or strategic recommendation details are unavailable."
            )
        if padded_fo:
            warnings_list.append(
                "Model returned fewer future outlook items than expected. "
                "Missing items were generated automatically."
            )

        # Statistics
        if "statistics" not in data or not isinstance(data["statistics"], list):
            data["statistics"] = []

        normalized_stats = []
        for item in data["statistics"]:
            if isinstance(item, dict):
                normalized_stats.append(item)
            elif isinstance(item, str):
                if ":" in item:
                    parts = item.split(":", 1)
                    normalized_stats.append(
                        {
                            "label": parts[0].strip(),
                            "value": parts[1].strip(),
                        }
                    )
                else:
                    normalized_stats.append(
                        {
                            "label": item,
                            "value": "Value",
                        }
                    )
        data["statistics"] = normalized_stats

        for item in data["statistics"]:
            if "label" in item and isinstance(item["label"], dict):
                item["label"] = (
                    item["label"].get("label")
                    or item["label"].get("value")
                    or str(item["label"])
                )
            if "value" in item and isinstance(item["value"], dict):
                item["value"] = (
                    item["value"].get("value")
                    or item["value"].get("label")
                    or str(item["value"])
                )

            if "label" not in item or not item["label"]:
                item["label"] = "Metric"
            if "value" not in item or not item["value"]:
                item["value"] = "N/A"

        padded_s = False
        while len(data["statistics"]) < 3:
            padded_s = True
            idx = len(data["statistics"]) + 1
            data["statistics"].append(
                {
                    "label": "Additional metric",
                    "value": "N/A",
                }
            )
        if padded_s:
            warnings_list.append(
                "Model returned fewer statistics than expected. "
                "Missing statistics were generated automatically."
            )

        # References
        if "references" not in data or not isinstance(data["references"], list):
            data["references"] = []

        normalized_ref = []
        for item in data["references"]:
            if isinstance(item, dict):
                normalized_ref.append(item)
            elif isinstance(item, str):
                normalized_ref.append(
                    {
                        "title": item,
                        "url": "https://example.com",
                        "snippet": f"Reference source for {item}.",
                    }
                )
        data["references"] = normalized_ref

        for item in data["references"]:
            if "title" not in item or not item["title"]:
                item["title"] = "Reference Source"
            if "url" not in item or not item["url"]:
                item["url"] = "https://example.com"
            if "snippet" not in item or not item["snippet"]:
                item["snippet"] = "Source reference information."

        padded_r = False
        while len(data["references"]) < 3:
            padded_r = True
            idx = len(data["references"]) + 1
            data["references"].append(
                {
                    "title": f"Reference Source {idx}",
                    "url": "https://example.com",
                    "snippet": f"Additional reference info for {topic}.",
                }
            )
        if padded_r:
            warnings_list.append(
                "Model returned fewer references than expected. "
                "Missing references were generated automatically."
            )

    # ── 3. Extract required scalar fields ────────────────────────────
    executive_summary = data.get("executive_summary")
    if not executive_summary or not isinstance(executive_summary, str):
        raise ValueError("Missing or invalid 'executive_summary' in AI response.")

    background_context = data.get("background_context")
    if not background_context or not isinstance(background_context, str):
        raise ValueError("Missing or invalid 'background_context' in AI response.")

    # ── 4. Extract and validate list fields ─────────────────────────
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

    # ── 5. Build and return validated dataclass ─────────────────────
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
        warnings=warnings_list,
    )
