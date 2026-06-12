"""
DeepDive AI — 🔬 Research Page

Streamlit page view for the research report workflow:
1. User enters a research topic
2. Clicks "Generate Report"
3. AI generates a structured report
4. Report sections are rendered in the UI
5. PDF and PPTX download buttons are provided

All business logic lives in utils/; this module handles UI only (Constitution §IV).
"""

from __future__ import annotations

import logging
import os
import traceback

import streamlit as st

from utils.ai_client import (
    OLLAMA_BASE_URL,
    OLLAMA_MODELS,
    generate_research_report,
    is_ollama_available,
)
from utils.localization import LANGUAGES, detect_browser_language, get_text
from utils.pdf_generator import build_pdf
from utils.ppt_generator import build_ppt
from utils.report_schema import ResearchReport, parse_report
from utils.reviews_manager import load_reviews, render_sidebar_review_form

logger = logging.getLogger(__name__)

# ── Page Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title="DeepDive AI — Research",
    page_icon="🔬",
    layout="wide",
)

# ── Session State Defaults ──────────────────────────────────────────
if "ui_lang" not in st.session_state:
    st.session_state["ui_lang"] = detect_browser_language()
if "report_lang" not in st.session_state:
    st.session_state["report_lang"] = "en"
if "report" not in st.session_state:
    st.session_state["report"] = None
if "generating" not in st.session_state:
    st.session_state["generating"] = False
if "pdf_path" not in st.session_state:
    st.session_state["pdf_path"] = None
if "ppt_path" not in st.session_state:
    st.session_state["ppt_path"] = None
if "ai_provider" not in st.session_state:
    st.session_state["ai_provider"] = "gemini_builtin"
if "byok_api_key" not in st.session_state:
    st.session_state["byok_api_key"] = ""
if "ollama_model" not in st.session_state:
    st.session_state["ollama_model"] = OLLAMA_MODELS[0]
if "raw_ollama_response" not in st.session_state:
    st.session_state["raw_ollama_response"] = None
if "cleaned_ollama_response" not in st.session_state:
    st.session_state["cleaned_ollama_response"] = None
if "parsed_json" not in st.session_state:
    st.session_state["parsed_json"] = None
if "validation_results" not in st.session_state:
    st.session_state["validation_results"] = None
if "prompt_sent" not in st.session_state:
    st.session_state["prompt_sent"] = None
if "missing_fields" not in st.session_state:
    st.session_state["missing_fields"] = None

lang = st.session_state["ui_lang"]
report_lang = st.session_state["report_lang"]

# ── Custom CSS ──────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* ─── Global Styling ─── */
    html, body, [class*="st-"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        color: #F8FAFC;
    }

    /* Fix Streamlit Material Icons font family override glitch */
    [data-testid="collapsedControl"] span,
    [data-testid="stIconMaterial"],
    .material-symbols-outlined,
    .material-icons {
        font-family: 'Material Symbols Outlined', 'Material Icons' !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', -apple-system, sans-serif;
        font-weight: 700 !important;
        color: #F8FAFC !important;
        letter-spacing: -0.02em;
    }

    :root {
        --background-color: #0B0F19;
        --secondary-bg: #111827;
        --card-bg: #1A2236;
        --accent-1: #7C3AED;
        --accent-2: #A855F7;
        --accent-3: #EC4899;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --border-color: rgba(255, 255, 255, 0.08);
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
        --shadow-lg: 0 10px 30px rgba(124, 58, 237, 0.15);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
    }

    .stApp {
        background-color: #0B0F19 !important;
        background-image: radial-gradient(
            circle at 10% 20%,
            rgba(124, 58, 237, 0.06) 0%,
            transparent 45/
        ),
        radial-gradient(
            circle at 90% 80%,
            rgba(236, 72, 153, 0.06) 0%,
            transparent 45/
        ) !important;
    }

    /* ─── Sidebar Styling ─── */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    [data-testid="stSidebar"] * {
        color: #94A3B8 !important;
    }
    /* Uppercase the 'app' page link in sidebar navigation */
    div[data-testid="stSidebarNav"] ul li:first-child a p,
    div[data-testid="stSidebarNav"] a[href="/"] p,
    div[data-testid="stSidebarNav"] a[href=""] p {
        text-transform: uppercase !important;
    }
    [data-testid="stSidebar"] h3 {
        color: #F8FAFC !important;
        background: linear-gradient(135deg, #A855F7 0%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    [data-testid="stSidebar"] .stMarkdown a {
        color: #EC4899 !important;
        font-weight: 500;
        text-decoration: none;
    }
    [data-testid="stSidebar"] .stMarkdown a:hover {
        text-decoration: underline;
    }

    /* ─── Form Elements Override ─── */
    .stTextInput input {
        background-color: #1A2236 !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: var(--radius-md) !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stTextInput input:focus {
        border-color: #A855F7 !important;
        box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.25) !important;
    }

    /* ─── Buttons Override ─── */
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #7C3AED 0%, #EC4899 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: var(--radius-md) !important;
        padding: 0.65rem 1.5rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(236, 72, 153, 0.4) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    .stButton > button:active, .stDownloadButton > button:active {
        transform: translateY(0) !important;
    }

    /* ─── Main Header Styling ─── */
    .main-header {
        background: linear-gradient(
            135deg,
            rgba(26, 34, 54, 0.4) 0%,
            rgba(17, 24, 39, 0.6) 100/
        );
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 2rem 2.5rem;
        border-radius: var(--radius-lg);
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
        backdrop-filter: blur(12px);
    }
    .main-header h1 {
        background: linear-gradient(135deg, #F8FAFC 30%, #A855F7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        font-weight: 800;
        margin: 0 !important;
    }
    .main-header p {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    /* ─── Section Cards ─── */
    .section-card {
        background: rgba(26, 34, 54, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: var(--radius-lg);
        padding: 2rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        box-shadow: var(--shadow-md);
    }
    .section-card h3 {
        color: #F8FAFC !important;
        font-size: 1.4rem;
        font-weight: 600;
        margin-top: 0 !important;
        margin-bottom: 1.25rem !important;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* ─── Insight Items ─── */
    .insight-item {
        background: rgba(255, 255, 255, 0.02);
        border-left: 4px solid #A855F7;
        padding: 1rem 1.4rem;
        border-radius: 0 12px 12px 0;
        margin-bottom: 0.75rem;
        font-size: 1rem;
        line-height: 1.6;
        color: #F8FAFC;
        border-top: 1px solid rgba(255, 255, 255, 0.02);
        border-bottom: 1px solid rgba(255, 255, 255, 0.02);
        border-right: 1px solid rgba(255, 255, 255, 0.02);
    }

    /* ─── Stat Cards ─── */
    .stat-card {
        background: linear-gradient(
            135deg,
            rgba(124, 58, 237, 0.1) 0%,
            rgba(236, 72, 153, 0.05) 100/
        );
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(124, 58, 237, 0.15);
        border-color: rgba(168, 85, 247, 0.3);
    }
    .stat-label {
        color: #94A3B8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.5rem;
    }
    .stat-value {
        color: #F8FAFC;
        background: linear-gradient(135deg, #A855F7 0%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.85rem;
        font-weight: 700;
    }

    /* ─── Reference Cards ─── */
    .ref-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: var(--radius-md);
        padding: 1.25rem 1.5rem;
        margin-bottom: 0.75rem;
        transition: all 0.3s ease;
    }
    .ref-card:hover {
        border-color: #A855F7;
        background: rgba(255, 255, 255, 0.03);
    }
    .ref-title {
        color: #F8FAFC;
        font-weight: 600;
        font-size: 1.1rem;
    }
    .ref-snippet {
        color: #94A3B8;
        font-size: 0.95rem;
        margin-top: 0.4rem;
        line-height: 1.5;
    }
    .ref-url {
        color: #A855F7;
        font-size: 0.82rem;
        margin-top: 0.3rem;
        word-break: break-all;
    }

    /* ─── Download Area ─── */
    .download-section {
        background: linear-gradient(
            135deg,
            rgba(26, 34, 54, 0.2) 0%,
            rgba(17, 24, 39, 0.4) 100/
        );
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: var(--radius-lg);
        padding: 2rem;
        margin-top: 2rem;
        text-align: center;
        box-shadow: var(--shadow-md);
    }
    .download-section h3 {
        color: #F8FAFC !important;
        font-size: 1.4rem;
        margin-top: 0 !important;
        margin-bottom: 1.25rem !important;
    }

    /* ─── Warning Banner ─── */
    .limited-data-banner {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #F59E0B;
        padding: 1rem 1.4rem;
        border-radius: 0 12px 12px 0;
        margin-bottom: 1.25rem;
        color: #FBBF24;
        font-weight: 500;
        font-size: 0.95rem;
        border-top: 1px solid rgba(245, 158, 11, 0.15);
        border-bottom: 1px solid rgba(245, 158, 11, 0.15);
        border-right: 1px solid rgba(245, 158, 11, 0.15);
    }

    /* ─── Spinner Customization ─── */
    div[data-testid="stSpinner"] > div {
        border-top-color: #A855F7 !important;
    }

    /* ─── Review Card Styling ─── */
    .reviews-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1.25rem;
        margin-top: 1.5rem;
    }
    .review-card {
        background: rgba(26, 34, 54, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: var(--radius-md) !important;
        padding: 1.5rem !important;
        backdrop-filter: blur(8px) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    .review-card:hover {
        transform: translateY(-4px) !important;
        background: rgba(26, 34, 54, 0.5) !important;
        border-color: rgba(168, 85, 247, 0.35) !important;
        box-shadow: 0 10px 25px rgba(124, 58, 237, 0.08) !important;
    }
    .review-stars {
        color: #A855F7;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
    }
    .review-author {
        color: #F8FAFC;
        font-weight: 600;
        font-size: 1.05rem;
        margin-bottom: 0.5rem;
    }
    .review-comment {
        color: #F8FAFC;
        font-style: italic;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-top: 0.5rem;
        margin-bottom: 0.75rem;
    }
    .review-date {
        color: #94A3B8;
        font-size: 0.82rem;
    }

    /* ─── Hide Default Branding ─── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {background: transparent;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### {get_text('app_title', lang)}")
    st.caption(get_text("app_tagline", lang))
    st.divider()

    # ── AI Provider selector ──────────────────────────────────────
    st.markdown("#### 🤖 AI Provider")
    provider_options = {
        "gemini_builtin": "☁️ Built-in Gemini",
        "gemini_byok": "🔑 Gemini (Bring Your Own Key)",
        "ollama": "🖥️ Ollama Local",
    }

    # Map old provider values to new ones gracefully if needed
    current_provider = st.session_state["ai_provider"]
    if current_provider == "gemini" or current_provider not in provider_options:
        st.session_state["ai_provider"] = "gemini_builtin"

    selected_provider = st.selectbox(
        "AI Provider",
        options=list(provider_options.keys()),
        format_func=lambda k: provider_options[k],
        index=list(provider_options.keys()).index(
            st.session_state["ai_provider"]
        ),
        key="ai_provider_selector_research",
        label_visibility="collapsed",
    )
    if selected_provider != st.session_state["ai_provider"]:
        st.session_state["ai_provider"] = selected_provider
        st.rerun()

    if st.session_state["ai_provider"] == "gemini_builtin":
        st.caption(
            "☁️ **Built-in Gemini**: Uses the application's pre-configured "
            "Gemini API key from Streamlit secrets. Works immediately for all users."
        )
        st.markdown(
            "<div style='"
            "background:rgba(124,58,237,0.12);"
            "border-left:3px solid #7C3AED;"
            "padding:6px 10px;border-radius:6px;"
            "font-size:0.78rem;color:#A855F7;margin-top:4px'"
            ">☁️ Active: Built-in Gemini</div>",
            unsafe_allow_html=True,
        )
    elif st.session_state["ai_provider"] == "gemini_byok":
        st.caption(
            "🔑 **BYOK Gemini**: Use your personal Gemini API key. "
            "Falls back to built-in if left blank."
        )
        byok_input = st.text_input(
            "🔑 Gemini API Key",
            value=st.session_state["byok_api_key"],
            type="password",
            placeholder="Paste key, or leave blank to use secrets",
            key="byok_key_input_research",
            help="Stored only in this browser session.",
        )
        st.session_state["byok_api_key"] = byok_input
        st.markdown(
            "<div style='"
            "background:rgba(124,58,237,0.12);"
            "border-left:3px solid #7C3AED;"
            "padding:6px 10px;border-radius:6px;"
            "font-size:0.78rem;color:#A855F7;margin-top:4px'"
            ">☁️ Active: BYOK Gemini</div>",
            unsafe_allow_html=True,
        )
    elif st.session_state["ai_provider"] == "ollama":
        st.caption(
            "🖥️ **Ollama Local**: Runs models locally on your machine. "
            "Requires Ollama to be running on localhost:11434."
        )
        selected_model = st.selectbox(
            "🧠 Local Model",
            options=OLLAMA_MODELS,
            index=(
                OLLAMA_MODELS.index(st.session_state["ollama_model"])
                if st.session_state["ollama_model"] in OLLAMA_MODELS
                else 0
            ),
            key="ollama_model_selector_research",
        )
        st.session_state["ollama_model"] = selected_model

        # Non-blocking connection check
        if not is_ollama_available():
            st.warning(
                "🖥️ **Ollama not reachable.** "
                "Make sure Ollama is installed and running at "
                f"`{OLLAMA_BASE_URL}` (`ollama serve`)."
            )
        else:
            st.markdown(
                "<div style='"
                "background:rgba(16,185,129,0.12);"
                "border-left:3px solid #10B981;"
                "padding:6px 10px;border-radius:6px;"
                "font-size:0.78rem;color:#34D399;margin-top:4px'"
                f">🖥️ Active: Ollama · {selected_model}</div>",
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown(
        f"**{get_text('how_to_use', lang)}**\n\n"
        f"{get_text('step_1', lang)}\n\n"
        f"{get_text('step_2', lang)}\n\n"
        f"{get_text('step_3', lang)}\n\n"
        f"{get_text('step_4', lang)}"
    )
    st.divider()
    st.markdown(
        f"{get_text('built_with', lang)} "
        "[Streamlit](https://streamlit.io) & "
        "[Gemini AI](https://ai.google.dev) / "
        "[Ollama](https://ollama.com)",
    )
    st.divider()
    render_sidebar_review_form()

# ── Header & Language Switchers Row ──────────────────────────────────
col_title, col_ui_lang, col_rep_lang = st.columns([4, 1, 1])
with col_title:
    st.markdown(
        f"""
        <div class="main-header">
            <h1>{get_text("hero_title", lang)}</h1>
            <p>{get_text("app_tagline", lang)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_ui_lang:
    ui_lang_selected = st.selectbox(
        f"🌐 {get_text('ui_language', lang)}",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=list(LANGUAGES.keys()).index(st.session_state["ui_lang"]),
        key="ui_lang_selector_research",
    )
    if ui_lang_selected != st.session_state["ui_lang"]:
        st.session_state["ui_lang"] = ui_lang_selected
        st.toast(get_text("welcome_back", ui_lang_selected), icon="🔬")
        st.rerun()

with col_rep_lang:
    report_labels = {
        "en": "English",
        "hi": "हिन्दी (Hindi)",
        "mr": "मराठी (Marathi)",
        "te": "తెలుగు (Telugu)",
    }
    report_lang_selected = st.selectbox(
        f"📄 {get_text('report_language', lang)}",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: report_labels[x],
        index=list(LANGUAGES.keys()).index(st.session_state["report_lang"]),
        key="report_lang_selector_research",
    )
    if report_lang_selected != st.session_state["report_lang"]:
        st.session_state["report_lang"] = report_lang_selected
        st.rerun()

# Welcome banner callout
welcome_msg = get_text("welcome_back", lang)
st.markdown(
    f"<p style='color: #A855F7; font-weight: 500;'>👋 {welcome_msg}</p>",
    unsafe_allow_html=True,
)

# ── Topic Input & Generate Button ──────────────────────────────────
col_input, col_btn = st.columns([4, 1])

with col_input:
    topic = st.text_input(
        get_text("research_topic", lang),
        placeholder=get_text("input_placeholder", lang),
        label_visibility="collapsed",
        max_chars=500,
        key="topic_input",
    )

with col_btn:
    generate_clicked = st.button(
        get_text("btn_generate", lang),
        use_container_width=True,
        disabled=st.session_state.get("generating", False),
        type="primary",
    )

# ── Input Validation & Generation ──────────────────────────────────
if generate_clicked:
    if not topic or not topic.strip():
        st.warning(get_text("warning_empty_topic", lang))
    else:
        display_topic = topic[:200] + "…" if len(topic) > 200 else topic

        # Dynamic reload of helper modules to bypass Streamlit import caching
        import importlib

        import utils.ai_client
        import utils.report_schema
        importlib.reload(utils.ai_client)
        importlib.reload(utils.report_schema)
        from utils.ai_client import generate_research_report
        from utils.report_schema import parse_report

        st.session_state["generating"] = True
        st.session_state["report"] = None
        st.session_state["pdf_path"] = None
        st.session_state["ppt_path"] = None

        spinner_msg = get_text("spinner_msg", lang).format(
            topic=display_topic
        )
        with st.spinner(spinner_msg):
            try:
                raw_json = generate_research_report(
                    topic.strip(),
                    report_lang=st.session_state["report_lang"],
                    provider=st.session_state["ai_provider"],
                    byok_key=st.session_state["byok_api_key"] or None,
                    ollama_model=st.session_state["ollama_model"],
                )
                is_ollama = (st.session_state.get("ai_provider") == "ollama")
                st.session_state["raw_ollama_response"] = raw_json
                cleaned_or_raw = (
                    st.session_state.get("cleaned_ollama_response")
                    or raw_json
                )
                st.session_state["cleaned_ollama_response"] = cleaned_or_raw
                try:
                    import json
                    st.session_state["parsed_json"] = json.loads(raw_json)
                except Exception:
                    st.session_state["parsed_json"] = None

                parsed_report = parse_report(
                    raw_json, topic=topic.strip(), strict=not is_ollama
                )
                st.session_state["report"] = parsed_report
                st.session_state["validation_results"] = "Success"
                st.session_state["generating"] = False
                st.success(get_text("success_msg", lang))

            except OSError as exc:
                st.session_state["generating"] = False
                st.session_state["validation_results"] = f"Failed (OS/API Key): {exc}"
                st.error(f"❌ **Environment/API Key Error**: {exc}")
                logger.error("Environment error: %s", exc)
                logger.debug(traceback.format_exc())

            except RuntimeError as exc:
                st.session_state["generating"] = False
                st.session_state["validation_results"] = f"Failed (Runtime): {exc}"
                err_detail = str(exc)
                if "is not running" in err_detail or "request failed" in err_detail:
                    st.error(
                        "🖥️ **Ollama not reachable.** "
                        "Make sure Ollama is installed and running at "
                        f"`{OLLAMA_BASE_URL}`: `ollama serve`"
                    )
                else:
                    st.error(f"❌ **Ollama Error**: {exc}")
                logger.error("API error: %s", exc)
                logger.debug(traceback.format_exc())

            except ValueError as exc:
                st.session_state["generating"] = False
                st.session_state["validation_results"] = f"Failed (Validation): {exc}"
                st.error(f"⚠️ **Response Format Error**: {exc}")
                logger.error("Schema / model error: %s", exc)
                logger.debug(traceback.format_exc())

            except Exception as exc:
                st.session_state["generating"] = False
                st.session_state["validation_results"] = f"Failed (Unexpected): {exc}"
                st.error(f"❌ **Unexpected Error**: {exc}")
                logger.error("Unexpected error: %s", exc)
                logger.debug(traceback.format_exc())

# ── Report Display ──────────────────────────────────────────────────
report: ResearchReport | None = st.session_state.get("report")

if report is not None:
    st.divider()

    # Render any validation/auto-correction warnings if present (Task 6)
    if report.warnings:
        for warning in report.warnings:
            st.warning(f"⚠️ {warning}")

    # ── Executive Summary ────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="section-card">
            <h3>{get_text("sec_summary", lang)}</h3>
            <p style="color: #94A3B8; line-height: 1.75; font-size: 1.05rem;">
                {report.executive_summary}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Background & Context ─────────────────────────────────────────
    st.markdown(
        f"""
        <div class="section-card">
            <h3>{get_text("sec_background", lang)}</h3>
            <p style="color: #94A3B8; line-height: 1.75; font-size: 1.05rem;">
                {report.background_context}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Core Concepts ────────────────────────────────────────────────
    st.markdown(
        f'<div class="section-card"><h3>{get_text("sec_concepts", lang)}</h3>',
        unsafe_allow_html=True,
    )
    for concept in report.core_concepts:
        term = concept.get("term", "Term")
        definition = concept.get("definition", "Definition")
        div_c = (
            '<div style="margin-bottom: 1rem; '
            'border-left: 3px solid #7C3AED; padding-left: 1rem;">'
        )
        term_style = "font-weight: 700; font-size: 1.1rem; color: #F8FAFC;"
        desc_style = "color: #94A3B8; font-size: 0.95rem; margin-top: 0.25rem;"
        st.markdown(
            f"""
            {div_c}
                <div style="{term_style}">{term}</div>
                <div style="{desc_style}">{definition}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Key Insights ─────────────────────────────────────────────────
    if len(report.key_insights) < 3:
        warn_msg = get_text("limited_data_warn", lang)
        st.markdown(
            f'<div class="limited-data-banner">{warn_msg}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div class="section-card"><h3>{get_text("sec_insights", lang)}</h3>',
        unsafe_allow_html=True,
    )
    for insight in report.key_insights:
        st.markdown(
            f'<div class="insight-item">{insight}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Statistics ───────────────────────────────────────────────────
    st.markdown(
        f'<div class="section-card"><h3>{get_text("sec_stats", lang)}</h3></div>',
        unsafe_allow_html=True,
    )

    if len(report.statistics) < 3:
        stats_warn = get_text("limited_stats_warn", lang)
        st.markdown(
            f'<div class="limited-data-banner">{stats_warn}</div>',
            unsafe_allow_html=True,
        )

    # Render stat cards in columns (up to 3 per row) (Task 5)
    stats = [
        s for s in report.statistics
        if isinstance(s, dict)
        and s.get("label")
        and s.get("value")
        and s.get("value") != "N/A"
    ]
    if stats:
        for row_start in range(0, len(stats), 3):
            row_stats = stats[row_start : row_start + 3]
            cols = st.columns(len(row_stats))
            for col, stat in zip(cols, row_stats, strict=True):
                with col:
                    st.markdown(
                        f"""
                        <div class="stat-card">
                            <div class="stat-label">{stat.get("label", "")}</div>
                            <div class="stat-value">{stat.get("value", "")}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # ── Benefits, Challenges & Risks ─────────────────────────────────
    st.markdown(
        f'<div class="section-card"><h3>{get_text("sec_benefits", lang)}</h3>',
        unsafe_allow_html=True,
    )
    col_b, col_c, col_r = st.columns(3)

    with col_b:
        b_header = (
            f"<h4 style='color: #4ADE80 !important; font-size: 1.1rem; "
            f"margin-bottom: 0.75rem;'>{get_text('benefit_label', lang)}</h4>"
        )
        st.markdown(b_header, unsafe_allow_html=True)
        benefits = [
            item
            for item in report.benefits_challenges_risks
            if item.get("type", "").lower() == "benefit"
        ]
        if not benefits:
            benefits = [
                item
                for item in report.benefits_challenges_risks
                if "benefit" in item.get("type", "").lower()
            ]
        for b in benefits:
            div_style = (
                "background: rgba(74, 222, 128, 0.05); "
                "border: 1px solid rgba(74, 222, 128, 0.1); "
                "border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;"
            )
            desc_style = "color: #94A3B8; font-size: 0.88rem; margin-top: 0.25rem;"
            st.markdown(
                f"""
                <div style="{div_style}">
                    <strong style="color: #F8FAFC;">{b.get("item", "")}</strong>
                    <div style="{desc_style}">{b.get("description", "")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_c:
        c_header = (
            f"<h4 style='color: #FBBF24 !important; font-size: 1.1rem; "
            f"margin-bottom: 0.75rem;'>{get_text('challenge_label', lang)}</h4>"
        )
        st.markdown(c_header, unsafe_allow_html=True)
        challenges = [
            item
            for item in report.benefits_challenges_risks
            if item.get("type", "").lower() == "challenge"
        ]
        if not challenges:
            challenges = [
                item
                for item in report.benefits_challenges_risks
                if "challenge" in item.get("type", "").lower()
            ]
        for c in challenges:
            div_style = (
                "background: rgba(251, 191, 36, 0.05); "
                "border: 1px solid rgba(251, 191, 36, 0.1); "
                "border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;"
            )
            desc_style = "color: #94A3B8; font-size: 0.88rem; margin-top: 0.25rem;"
            st.markdown(
                f"""
                <div style="{div_style}">
                    <strong style="color: #F8FAFC;">{c.get("item", "")}</strong>
                    <div style="{desc_style}">{c.get("description", "")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_r:
        r_header = (
            f"<h4 style='color: #F87171 !important; font-size: 1.1rem; "
            f"margin-bottom: 0.75rem;'>{get_text('risk_label', lang)}</h4>"
        )
        st.markdown(r_header, unsafe_allow_html=True)
        risks = [
            item
            for item in report.benefits_challenges_risks
            if item.get("type", "").lower() == "risk"
        ]
        if not risks:
            risks = [
                item
                for item in report.benefits_challenges_risks
                if "risk" in item.get("type", "").lower()
            ]
        for r in risks:
            div_style = (
                "background: rgba(248, 113, 113, 0.05); "
                "border: 1px solid rgba(248, 113, 113, 0.1); "
                "border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;"
            )
            desc_style = "color: #94A3B8; font-size: 0.88rem; margin-top: 0.25rem;"
            st.markdown(
                f"""
                <div style="{div_style}">
                    <strong style="color: #F8FAFC;">{r.get("item", "")}</strong>
                    <div style="{desc_style}">{r.get("description", "")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Real-World Applications ──────────────────────────────────────
    st.markdown(
        f'<div class="section-card"><h3>{get_text("sec_apps", lang)}</h3>',
        unsafe_allow_html=True,
    )
    for app in report.real_world_applications:
        application = app.get("application", "Application")
        description = app.get("description", "Description")
        div_app = (
            '<div style="margin-bottom: 1rem; '
            'border-left: 3px solid #EC4899; padding-left: 1rem;">'
        )
        term_style = "font-weight: 700; font-size: 1.1rem; color: #F8FAFC;"
        desc_style = "color: #94A3B8; font-size: 0.95rem; margin-top: 0.25rem;"
        st.markdown(
            f"""
            {div_app}
                <div style="{term_style}">{application}</div>
                <div style="{desc_style}">{description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Future Outlook ───────────────────────────────────────────────
    st.markdown(
        f'<div class="section-card"><h3>{get_text("sec_outlook", lang)}</h3>',
        unsafe_allow_html=True,
    )
    for outlook in report.future_outlook:
        st.markdown(
            f'<div class="insight-item" '
            f'style="border-left-color: #EC4899;">{outlook}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── References ───────────────────────────────────────────────────
    st.markdown(
        f'<div class="section-card"><h3>{get_text("sec_references", lang)}</h3></div>',
        unsafe_allow_html=True,
    )

    for ref in report.references:
        title = ref.get("title", "Untitled")
        url = ref.get("url", "#")
        snippet = ref.get("snippet", "")
        st.markdown(
            f"""
            <div class="ref-card">
                <div class="ref-title">{title}</div>
                <div class="ref-snippet">{snippet}</div>
                <div class="ref-url">{url}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Download Buttons ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        f'<div class="download-section">'
        f"<h3>{get_text('download_section_title', lang)}</h3>"
        f"</div>",
        unsafe_allow_html=True,
    )

    col_pdf, col_ppt = st.columns(2)

    with col_pdf:
        try:
            if st.session_state.get("pdf_path") is None:
                pdf_path = build_pdf(report, lang=st.session_state["report_lang"])
                st.session_state["pdf_path"] = pdf_path
            else:
                pdf_path = st.session_state["pdf_path"]

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label=get_text("btn_download_pdf", lang),
                    data=f.read(),
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                )
        except Exception as exc:
            logger.exception("PDF generation error: %s", exc)
            st.error(f"❌ **PDF Error**: {exc}")

    with col_ppt:
        try:
            if st.session_state.get("ppt_path") is None:
                ppt_path = build_ppt(report, lang=st.session_state["report_lang"])
                st.session_state["ppt_path"] = ppt_path
            else:
                ppt_path = st.session_state["ppt_path"]

            with open(ppt_path, "rb") as f:
                st.download_button(
                    label=get_text("btn_download_ppt", lang),
                    data=f.read(),
                    file_name=os.path.basename(ppt_path),
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True,
                    type="primary",
                )
        except Exception as exc:
            logger.exception("PPTX generation error: %s", exc)
            st.error(f"❌ **PPT Error**: {exc}")

        # ── Debug diagnostics expander ──────────────────────────────────
        # Task 8: Add parser diagnostics expander
        with st.expander("🛠️ Debug Diagnostics"):
            st.markdown("### Raw AI Response")
            raw_resp = st.session_state.get("raw_ollama_response") or "N/A"
            st.code(raw_resp, language="json")

            st.markdown("### Parsed JSON")
            try:
                parsed_dict = {
                    "executive_summary": report.executive_summary,
                    "background_context": report.background_context,
                    "core_concepts": report.core_concepts,
                    "key_insights": report.key_insights,
                    "benefits_challenges_risks": (
                        report.benefits_challenges_risks
                    ),
                    "real_world_applications": (
                        report.real_world_applications
                    ),
                    "future_outlook": report.future_outlook,
                    "statistics": report.statistics,
                    "references": report.references,
                }
                st.json(parsed_dict)
            except Exception as e:
                st.error(f"Error displaying parsed JSON: {e}")

            st.markdown("### Validation Warnings / Dynamic Corrections")
            if report.warnings:
                for w in report.warnings:
                    st.write(f"- {w}")
            else:
                st.write("No warnings. Perfect schema match!")

else:
    st.markdown("---")
    # Native suggestion hint
    hint_text = (
        "👆 Enter a research topic above and click **Generate Report** to get started."
    )
    if lang == "hi":
        hint_text = (
            "👆 ऊपर एक शोध विषय दर्ज करें और आरंभ करने के लिए **रिपोर्ट उत्पन्न करें** पर क्लिक करें।"
        )
    elif lang == "mr":
        hint_text = (
            "👆 वर एक संशोधन विषय प्रविष्ट करा आणि "
            "सुरू करण्यासाठी **अहवाल तयार करा** वर क्लिक करा।"
        )
    elif lang == "te":
        hint_text = (
            "👆 పైన ఒక పరిశోధనా అంశాన్ని నమోదు చేసి, ప్రారంభించడానికి **నివేదికను సృష్టించండి** క్లిక్ చేయండి."
        )
    st.info(hint_text)

# ── Reviews Dashboard Section ────────────────────────────────────
st.markdown("---")
st.markdown("## 🌟 Community Reviews")

reviews = load_reviews()
if not reviews:
    st.markdown(
        """
        <div style="padding: 2rem; text-align: center; background: """
        """rgba(26, 34, 54, 0.3); border-radius: var(--radius-md); """
        """border: 1px solid rgba(255, 255, 255, 0.06);">
            <h3 style="margin: 0; color: #F8FAFC;">🌟 No reviews yet</h3>
            <p style="color: #94A3B8; margin-top: 0.5rem; """
            """margin-bottom: 0;">Be the first person to review DeepDive AI.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Load calculations
    from utils.reviews_manager import (
        calculate_average_rating,
        get_rating_distribution,
    )

    average_rating = calculate_average_rating(reviews)
    total_reviews = len(reviews)
    distribution = get_rating_distribution(reviews)

    # 1. Rating Summary Header columns
    col_summary, col_analytics = st.columns([1, 2])
    with col_summary:
        filled_stars = "★" * round(average_rating)
        empty_stars = "☆" * (5 - round(average_rating))
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1.5rem; height: 100%; """
            """background: rgba(26, 34, 54, 0.3); border-radius: """
            """var(--radius-md); border: 1px solid rgba(255, 255, 255, 0.06); """
            """display: flex; flex-direction: column; justify-content: """
            """center; align-items: center;">
                <div style="font-size: 3.2rem; font-weight: 800; """
                f"""color: #F8FAFC; line-height: 1;">{average_rating}</div>
                <div style="color: #A855F7; font-size: 1.6rem; margin: """
                """0.5rem 0; letter-spacing: 2px;">"""
                f"""{filled_stars}{empty_stars}</div>
                <div style="color: #94A3B8; font-size: 0.95rem;">"""
                f"""Based on {total_reviews} reviews</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_analytics:
        # Star distribution progress bars
        for star in [5, 4, 3, 2, 1]:
            count = distribution.get(star, 0)
            pct = (count / total_reviews * 100) if total_reviews > 0 else 0
            star_label = "★" * star + "☆" * (5 - star)
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; """
                """margin-bottom: 0.5rem;">
                    <div style="width: 85px; color: #A855F7; """
                    """font-family: monospace; """
                    f"""font-size: 0.9rem; letter-spacing: 1px;">{star_label}</div>
                    <div style="flex-grow: 1; height: 8px; background: """
                    """rgba(255, 255, 255, 0.05); border-radius: 4px; """
                    """margin: 0 12px; overflow: hidden; position: relative;">
                        <div style="width: {pct}%; height: 100%; background: """
                        """linear-gradient(90deg, #7C3AED, #EC4899); """
                        """border-radius: 4px;"></div>
                    </div>
                    <div style="width: 35px; text-align: right; color: #94A3B8; """
                    f"""font-size: 0.85rem; font-weight: 600;">{count}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Sorting select box
    col_sort_empty, col_sort_select = st.columns([4, 1])
    with col_sort_select:
        sort_option = st.selectbox(
            "Sort reviews:",
            options=["Newest", "Highest Rating", "Lowest Rating"],
            key="reviews_dashboard_sort",
            label_visibility="collapsed",
        )

    # Sort the reviews list
    from datetime import datetime

    def parse_ts(ts_str: str) -> float:
        try:
            return datetime.strptime(ts_str, "%Y-%m-%d %H:%M").timestamp()
        except Exception:
            return 0.0

    if sort_option == "Newest":
        sorted_reviews = sorted(
            reviews, key=lambda x: parse_ts(x.timestamp), reverse=True
        )
    elif sort_option == "Highest Rating":
        sorted_reviews = sorted(
            reviews,
            key=lambda x: (x.rating, parse_ts(x.timestamp)),
            reverse=True,
        )
    else:
        sorted_reviews = sorted(
            reviews, key=lambda x: (x.rating, -parse_ts(x.timestamp))
        )

    # 3. Format Date function helper
    def format_date(ts_str: str) -> str:
        try:
            dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M")
            return dt.strftime("%d %b %Y")
        except Exception:
            return ts_str

    # 4. Render Reviews Cards Grid
    st.markdown('<div class="reviews-container">', unsafe_allow_html=True)
    for rev in sorted_reviews:
        r_stars_filled = "★" * rev.rating
        r_stars_empty = "☆" * (5 - rev.rating)
        comment_html = ""
        if rev.comment:
            comment_html = f'<div class="review-comment">"{rev.comment}"</div>'

        formatted_date = format_date(rev.timestamp)

        st.markdown(
            f"""
            <div class="review-card">
                <div class="review-stars">{r_stars_filled}{r_stars_empty}</div>
                <div class="review-author">{rev.name}</div>
                {comment_html}
                <div class="review-date">{formatted_date}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ── Temporary Streamlit Debug Expanders (Task 1 & Task 2) ───────────
if (
    st.session_state.get("raw_ollama_response") is not None
    or st.session_state.get("cleaned_ollama_response") is not None
    or st.session_state.get("parsed_json") is not None
    or st.session_state.get("validation_results") is not None
):
    st.markdown("---")
    st.markdown("### 🛠️ Ollama Diagnostic Logs")

    # Task 6: Add prompt diagnostics expander
    with st.expander("DEBUG - PROMPT"):
        st.text(st.session_state.get("prompt_sent") or "N/A")

    # Task 1 debug expander
    with st.expander("DEBUG - RAW MODEL OUTPUT"):
        st.code(str(st.session_state.get("raw_ollama_response")))

    # Task 2 debug expander
    with st.expander("DEBUG - PARSING"):
        st.write("RAW:", st.session_state.get("raw_ollama_response"))
        st.write("CLEANED:", st.session_state.get("cleaned_ollama_response"))

        parsed_obj = st.session_state.get("parsed_json")
        st.write("PARSED JSON KEYS:")
        st.write(list(parsed_obj.keys()) if isinstance(parsed_obj, dict) else [])

        st.write("PARSED JSON:")
        st.json(parsed_obj or {})

        from utils.report_schema import REQUIRED_FIELDS
        st.write("EXPECTED SCHEMA:")
        st.json(REQUIRED_FIELDS)

        missing_fields = st.session_state.get("missing_fields") or []
        st.write("MISSING FIELDS:")
        if missing_fields:
            st.error(f"Missing fields: {missing_fields}")
        else:
            st.write([])

        st.write("VALIDATION RESULTS:", st.session_state.get("validation_results"))
