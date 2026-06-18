"""Automated Health Checks for imports.

Verifies that all core packages and modules can be successfully imported
in a clean environment.
"""

from __future__ import annotations


def test_streamlit_imports() -> None:
    """Verifies that streamlit is importable."""
    import streamlit as st

    assert st is not None


def test_ai_provider_imports() -> None:
    """Verifies that google.genai and other AI providers are importable."""
    from google import genai
    from google.genai import types

    assert genai is not None
    assert types is not None


def test_ollama_integration() -> None:
    """Verifies that ollama-related client structures are importable."""
    import ollama
    from utils.ai_client import (
        OLLAMA_BASE_URL,
        OLLAMA_MODELS,
        is_ollama_available,
    )

    assert OLLAMA_BASE_URL is not None
    assert OLLAMA_MODELS is not None
    assert is_ollama_available is not None
    assert ollama is not None


def test_rag_modules() -> None:
    """Verifies that RAG pipeline modules import correctly."""
    from utils import embedding_service, rag_pipeline, vector_store

    assert embedding_service is not None
    assert rag_pipeline is not None
    assert vector_store is not None


def test_utility_modules() -> None:
    """Verifies that shared utilities import correctly."""
    from utils import (
        ai_client,
        env_validator,
        font_manager,
        localization,
        pdf_generator,
        ppt_generator,
        report_schema,
    )

    assert ai_client is not None
    assert pdf_generator is not None
    assert ppt_generator is not None
    assert report_schema is not None
    assert font_manager is not None
    assert localization is not None
    assert env_validator is not None
