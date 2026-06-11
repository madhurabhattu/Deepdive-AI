"""
DeepDive AI — Streamlit Entry Point

Configures the app-wide page settings, custom theme CSS, and sidebar navigation.
All business logic lives in utils/; pages handle UI only (Constitution §IV).
"""

from __future__ import annotations

import logging
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
