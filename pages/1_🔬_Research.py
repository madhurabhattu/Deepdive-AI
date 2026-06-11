"""
DeepDive AI — 🔬 Research Page

Streamlit page view for the research report workflow:
1. User enters a research topic
2. Clicks "Generate Report"
3. AI generates a structured report
4. Report sections are rendered in the UI
5. PDF and PPTX download buttons are provided

All business logic lives in utils/; this module handles UI only
(Constitution §IV).
"""

from __future__ import annotations

import logging
import os
import traceback

import streamlit as st

from utils.ai_client import generate_research_report
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

# ── Header ──────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="main-header">
        <h1>🔬 Research Report Generator</h1>
        <p>Enter a topic and let AI generate a comprehensive
        research report for you.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Session State Defaults ──────────────────────────────────────────
if "report" not in st.session_state:
    st.session_state["report"] = None
if "generating" not in st.session_state:
    st.session_state["generating"] = False
if "pdf_path" not in st.session_state:
    st.session_state["pdf_path"] = None
if "ppt_path" not in st.session_state:
    st.session_state["ppt_path"] = None

# ── Topic Input & Generate Button ──────────────────────────────────
col_input, col_btn = st.columns([4, 1])

with col_input:
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Impact of climate change on agriculture",
        label_visibility="collapsed",
        max_chars=500,
        key="topic_input",
    )

with col_btn:
    generate_clicked = st.button(
        "🚀 Generate Report",
        use_container_width=True,
        disabled=st.session_state.get("generating", False),
        type="primary",
    )

# ── Input Validation & Generation ──────────────────────────────────
if generate_clicked:
    if not topic or not topic.strip():
        st.warning("⚠️ Please enter a research topic.")
    else:
        display_topic = topic[:200] + "…" if len(topic) > 200 else topic

        st.session_state["generating"] = True
        st.session_state["report"] = None
        st.session_state["pdf_path"] = None
        st.session_state["ppt_path"] = None

        spinner_msg = (
            f"🔍 Researching **{display_topic}**… "
            "This may take up to 30 seconds."
        )
        with st.spinner(spinner_msg):
            try:
                raw_json = generate_research_report(topic.strip())
                parsed_report = parse_report(raw_json, topic=topic.strip())
                st.session_state["report"] = parsed_report
                st.session_state["generating"] = False
                st.success("✅ Report generated successfully!")

            except OSError as exc:
                st.session_state["generating"] = False
                st.error(
                    "🔑 API key not configured. Please configure "
                    "`GEMINI_API_KEY` in Streamlit Secrets, environment "
                    "variables, or your `.env` file."
                )
                logger.error("Environment error: %s", exc)
                logger.debug(traceback.format_exc())

            except RuntimeError as exc:
                st.session_state["generating"] = False
                st.error(
                    "❌ Research generation failed. Please try again."
                )
                logger.error("API error: %s", exc)
                logger.debug(traceback.format_exc())

            except ValueError as exc:
                st.session_state["generating"] = False
                st.error(
                    "⚠️ The AI returned an unexpected response format. "
                    "Please try again."
                )
                logger.error("Schema validation error: %s", exc)
                logger.debug(traceback.format_exc())

            except Exception as exc:
                st.session_state["generating"] = False
                st.error(
                    "❌ An unexpected error occurred. Please try again."
                )
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
            <h3>📝 Executive Summary</h3>
            <p style="color: #94A3B8; line-height: 1.75; font-size: 1.05rem;">
                {report.executive_summary}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Key Insights ─────────────────────────────────────────────────
    if len(report.key_insights) < 3:
        st.markdown(
            '<div class="limited-data-banner">'
            "⚠️ Limited data available for this topic."
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section-card"><h3>💡 Key Insights</h3>',
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
        '<div class="section-card"><h3>📊 Statistics &amp; Data</h3></div>',
        unsafe_allow_html=True,
    )

    if len(report.statistics) < 3:
        st.markdown(
            '<div class="limited-data-banner">'
            "⚠️ Limited statistical data available for this topic."
            "</div>",
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

    # ── References ───────────────────────────────────────────────────
    st.markdown(
        '<div class="section-card"><h3>📚 References &amp; Citations</h3></div>',
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
        '<div class="download-section">'
        "<h3>⬇_ Download Your Report</h3>"
        "</div>",
        unsafe_allow_html=True,
    )

    col_pdf, col_ppt = st.columns(2)

    with col_pdf:
        try:
            if st.session_state.get("pdf_path") is None:
                pdf_path = build_pdf(report)
                st.session_state["pdf_path"] = pdf_path
            else:
                pdf_path = st.session_state["pdf_path"]

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=f.read(),
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                )
        except Exception as exc:
            st.error("Failed to generate PDF. Please try again.")
            logger.error("PDF generation error: %s", exc)

    with col_ppt:
        try:
            if st.session_state.get("ppt_path") is None:
                ppt_path = build_ppt(report)
                st.session_state["ppt_path"] = ppt_path
            else:
                ppt_path = st.session_state["ppt_path"]

            with open(ppt_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download PPT",
                    data=f.read(),
                    file_name=os.path.basename(ppt_path),
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True,
                    type="primary",
                )
        except Exception as exc:
            st.error("Failed to generate PowerPoint. Please try again.")
            logger.error("PPTX generation error: %s", exc)

else:
    st.markdown("---")
    st.info(
        "👆 Enter a research topic above and click **Generate Report** "
        "to get started."
    )
