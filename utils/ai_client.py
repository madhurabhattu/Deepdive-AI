"""
DeepDive AI — Gemini AI Client

Sends structured prompts to the Gemini API and returns the raw JSON
string for downstream parsing by report_schema.parse_report().

Responsibilities:
- Load GEMINI_API_KEY from environment (via python-dotenv).
- Construct the research prompt.
- Call gemini-1.5-flash and return raw JSON.
- Raise RuntimeError on API failures.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _get_api_key() -> str:
    """Retrieve the Gemini API key from environment variables.

    Raises
    ------
    EnvironmentError
        If GEMINI_API_KEY is not set or is empty.
    """
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or key == "your_gemini_api_key_here":
        raise OSError(
            "GEMINI_API_KEY is not configured. "
            "Please set it in your .env file. "
            "See .env.example for the expected format."
        )
    return key


_RESEARCH_PROMPT_TEMPLATE = """\
You are an expert research analyst. Given the topic below, produce a
comprehensive, well-structured research report.

TOPIC: {topic}

Return your response as a **single JSON object** with exactly these keys:

{{
  "executive_summary": "<a 150-250 word professional summary of the topic>",
  "key_insights": [
    "<insight 1>",
    "<insight 2>",
    "<insight 3>",
    "<insight 4>",
    "<insight 5>"
  ],
  "statistics": [
    {{"label": "<metric name>", "value": "<metric value>"}},
    {{"label": "<metric name>", "value": "<metric value>"}},
    {{"label": "<metric name>", "value": "<metric value>"}},
    {{"label": "<metric name>", "value": "<metric value>"}},
    {{"label": "<metric name>", "value": "<metric value>"}}
  ],
  "references": [
    {{"title": "<source title>", "url": "<source URL>", "snippet": "<1-2 sentence description>"}},
    {{"title": "<source title>", "url": "<source URL>", "snippet": "<1-2 sentence description>"}},
    {{"title": "<source title>", "url": "<source URL>", "snippet": "<1-2 sentence description>"}},
    {{"title": "<source title>", "url": "<source URL>", "snippet": "<1-2 sentence description>"}},
    {{"title": "<source title>", "url": "<source URL>", "snippet": "<1-2 sentence description>"}}
  ]
}}

RULES:
- Return ONLY the JSON object. No markdown fences, no extra text.
- Provide at least 5 key insights.
- Provide at least 5 statistics with real, plausible data.
- Provide at least 5 references with valid-looking URLs.
- All content must be factual, professional, and well-researched.
"""


def generate_research_report(topic: str) -> str:
    """Send a research prompt to Gemini and return the raw JSON response.

    Parameters
    ----------
    topic : str
        The user-provided research topic.

    Returns
    -------
    str
        Raw JSON string matching the ResearchReport schema.

    Raises
    ------
    EnvironmentError
        If the API key is missing.
    RuntimeError
        If the Gemini API call fails for any reason.
    """
    api_key = _get_api_key()
    genai.configure(api_key=api_key)

    prompt = _RESEARCH_PROMPT_TEMPLATE.format(topic=topic)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7,
            ),
        )

        raw_text = response.text.strip()
        logger.info("Gemini returned %d characters for topic '%s'", len(raw_text), topic)

        # Quick sanity check: is this parseable JSON?
        json.loads(raw_text)

        return raw_text

    except Exception as exc:
        logger.error("Gemini API call failed for topic '%s': %s", topic, exc)
        raise RuntimeError(
            f"Research generation failed. Please try again. (Detail: {exc})"
        ) from exc
