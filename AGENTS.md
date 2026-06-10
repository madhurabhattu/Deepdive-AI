# Instructions for AI Coding Agents (AGENTS.md)

Welcome! If you are an AI coding agent modifying or collaborating on the **DeepDive AI** project, please read and follow these guidelines carefully.

---

## 1. Project Purpose & Tech Stack

**DeepDive AI** is a Streamlit-based web application integrated with the Google Gemini API that enables users to generate deep-dive research reports and export them as PDFs and PowerPoint presentations.

### Tech Stack:
* **Frontend/UI:** Streamlit (Python-based multi-page setup)
* **AI Engine:** Google Gemini Pro (`google-generativeai`)
* **Data Schema/Validation:** Python `dataclasses` (with custom validations)
* **Document Export:** ReportLab (for PDF generation) and `python-pptx` (for PowerPoint generation)
* **Testing:** pytest
* **Code Quality:** Ruff, MyPy, EditorConfig

---

## 2. Directory Structure

```
DeepDive-AI/
├── app.py                # Main Streamlit application entry point
├── pages/                # Multi-page views (Streamlit pages)
│   └── 1_🔬_Research.py  # Research page logic
├── utils/                # Shared utilities & business logic
│   ├── __init__.py
│   ├── ai_client.py      # Google Gemini API integration and response parsing
│   ├── pdf_generator.py  # ReportLab PDF generation logic
│   ├── ppt_generator.py  # python-pptx presentation generation logic
│   └── report_schema.py  # Pydantic-like Python dataclass for parsing report JSON
├── tests/                # Unit and integration test suite
│   ├── __init__.py
│   ├── test_pdf_generator.py
│   ├── test_ppt_generator.py
│   └── test_report_schema.py
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container definition
├── .dockerignore         # Exclusions for Docker contexts
├── .editorconfig         # Code editor styles
├── pyproject.toml        # Ruff, MyPy, and tool configurations
└── cliff.toml            # git-cliff changelog generator config
```

---

## 3. Coding Standards

* **Python Version:** Python 3.10+
* **PEP 8:** Follow standard PEP 8 rules. Line length limit is set to 88 characters.
* **Type Hints:** Use type hints for all public functions, arguments, and return types.
* **Docstrings:** All modules, classes, and public functions must have descriptive Google-style or Sphinx-style docstrings.
* **Single Responsibility:** Keep functions small, focused, and under 50 lines where possible.
* **Error Handling:** Always gracefully handle external API timeouts and network errors (specifically Google Gemini API calls) and inform the user without crashing.

---

## 4. Git Workflow

We follow strict **Conventional Commits** and structured branches.

### Branch Naming:
`<type>/<short-description>` (e.g. `feat/pdf-export-watermark`, `fix/gemini-timeout-retry`)

### Commit Messages:
`<type>(<scope>): <short summary>`
* Use imperative, present tense: "add" not "added".
* Common types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`.
* Reference issues in the footer where applicable.

---

## 5. Testing & Verification

Before proposing or merging any changes, ensure all tests pass:
```bash
# Run the complete test suite
pytest tests/ -v --tb=short
```
When introducing new business logic or tools, you must write corresponding unit tests under `tests/`.

---

## 6. Security & Secrets Policy

* **API Keys:** NEVER commit API keys or credentials.
* **Environment Variables:** All local environment variables belong in `.env`. This file is explicitly ignored in `.gitignore` and `.dockerignore`.
* **Templates:** Place non-sensitive template variables or dummy values in `.env.example`.
* **Code Review:** Before submitting your change, verify that no debugging API keys or secret strings are hardcoded.
