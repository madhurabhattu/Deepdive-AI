"""
DeepDive AI — Gemini AI Client

Sends structured prompts to the Gemini API and returns the raw JSON
string for downstream parsing by report_schema.parse_report().

Responsibilities:
- Load GEMINI_API_KEY from environment (via python-dotenv).
- Construct the research prompt.
- Call gemini-2.5-flash and return raw JSON.
- Raise RuntimeError on API failures.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _get_api_key() -> str:
    """Retrieve the Gemini API key from various configuration sources.

    Priority order:
    1. Streamlit secrets (for deployment)
    2. Environment variables (set directly in OS/container)
    3. Local .env file (development only)

    Raises
    ------
    OSError
        If GEMINI_API_KEY is not set or is set to a placeholder.
    """
    # 1. Try Streamlit secrets
    try:
        import streamlit as st

        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            key = st.secrets["GEMINI_API_KEY"]
            if isinstance(key, str):
                key = key.strip()
                if key and key != "your_gemini_api_key_here":
                    logger.info("Loaded GEMINI_API_KEY from Streamlit secrets.")
                    return key
    except Exception as exc:
        logger.debug("Failed to load API key from Streamlit secrets: %s", exc)

    # 2. Try environment variables (populated by load_dotenv from .env if present)
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key and key != "your_gemini_api_key_here":
        logger.info("Loaded GEMINI_API_KEY from environment variables.")
        return key

    raise OSError(
        "GEMINI_API_KEY is not configured. Please configure it in "
        "Streamlit Secrets, environment variables, or your .env file."
    )


_RESEARCH_PROMPT_TEMPLATE = """\
You are an expert research analyst. Given the topic below, produce a
comprehensive, well-structured research report.

TOPIC: {topic}

Return your response as a **single JSON object** with exactly these keys:

{{
  "executive_summary": "<a 150-250 word professional summary of the topic>",
  "background_context": "<a 100-150 word context/industry relevance>",
  "core_concepts": [
    {{
      "term": "<concept or term 1>",
      "definition": "<concise definition/explanation>"
    }},
    {{
      "term": "<concept or term 2>",
      "definition": "<concise definition/explanation>"
    }},
    {{
      "term": "<concept or term 3>",
      "definition": "<concise definition/explanation>"
    }}
  ],
  "key_insights": [
    "<major discovery, trend, or data-driven finding 1>",
    "<major discovery, trend, or data-driven finding 2>",
    "<major discovery, trend, or data-driven finding 3>",
    "<major discovery, trend, or data-driven finding 4>",
    "<major discovery, trend, or data-driven finding 5>"
  ],
  "benefits_challenges_risks": [
    {{
      "item": "<benefit/advantage 1>",
      "type": "benefit",
      "description": "<why it is beneficial>"
    }},
    {{
      "item": "<challenge/limitation 1>",
      "type": "challenge",
      "description": "<the limitation>"
    }},
    {{
      "item": "<risk/threat 1>",
      "type": "risk",
      "description": "<the risk or trade-off>"
    }}
  ],
  "real_world_applications": [
    {{
      "application": "<practical use case or success story 1>",
      "description": "<details of industry adoption>"
    }},
    {{
      "application": "<practical use case or success story 2>",
      "description": "<details of industry adoption>"
    }},
    {{
      "application": "<practical use case or success story 3>",
      "description": "<details of industry adoption>"
    }}
  ],
  "future_outlook": [
    "<emerging trend or strategic recommendation 1>",
    "<emerging trend or strategic recommendation 2>",
    "<emerging trend or strategic recommendation 3>"
  ],
  "statistics": [
    {{"label": "<metric name>", "value": "<metric value>"}},
    {{"label": "<metric name>", "value": "<metric value>"}},
    {{"label": "<metric name>", "value": "<metric value>"}}
  ],
  "references": [
    {{
      "title": "<source title>",
      "url": "<source URL>",
      "snippet": "<1-2 sentence description>"
    }},
    {{
      "title": "<source title>",
      "url": "<source URL>",
      "snippet": "<1-2 sentence description>"
    }},
    {{
      "title": "<source title>",
      "url": "<source URL>",
      "snippet": "<1-2 sentence description>"
    }},
    {{
      "title": "<source title>",
      "url": "<source URL>",
      "snippet": "<1-2 sentence description>"
    }},
    {{
      "title": "<source title>",
      "url": "<source URL>",
      "snippet": "<1-2 sentence description>"
    }}
  ]
}}

RULES:
- Return ONLY the JSON object. No markdown fences, no extra text.
- Provide exactly the keys listed.
- All content must be factual, professional, and well-researched.
"""


def generate_research_report(topic: str, report_lang: str = "en") -> str:
    """Send a research prompt to Gemini and return the raw JSON response.

    Parameters
    ----------
    topic : str
        The user-provided research topic.
    report_lang : str
        The language code ('en', 'hi', 'mr', 'te') for the output report.

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
    client = genai.Client(api_key=api_key)

    lang_names = {
        "en": "English",
        "hi": "Hindi",
        "mr": "Marathi",
        "te": "Telugu",
    }
    lang_name = lang_names.get(report_lang, "English")

    prompt = _RESEARCH_PROMPT_TEMPLATE.format(topic=topic)
    if report_lang != "en":
        prompt += (
            f"\nCRITICAL LOCALIZATION RULE:\n"
            f"- Generate the entire research report content in the "
            f"{lang_name} language.\n"
            f"- Translate all strings (such as summaries, terms, definitions, "
            f"key insights, benefits, descriptions, applications, future "
            f"outlooks, metrics labels, reference snippets, etc.) "
            f"fully into {lang_name}.\n"
            f'- Keep the JSON keys exactly in English (e.g. "executive_summary", '
            f'"term", "definition", "type", etc.) as defined in the schema '
            f"template. Do NOT translate the JSON keys."
        )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.7,
            ),
        )

        raw_text = response.text.strip()
        logger.info(
            "Gemini returned %d characters for topic '%s' in language '%s'",
            len(raw_text),
            topic,
            report_lang,
        )

        # Quick sanity check: is this parseable JSON?
        json.loads(raw_text)

        return raw_text

    except Exception as exc:
        logger.error("Gemini API call failed for topic '%s': %s", topic, exc)
        raise RuntimeError(
            f"Research generation failed. Please try again. (Detail: {exc})"
        ) from exc
