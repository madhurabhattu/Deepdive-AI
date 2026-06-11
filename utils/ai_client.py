"""
DeepDive AI — AI Client (Multi-Backend)

Supports two AI provider backends:
  - Gemini API  (cloud, BYOK)
  - Ollama      (local inference, no key required)

The active backend is driven by st.session_state["ai_provider"] and
st.session_state["byok_api_key"] set from the sidebar UI.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Load .env for local development — gracefully skip if python-dotenv is absent
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    logger.debug("python-dotenv not installed; skipping .env load.")

# ── Prompt template (shared across backends) ────────────────────────────────

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

# ── Ollama supported models ──────────────────────────────────────────────────

OLLAMA_MODELS: list[str] = ["llama3", "mistral", "gemma", "qwen"]
OLLAMA_BASE_URL: str = "http://localhost:11434"

__all__ = [
    "OLLAMA_BASE_URL",
    "OLLAMA_MODELS",
    "generate_research_report",
    "is_ollama_available",
]


def is_ollama_available() -> bool:
    """Check if Ollama server is reachable on http://localhost:11434."""
    import urllib.error
    import urllib.request

    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/tags",
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=2):
            return True
    except Exception:
        return False


# ── Gemini backend ───────────────────────────────────────────────────────────


def _get_gemini_api_key(byok_key: str | None = None) -> str:
    """Resolve the Gemini API key from BYOK input, then secrets, then env.

    Priority order
    --------------
    1. ``byok_key`` supplied directly from the sidebar UI.
    2. ``st.secrets["GEMINI_API_KEY"]`` (Streamlit Cloud deployment).
    3. ``GEMINI_API_KEY`` environment variable / ``.env`` file.

    Raises
    ------
    OSError
        If no valid key is found from any source.
    """
    # 1. BYOK from session state / caller
    if byok_key and byok_key.strip() not in ("", "your_gemini_api_key_here"):
        logger.info("Using BYOK Gemini API key from sidebar input.")
        return byok_key.strip()

    # 2. Streamlit secrets
    try:
        import streamlit as st

        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            key = str(st.secrets["GEMINI_API_KEY"]).strip()
            if key and key != "your_gemini_api_key_here":
                logger.info("Loaded GEMINI_API_KEY from Streamlit secrets.")
                return key
    except Exception as exc:
        logger.debug("Streamlit secrets unavailable: %s", exc)

    # 3. Environment variable / .env
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key and key != "your_gemini_api_key_here":
        logger.info("Loaded GEMINI_API_KEY from environment variables.")
        return key

    raise OSError(
        "GEMINI_API_KEY is not configured. Enter your key in the sidebar "
        "or configure it in Streamlit Secrets / your .env file."
    )


def _build_prompt(topic: str, report_lang: str) -> str:
    """Build the full research prompt including any localisation directive."""
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
            f'- Keep the JSON keys exactly in English (e.g. "executive_summary",'
            f' "term", "definition", "type", etc.) as defined in the schema '
            f"template. Do NOT translate the JSON keys."
        )
    return prompt


def _call_gemini(
    topic: str,
    report_lang: str = "en",
    byok_key: str | None = None,
) -> str:
    """Call the Gemini API and return raw JSON string.

    Raises
    ------
    RuntimeError
        On API failure or JSON parse error.
    """
    from google import genai
    from google.genai import types

    api_key = _get_gemini_api_key(byok_key)
    client = genai.Client(api_key=api_key)
    prompt = _build_prompt(topic, report_lang)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.7,
            ),
        )
        raw_text: str = response.text or ""
        raw_text = raw_text.strip()
        logger.info(
            "Gemini returned %d chars for topic '%s' [lang=%s]",
            len(raw_text),
            topic,
            report_lang,
        )
        json.loads(raw_text)  # sanity check
        return raw_text

    except Exception as exc:
        logger.error("Gemini API call failed: %s", exc)
        raise RuntimeError(
            f"Gemini generation failed. Please try again. (Detail: {exc})"
        ) from exc


# ── Ollama backend ───────────────────────────────────────────────────────────


def _check_ollama_available() -> None:
    """Verify that the Ollama server is reachable.

    Raises
    ------
    RuntimeError
        If Ollama is not running or not reachable.
    """
    import urllib.error
    import urllib.request

    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/tags",
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5):
            pass
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Ollama is not running at {OLLAMA_BASE_URL}. "
            "Start it with: `ollama serve`"
        ) from exc


def _call_ollama(
    topic: str,
    model: str,
    report_lang: str = "en",
) -> str:
    """Call a local Ollama model and return raw JSON string.

    Parameters
    ----------
    topic:
        Research topic string.
    model:
        One of ``OLLAMA_MODELS``.
    report_lang:
        Language code for the output report.

    Raises
    ------
    ValueError
        If ``model`` is not in the allowed list.
    RuntimeError
        If Ollama is unreachable or the response is not valid JSON.
    """
    import urllib.error
    import urllib.request

    if model not in OLLAMA_MODELS:
        raise ValueError(
            f"Invalid Ollama model '{model}'. "
            f"Allowed: {', '.join(OLLAMA_MODELS)}"
        )

    _check_ollama_available()

    prompt = _build_prompt(topic, report_lang)
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.7},
    }
    data = json.dumps(payload).encode("utf-8")

    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        raw_text: str = body.get("response", "").strip()
        logger.info(
            "Ollama (%s) returned %d chars for topic '%s' [lang=%s]",
            model,
            len(raw_text),
            topic,
            report_lang,
        )
        json.loads(raw_text)  # sanity check
        return raw_text

    except urllib.error.URLError as exc:
        logger.error("Ollama request failed: %s", exc)
        raise RuntimeError(
            f"Ollama request failed. Is it running? (Detail: {exc})"
        ) from exc
    except (KeyError, json.JSONDecodeError) as exc:
        logger.error("Ollama returned invalid JSON: %s", exc)
        raise RuntimeError(
            f"Ollama returned an unexpected response format. (Detail: {exc})"
        ) from exc


# ── Public interface ─────────────────────────────────────────────────────────


def generate_research_report(
    topic: str,
    report_lang: str = "en",
    provider: str = "gemini",
    byok_key: str | None = None,
    ollama_model: str = "llama3",
) -> str:
    """Generate a structured research report using the selected AI provider.

    Parameters
    ----------
    topic:
        User-provided research topic.
    report_lang:
        Language code ('en', 'hi', 'mr', 'te') for report content.
    provider:
        ``'gemini'`` (cloud) or ``'ollama'`` (local).
    byok_key:
        Optional Gemini API key entered by the user in the sidebar.
    ollama_model:
        Local model to use when ``provider='ollama'``.

    Returns
    -------
    str
        Raw JSON string matching the ResearchReport schema.

    Raises
    ------
    ValueError
        On invalid ``provider`` or ``ollama_model``.
    RuntimeError
        On any backend failure.
    """
    if provider in ("gemini_builtin", "gemini"):
        resolved_byok = byok_key if provider == "gemini" else None
        return _call_gemini(topic, report_lang, byok_key=resolved_byok)
    if provider == "gemini_byok":
        return _call_gemini(topic, report_lang, byok_key=byok_key)
    if provider == "ollama":
        return _call_ollama(topic, model=ollama_model, report_lang=report_lang)
    raise ValueError(
        f"Unknown AI provider '{provider}'. "
        "Use 'gemini_builtin', 'gemini_byok', or 'ollama'."
    )
