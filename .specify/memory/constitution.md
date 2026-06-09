# DeepDive AI Constitution

## Core Principles

### I. Offline & Privacy-First (NON-NEGOTIABLE)
All document ingestion, vector calculations, indexing, and LLM inferences must occur completely offline on the local system. No proprietary codebase fragments or document chunks may be transmitted to external servers. All APIs must connect to local servers (e.g., local Ollama instance).

### II. AST-Based Code Separation & Chunking
When parsing code, the system must utilize Abstract Syntax Tree (AST) analyzers (or equivalent language-aware parser structures) to respect code blocks. Chunks must avoid breaking inside logical functions or classes where possible, prioritizing semantic boundaries over strict token counts.

### III. Separation of UI and Business Logic
The UI (Streamlit pages) must serve strictly as a presentation and interaction layer. All heavy lifting, including folder crawling, vector store queries, memory buffering, and Ollama REST interactions, must be decoupled into testable modular packages within the `utils/` directory.

### IV. Grounded Answers with Traceable Citations
Any response generated in the interactive chat must contain explicit references (file names, line number ranges, and short code snippets) to the exact parts of the ingested workspace that were retrieved. Responses without verifiable references are unacceptable.

### V. Test Coverage & Code Quality
All core modules inside `utils/` must be thoroughly covered by unit tests. A minimum threshold of **80% code coverage** must be maintained for any code merged into main, ensuring stability during future refactoring.

## Technology Constraints

* **Frontend:** Streamlit multi-page structure (`app.py`, `pages/`).
* **Storage:** Locally-persisted ChromaDB database.
* **LLM Engine:** Local Ollama server interface.
* **Language:** Python 3.10+ using standard formatting guidelines.

## Development Workflow

1. **Spec-Driven Development:** All new features must begin by defining a feature specification (`spec.md`), technical design (`plan.md`), and actionable tasks (`tasks.md`) under the `specs/` folder.
2. **Phase Completion Gate:** No implementation code may be written until the feature spec and plan are completed and approved.
3. **Automated Testing:** All unit tests must run successfully before final verification.

## Governance
This constitution is the source of truth for all architectural decisions. Changes or amendments to these principles require document updates and version increments.

**Version**: 1.0.0 | **Ratified**: 2026-06-09 | **Last Amended**: 2026-06-09
