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
from collections.abc import Generator
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Load .env for local development — gracefully skip if python-dotenv is absent
try:
    from dotenv import load_dotenv  # type: ignore[import-not-found]

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

OLLAMA_MODELS: list[str] = [
    "llama3.1:8b",
    "llama3",
    "mistral",
    "gemma",
    "qwen",
    "qwen2.5-coder:3b",
    "phi",
]


def _resolve_ollama_base_url() -> str:
    """Resolve the Ollama base URL.

    Resolves from environment variables (OLLAMA_BASE_URL or OLLAMA_HOST),
    falling back to host.docker.internal if inside a Docker container,
    and defaulting to http://localhost:11434.
    """
    env_url = os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST")
    if env_url:
        url = env_url.strip()
        if not url.startswith(("http://", "https://")):
            url = f"http://{url}"
        return url

    # Detect container environment
    in_container = os.path.exists("/.dockerenv")
    if not in_container and os.path.exists("/proc/1/cgroup"):
        try:
            with open("/proc/1/cgroup", encoding="utf-8") as f:
                in_container = any(
                    "docker" in line or "containerd" in line for line in f
                )
        except Exception:  # nosec B110
            pass

    if in_container:
        import socket

        try:
            # Quick DNS resolution check for host.docker.internal
            socket.gethostbyname("host.docker.internal")
            return "http://host.docker.internal:11434"
        except socket.gaierror:
            pass

    return "http://localhost:11434"


OLLAMA_BASE_URL: str = _resolve_ollama_base_url()

__all__ = [
    "OLLAMA_BASE_URL",
    "OLLAMA_MODELS",
    "generate_research_report",
    "is_ollama_available",
    "stream_chat",
]


def is_ollama_available() -> bool:
    """Check if Ollama server is reachable on OLLAMA_BASE_URL."""
    import urllib.error
    import urllib.request

    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/tags",
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=2):  # nosec B310
            return True
    except Exception as exc:
        logger.warning("Ollama server at %s not reachable: %s", OLLAMA_BASE_URL, exc)
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
    import random
    import time

    from google import genai
    from google.genai import types

    api_key = _get_gemini_api_key(byok_key)
    client = genai.Client(api_key=api_key)
    prompt = _build_prompt(topic, report_lang)

    models_to_try = ["gemini-2.5-flash-lite", "gemini-2.5-flash"]
    last_exception = None

    for model_name in models_to_try:
        max_retries = 2
        initial_backoff = 2.0

        for attempt in range(max_retries + 1):
            try:
                logger.info(
                    "Attempting Gemini call with model: %s (attempt %d/%d)",
                    model_name,
                    attempt + 1,
                    max_retries + 1,
                )
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.7,
                    ),
                )
                raw_text: str = response.text or ""
                raw_text = raw_text.strip()
                logger.info(
                    "Gemini (%s) returned %d chars for topic '%s' [lang=%s]",
                    model_name,
                    len(raw_text),
                    topic,
                    report_lang,
                )
                json.loads(raw_text)  # sanity check
                return raw_text

            except Exception as exc:
                last_exception = exc
                exc_str = str(exc)
                is_transient = any(
                    err in exc_str
                    for err in [
                        "503",
                        "429",
                        "UNAVAILABLE",
                        "RESOURCE_EXHAUSTED",
                        "ResourceExhausted",
                        "rate limit",
                        "deadline exceeded",
                        "timeout",
                    ]
                )

                if is_transient and attempt < max_retries:
                    sleep_time = initial_backoff * (2**attempt) + random.uniform(0, 1)  # nosec B311
                    logger.warning(
                        "Gemini API transient failure with model %s: %s. Retrying in %.2fs...",
                        model_name,
                        exc,
                        sleep_time,
                    )
                    time.sleep(sleep_time)
                    continue

                logger.warning(
                    "Gemini API model %s failed: %s. Trying next model if available.",
                    model_name,
                    exc,
                )
                break

    raise RuntimeError(
        f"Gemini generation failed on all attempted models. Please try again. (Detail: {last_exception})"
    ) from last_exception


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
        with urllib.request.urlopen(req, timeout=5):  # nosec B310
            pass
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Ollama is not running at {OLLAMA_BASE_URL}. Start it with: `ollama serve`"
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
            f"Invalid Ollama model '{model}'. Allowed: {', '.join(OLLAMA_MODELS)}"
        )

    _check_ollama_available()

    prompt = _build_prompt(topic, report_lang)
    prompt += (
        "\nCRITICAL RULES FOR LOCAL MODELS:\n"
        "- Return valid JSON only.\n"
        "- Do not include markdown.\n"
        "- Do not include explanations.\n"
        "- Populate all fields.\n"
        "- Provide:\n"
        "  - executive_summary\n"
        "  - core_concepts (minimum 5)\n"
        "  - key_insights (minimum 5)\n"
        "  - benefits_challenges_risks\n"
        "  - real_world_applications\n"
        "  - future_outlook\n"
        "  - statistics\n"
        "  - references"
    )

    # Task 1: Log the exact prompt being sent to Ollama
    logger.info("PROMPT SENT TO OLLAMA")
    logger.info(prompt)

    # Store prompt in session state for Streamlit diagnostics
    try:
        import streamlit as st

        st.session_state["prompt_sent"] = prompt
    except ImportError:
        pass

    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional research analyst. You must output "
                    "a JSON object containing all the requested keys. Every "
                    "key must be fully populated with real research content. "
                    "Do not output placeholders."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.5,
            "num_predict": 4096,
            "num_ctx": 8192,
        },
    }
    data = json.dumps(payload).encode("utf-8")

    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        logger.info(f"Starting Ollama request: {model}")
        with urllib.request.urlopen(req, timeout=300) as resp:  # nosec B310
            raw_data = resp.read().decode("utf-8")
        logger.info("Ollama response received")

        # Task 4: Save the raw output to disk
        try:
            debug_path = (
                Path(__file__).resolve().parent.parent / "debug_ollama_response.txt"
            )
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(raw_data)
        except Exception as file_exc:
            logger.error("Failed to write debug_ollama_response.txt: %s", file_exc)

        # Task 1: Display raw Ollama output
        logger.info("=" * 80)
        logger.info("RAW OLLAMA RESPONSE")
        logger.info("=" * 80)
        logger.info(raw_data)
        logger.info("=" * 80)

        # Store in streamlit session state for diagnostics
        try:
            import streamlit as st

            st.session_state["raw_ollama_response"] = raw_data
        except ImportError:
            pass

        try:
            body = json.loads(raw_data)
        except Exception:
            body = raw_data

        # Task 3: Log complete returned object and verify field extraction
        logger.info("Ollama parsed body object: %s", body)

        # Support Format A ("response") & Format B ("message" -> "content")
        content = None
        if isinstance(body, dict):
            if "response" in body:
                content = body["response"]
            elif "message" in body and isinstance(body["message"], dict):
                content = body["message"].get("content")

        # Fallback handling if not in expected structure
        if not content:
            if body:
                content = str(body)
            else:
                raise ValueError(
                    f"Unable to extract text from Ollama response. Response={body}"
                )

        raw_text: str = content.strip()
        logger.info(
            "Ollama (%s) returned %d chars for topic '%s' [lang=%s]",
            model,
            len(raw_text),
            topic,
            report_lang,
        )

        # JSON Repair Layer
        raw_text = raw_text.replace("```json", "")
        raw_text = raw_text.replace("```", "")
        json_start = raw_text.find("{")
        json_end = raw_text.rfind("}")
        if json_start >= 0 and json_end >= 0:
            raw_text = raw_text[json_start : json_end + 1]

        # Store cleaned response in session state
        try:
            import streamlit as st

            st.session_state["cleaned_ollama_response"] = raw_text
        except ImportError:
            pass

        try:
            json.loads(raw_text)
            return raw_text
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"AI response content is not valid JSON: {exc}. Content: {raw_text}"
            ) from exc

    except urllib.error.URLError as exc:
        logger.error("Ollama request failed: %s", exc)
        raise RuntimeError(
            f"Ollama request failed. Is it running? (Detail: {exc})"
        ) from exc
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        logger.error("Ollama returned invalid response format: %s", exc)
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


def stream_chat(
    prompt: str,
    system_instruction: str | None = None,
    provider: str = "gemini",
    byok_key: str | None = None,
    ollama_model: str = "llama3",
) -> Generator[str, None, None]:
    """Streams a chat conversation from the selected provider.

    Args:
        prompt: User prompt.
        system_instruction: Optional system instruction.
        provider: 'gemini', 'gemini_builtin', 'gemini_byok', or 'ollama'.
        byok_key: User-provided Gemini API key (for BYOK mode).
        ollama_model: Selected local Ollama model.

    Yields:
        Tokens generated by the model.
    """
    if provider in ("gemini_builtin", "gemini", "gemini_byok"):
        from google import genai
        from google.genai import types

        resolved_byok = byok_key if provider in ("gemini", "gemini_byok") else None
        api_key = _get_gemini_api_key(resolved_byok)
        client = genai.Client(api_key=api_key)

        config = types.GenerateContentConfig(
            temperature=0.3,
        )
        if system_instruction:
            config.system_instruction = system_instruction

        models_to_try = ["gemini-2.5-flash-lite", "gemini-2.5-flash"]
        last_exc = None

        for model_name in models_to_try:
            try:
                response = client.models.generate_content_stream(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )
                for chunk in response:
                    yield chunk.text or ""
                return
            except Exception as exc:
                last_exc = exc
                logger.warning("Gemini stream failed for model %s: %s", model_name, exc)
                continue

        raise RuntimeError(
            f"Gemini streaming failed on all models: {last_exc}"
        ) from last_exc

    elif provider == "ollama":
        import json
        import urllib.request

        _check_ollama_available()

        payload: dict[str, Any] = {
            "model": ollama_model,
            "messages": [],
            "stream": True,
            "options": {
                "temperature": 0.3,
            },
        }
        if system_instruction:
            payload["messages"].append(
                {"role": "system", "content": system_instruction}
            )
        payload["messages"].append({"role": "user", "content": prompt})

        data = json.dumps(payload).encode("utf-8")
        try:
            req = urllib.request.Request(
                f"{OLLAMA_BASE_URL}/api/chat",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:  # nosec B310
                for line in resp:
                    if line:
                        chunk_data = json.loads(line.decode("utf-8"))
                        content = chunk_data.get("message", {}).get("content", "")
                        yield content
        except Exception as exc:
            logger.error("Ollama stream generation failed: %s", exc)
            raise RuntimeError(f"Ollama streaming failed: {exc}") from exc

    else:
        raise ValueError(f"Unknown AI provider '{provider}'")
