# Feature Specification: AI Research Report Generator

**Feature Branch**: `001-research-report-generator`

**Created**: 2026-06-09

**Status**: Draft

**Input**: User enters a plain-text research topic (e.g. "Impact of climate change on agriculture") and clicks **Generate Report**.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Generate a Structured Research Report (Priority: P1)

As a researcher or student, I want to enter any topic and instantly receive a fully structured AI-generated research report, so that I can understand the subject quickly without spending hours reading papers.

**Why this priority**: This is the entire purpose of the application. Nothing else works without it.

**Independent Test**: Enter the topic "Quantum Computing", click Generate, and verify the UI displays all five report sections (executive summary, key insights, statistics, references, and download buttons) within 30 seconds.

**Acceptance Scenarios**:

1. **Given** the user is on the main Research page, **When** they type "Renewable Energy Trends" into the topic field and click "Generate Report", **Then** the app calls the AI backend, and within 30 seconds displays a non-empty executive summary, at least 3 key insights, at least 3 statistics, and at least 3 references.
2. **Given** the user submits an empty topic field, **When** they click "Generate Report", **Then** the system shows an inline validation error: "Please enter a research topic." and does not make any AI API call.
3. **Given** the AI API returns an error or times out, **When** generation fails, **Then** the app shows a user-friendly error message: "Research generation failed. Please try again." and logs the full error server-side.

---

### User Story 2 — Download as PDF Report (Priority: P2)

As a professional, I want to download the generated research as a formatted PDF, so that I can share or archive it offline.

**Why this priority**: A downloadable PDF transforms the tool from a read-only dashboard into a shareable deliverable — a key differentiator.

**Independent Test**: After a successful report generation, click "Download PDF" and verify a valid, non-empty `.pdf` file downloads with the topic title on the first page.

**Acceptance Scenarios**:

1. **Given** a research report has been generated, **When** the user clicks "⬇️ Download PDF", **Then** a PDF file named `<topic>_report.pdf` is downloaded, containing the executive summary, insights, statistics, and references formatted with headings.
2. **Given** a report has not yet been generated, **When** the user navigates to the page, **Then** the download buttons are disabled or hidden until a report exists.

---

### User Story 3 — Download as PowerPoint Presentation (Priority: P3)

As a presenter, I want to download the research as a ready-to-use PowerPoint presentation, so that I can present findings without building slides from scratch.

**Why this priority**: PPT output makes the tool useful for classroom, conference, or business presentation contexts — significantly expanding its value.

**Independent Test**: After generation, click "Download PPT" and verify a valid `.pptx` file downloads, opens in PowerPoint/LibreOffice, contains at minimum 5 slides (title, summary, insights, statistics, references), and has no placeholder text remaining.

**Acceptance Scenarios**:

1. **Given** a research report has been generated, **When** the user clicks "⬇️ Download PPT", **Then** a `.pptx` file named `<topic>_presentation.pptx` is downloaded with slides for: Title, Executive Summary, Key Insights, Statistics & Data, and References.
2. **Given** the topic name contains special characters (e.g. `/`, `:`), **When** the file is saved, **Then** the filename is sanitised (special chars replaced with `_`) and the file saves without error.

---

### Edge Cases

- **Very long topics** (> 200 characters): Truncate to 200 chars for display; pass full text to the AI.
- **AI returns fewer than 3 insights or statistics**: Show a warning banner "Limited data available for this topic" but still render what was returned.
- **Network unavailable / API key missing**: Show a clear error "API key not configured. Please set GEMINI_API_KEY in your .env file."
- **Concurrent requests**: If the user clicks Generate multiple times rapidly, debounce — disable the button and show a spinner during generation.
- **Unsupported characters in filenames**: Sanitise topic string before writing any file to `output/`.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a free-text topic string as the sole required input.
- **FR-002**: System MUST call a configured AI LLM API (Gemini) and prompt it to return a structured JSON object matching the report schema.
- **FR-003**: System MUST validate the returned JSON against the report schema before rendering. Invalid/partial responses must surface a recoverable UI error.
- **FR-004**: System MUST render the following report sections in the Streamlit UI: Executive Summary, Key Insights, Statistics, References & Citations.
- **FR-005**: System MUST generate a downloadable PDF report from the structured data.
- **FR-006**: System MUST generate a downloadable PowerPoint presentation (`.pptx`) from the structured data.
- **FR-007**: System MUST write generated files to the local `output/` directory and serve them as Streamlit download buttons.
- **FR-008**: System MUST NOT hardcode any API keys. All secrets are loaded from environment variables via a `.env` file.
- **FR-009**: System MUST display a loading spinner with status text while the AI call is in progress.

### Key Entities

- **ResearchReport**: The core data object — `topic`, `executive_summary`, `key_insights: list[str]`, `statistics: list[{label, value}]`, `references: list[{title, url, snippet}]`.
- **ReportExport**: Represents a generated file on disk — `filepath`, `format` (pdf | pptx), `created_at`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A research report for any valid topic is generated and fully rendered in the UI within **30 seconds** under normal network conditions.
- **SC-002**: The downloaded PDF opens without errors in standard PDF readers and contains all five report sections.
- **SC-003**: The downloaded PPTX opens without errors in Microsoft PowerPoint or LibreOffice Impress and contains at minimum **5 slides** with no unfilled placeholder text.
- **SC-004**: The system gracefully handles API errors in 100% of failure cases — no unhandled Python exceptions reach the user.
- **SC-005**: All secrets are loaded from `.env` — zero hardcoded credentials in any committed file.

---

## Assumptions

- The user has a valid Gemini API key available to configure in `.env`.
- Internet connectivity is available for AI API calls (this is not an offline tool).
- Generated files are ephemeral; the `output/` directory is gitignored and not synced.
- Mobile responsiveness is out of scope for v1; the app targets desktop browsers.
- The app supports English-language topics only for v1.
