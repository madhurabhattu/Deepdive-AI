"""
DeepDive AI — Streamlit Entry Point

Configures the app-wide page settings, custom theme CSS, and sidebar navigation.
All business logic lives in utils/; pages handle UI only (Constitution §IV).
"""

from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st

from utils.ai_client import OLLAMA_BASE_URL, OLLAMA_MODELS, is_ollama_available
from utils.env_validator import validate_environment
from utils.localization import LANGUAGES, detect_browser_language, get_text
from utils.reviews_manager import render_sidebar_review_form

# ── Logging Configuration ───────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

# ── Validate Environment variables ──────────────────────────────────
validate_environment()

# ── Ensure output directory exists at startup (T024) ────────────────
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Page Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title="DeepDive AI — Research Report Generator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State Defaults ──────────────────────────────────────────
if "ui_lang" not in st.session_state:
    st.session_state["ui_lang"] = detect_browser_language()
if "ai_provider" not in st.session_state:
    st.session_state["ai_provider"] = "gemini_builtin"
if "byok_api_key" not in st.session_state:
    st.session_state["byok_api_key"] = ""
if "ollama_model" not in st.session_state:
    st.session_state["ollama_model"] = OLLAMA_MODELS[0]

# ── Global Custom CSS (T021) ────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* ─── Global Styling ─── */
    html, body, .stApp {
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

    /* Reset button styling inside File Uploader to prevent override issues */
    div[data-testid="stFileUploader"] button {
        background: transparent !important;
        color: #94A3B8 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: none !important;
        padding: 0.3rem 0.8rem !important;
        font-weight: 500 !important;
        transition: none !important;
        transform: none !important;
    }
    div[data-testid="stFileUploader"] button:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
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

    /* ─── Hero Card Styling ─── */
    .hero-container {
        background: linear-gradient(
            135deg,
            rgba(26, 34, 54, 0.4) 0%,
            rgba(17, 24, 39, 0.6) 100/
        );
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 3.5rem 2rem;
        border-radius: var(--radius-lg);
        margin-bottom: 2.5rem;
        box-shadow: var(--shadow-lg);
        backdrop-filter: blur(12px);
        position: relative;
        overflow: hidden;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: -40%;
        left: -20%;
        width: 300px;
        height: 300px;
        background: radial-gradient(
            circle,
            rgba(124, 58, 237, 0.15) 0%,
            transparent 70/
        );
        filter: blur(40px);
        pointer-events: none;
    }
    .hero-container::after {
        content: '';
        position: absolute;
        bottom: -40%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: radial-gradient(
            circle,
            rgba(236, 72, 153, 0.15) 0%,
            transparent 70/
        );
        filter: blur(40px);
        pointer-events: none;
    }
    .hero-container h1 {
        background: linear-gradient(135deg, #F8FAFC 30%, #A855F7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.04em;
        line-height: 1.15;
    }
    .hero-container .subtitle {
        color: #94A3B8;
        font-size: 1.2rem;
        margin-top: 1rem;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
    }

    /* ─── Feature Card Grid Styling ─── */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.25rem;
        margin-top: 1.5rem;
    }
    .feature-card {
        background: rgba(26, 34, 54, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: var(--radius-md);
        padding: 1.6rem;
        backdrop-filter: blur(8px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-sm);
    }
    .feature-card:hover {
        transform: translateY(-4px);
        background: rgba(26, 34, 54, 0.5);
        border-color: rgba(168, 85, 247, 0.25);
        box-shadow: 0 10px 25px rgba(124, 58, 237, 0.08);
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
        display: inline-block;
    }
    .feature-title {
        color: #F8FAFC;
        font-weight: 600;
        font-size: 1.15rem;
        margin-bottom: 0.4rem;
    }
    .feature-desc {
        color: #94A3B8;
        font-size: 0.92rem;
        line-height: 1.5;
    }

    /* ─── CTA Box ─── */
    .cta-section {
        text-align: center;
        margin-top: 2.5rem;
        padding: 1.8rem;
        background: linear-gradient(
            135deg,
            rgba(26, 34, 54, 0.2) 0%,
            rgba(17, 24, 39, 0.4) 100/
        );
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: var(--radius-md);
        backdrop-filter: blur(8px);
    }
    .cta-section p {
        color: #F8FAFC;
        font-size: 1.15rem;
        font-weight: 500;
        margin: 0;
        background: linear-gradient(135deg, #F8FAFC 0%, #A855F7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* ─── Other Custom Cards ─── */
    .section-card {
        background: rgba(26, 34, 54, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.8rem !important;
        margin-bottom: 1.5rem !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: var(--shadow-md) !important;
    }
    .section-card h3 {
        color: #F8FAFC !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.6rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* ─── Hide default branding ─── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {background: transparent;}
    </style>
    """,
    unsafe_allow_html=True,
)

lang = st.session_state["ui_lang"]

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
        key="ai_provider_selector",
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
            ">☁️ Provider: Built-in Gemini</div>",
            unsafe_allow_html=True,
        )
    elif st.session_state["ai_provider"] == "gemini_byok":
        st.caption(
            "🔑 **BYOK Gemini**: Use your personal Gemini API key. "
            "Falls back to built-in if left blank."
        )
        # ── BYOK key input ────────────────────────────────────────
        byok_input = st.text_input(
            "🔑 Gemini API Key",
            value=st.session_state["byok_api_key"],
            type="password",
            placeholder="Paste your API key or leave blank to use secrets",
            key="byok_key_input_app",
            help=(
                "Your key is stored only in this browser session. "
                "Get one free at ai.google.dev"
            ),
        )
        st.session_state["byok_api_key"] = byok_input
        st.caption(
            "[Get a free key](https://ai.google.dev)"
        )
        st.markdown(
            "<div style='"
            "background:rgba(124,58,237,0.12);"
            "border-left:3px solid #7C3AED;"
            "padding:6px 10px;border-radius:6px;"
            "font-size:0.78rem;color:#A855F7;margin-top:4px'"
            ">☁️ Provider: BYOK Gemini</div>",
            unsafe_allow_html=True,
        )
    elif st.session_state["ai_provider"] == "ollama":
        st.caption(
            "🖥️ **Ollama Local**: Runs models locally on your machine. "
            "Requires Ollama to be running on localhost:11434."
        )
        # ── Ollama model selector ─────────────────────────────────
        selected_model = st.selectbox(
            "🧠 Local Model",
            options=OLLAMA_MODELS,
            index=(
                OLLAMA_MODELS.index(st.session_state["ollama_model"])
                if st.session_state["ollama_model"] in OLLAMA_MODELS
                else 0
            ),
            key="ollama_model_selector_app",
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
                f">🖥️ Provider: Ollama · {selected_model}</div>",
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

# ── Top Navigation / Language Switcher Row ──────────────────────────
col_empty, col_lang_switch = st.columns([5, 1])
with col_lang_switch:
    ui_lang_selected = st.selectbox(
        "🌐 Language / भाषा / भाषा / భాష",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: f"🌐 {LANGUAGES[x]}",
        index=list(LANGUAGES.keys()).index(st.session_state["ui_lang"]),
        key="ui_lang_selector_app",
        label_visibility="collapsed",
    )
    if ui_lang_selected != st.session_state["ui_lang"]:
        st.session_state["ui_lang"] = ui_lang_selected
        st.rerun()

# ── Main Landing Page ──────────────────────────────────────────────
st.markdown(
    f"""
    <div class="hero-container">
        <h1>{get_text("app_title", lang)}</h1>
        <p class="subtitle">
            {get_text("hero_subtitle", lang)}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <div class="feature-title">{get_text("feat_summary_title", lang)}</div>
            <div class="feature-desc">
                {get_text("feat_summary_desc", lang)}
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">💡</div>
            <div class="feature-title">{get_text("feat_insights_title", lang)}</div>
            <div class="feature-desc">
                {get_text("feat_insights_desc", lang)}
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">{get_text("feat_stats_title", lang)}</div>
            <div class="feature-desc">
                {get_text("feat_stats_desc", lang)}
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <div class="feature-title">{get_text("feat_ref_title", lang)}</div>
            <div class="feature-desc">
                {get_text("feat_ref_desc", lang)}
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">{get_text("feat_pdf_title", lang)}</div>
            <div class="feature-desc">
                {get_text("feat_pdf_desc", lang)}
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📽️</div>
            <div class="feature-title">{get_text("feat_ppt_title", lang)}</div>
            <div class="feature-desc">
                {get_text("feat_ppt_desc", lang)}
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="cta-section">
        <p>{get_text("cta_text", lang)}</p>
    </div>
    """,
    unsafe_allow_html=True,
)
