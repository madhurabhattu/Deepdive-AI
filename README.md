# 🔬 DeepDive AI — Research Report Generator

**DeepDive AI** is an AI-powered research report generator built with **Streamlit** and the **Google Gemini API**. Enter any research topic and receive a comprehensive, structured report — complete with downloadable PDF and PowerPoint exports.

---

## ✨ Features

| Feature | Description |
|---|---|
| **📝 Executive Summary** | A concise, professional overview of the research topic |
| **💡 Key Insights** | The most important findings and takeaways |
| **📊 Statistics & Data** | Relevant numbers, metrics, and data points |
| **📚 References & Citations** | Credible sources with descriptions and URLs |
| **📄 PDF Report** | Professionally formatted multi-page PDF download |
| **📽️ PowerPoint Deck** | Ready-to-present 5+ slide PPTX download |

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Streamlit** — UI framework
- **Google Gemini API** (`google-generativeai`) — AI content generation
- **ReportLab** — PDF generation
- **python-pptx** — PowerPoint generation
- **python-dotenv** — Environment variable management
- **pytest** — Testing framework

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

### 3. Configure your API key

```bash
cp .env.example .env
```

Edit `.env` and replace `your_gemini_api_key_here` with your actual [Google Gemini API key](https://ai.google.dev/).

### 4. Run the application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

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
│   ├── ai_client.py                # Gemini API wrapper
│   ├── report_schema.py            # ResearchReport dataclass & validator
│   ├── pdf_generator.py            # PDF report builder (ReportLab)
│   └── ppt_generator.py            # PPTX presentation builder (python-pptx)
│
├── tests/
│   ├── test_report_schema.py       # Schema parsing unit tests
│   ├── test_pdf_generator.py       # PDF generation unit tests
│   └── test_ppt_generator.py       # PPTX generation unit tests
│
└── specs/
    └── 001-research-report-generator/
        ├── spec.md                 # Feature specification
        ├── plan.md                 # Implementation plan
        └── tasks.md               # Task checklist
```

---

## 🧪 Running Tests

```bash
source .venv/bin/activate
pytest tests/ -v --tb=short
```

---

## 📋 Usage

1. Open the app in your browser (`streamlit run app.py`)
2. Click **🔬 Research** in the sidebar
3. Enter a research topic (e.g., "Impact of AI on Healthcare")
4. Click **🚀 Generate Report**
5. Review the generated report sections
6. Click **⬇️ Download PDF** or **⬇️ Download PPT** to save your report

---

## ⚠️ Requirements

- A valid **Google Gemini API key** — get one free at [ai.google.dev](https://ai.google.dev/)
- **Python 3.10+**
- **Internet connection** (for AI API calls)

## 🔒 Secret Scanning

This repository uses **Gitleaks** to detect and prevent secrets (like API keys, passwords, and private tokens) from being committed.

### Running Secret Scanning Locally

#### 1. Using Gitleaks CLI
You can install and run Gitleaks directly to scan the repository:
```bash
gitleaks detect --verbose
```

#### 2. Using pre-commit
Pre-commit hooks are configured to scan for secrets before every commit. To install and configure them:
```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# Manually run secret scanning on all files
pre-commit run gitleaks --all-files
```

---

## 📄 License

This project is for educational and research purposes.
