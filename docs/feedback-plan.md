# DeepDive AI — User Feedback Loop & Plan

This document explains how user feedback is collected, categorized, prioritized, and converted into product enhancements.

---

## 1. Feedback Collection Infrastructure

DeepDive AI implements an in-app community rating and feedback system in the Streamlit sidebar, managed by [reviews_manager.py](file:///Users/madhurabhattu/DeepDive-AI/utils/reviews_manager.py).

### How it Works:
1. **User Input:** Users enter their Name, Rate the application on a scale from 1 to 5 stars, type comments, and provide explicit consent via the GDPR checkbox.
2. **Persistent Storage:** Reviews are appended to [reviews.json](file:///Users/madhurabhattu/DeepDive-AI/data/reviews.json) in the `data/` directory.
3. **Atomic Operations:** To prevent database corruption, reviews are written to a temporary file (`.tmp`) and replaced atomically.
4. **Duplicate Prevention:** The form blocks rapid, duplicate submissions from the same browser session.

---

## 2. Review Categorization Process

On a regular review cycle, comments from `data/reviews.json` are parsed and categorized into four buckets:

```
┌───────────────────────────────────────────────┐
│              Feedback Comments                │
└──────────────────────┬────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    [ Bug Reports ] [ UX/UI ] [ Feature Requests ]
```

* **Bug Reports:** Technical failures (e.g., Gemini API key errors, PDF rendering issues on special characters, Ollama connection timeouts).
* **Feature Requests:** Requests for additional formats, more local models, or new languages.
* **UX/UI Improvements:** Font sizes, colors, layout alignment, or loading spinner messaging.
* **General Praise/Testimonials:** Positive reviews (4-5 stars) used for community testimonials.

---

## 3. Prioritization Framework

Issues are prioritized into three severity tiers to determine when they will be addressed:

| Priority | Criteria | Target Resolution | Example |
| :--- | :--- | :--- | :--- |
| **High** | Core functionality is broken or security vulnerability detected. | Within 48 hours | PDF generation fails with Unicode errors on regional languages. |
| **Medium** | App is usable, but major feature or UI component is degraded or confusing. | Next weekly release | Ollama model selection dropdown is missing a newly popular local model. |
| **Low** | Aesthetic improvements, typos, minor edge cases. | Backlog / Next major release | Aligning the download buttons or adding custom icons. |

---

## 4. Monthly Review Cycle & Workflow

Feedback is managed in a monthly loop:

```
  ┌────────────────────────────────────────────────────────┐
  │ 1. Collect & Parse Reviews from data/reviews.json      │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 2. Categorize & Assign Priority (High / Medium / Low)   │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 3. Create GitLab Issues & Track Progress               │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 4. Build, Test, and Deploy Bug Fixes/Features          │
  └────────────────────────────────────────────────────────┘
```

1. **Extraction (1st of the month):** Read the local reviews file. Run aggregate queries (e.g., average ratings and review distribution).
2. **Classification (3rd of the month):** Assign categories and priorities.
3. **Escalation & Issue Mapping (5th of the month):**
   * If a review is classified as a **High Priority Bug**, escalate it to the engineering team immediately.
   * If it is a **Feature Request** or **UX enhancement**, map it to a GitLab issue template under `.gitlab/issue_templates/`.
4. **Resolution:** Implement modifications, verify through tests (`pytest tests/`), and merge via PRs.

---

## 5. Example Feedback Lifecycle Scenario

Here is an example of the workflow in action:

1. **User Submission:** A user named Amit submits a 3-star review saying: *"Telugu reports generate fine, but the PDF download displays empty rectangles instead of Telugu characters."*
2. **Detection & Categorization:** The script loads `data/reviews.json`. The reviewer flags this as a **Bug Report - Font Rendering**.
3. **Prioritization:** Since this blocks the Telugu PDF download feature, it is prioritized as **High**.
4. **Escalation & Fix:**
   * A developer is assigned. They locate the font downloading logic in `utils/font_manager.py`.
   * They discover that the Telugu TTF file was not registerd correctly in the ReportLab font register.
   * They resolve it, write tests in `tests/test_pdf_generator.py`, and run `pytest`.
5. **Deployment:** The patch is pushed. The changelog is updated.
6. **Closing the Loop:** In the release notes, the team explicitly writes: *"Fixed Telugu font registration in PDF generation, resolving issues reported by community users in reviews."*
