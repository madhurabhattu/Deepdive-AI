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

from utils.ai_client import generate_research_report
from utils.localization import LANGUAGES, detect_browser_language, get_text
from utils.pdf_generator import build_pdf
from utils.ppt_generator import build_ppt
from utils.report_schema import ResearchReport, parse_report

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
    st.markdown(
        f"**{get_text('how_to_use', lang)}**\n\n"
        f"{get_text('step_1', lang)}\n\n"
        f"{get_text('step_2', lang)}\n\n"
        f"{get_text('step_3', lang)}\n\n"
        f"{get_text('step_4', lang)}"
    )
    st.divider()
    st.markdown(
        f"{get_text('built_with', lang)} [Streamlit](https://streamlit.io) "
        "& [Gemini AI](https://ai.google.dev)",
    )

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

        st.session_state["generating"] = True
        st.session_state["report"] = None
        st.session_state["pdf_path"] = None
        st.session_state["ppt_path"] = None

        spinner_msg = get_text("spinner_msg", lang).format(topic=display_topic)
        with st.spinner(spinner_msg):
            try:
                raw_json = generate_research_report(
                    topic.strip(), report_lang=st.session_state["report_lang"]
                )
                parsed_report = parse_report(raw_json, topic=topic.strip())
                st.session_state["report"] = parsed_report
                st.session_state["generating"] = False
                st.success(get_text("success_msg", lang))

            except OSError as exc:
                st.session_state["generating"] = False
                st.error(get_text("err_api_key", lang))
                logger.error("Environment error: %s", exc)
                logger.debug(traceback.format_exc())

            except RuntimeError as exc:
                st.session_state["generating"] = False
                st.error(get_text("err_generation", lang))
                logger.error("API error: %s", exc)
                logger.debug(traceback.format_exc())

            except ValueError as exc:
                st.session_state["generating"] = False
                st.error(get_text("err_schema", lang))
                logger.error("Schema validation error: %s", exc)
                logger.debug(traceback.format_exc())

            except Exception as exc:
                st.session_state["generating"] = False
                st.error(get_text("err_unexpected", lang))
                logger.error("Unexpected error: %s", exc)
                logger.debug(traceback.format_exc())

# ── Report Display ──────────────────────────────────────────────────
report: ResearchReport | None = st.session_state.get("report")

if report is not None:
    st.divider()

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

    # Render stat cards in columns (up to 3 per row)
    stats = report.statistics
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
            st.error(get_text("pdf_err", lang))
            logger.error("PDF generation error: %s", exc)

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
            st.error(get_text("ppt_err", lang))
            logger.error("PPTX generation error: %s", exc)

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
