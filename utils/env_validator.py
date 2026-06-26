"""Environment Variable Validator.

Checks that required and optional AI provider API keys are configured in the
environment or a local .env file. Logs warnings instead of crashing to allow
local-first fallback mode (Ollama) to work seamlessly.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Resolve path to the root .env file and load it if python-dotenv is installed
try:
    from dotenv import load_dotenv  # type: ignore[import-not-found]

    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        logger.debug(".env file not found at %s", env_path)
except ImportError:
    logger.debug("python-dotenv not installed; skipping .env load.")


def validate_environment() -> dict[str, bool]:
    """Checks for the presence of required AI provider API keys.

    Returns:
        A dictionary mapping the environment variable names to a boolean
        indicating whether they are configured.
    """
    keys_to_check = [
        "GEMINI_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
    ]

    status = {}
    missing_keys = []

    for key in keys_to_check:
        value = os.getenv(key, "").strip()
        # Treat default template value as missing
        if not value or value == "your_gemini_api_key_here":
            status[key] = False
            missing_keys.append(key)
        else:
            status[key] = True

    if missing_keys:
        logger.warning(
            "The following environment variables are missing or unconfigured: %s. "
            "Some cloud-based AI providers (e.g. Gemini, OpenAI, Anthropic) "
            "may not function correctly. However, local-first mode (Ollama) "
            "will function without any API keys.",
            ", ".join(missing_keys),
        )

    return status
