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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global typography */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 50%, #1565c0 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(26, 35, 126, 0.25);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .main-header p {
        color: #c5cae9;
        font-size: 1.05rem;
        margin: 0.5rem 0 0 0;
    }

    /* Section cards */
    .section-card {
        background: #ffffff;
        border: 1px solid #e8eaf6;
        border-radius: 12px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
        transition: box-shadow 0.2s ease;
    }
    .section-card:hover {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    .section-card h3 {
        color: #1a237e;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e8eaf6;
    }

    /* Insight items */
    .insight-item {
        background: linear-gradient(135deg, #e8eaf6 0%, #f3e5f5 100%);
        border-left: 4px solid #1a237e;
        padding: 0.9rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.7rem;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* Stat cards */
    .stat-card {
        background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(26, 35, 126, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(26, 35, 126, 0.15);
    }
    .stat-label {
        color: #1a237e;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.3rem;
    }
    .stat-value {
        color: #0d47a1;
        font-size: 1.6rem;
        font-weight: 700;
    }

    /* Reference cards */
    .ref-card {
        background: #fafafa;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem 1.3rem;
        margin-bottom: 0.7rem;
        transition: border-color 0.2s ease;
    }
    .ref-card:hover {
        border-color: #1a237e;
    }
    .ref-title {
        color: #0d47a1;
        font-weight: 600;
        font-size: 1rem;
    }
    .ref-snippet {
        color: #616161;
        font-size: 0.9rem;
        margin-top: 0.3rem;
        line-height: 1.4;
    }
    .ref-url {
        color: #9e9e9e;
        font-size: 0.8rem;
        margin-top: 0.2rem;
        word-break: break-all;
    }

    /* Download button area */
    .download-section {
        background: linear-gradient(135deg, #e8eaf6 0%, #ede7f6 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        text-align: center;
    }

    /* Warning banner */
    .limited-data-banner {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 0.8rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
        color: #e65100;
        font-weight: 500;
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
    # T013: Input validation
    if not topic or not topic.strip():
        st.warning("⚠️ Please enter a research topic.")
    else:
        # T023: Handle topic > 200 chars for display
        display_topic = topic[:200] + "…" if len(topic) > 200 else topic

        st.session_state["generating"] = True
        st.session_state["report"] = None
        st.session_state["pdf_path"] = None
        st.session_state["ppt_path"] = None

        # T011: Generate report with spinner
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
                # T014: API key missing
                st.session_state["generating"] = False
                st.error(
                    "🔑 API key not configured. Please configure "
                    "`GEMINI_API_KEY` in Streamlit Secrets, environment "
                    "variables, or your `.env` file."
                )
                logger.error("Environment error: %s", exc)
                logger.debug(traceback.format_exc())

            except RuntimeError as exc:
                # T014: API failure
                st.session_state["generating"] = False
                st.error(
                    "❌ Research generation failed. Please try again."
                )
                logger.error("API error: %s", exc)
                logger.debug(traceback.format_exc())

            except ValueError as exc:
                # T014: Schema validation failure
                st.session_state["generating"] = False
                st.error(
                    "⚠️ The AI returned an unexpected response format. "
                    "Please try again."
                )
                logger.error("Schema validation error: %s", exc)
                logger.debug(traceback.format_exc())

            except Exception as exc:
                # Catch-all: no unhandled exceptions reach the user (SC-004)
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
            <p style="color: #424242; line-height: 1.7; font-size: 1rem;">
                {report.executive_summary}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Key Insights ─────────────────────────────────────────────────
    # Show warning if fewer than 3 insights (edge case)
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

    # Show warning if fewer than 3 statistics (edge case)
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
        "<h3>⬇️ Download Your Report</h3>"
        "</div>",
        unsafe_allow_html=True,
    )

    col_pdf, col_ppt = st.columns(2)

    # T017: PDF Download
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

    # T020: PPT Download
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
    # No report yet — show guidance
    st.markdown("---")
    st.info(
        "👆 Enter a research topic above and click **Generate Report** "
        "to get started."
    )
