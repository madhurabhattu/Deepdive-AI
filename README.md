# 🔬 DeepDive AI — Research Report Generator

[![pipeline status](https://code.swecha.org/madhura1/deepdive-ai/badges/main/pipeline.svg)](https://code.swecha.org/madhura1/deepdive-ai/-/commits/main)
[![coverage report](https://code.swecha.org/madhura1/deepdive-ai/badges/main/coverage.svg)](https://code.swecha.org/madhura1/deepdive-ai/-/commits/main)

**DeepDive AI** is an AI-powered research report generator built with **Streamlit**.
Enter any research topic and receive a comprehensive, structured report — complete
with downloadable PDF and PowerPoint exports.

Supports two AI backends:

| Backend | Description |
|---|---|
| ☁️ **Gemini API** | Cloud inference via Google Gemini (BYOK — bring your own key) |
| 🖥️ **Ollama Local** | 100% local inference via Ollama — no API key, no internet |

---

## ✨ Features

| Feature | Description |
|---|---|
| **📝 Executive Summary** | A concise, professional overview of the research topic |
| **💡 Key Insights** | The most important findings and takeaways |
| **📊 Statistics & Data** | Relevant numbers, metrics, and data points |
| **📚 References & Citations** | Credible sources with descriptions and URLs |
| **📄 PDF Report** | Professionally formatted multi-page PDF download |
| **📽️ PowerPoint Deck** | Ready-to-present 7-slide PPTX download |
| **🌐 Multilingual** | UI & reports in English, Hindi, Marathi, Telugu |
| **🤖 BYOK / Local AI** | Use Gemini with your own key or run Ollama locally |

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Streamlit** — UI framework
- **Google Gemini API** (`google-genai`) — cloud AI (optional)
- **Ollama** — local AI inference (optional, no key needed)
- **ReportLab** — PDF generation
- **python-pptx** — PowerPoint generation
- **python-dotenv** — Environment variable management
- **pytest / pytest-cov** — Testing framework

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://code.swecha.org/madhura1/deepdive-ai.git
cd deepdive-ai
```

### 2. Create a virtual environment & install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.
Choose your AI provider from the **sidebar** before generating a report.

---

## ☁️ Option A — Gemini API (Cloud)

### Get a free API key

1. Visit [ai.google.dev](https://ai.google.dev/) and click **Get API key**.
2. Copy the key.

### Configure the key (choose one method)

**Method 1 — Sidebar BYOK (simplest)**
Paste the key directly into the **🔑 Gemini API Key** field in the sidebar.
It is stored only in your browser session — never on disk.

**Method 2 — `.env` file (local development)**

```bash
cp .env.example .env
# Edit .env and set:
GEMINI_API_KEY=your_key_here
```

**Method 3 — Streamlit Cloud secrets (deployment)**

In your Streamlit Cloud dashboard → *App settings → Secrets*, add:

```toml
GEMINI_API_KEY = "your_key_here"
```

### Key resolution priority

```
Sidebar BYOK input  →  Streamlit secrets  →  Environment variable / .env
```

---

## 🖥️ Option B — Ollama Local (No API Key)

Run AI inference entirely on your own machine — no account, no internet needed.

### 1. Install Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows — download the installer from:
# https://ollama.com/download
```

### 2. Start the Ollama server

```bash
ollama serve
```

The server listens on `http://localhost:11434` by default.

### 3. Pull a supported model

```bash
ollama pull llama3     # Meta LLaMA 3 (recommended — best quality)
ollama pull mistral    # Mistral 7B (fast, good quality)
ollama pull gemma      # Google Gemma 7B
ollama pull qwen       # Alibaba Qwen
```

> **Tip:** Start with `llama3` or `mistral` — both run comfortably on 8 GB RAM.

### 4. Select Ollama in the app

1. Open the app sidebar.
2. Select **🖥️ Ollama Local** from the **AI Provider** dropdown.
3. Choose your model from the **🧠 Local Model** dropdown.
4. Generate a report — no key needed.

### Supported Ollama models

| Model | Size | Notes |
|---|---|---|
| `llama3` | ~4.7 GB | Best report quality |
| `mistral` | ~4.1 GB | Fast, good balance |
| `gemma` | ~5.0 GB | Google's open model |
| `qwen` | ~4.5 GB | Multilingual capable |

---

## 📁 Project Structure

```
DeepDive-AI/
├── app.py                          # Streamlit entry point & navigation
├── .env                            # API key (gitignored)
├── .env.example                    # Template for .env
├── requirements.txt                # Python dependencies
├── output/                         # Generated PDFs & PPTs (gitignored)
│
├── pages/
│   └── 1_🔬_Research.py            # Research page: input, display, downloads
│
├── utils/
│   ├── __init__.py
│   ├── ai_client.py                # Multi-backend AI client (Gemini + Ollama)
│   ├── font_manager.py             # Indic font downloader for PDF
│   ├── localization.py             # Translation dictionaries (EN/HI/MR/TE)
│   ├── report_schema.py            # ResearchReport dataclass & validator
│   ├── pdf_generator.py            # PDF report builder (ReportLab)
│   └── ppt_generator.py            # PPTX presentation builder (python-pptx)
│
└── tests/
    ├── test_report_schema.py       # Schema parsing unit tests
    ├── test_pdf_generator.py       # PDF generation unit tests
    └── test_ppt_generator.py       # PPTX generation unit tests
```

---

## 🧪 Running Tests

```bash
source .venv/bin/activate
pytest tests/ -v --tb=short

# With coverage
pytest --cov=. --cov-report=term --cov-report=xml
```

---

## 📋 Usage

1. Open the app (`streamlit run app.py`)
2. **Choose AI provider** in the sidebar (Gemini or Ollama)
3. If using Gemini, paste your API key or configure it in `.env`
4. Click **🔬 Research** in the sidebar
5. Enter a research topic (e.g., "Impact of AI on Healthcare")
6. Click **🚀 Generate Report**
7. Review the generated report sections
8. Click **⬇️ Download PDF** or **⬇️ Download PPT**

---

## ⚠️ Requirements

- **Python 3.10+**
- **Gemini API key** (only for Gemini provider) — free at [ai.google.dev](https://ai.google.dev/)
- **Ollama installed and running** (only for local provider)
- **Internet connection** — required for Gemini; not required for Ollama

---

## 🔒 Secret Scanning

This repository uses **Gitleaks** to detect and prevent secrets from being committed.

```bash
# Scan manually
gitleaks detect --verbose

# Via pre-commit hooks
pip install pre-commit
pre-commit install
pre-commit run gitleaks --all-files
```

---

## 📄 License

This project is for educational and research purposes.
