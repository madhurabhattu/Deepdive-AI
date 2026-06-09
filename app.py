"""
DeepDive AI — Streamlit Entry Point

Configures the app-wide page settings and sidebar navigation.
All business logic lives in utils/; pages handle UI only.
"""

import streamlit as st


# ── Page Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title="DeepDive AI — Research Report Generator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/microscope.png",
        width=64,
    )
    st.title("DeepDive AI")
    st.caption("AI-Powered Research Report Generator")
    st.divider()
    st.markdown(
        """
        **How to use:**
        1. Navigate to the **🔬 Research** page.
        2. Enter any research topic.
        3. Click **Generate Report**.
        4. Download your **PDF** or **PowerPoint**.
        """
    )
    st.divider()
    st.markdown(
        "Built with [Streamlit](https://streamlit.io) "
        "& [Gemini AI](https://ai.google.dev)",
    )


# ── Main Landing Page ──────────────────────────────────────────────
st.title("🔬 DeepDive AI")
st.subheader("AI-Powered Research Report Generator")

st.markdown(
    """
    Welcome to **DeepDive AI** — enter any research topic and receive a
    fully structured, AI-generated report in seconds.

    ### What you get:
    - 📝 **Executive Summary** — a concise overview of the topic
    - 💡 **Key Insights** — the most important findings
    - 📊 **Statistics & Data** — relevant numbers and metrics
    - 📚 **References & Citations** — credible sources for further reading
    - ⬇️ **Downloadable PDF** — a professionally formatted report
    - ⬇️ **Downloadable PowerPoint** — a ready-to-present slide deck

    👉 **Get started** by selecting **🔬 Research** from the sidebar.
    """
)
