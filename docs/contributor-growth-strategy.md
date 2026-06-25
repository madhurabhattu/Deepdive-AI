# DeepDive AI — Contributor Growth & Outreach Strategy

This document outlines the strategy for growing, onboarding, and mentoring our contributor base. It defines the paths for developers, technical writers, and localizers to participate in the DeepDive AI open-source ecosystem.

---

## 1. Contributor Onboarding Process

We aim to make the first-contribution experience as smooth as possible. When a new contributor joins:

1. **Orientation:** They read [CONTRIBUTING.md](file:///Users/madhurabhattu/DeepDive-AI/CONTRIBUTING.md) to understand coding standards (PEP 8, type hints, Google-style docstrings) and Git workflows.
2. **Local Environment Setup:** Follow the steps in [README.md](file:///Users/madhurabhattu/DeepDive-AI/README.md#quick-start) to fork, clone, set up a virtual environment, and execute existing tests (`pytest tests/ -v`).
3. **Pick an Issue:** Browse GitLab issues labeled `good-first-issue` or `documentation`.
4. **Communication:** Join community communication channels (e.g., chat platforms or GitLab discussions) to discuss their proposed implementation.

---

## 2. Good First Issues Policy

To encourage newcomers, we maintain a dedicated backlog of `good-first-issue` items. These issues are:
* **Self-Contained:** Require modifying only 1 or 2 files.
* **Low Risk:** Unlikely to cause system regressions.
* **Well-Documented:** Include clear instructions, pointer files (e.g. [localization.py](file:///Users/madhurabhattu/DeepDive-AI/utils/localization.py)), and expected outcomes.

### Examples of Good First Issues:
* Adding a new UI string translation in Telugu, Marathi, or Hindi.
* Formatting UI elements (e.g., margins, alignment) using Custom CSS in [app.py](file:///Users/madhurabhattu/DeepDive-AI/app.py).
* Writing minor test cases for helper scripts.

---

## 3. Mentorship Workflow

To help contributors progress from minor fixes to core features, we employ a structured mentorship model:

```
  ┌────────────────────────────────────────────────────────┐
  │ 1. Welcome & Initial Issue Assignment (First PR)       │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 2. Guided Code Review & Iteration (Learning Standards)  │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 3. Core Feature Collaboration (Paired Programming)     │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 4. Maintainer Rights & Issue Triaging Role             │
  └────────────────────────────────────────────────────────┘
```

* **Paired Programming:** Experienced maintainers schedule weekly pairing sessions for complex features (like modifying report templates in `pdf_generator.py` or editing RAG pipelines).
* **Detailed PR Feedback:** Reviews focus not just on correctness, but also on teaching design patterns (e.g., explaining why dataclass validation in `report_schema.py` is important).

---

## 4. Weekly Contributor Engagement Plan

To maintain momentum, we structure contributor activities week-by-week:

* **Monday - Triaging:** Review and label new issues, categorizing bug reports and marking newcomers' tasks.
* **Wednesday - Developer Sync:** A 30-minute virtual meeting to review active PRs, unblock technical issues, and demonstrate new features.
* **Friday - Review & Merges:** Focus on merging approved PRs and updating the `Unreleased` section in `CHANGELOG.md`.
* **Saturday - Open Hacking Sessions:** Online study groups for Swecha students to collaborate on specific features (e.g., adding local Ollama model options).

---

## 5. Pull Request Review Process

To maintain codebase health, all pull requests undergo a rigorous pipeline:
1. **Automated Verification:** The GitLab runner pipeline executes checks as defined in [.gitlab-ci.yml](file:///Users/madhurabhattu/DeepDive-AI/.gitlab-ci.yml):
   * `security_gitleaks` & `security_bandit` (scans secrets and vulnerabilities)
   * `format_ruff` & `lint_ruff` (ensures styling compliance)
   * `test_stage` & `build_stage` (runs full test suite)
2. **Review Checklist:** Maintainers review the code structure against the constraints in [AGENTS.md](file:///Users/madhurabhattu/DeepDive-AI/AGENTS.md):
   * Do functions stay under ~50 lines?
   * Are type hints and docstrings present?
   * Was a corresponding test added under `tests/`?
3. **Squash-and-Merge:** Once approved, commits are squashed to keep a clean main history using Conventional Commit prefixes (`feat(pdf): ...`, `fix(api): ...`).

---

## 6. Contributor Recognition & Rewards

We value and celebrate every contribution:
* **All Contributors List:** Every contributor is added to the README.md credits.
* **Badges & Swag:** Free software stickers, shirts, and custom git badges for active members.
* **Reference Letters:** Active student contributors receive letters of recommendation detailing their technical contributions to a production-grade Python/Streamlit codebase.
