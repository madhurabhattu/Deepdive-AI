# Tasks: Workspace Ingestion

**Input**: Design documents from `/specs/001-workspace-ingestion/`

**Prerequisites**: plan.md (required), spec.md (required)

**Format**: `[ID] [P?] [Story] Description`
* **[P]**: Can run in parallel
* **[Story]**: Story correlation (e.g. US1, US2, US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Set up workspace dependencies and structure

- [ ] T001 Initialize `requirements.txt` with dependencies: `streamlit`, `langchain`, `chromadb`, `pathspec`, `pytest`, `ollama`
- [ ] T002 Create initial folder skeleton: `utils/`, `pages/`, `tests/`
- [ ] T003 [P] Configure a basic `pytest.ini` test configuration

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core backend utilities for file crawling and database indexing

**⚠️ CRITICAL**: Must be completed before starting UI pages or user stories

- [ ] T004 Create `utils/parser.py` file with basic imports and type definitions
- [ ] T005 Create `utils/vectorstore.py` with standard ChromaDB persistence setup
- [ ] T006 [P] Add Winston-style Python log configurations in `utils/logger.py`

---

## Phase 3: User Story 1 - Local Directory Ingestion (Priority: P1) 🎯 MVP

**Goal**: Ingest a folder of files and persist embeddings in ChromaDB

**Independent Test**: Run a command-line test script or unit test to ingest `/Users/madhurabhattu/DeepDive-AI/utils` and verify vectors are in ChromaDB.

### Tests for User Story 1
- [ ] T007 Write unit tests in `tests/test_parser.py` for directory crawler and splitters (expect fail first)
- [ ] T008 Write integration test in `tests/test_vectorstore.py` to assert embeddings are written to ChromaDB

### Implementation for User Story 1
- [ ] T009 [P] [US1] Implement recursive directory search in `utils/parser.py`
- [ ] T010 [US1] Implement text and python splitters in `utils/parser.py`
- [ ] T011 [US1] Implement ChromaDB collection connector in `utils/vectorstore.py`
- [ ] T012 [US1] Implement Ollama embedding generator calling REST endpoint in `utils/vectorstore.py`
- [ ] T013 [US1] Implement batch upsert logic for ChromaDB in `utils/vectorstore.py`
- [ ] T014 [US1] Create the Ingestion UI page `pages/1_📂_Ingestion.py` with path input and Start button
- [ ] T015 [US1] Link Ingestion UI page to crawler and indexer methods, showing progress bar

---

## Phase 4: User Story 2 - Respecting .gitignore Rules (Priority: P2)

**Goal**: Ignore paths matched by `.gitignore` rules during crawls

**Independent Test**: Verify that files in folders like `.venv/` or `.git/` are skipped during folder scan.

### Tests for User Story 2
- [ ] T016 Write unit test in `tests/test_parser.py` checking gitignore match rules on a mock structure

### Implementation for User Story 2
- [ ] T017 [US2] Implement `.gitignore` parser using `pathspec` library in `utils/parser.py`
- [ ] T018 [US2] Integrate `.gitignore` filtering inside the crawler file search function

---

## Phase 5: User Story 3 - Code-Aware Chunking (Priority: P3)

**Goal**: Split code using Python AST boundaries to preserve logical sections

**Independent Test**: Verify that python files split into chunks containing complete function scopes.

### Tests for User Story 3
- [ ] T019 Write unit test checking split output of a multi-function class structure

### Implementation for User Story 3
- [ ] T020 [US3] Configure language-specific splitters (`Language.PYTHON`, `Language.JS`) in `utils/parser.py`
- [ ] T021 [US3] Capture starting line numbers and ending line numbers of code snippets in chunk metadata

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation, error resilience, and dashboard details

- [ ] T022 [P] Implement validation to ensure user input paths exist before initiating scan
- [ ] T023 Implement exception handlers for file read permissions or Ollama server connection failure
- [ ] T024 Add styling (custom CSS) to Streamlit widgets on the Ingestion page
- [ ] T025 Confirm all tests pass with `pytest tests/`
