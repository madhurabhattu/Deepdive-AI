# Contributing to DeepDive AI

Thank you for your interest in contributing to **DeepDive AI**! We welcome contributions of all kinds — bug fixes, new features, documentation improvements, and more.

Please take a moment to read this guide before opening an issue or pull request.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Branch Naming Conventions](#branch-naming-conventions)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful and constructive in all interactions.

---

## Getting Started

1. **Fork** the repository on your Git hosting platform.
2. **Clone** your fork locally:
   ```bash
   git clone https://code.swecha.org/<your-username>/deepdive-ai.git
   cd deepdive-ai
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://code.swecha.org/madhura1/deepdive-ai.git
   ```
4. **Create a virtual environment** and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and fill in your GEMINI_API_KEY
   ```

---

## Branch Naming Conventions

All branches should follow this naming pattern:

```
<type>/<short-description>
```

| Type        | When to use                                    |
|-------------|------------------------------------------------|
| `feat/`     | New feature or functionality                   |
| `fix/`      | Bug fix                                        |
| `docs/`     | Documentation changes only                    |
| `chore/`    | Maintenance, dependency updates, CI config     |
| `refactor/` | Code restructuring without behaviour change    |
| `test/`     | Adding or improving tests                      |
| `hotfix/`   | Critical production fix from `main`            |

**Examples:**
```
feat/pdf-export-watermark
fix/gemini-timeout-retry
docs/update-installation-guide
chore/upgrade-streamlit-1-35
refactor/ai-client-retry-logic
test/add-ppt-generator-edge-cases
```

Keep descriptions lowercase, hyphen-separated, and under 50 characters.

---

## Commit Message Guidelines

We follow the **Conventional Commits** specification.

### Format

```
<type>(<scope>): <short summary>

[optional body]

[optional footer(s)]
```

### Types

| Type       | Description                                          |
|------------|------------------------------------------------------|
| `feat`     | A new feature                                        |
| `fix`      | A bug fix                                            |
| `docs`     | Documentation only changes                          |
| `style`    | Formatting, missing semicolons — no logic change     |
| `refactor` | Code change that neither fixes a bug nor adds a feat |
| `test`     | Adding missing tests or correcting existing ones     |
| `chore`    | Build process, auxiliary tooling changes             |
| `perf`     | A code change that improves performance              |
| `ci`       | Changes to CI configuration files/scripts            |

### Rules

- Use the **imperative, present tense**: "add feature" not "added feature"
- Keep the **summary line ≤ 72 characters**
- Reference issues in the footer: `Closes #42` or `Refs #17`
- Separate the body from the summary with a blank line

### Examples

```
feat(pdf): add watermark to exported PDF reports

Adds a semi-transparent "DeepDive AI" watermark on each page
to brand the generated reports.

Closes #23
```

```
fix(ai-client): handle Gemini API timeout with exponential backoff

Previously the app raised an unhandled exception on API timeout.
Now it retries up to 3 times with exponential backoff before
surfacing an error to the user.

Refs #41
```

```
docs: update installation steps in README
```

---

## Pull Request Process

1. **Sync your fork** with the latest upstream `main` before starting work:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```
2. **Create a feature branch** from `main` following the naming conventions above.
3. **Make your changes**, keeping commits atomic and well-described.
4. **Run tests** and ensure they pass:
   ```bash
   pytest tests/ -v --tb=short
   ```
5. **Push** your branch to your fork:
   ```bash
   git push origin feat/your-feature-name
   ```
6. **Open a Pull Request** against `main` on the upstream repository.

### PR Checklist

Before submitting, please confirm:

- [ ] My code follows the project's coding style
- [ ] I have added/updated tests for any new or changed behaviour
- [ ] All existing tests pass (`pytest tests/ -v`)
- [ ] I have updated relevant documentation (README, docstrings, etc.)
- [ ] My commit messages follow the Conventional Commits format
- [ ] I have referenced any related issues in the PR description

### Review Process

- At least **one maintainer approval** is required before merging.
- Address all review comments; push additional commits to the same branch.
- Maintainers may request changes, edits to tests, or additional documentation.
- Once approved, a maintainer will merge the PR using **squash-and-merge** to keep history clean.

---

## Development Setup

### Project Structure

```
DeepDive-AI/
├── app.py               # Streamlit entry point
├── pages/               # Streamlit multi-page views
├── utils/               # Business logic (AI, PDF, PPT)
├── tests/               # pytest test suite
├── requirements.txt     # Python dependencies
└── .env.example         # Environment variable template
```

### Coding Standards

- Python **3.10+** required
- Follow **PEP 8** style guidelines
- Use **type hints** for all public function signatures
- Write **docstrings** for all public modules, classes, and functions
- Keep functions focused and under ~50 lines where possible

---

## Running Tests

```bash
source .venv/bin/activate
pytest tests/ -v --tb=short
```

To run a specific test file:
```bash
pytest tests/test_pdf_generator.py -v
```

---

## Reporting Bugs

Please open an issue and include:

- A clear, descriptive **title**
- Steps to **reproduce** the bug
- **Expected** behaviour
- **Actual** behaviour (including error messages or screenshots)
- Your **environment**: Python version, OS, package versions (`pip freeze`)

---

## Suggesting Features

Open an issue with the `enhancement` label and describe:

- The **problem** you are trying to solve
- Your **proposed solution**
- Any **alternatives** you considered
- Why this would benefit the broader user base

---

Thank you for helping make DeepDive AI better! 🔬
