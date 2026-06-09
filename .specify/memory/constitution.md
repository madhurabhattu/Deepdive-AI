# DeepDive AI Constitution

## Core Principles

### I. Topic-In, Report-Out (NON-NEGOTIABLE)
The application's primary contract is: the user provides a research topic (plain text), and the system produces a structured research report. Every feature, page, and utility must serve this pipeline. Features that do not contribute to input → research → output are out of scope.

### II. AI-Powered, Not Just Retrieval
All content generation (executive summaries, key insights, statistics, references) must be produced by an AI language model — not static templates or simple web scraping. The LLM is the engine; the app is the interface.

### III. Output-First Design
Every research run must produce at minimum two downloadable artefacts: a **PDF report** and a **PowerPoint presentation**. These are first-class outputs, not optional extras. The Streamlit UI must make downloading them the primary call-to-action after a run completes.

### IV. Separation of Concerns
- `app.py` — entry point and navigation only.
- `pages/` — Streamlit page views (UI logic only, no business logic).
- `utils/` — all AI calls, document generation, and data formatting. Pages import from `utils/`; `utils/` never imports from `pages/`.
- `output/` — generated artefacts (PDFs, PPTs) written here; never committed to git.

### V. Structured, Validated Report Schema
Every research run must produce a consistent, validated Python data structure (dataclass or TypedDict) before rendering or exporting. The schema must include:
- `topic` (str)
- `executive_summary` (str)
- `key_insights` (list[str], min 3)
- `statistics` (list[dict] with `label` and `value`)
- `references` (list[dict] with `title`, `url`, `snippet`)

Partial/malformed schemas must raise a recoverable error shown in the UI — never silently produce empty exports.

## Technology Constraints

- **Frontend:** Streamlit multi-page app (`app.py` + `pages/`).
- **AI:** Google Gemini API (via `google-generativeai`) or configurable via `.env`.
- **PDF generation:** `reportlab` or `fpdf2`.
- **PPT generation:** `python-pptx`.
- **Language:** Python 3.10+, type-annotated, formatted with `black`.
- **Config:** All secrets (API keys) via environment variables; never hardcoded.

## Development Workflow

1. All features begin with a complete `spec.md` → `plan.md` → `tasks.md` in `specs/<id>-<name>/`.
2. No implementation code is written until the spec is approved.
3. The `output/` directory must be listed in `.gitignore`.
4. Every utility function in `utils/` must have a corresponding unit test.

## Governance
This constitution supersedes all other conventions. Amendments require a version bump and ratification date update.

**Version**: 1.0.0 | **Ratified**: 2026-06-09 | **Last Amended**: 2026-06-09
