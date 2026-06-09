"""
DeepDive AI — Streamlit Entry Point

Configures the app-wide page settings, custom theme CSS, and sidebar navigation.
All business logic lives in utils/; pages handle UI only (Constitution §IV).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import streamlit as st

# ── Logging Configuration ───────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

# ── Ensure output directory exists at startup (T024) ────────────────
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Page Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title="DeepDive AI — Research Report Generator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Global Custom CSS (T021) ────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ─── Global Typography ─────────────────────────────────────── */
    html, body, [class*="st-"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ─── Dark Theme Palette ────────────────────────────────────── */
    :root {
        --primary: #1a237e;
        --primary-light: #3949ab;
        --accent: #0d47a1;
        --accent-light: #1565c0;
        --surface: #ffffff;
        --surface-alt: #f5f5f7;
        --text-primary: #212121;
        --text-secondary: #616161;
        --indigo-50: #e8eaf6;
        --indigo-100: #c5cae9;
        --purple-50: #f3e5f5;
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 32px rgba(26, 35, 126, 0.15);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
    }

    /* ─── Streamlit Overrides ───────────────────────────────────── */
    .stApp {
        background: linear-gradient(180deg, #f8f9ff 0%, #f0f1f7 100%);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a237e 0%, #0d47a1 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e8eaf6 !important;
    }
    [data-testid="stSidebar"] .stMarkdown a {
        color: #90caf9 !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"],
    .stDownloadButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        border: none;
        border-radius: var(--radius-sm);
        font-weight: 600;
        letter-spacing: 0.02em;
        transition: all 0.25s ease;
        box-shadow: var(--shadow-sm);
    }
    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button[kind="primary"]:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-1px);
    }

    /* Text input */
    .stTextInput input {
        border-radius: var(--radius-sm);
        border: 2px solid var(--indigo-100);
        padding: 0.7rem 1rem;
        font-size: 1rem;
        transition: border-color 0.2s ease;
    }
    .stTextInput input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(26, 35, 126, 0.1);
    }

    /* Divider */
    hr {
        border-color: var(--indigo-50);
    }

    /* Hero section on landing */
    .hero-container {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 40%, #1565c0 100%);
        padding: 3rem;
        border-radius: var(--radius-lg);
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 60%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-container h1 {
        color: #ffffff;
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.03em;
        line-height: 1.15;
    }
    .hero-container .subtitle {
        color: #c5cae9;
        font-size: 1.15rem;
        margin-top: 0.6rem;
        font-weight: 400;
    }

    /* Feature cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1rem;
        margin-top: 1.5rem;
    }
    .feature-card {
        background: var(--surface);
        border: 1px solid var(--indigo-50);
        border-radius: var(--radius-md);
        padding: 1.4rem;
        transition: all 0.25s ease;
        box-shadow: var(--shadow-sm);
    }
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
        border-color: var(--indigo-100);
    }
    .feature-icon {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    .feature-title {
        color: var(--primary);
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.3rem;
    }
    .feature-desc {
        color: var(--text-secondary);
        font-size: 0.88rem;
        line-height: 1.45;
    }

    /* CTA */
    .cta-section {
        text-align: center;
        margin-top: 2rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, var(--indigo-50) 0%, var(--purple-50) 100%);
        border-radius: var(--radius-md);
    }
    .cta-section p {
        color: var(--primary);
        font-size: 1.1rem;
        font-weight: 500;
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔬 DeepDive AI")
    st.caption("AI-Powered Research Report Generator")
    st.divider()
    st.markdown(
        """
        **How to use:**
        1. Go to **🔬 Research** page
        2. Enter any research topic
        3. Click **Generate Report**
        4. Download **PDF** or **PPT**
        """
    )
    st.divider()
    st.markdown(
        "Built with [Streamlit](https://streamlit.io) "
        "& [Gemini AI](https://ai.google.dev)",
    )


# ── Main Landing Page ──────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-container">
        <h1>🔬 DeepDive AI</h1>
        <p class="subtitle">
            Enter any research topic and receive a comprehensive, AI-generated
            report — complete with executive summary, key insights, statistics,
            and downloadable exports.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <div class="feature-title">Executive Summary</div>
            <div class="feature-desc">
                A concise, professional overview of your research topic
                crafted by AI.
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">💡</div>
            <div class="feature-title">Key Insights</div>
            <div class="feature-desc">
                The most important findings and takeaways, distilled for
                quick understanding.
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Statistics &amp; Data</div>
            <div class="feature-desc">
                Relevant numbers, metrics, and data points to support
                your research.
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <div class="feature-title">References &amp; Citations</div>
            <div class="feature-desc">
                Credible sources for further reading, complete with
                descriptions and URLs.
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">PDF Report</div>
            <div class="feature-desc">
                Download a professionally formatted PDF report ready
                for sharing or archiving.
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📽️</div>
            <div class="feature-title">PowerPoint Deck</div>
            <div class="feature-desc">
                Get a ready-to-present slide deck — perfect for
                meetings and classrooms.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="cta-section">
        <p>👉 Select <strong>🔬 Research</strong> from the sidebar to get started.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
