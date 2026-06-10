# Changelog

All notable changes to **DeepDive AI** will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and the format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added

- **Compliance and Repository Standards**
  - `AGENTS.md` containing repository-level instructions for AI coding agents.
  - Ruff and MyPy configurations added to `pyproject.toml` for standard Python code linting and type checking.
  - git-cliff configuration (`cliff.toml`) for automated changelog generation.
  - Updated `.gitignore` to completely ignore the output folder and caches.

---

## [1.0.0] — 2026-06-10

### Added

- **Core Application**
  - Streamlit-based multi-page web application (`app.py`) with a branded landing page, sidebar navigation, and custom CSS theme using the Inter typeface.
  - Research page (`pages/1_🔬_Research.py`) with topic input, AI report generation, and section display.

- **AI Integration**
  - `utils/ai_client.py` — Google Gemini API wrapper with structured JSON output for research reports.
  - Automatic retry handling for API timeouts and transient errors.

- **Report Schema**
  - `utils/report_schema.py` — `ResearchReport` dataclass with field validation for executive summary, key insights, statistics, and references.

- **Export Functionality**
  - `utils/pdf_generator.py` — Multi-page PDF generation using ReportLab with title page, section headings, and references.
  - `utils/ppt_generator.py` — 5-slide PowerPoint presentation generation using python-pptx.
  - In-browser download buttons for both PDF and PPTX formats.

- **Testing**
  - `tests/test_report_schema.py` — Unit tests for schema parsing and validation.
  - `tests/test_pdf_generator.py` — Unit tests for PDF generation logic.
  - `tests/test_ppt_generator.py` — Unit tests for PowerPoint generation logic.

- **Project Infrastructure**
  - `requirements.txt` with pinned minimum versions for all runtime and test dependencies.
  - `.env.example` environment variable template.
  - `.gitignore` configured for Python, virtualenv, IDE artefacts, and generated output.
  - `README.md` with quick-start guide, project structure, and usage instructions.
  - `CONTRIBUTING.md` — Contribution workflow, branch conventions, and PR process.
  - `USER_MANUAL.md` — End-user installation and usage documentation.
  - `SECURITY.md` — Vulnerability reporting policy.
  - `CODE_OF_CONDUCT.md` — Contributor Covenant v2.1.
  - `LICENSE` — GNU Affero General Public License v3.
  - `Dockerfile` and `.dockerignore` for containerised deployment.
  - `.editorconfig` for consistent editor settings across contributors.

### Changed

_N/A — initial release._

### Deprecated

_N/A — initial release._

### Removed

_N/A — initial release._

### Fixed

_N/A — initial release._

### Security

_N/A — initial release._

---

[Unreleased]: https://code.swecha.org/madhura1/deepdive-ai/compare/v1.0.0...HEAD
[1.0.0]: https://code.swecha.org/madhura1/deepdive-ai/releases/tag/v1.0.0
