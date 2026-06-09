---
description: "Task list for DeepDive AI — Research Report Generator"
---

# Tasks: AI Research Report Generator

**Input**: Design documents from `specs/001-research-report-generator/`

**Prerequisites**: `plan.md` ✅, `spec.md` ✅

**Format**: `[ID] [P?] [Story] Description`
- **[P]** = can run in parallel (different files, no shared dependencies)
- **[USn]** = maps to User Story n in spec.md

---

## Phase 1: Project Setup

**Purpose**: Establish the repo skeleton and dependency baseline before any feature work.

- [ ] T001 Add all dependencies to `requirements.txt`: `streamlit`, `google-generativeai`, `python-dotenv`, `reportlab`, `python-pptx`, `pytest`, `pytest-mock`
- [ ] T002 Create `.env.example` with placeholder `GEMINI_API_KEY=your_key_here`
- [ ] T003 Add `.env` and `output/` to `.gitignore`
- [ ] T004 [P] Create empty package stubs: `utils/__init__.py`, `tests/` directory
- [ ] T005 [P] Write minimal `app.py` with `st.set_page_config` and sidebar navigation

**Checkpoint**: `streamlit run app.py` launches without errors.

---

## Phase 2: Foundational — Report Schema & AI Client

**Purpose**: The data contract and AI integration that every other module depends on.

**⚠️ CRITICAL**: All downstream modules (PDF, PPT, UI) depend on `ResearchReport`. Complete this phase before Phase 3.

- [ ] T006 Implement `ResearchReport` dataclass in `utils/report_schema.py` with fields: `topic`, `executive_summary`, `key_insights`, `statistics`, `references`
- [ ] T007 Implement `parse_report(raw_json: str, topic: str) -> ResearchReport` in `utils/report_schema.py` — validate min-3 items on insights/stats/references, raise `ValueError` on violations
- [ ] T008 [P] Write unit tests in `tests/test_report_schema.py`:
  - valid full JSON → returns correct `ResearchReport`
  - missing `executive_summary` field → raises `ValueError`
  - fewer than 3 insights → raises `ValueError`
  - malformed JSON string → raises `ValueError`
- [ ] T009 Implement `utils/ai_client.py`:
  - Load `GEMINI_API_KEY` from env via `python-dotenv`; raise `EnvironmentError` if missing
  - Build structured prompt instructing Gemini to return JSON matching the report schema
  - Call `gemini-1.5-flash` and return raw JSON string
  - Raise `RuntimeError` on API failure with original exception chained

**Checkpoint**: `pytest tests/test_report_schema.py` passes. `ai_client.py` can be imported cleanly.

---

## Phase 3: User Story 1 — Generate & Display Research Report (Priority: P1) 🎯 MVP

**Goal**: User enters a topic → sees a full structured report in the Streamlit UI.

**Independent Test**: Run the app, enter "Quantum Computing", click Generate — all five sections render within 30 seconds.

### Tests for User Story 1
- [ ] T010 [P] [US1] Write `tests/test_report_schema.py` integration-style test: mock Gemini response → `parse_report` → assert all fields populated correctly

### Implementation for User Story 1
- [ ] T011 [US1] Create `pages/1_🔬_Research.py` with:
  - `st.text_input` for topic
  - "Generate Report" `st.button`
  - `st.spinner` wrapping the AI call
  - Store result in `st.session_state["report"]`
- [ ] T012 [US1] Add report rendering below the form:
  - `st.subheader("Executive Summary")` + `st.markdown`
  - `st.subheader("Key Insights")` + bulleted `st.markdown`
  - `st.subheader("Statistics")` + `st.metric` columns
  - `st.subheader("References & Citations")` + `st.expander` per reference
- [ ] T013 [US1] Add input validation: disable Generate button / show `st.warning` when topic field is empty
- [ ] T014 [US1] Add error handling: catch `RuntimeError` from `ai_client` and `ValueError` from `parse_report`; display `st.error` with user-friendly message; log full traceback to console

**Checkpoint**: Full end-to-end flow works — enter topic, see report.

---

## Phase 4: User Story 2 — PDF Download (Priority: P2)

**Goal**: User can download the generated report as a formatted PDF.

**Independent Test**: After generation, click "Download PDF" — a valid `.pdf` file downloads containing all five sections.

### Tests for User Story 2
- [ ] T015 [P] [US2] Write `tests/test_pdf_generator.py`:
  - `build_pdf(mock_report)` → file exists at returned path
  - File size > 0 bytes
  - Filepath ends with `.pdf`

### Implementation for User Story 2
- [ ] T016 [US2] Implement `utils/pdf_generator.py`:
  - `sanitise_filename(topic: str) -> str` helper (replace non-alphanumeric with `_`)
  - `build_pdf(report: ResearchReport) -> str` using `reportlab`:
    - Cover page: topic title + date
    - Executive Summary section
    - Key Insights bulleted list
    - Statistics two-column layout
    - References numbered list with URLs
  - Save to `output/<sanitised_topic>_report.pdf`; return filepath
- [ ] T017 [US2] Add "⬇️ Download PDF" `st.download_button` in `pages/1_🔬_Research.py`:
  - Only visible when `st.session_state["report"]` exists
  - Calls `build_pdf` on first click; caches filepath in session state

**Checkpoint**: PDF downloads correctly and opens in a standard reader with all sections.

---

## Phase 5: User Story 3 — PowerPoint Download (Priority: P3)

**Goal**: User can download the generated report as a ready-to-use `.pptx` presentation.

**Independent Test**: After generation, click "Download PPT" — a valid `.pptx` downloads with ≥ 5 slides, no placeholder text remaining.

### Tests for User Story 3
- [ ] T018 [P] [US3] Write `tests/test_ppt_generator.py`:
  - `build_ppt(mock_report)` → file exists at returned path
  - `Presentation(filepath).slides` count ≥ 5
  - Slide titles are non-empty strings

### Implementation for User Story 3
- [ ] T019 [US3] Implement `utils/ppt_generator.py`:
  - `build_ppt(report: ResearchReport) -> str` using `python-pptx`:
    - Slide 1: Title layout — topic name + generation date
    - Slide 2: Executive Summary (content placeholder)
    - Slide 3: Key Insights (bulleted content placeholder)
    - Slide 4: Statistics & Data (text box or table)
    - Slide 5: References & Citations (numbered list)
  - Save to `output/<sanitised_topic>_presentation.pptx`; return filepath
- [ ] T020 [US3] Add "⬇️ Download PPT" `st.download_button` in `pages/1_🔬_Research.py`:
  - Only visible when `st.session_state["report"]` exists
  - Calls `build_ppt` on first click; caches filepath in session state

**Checkpoint**: PPTX downloads, opens in PowerPoint/LibreOffice, 5 slides visible.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: UI refinement, edge-case hardening, final quality gates.

- [ ] T021 [P] Add custom CSS via `st.markdown` in `app.py`: dark theme palette, typography, button styling
- [ ] T022 Add debounce: disable "Generate Report" button while a generation is in progress (use `st.session_state["generating"]` flag)
- [ ] T023 Handle topic string > 200 characters: truncate display label; pass full text to AI
- [ ] T024 Ensure `output/` directory is created at startup if it does not exist (`output/.gitkeep` committed; contents gitignored)
- [ ] T025 [P] Run full test suite: `pytest tests/ -v --tb=short` — all tests must pass
- [ ] T026 [P] Update `README.md` with: project description, setup instructions (`pip install -r requirements.txt`, `.env` config, `streamlit run app.py`), and screenshot placeholder

---

## Dependencies & Execution Order

```
Phase 1 (Setup)
    └── Phase 2 (Schema + AI Client)  ← BLOCKS everything below
            ├── Phase 3 (US1: Generate & Display)
            │       └── Phase 4 (US2: PDF Download)
            │               └── Phase 5 (US3: PPT Download)
            └── Phase 6 (Polish) — can begin after Phase 3 checkpoint
```

### Parallel Opportunities
- T004, T005 can run alongside each other (Phase 1)
- T008 (schema tests) can be written in parallel with T009 (ai_client)
- T015 (PDF tests) and T018 (PPT tests) can be written in parallel
- T016 (PDF impl) and T019 (PPT impl) can be developed in parallel once T006–T007 are complete
- T021, T025, T026 (Phase 6) are all independent of each other

---

## Notes

- Write tests **before** implementation (TDD). Tests must fail first.
- Commit after each phase checkpoint.
- Never hardcode `GEMINI_API_KEY` — always load from environment.
- `output/` is gitignored; `output/.gitkeep` is the only committed file in that directory.
