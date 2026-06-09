# Implementation Plan: AI Research Report Generator

**Branch**: `001-research-report-generator` | **Date**: 2026-06-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-research-report-generator/spec.md`

---

## Summary

Build a Streamlit multi-page application with a single primary workflow: a user enters a research topic, the app sends a structured prompt to the Gemini AI API, parses the JSON response into a validated `ResearchReport` dataclass, renders it section-by-section in the UI, and offers one-click PDF and PowerPoint downloads. All generation and export logic lives in `utils/`; the Streamlit page handles only layout and user interaction.

---

## Technical Context

| Field | Value |
|---|---|
| **Language / Version** | Python 3.10+ |
| **AI Backend** | Google Gemini API (`google-generativeai` SDK) |
| **PDF Generation** | `reportlab` |
| **PPT Generation** | `python-pptx` |
| **Config** | `python-dotenv` to load `GEMINI_API_KEY` from `.env` |
| **Testing** | `pytest` with `pytest-mock` for AI call mocking |
| **Target Platform** | Desktop browser (Streamlit local server) |
| **Performance Goal** | Full report rendered in < 30 seconds end-to-end |
| **Constraints** | Zero hardcoded secrets; `output/` is gitignored |
| **Project Type** | Streamlit multi-page web app |

---

## Constitution Check

| Principle | Status | Notes |
|---|---|---|
| Topic-In, Report-Out | ✅ Pass | Single input → full report pipeline |
| AI-Powered | ✅ Pass | Gemini API drives all content generation |
| Output-First Design | ✅ Pass | PDF + PPTX download buttons are primary CTA |
| Separation of Concerns | ✅ Pass | UI in `pages/`, logic in `utils/` |
| Structured Report Schema | ✅ Pass | `ResearchReport` dataclass validated before render |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-research-report-generator/
├── spec.md      ← Requirements & user stories
├── plan.md      ← This file
└── tasks.md     ← Actionable task checklist
```

### Source Code Layout

```text
DeepDive-AI/
├── app.py                          # Streamlit entry point: page config, navigation
├── .env                            # GEMINI_API_KEY (gitignored)
├── .env.example                    # Template with placeholder values (committed)
├── requirements.txt                # All Python dependencies
├── output/                         # Generated PDFs & PPTs (gitignored)
│
├── pages/
│   └── 1_🔬_Research.py           # Research page: topic input, report display, download buttons
│
├── utils/
│   ├── __init__.py
│   ├── ai_client.py               # Gemini API wrapper: send_research_prompt() → raw JSON str
│   ├── report_schema.py           # ResearchReport dataclass + parse_report() validator
│   ├── pdf_generator.py           # build_pdf(report: ResearchReport) → filepath str
│   └── ppt_generator.py           # build_ppt(report: ResearchReport) → filepath str
│
└── tests/
    ├── test_report_schema.py       # Unit tests: parse_report() with valid/invalid/partial JSON
    ├── test_pdf_generator.py       # Unit tests: PDF created, non-empty, sections present
    └── test_ppt_generator.py       # Unit tests: PPTX created, slide count ≥ 5
```

---

## Module Design Details

### `utils/report_schema.py`
Defines the canonical data model and parser:

```python
@dataclass
class ResearchReport:
    topic: str
    executive_summary: str
    key_insights: list[str]        # min 3 items
    statistics: list[dict]         # [{label: str, value: str}]
    references: list[dict]         # [{title: str, url: str, snippet: str}]

def parse_report(raw_json: str, topic: str) -> ResearchReport:
    """Parse and validate AI response. Raises ValueError on schema violations."""
```

### `utils/ai_client.py`
Single responsibility: construct the structured prompt and call Gemini.

- Prompt instructs Gemini to return **only** a JSON object matching the `ResearchReport` schema.
- Uses `response_mime_type="application/json"` where supported to enforce JSON output.
- Raises `RuntimeError` on API failure; caller (page) handles and shows UI error.

### `utils/pdf_generator.py`
Uses `reportlab` to build a multi-section PDF:
- **Page 1:** Title + topic
- **Page 2:** Executive Summary
- **Page 3:** Key Insights (bulleted list)
- **Page 4:** Statistics (two-column table)
- **Page 5:** References (numbered list with URLs)
- Saved to `output/<sanitised_topic>_report.pdf`

### `utils/ppt_generator.py`
Uses `python-pptx` to build a 5-slide deck:
- **Slide 1:** Title slide — topic name + date
- **Slide 2:** Executive Summary
- **Slide 3:** Key Insights (bullet points)
- **Slide 4:** Statistics & Data (text or table layout)
- **Slide 5:** References & Citations
- Saved to `output/<sanitised_topic>_presentation.pptx`

### `pages/1_🔬_Research.py`
Streamlit UI — no business logic:
1. Text input for topic
2. "Generate Report" button → spinner → calls `ai_client` → `parse_report` → stores in `st.session_state`
3. Renders `ResearchReport` sections with `st.markdown`, `st.metric`, `st.expander`
4. "⬇️ Download PDF" and "⬇️ Download PPT" buttons via `st.download_button`

---

## Complexity Tracking

*No constitution violations. Architecture is a single straightforward pipeline.*

---

## Open Questions (Resolved)

| Question | Decision |
|---|---|
| Which AI model? | `gemini-1.5-flash` (fast, low-cost, sufficient for structured output) |
| PDF library? | `reportlab` (pure Python, no binary deps) |
| Where are exports stored? | `output/` directory at repo root, gitignored |
| What if AI returns non-JSON? | `parse_report()` raises `ValueError`; page catches and shows UI error |
