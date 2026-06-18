"""DeepDive AI — Document Q&A Page.

Local-first document question-answering workflow.
"""

from __future__ import annotations

import logging
import os
import sys
import tempfile
import time
import streamlit as st

from utils.ai_client import OLLAMA_BASE_URL, OLLAMA_MODELS, is_ollama_available
from utils.document_chunker import chunk_document_pages
from utils.document_loader import load_pdf_document
from utils.embedding_service import get_embeddings
from utils.localization import LANGUAGES, get_text
from utils.rag_pipeline import stream_rag_answer
from utils.vector_store import FAISSVectorStore

logger = logging.getLogger(__name__)

# ── Localization for Q&A ───────────────────────────────────────────
QA_TRANSLATIONS = {
    "en": {
        "title": "📄 local-first Document Q&A",
        "subtitle": "Ask questions and search through your PDF documents locally and privately",
        "upload_section": "📄 Document Upload",
        "drag_drop": "Upload one or more PDF files",
        "index_btn": "⚡ Index Documents",
        "indexing_msg": "Processing and indexing documents...",
        "indexed_success": "Successfully indexed {count} documents into {chunks} chunks!",
        "no_docs": "No documents indexed yet.",
        "status_title": "📊 Vector DB Status",
        "stats_docs": "Indexed Documents",
        "stats_chunks": "Total Chunks",
        "stats_emb": "Embedding Model",
        "stats_llm": "LLM Model",
        "stats_size": "Index Size",
        "local_badge": "🔒 Local Processing Enabled",
        "cloud_badge": "☁️ Cloud Processing Active",
        "input_placeholder": "Ask something about your documents...",
        "sources_title": "📚 Source Citations",
        "source_item": "**{filename}** (Page {page_number}) (Similarity: {score:.2f})",
        "no_context_warn": "⚠️ Please upload and index documents first before asking questions.",
        "remove_doc": "Remove document",
        "active_docs": "Active Documents:",
        "clear_index": "🗑️ Clear Index",
        "settings_section": "⚙️ Settings",
    },
    "hi": {
        "title": "📄 स्थानीय दस्तावेज़ प्रश्नोत्तर",
        "subtitle": "स्थानीय और निजी तौर पर अपने पीडीएफ दस्तावेजों में प्रश्न पूछें और खोजें",
        "upload_section": "📄 दस्तावेज़ अपलोड",
        "drag_drop": "एक या अधिक पीडीएफ फाइलें अपलोड करें",
        "index_btn": "⚡ दस्तावेज़ अनुक्रमित करें",
        "indexing_msg": "दस्तावेज़ों को संसाधित और अनुक्रमित किया जा रहा है...",
        "indexed_success": "{count} दस्तावेज़ों को {chunks} टुकड़ों में सफलतापूर्वक अनुक्रमित किया गया!",
        "no_docs": "अभी तक कोई दस्तावेज़ अनुक्रमित नहीं किया गया है।",
        "status_title": "📊 वेक्टर डेटाबेस स्थिति",
        "stats_docs": "अनुक्रमित दस्तावेज़",
        "stats_chunks": "कुल टुकड़े",
        "stats_emb": "एम्बेडिंग मॉडल",
        "stats_llm": "एलएलएम मॉडल",
        "stats_size": "इंडेक्स आकार",
        "local_badge": "🔒 स्थानीय प्रसंस्करण सक्षम",
        "cloud_badge": "☁️ क्लाउड प्रसंस्करण सक्रिय",
        "input_placeholder": "अपने दस्तावेज़ों के बारे में कुछ पूछें...",
        "sources_title": "📚 स्रोत उद्धरण",
        "source_item": "**{filename}** (पृष्ठ {page_number}) (समानता: {score:.2f})",
        "no_context_warn": "⚠️ प्रश्न पूछने से पहले कृपया दस्तावेज़ अपलोड और अनुक्रमित करें।",
        "remove_doc": "दस्तावेज़ हटाएं",
        "active_docs": "सक्रिय दस्तावेज़:",
        "clear_index": "🗑️ इंडेक्स साफ़ करें",
        "settings_section": "⚙️ सेटिंग्स",
    },
    "mr": {
        "title": "📄 स्थानिक दस्तऐवज प्रश्नोत्तरे",
        "subtitle": "स्थानिक आणि खाजगीरित्या आपल्या पीडीएफ दस्तऐवजांमध्ये प्रश्न विचारा आणि शोधा",
        "upload_section": "📄 दस्तऐवज अपलोड",
        "drag_drop": "एक किंवा अधिक पीडीएफ फाईल्स अपलोड करा",
        "index_btn": "⚡ दस्तऐवज अनुक्रमित करा",
        "indexing_msg": "दस्तऐवज प्रक्रिया आणि अनुक्रमित केले जात आहेत...",
        "indexed_success": "{count} दस्तऐवज {chunks} तुकड्यांमध्ये यशस्वीरित्या अनुक्रमित केले गेले!",
        "no_docs": "अद्याप कोणतेही दस्तऐवज अनुक्रमित केलेले नाहीत.",
        "status_title": "📊 वेक्टर डेटाबेस स्थिती",
        "stats_docs": "अनुक्रमित दस्तऐवज",
        "stats_chunks": "एकूण तुकडे",
        "stats_emb": "एम्बेडिंग मॉडेल",
        "stats_llm": "एलएलएम मॉडेल",
        "stats_size": "इंडेक्स आकार",
        "local_badge": "🔒 स्थानिक प्रक्रिया सक्षम",
        "cloud_badge": "☁️ क्लाउड प्रक्रिया सक्रिय",
        "input_placeholder": "तुमच्या दस्तऐवजांबद्दल काहीतरी विचारा...",
        "sources_title": "📚 स्रोत उद्धरणे",
        "source_item": "**{filename}** (पृष्ठ {page_number}) (साम्य: {score:.2f})",
        "no_context_warn": "⚠️ प्रश्न विचारण्यापूर्वी कृपया दस्तऐवज अपलोड आणि अनुक्रमित करा.",
        "remove_doc": "दस्तऐवज काढा",
        "active_docs": "सक्रिय दस्तऐवज:",
        "clear_index": "🗑️ इंडेक्स साफ करा",
        "settings_section": "⚙️ सेटिंग्ज",
    },
    "te": {
        "title": "📄 స్థానిక పత్రం ప్రశ్నోత్తరాలు",
        "subtitle": "స్థానికంగా మరియు ప్రైవేట్‌గా మీ పిడిఎఫ్ పత్రాలలో ప్రశ్నలు అడగండి మరియు శోధించండి",
        "upload_section": "📄 పత్రం అప్‌లోడ్",
        "drag_drop": "ఒకటి లేదా అంతకంటే ఎక్కువ పిడిఎఫ్ ఫైల్‌లను అప్‌లోడ్ చేయండి",
        "index_btn": "⚡ పత్రాలను ఇండెక్స్ చేయండి",
        "indexing_msg": "పత్రాలను ప్రాసెస్ మరియు ఇండెక్స్ చేస్తోంది...",
        "indexed_success": "{count} పత్రాలు {chunks} ముక్కలుగా విజయవంతంగా ఇండెక్స్ చేయబడ్డాయి!",
        "no_docs": "ఇంకా పత్రాలు ఇండెక్స్ చేయబడలేదు.",
        "status_title": "📊 వెక్టర్ డేటాబేస్ స్థితి",
        "stats_docs": "ఇండెక్స్ చేయబడిన పత్రాలు",
        "stats_chunks": "మొత్తం ముక్కలు",
        "stats_emb": "ఎంబెడ్డింగ్ మోడల్",
        "stats_llm": "ఎల్ఎల్ఎమ్ మోడల్",
        "stats_size": "ఇండెక్స్ పరిమాణం",
        "local_badge": "🔒 స్థానిక ప్రాసెసింగ్ ప్రారంభించబడింది",
        "cloud_badge": "☁️ క్లౌడ్ ప్రాసెసింగ్ క్రియాశీలంగా ఉంది",
        "input_placeholder": "మీ పత్రాల గురించి ఏదైనా అడగండి...",
        "sources_title": "📚 మూలాధారాలు",
        "source_item": "**{filename}** (పేజీ {page_number}) (పోలిక: {score:.2f})",
        "no_context_warn": "⚠️ ప్రశ్నలు అడగడానికి ముందు దయచేసి పత్రాలను అప్‌లోడ్ మరియు ఇండెక్స్ చేయండి.",
        "remove_doc": "పత్రాన్ని తీసివేయి",
        "active_docs": "క్రియాశీల పత్రాలు:",
        "clear_index": "🗑️ ఇండెక్స్ క్లియర్ చేయి",
        "settings_section": "⚙️ సెట్టింగులు",
    }
}


def get_qa_text(key: str, lang: str = "en") -> str:
    """Gets localized QA text, falling back to English."""
    if lang not in QA_TRANSLATIONS:
        lang = "en"
    return QA_TRANSLATIONS[lang].get(
        key, QA_TRANSLATIONS["en"].get(key, key)
    )


# ── CSS Styling ─────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        color: #F8FAFC;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', -apple-system, sans-serif;
        font-weight: 700 !important;
        color: #F8FAFC !important;
        letter-spacing: -0.02em;
    }

    .main-header {
        background: linear-gradient(
            135deg,
            rgba(26, 34, 54, 0.4) 0%,
            rgba(17, 24, 39, 0.6) 100%
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

    .badge-container {
        margin-bottom: 1.5rem;
    }
    .badge-local {
        display: inline-block;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid #10B981;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #34D399;
    }
    .badge-cloud {
        display: inline-block;
        background: rgba(124, 58, 237, 0.12);
        border: 1px solid #7C3AED;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #A855F7;
    }

    .status-card {
        background: rgba(26, 34, 54, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        box-shadow: var(--shadow-md);
    }
    .status-card h3 {
        color: #F8FAFC !important;
        font-size: 1.25rem;
        margin-top: 0 !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .status-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
    }
    .status-label {
        color: #94A3B8;
        margin-right: 10px;
    }
    .status-value {
        color: #F8FAFC;
        font-weight: 600;
        text-align: right;
        word-break: break-all;
    }

    .source-box {
        background: rgba(26, 34, 54, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-left: 3px solid #EC4899;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
        font-size: 0.88rem;
    }

    div[data-testid="stSpinner"] > div {
        border-top-color: #A855F7 !important;
    }

    /* Reset button styling inside File Uploader */
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
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session State Initialization ─────────────────────────────────────
lang = st.session_state.get("ui_lang", "en")

if "qa_uploaded_files" not in st.session_state:
    st.session_state["qa_uploaded_files"] = {}  # {filename: {"bytes": bytes, "chunks": list}}
if "qa_vector_store" not in st.session_state:
    st.session_state["qa_vector_store"] = None
if "qa_indexed_files" not in st.session_state:
    st.session_state["qa_indexed_files"] = []
if "qa_messages" not in st.session_state:
    st.session_state["qa_messages"] = []
if "qa_embedding_model" not in st.session_state:
    st.session_state["qa_embedding_model"] = (
        "nomic-embed-text" if is_ollama_available() else "all-MiniLM-L6-v2"
    )

# ── Sidebar 📄 Document Q&A ──────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### {get_qa_text('upload_section', lang)}")

    # Embedding Model selection
    st.markdown(f"**{get_qa_text('stats_emb', lang)}**")
    emb_model_choices = {
        "nomic-embed-text": "nomic-embed-text (Ollama)",
        "all-MiniLM-L6-v2": "all-MiniLM-L6-v2 (Local Fallback)",
        "BGE-small": "BGE-small (Local Fallback)",
    }
    selected_emb = st.selectbox(
        "Embedding Model Selector",
        options=list(emb_model_choices.keys()),
        format_func=lambda k: emb_model_choices[k],
        index=list(emb_model_choices.keys()).index(
            st.session_state["qa_embedding_model"]
        ),
        key="qa_emb_selector",
        label_visibility="collapsed",
    )
    if selected_emb != st.session_state["qa_embedding_model"]:
        st.session_state["qa_embedding_model"] = selected_emb
        st.rerun()

    st.divider()

    # File uploader
    uploaded_files = st.file_uploader(
        get_qa_text("drag_drop", lang),
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    # Process files uploaded into session state
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state["qa_uploaded_files"]:
                st.session_state["qa_uploaded_files"][file.name] = {
                    "bytes": file.getvalue(),
                    "chunks": [],
                }

    # Debug: programmatic load button for automated browser checks
    if os.path.exists("sample_docs.pdf"):
        if st.button("📥 Load Sample PDF", use_container_width=True):
            with open("sample_docs.pdf", "rb") as f:
                st.session_state["qa_uploaded_files"]["sample_docs.pdf"] = {
                    "bytes": f.read(),
                    "chunks": [],
                }
            st.toast("Loaded sample_docs.pdf from disk!", icon="📥")
            st.rerun()

    # Display active files and allow removal
    if st.session_state["qa_uploaded_files"]:
        st.markdown(f"**{get_qa_text('active_docs', lang)}**")
        to_delete = []
        for filename in list(st.session_state["qa_uploaded_files"].keys()):
            col_name, col_del = st.columns([5, 1])
            with col_name:
                is_indexed = filename in st.session_state["qa_indexed_files"]
                indexed_bullet = "✅" if is_indexed else "⏳"
                st.caption(f"{indexed_bullet} {filename}")
            with col_del:
                if st.button("❌", key=f"del_{filename}", help=get_qa_text("remove_doc", lang)):
                    to_delete.append(filename)

        if to_delete:
            for filename in to_delete:
                del st.session_state["qa_uploaded_files"][filename]
                if filename in st.session_state["qa_indexed_files"]:
                    st.session_state["qa_indexed_files"].remove(filename)

            # Rebuild vector index after removal
            with st.spinner(get_qa_text("indexing_msg", lang)):
                all_chunks = []
                all_texts = []
                for fname, info in st.session_state["qa_uploaded_files"].items():
                    if fname in st.session_state["qa_indexed_files"] and info["chunks"]:
                        all_chunks.extend(info["chunks"])
                        all_texts.extend([c.text for c in info["chunks"]])

                if all_chunks:
                    embeddings = get_embeddings(
                        all_texts,
                        model_name=st.session_state["qa_embedding_model"],
                    )
                    store = FAISSVectorStore()
                    store.create_index(all_chunks, embeddings)
                    st.session_state["qa_vector_store"] = store
                else:
                    st.session_state["qa_vector_store"] = None
            st.rerun()

    # Index button
    unindexed_files = [
        f
        for f in st.session_state["qa_uploaded_files"].keys()
        if f not in st.session_state["qa_indexed_files"]
    ]
    if unindexed_files:
        st.divider()
        if st.button(get_qa_text("index_btn", lang), type="primary", use_container_width=True):
            progress_bar = st.progress(0.0)
            status_text = st.empty()

            try:
                all_chunks_new = []
                # First retain chunks from already indexed files
                for f_name in st.session_state["qa_indexed_files"]:
                    all_chunks_new.extend(
                        st.session_state["qa_uploaded_files"][f_name]["chunks"]
                    )

                # Process new files
                total_files = len(unindexed_files)
                for idx, filename in enumerate(unindexed_files):
                    status_text.text(f"Extracting text from {filename}...")
                    file_bytes = st.session_state["qa_uploaded_files"][filename]["bytes"]

                    # Write to temporary file for PyMuPDF/fitz extraction
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                        tmp.write(file_bytes)
                        tmp_path = tmp.name

                    try:
                        pages = load_pdf_document(tmp_path)
                    finally:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)

                    status_text.text(f"Chunking {filename}...")
                    chunks = chunk_document_pages(
                        pages, chunk_size=1000, chunk_overlap=200
                    )
                    st.session_state["qa_uploaded_files"][filename]["chunks"] = chunks
                    all_chunks_new.extend(chunks)

                    # Update indexing lists
                    st.session_state["qa_indexed_files"].append(filename)
                    progress_bar.progress(float(idx + 1) / total_files)

                # Get embeddings for ALL chunks to rebuild vector database index
                status_text.text("Generating embeddings...")
                all_texts = [c.text for c in all_chunks_new]
                embeddings = get_embeddings(
                    all_texts,
                    model_name=st.session_state["qa_embedding_model"],
                )

                status_text.text("Building search index...")
                store = FAISSVectorStore()
                store.create_index(all_chunks_new, embeddings)
                st.session_state["qa_vector_store"] = store

                status_text.empty()
                progress_bar.empty()
                st.toast(
                    get_qa_text("indexed_success", lang).format(
                        count=len(st.session_state["qa_indexed_files"]),
                        chunks=len(all_chunks_new),
                    ),
                    icon="⚡",
                )
                st.rerun()

            except Exception as exc:
                status_text.empty()
                progress_bar.empty()
                logger.error("Error during document indexing: %s", exc)
                st.error(f"Indexing failed: {exc}")

    # Clear index button
    if st.session_state["qa_indexed_files"]:
        if st.button(get_qa_text("clear_index", lang), use_container_width=True):
            st.session_state["qa_uploaded_files"] = {}
            st.session_state["qa_indexed_files"] = []
            st.session_state["qa_vector_store"] = None
            st.session_state["qa_messages"] = []
            st.rerun()

# ── Header Section ───────────────────────────────────────────────────
col_title, col_lang = st.columns([5, 1])
with col_title:
    st.markdown(
        f"""
        <div class="main-header">
            <h1>{get_qa_text("title", lang)}</h1>
            <p>{get_qa_text("subtitle", lang)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_lang:
    ui_lang_selected = st.selectbox(
        "🌐 Language Selector",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=list(LANGUAGES.keys()).index(st.session_state["ui_lang"]),
        key="ui_lang_selector_qa",
    )
    if ui_lang_selected != st.session_state["ui_lang"]:
        st.session_state["ui_lang"] = ui_lang_selected
        st.rerun()

# ── Privacy Badge ────────────────────────────────────────────────────
provider = st.session_state.get("ai_provider", "gemini_builtin")
is_local = provider == "ollama"

badge_html = (
    f'<div class="badge-container">'
    f'<span class="badge-local">{get_qa_text("local_badge", lang)}</span>'
    f"</div>"
    if is_local
    else f'<div class="badge-container">'
    f'<span class="badge-cloud">{get_qa_text("cloud_badge", lang)}</span>'
    f"</div>"
)
st.markdown(badge_html, unsafe_allow_html=True)

# ── Layout: Chat (left) and Status Panel (right) ──────────────────────
col_chat, col_stats = st.columns([3.2, 1.2])

with col_stats:
    # Estimate size in KB/MB
    size_str = "0.0 KB"
    if st.session_state["qa_vector_store"]:
        num_chunks = len(st.session_state["qa_vector_store"].chunks)
        dim = st.session_state["qa_vector_store"].dimension
        # vectors + text character size estimate
        size_bytes = (num_chunks * dim * 4) + sum(
            len(c.text) for c in st.session_state["qa_vector_store"].chunks
        )
        if size_bytes > 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{size_bytes / 1024:.2f} KB"

    st.markdown(
        f"""
        <div class="status-card">
            <h3>{get_qa_text("status_title", lang)}</h3>
            <div class="status-row">
                <span class="status-label">{get_qa_text("stats_docs", lang)}</span>
                <span class="status-value">{len(st.session_state["qa_indexed_files"])}</span>
            </div>
            <div class="status-row">
                <span class="status-label">{get_qa_text("stats_chunks", lang)}</span>
                <span class="status-value">{len(st.session_state["qa_vector_store"].chunks) if st.session_state["qa_vector_store"] else 0}</span>
            </div>
            <div class="status-row">
                <span class="status-label">{get_qa_text("stats_emb", lang)}</span>
                <span class="status-value">{st.session_state["qa_embedding_model"]}</span>
            </div>
            <div class="status-row">
                <span class="status-label">{get_qa_text("stats_llm", lang)}</span>
                <span class="status-value">{st.session_state.get("ollama_model", "llama3") if is_local else "gemini-2.5-flash"}</span>
            </div>
            <div class="status-row">
                <span class="status-label">{get_qa_text("stats_size", lang)}</span>
                <span class="status-value">{size_str}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_chat:
    # Render Chat History
    for msg in st.session_state["qa_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(get_qa_text("sources_title", lang)):
                    for s in msg["sources"]:
                        formatted = get_qa_text("source_item", lang).format(
                            filename=s["filename"],
                            page_number=s["page_number"],
                            score=s["score"],
                        )
                        st.markdown(formatted)
                        st.markdown(
                            f'<div class="source-box">{s["text"]}</div>',
                            unsafe_allow_html=True,
                        )

    # Chat Input
    query = st.chat_input(get_qa_text("input_placeholder", lang))
    if query:
        # Display user question
        with st.chat_message("user"):
            st.markdown(query)
        st.session_state["qa_messages"].append({"role": "user", "content": query})

        # Generate grounded response
        with st.chat_message("assistant"):
            if not st.session_state["qa_vector_store"]:
                warn = get_qa_text("no_context_warn", lang)
                st.warning(warn)
                st.session_state["qa_messages"].append(
                    {"role": "assistant", "content": warn}
                )
            else:
                placeholder = st.empty()
                response_text = ""
                source_chunks = []

                # Call RAG generator
                generator = stream_rag_answer(
                    question=query,
                    vector_store=st.session_state["qa_vector_store"],
                    embedding_model=st.session_state["qa_embedding_model"],
                    llm_model=st.session_state.get("ollama_model", "llama3"),
                    provider=provider,
                    byok_key=st.session_state.get("byok_api_key") or None,
                    k=4,
                )

                # Process tokens and sources
                for item in generator:
                    if item["type"] == "token":
                        response_text += item["content"]
                        placeholder.markdown(response_text + "▌")
                    elif item["type"] == "sources":
                        source_chunks = item["content"]

                placeholder.markdown(response_text)

                # Render sources
                if source_chunks:
                    with st.expander(get_qa_text("sources_title", lang)):
                        for s in source_chunks:
                            formatted = get_qa_text("source_item", lang).format(
                                filename=s["filename"],
                                page_number=s["page_number"],
                                score=s["score"],
                            )
                            st.markdown(formatted)
                            st.markdown(
                                f'<div class="source-box">{s["text"]}</div>',
                                unsafe_allow_html=True,
                            )

                # Store message in history
                st.session_state["qa_messages"].append(
                    {
                        "role": "assistant",
                        "content": response_text,
                        "sources": source_chunks,
                    }
                )
