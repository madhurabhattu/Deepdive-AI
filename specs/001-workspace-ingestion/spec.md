# Feature Specification: Workspace Ingestion

**Feature Branch**: `001-workspace-ingestion`

**Created**: 2026-06-09

**Status**: Draft

**Input**: User specifies a directory path to scan, chunk, embed, and store in a local ChromaDB database.

## User Scenarios & Testing

### User Story 1 - Local Directory Ingestion (Priority: P1)
As a developer, I want to provide a local folder path to DeepDive AI, so that the system crawls, chunks, and indexes all supported code and text files.

**Why this priority**: Ingestion is the entry point for the entire application. Without indexing the workspace, search and Q&A features cannot function.

**Independent Test**: Provide a test folder with dummy Python and markdown files, click "Start Ingestion", and verify that files are successfully crawled and indexed without errors.

**Acceptance Scenarios**:
1. **Given** the user is on the Ingestion page, **When** they input a valid path `/Users/madhurabhattu/DeepDive-AI/utils` and click "Start Ingestion", **Then** the files are processed, and a success message displays "Ingested 4 files successfully".
2. **Given** the user is on the Ingestion page, **When** they input an invalid or non-existent path, **Then** the system displays a friendly error: "Directory does not exist".

---

### User Story 2 - Respecting .gitignore Rules (Priority: P2)
As a developer, I want the ingestion crawler to respect `.gitignore` rules, so that temporary build artifacts, virtual environments (`venv`), and private configurations are not indexed.

**Why this priority**: Avoids cluttering the vector store with irrelevant or sensitive files, improving search accuracy and performance.

**Independent Test**: Create a folder with a `.gitignore` containing `*.log` and `.venv/`, put files inside `.venv/` and a `.log` file in the root, run ingestion, and assert that these ignored files are skipped.

**Acceptance Scenarios**:
1. **Given** a directory containing a `.venv/` folder and `test.log`, **When** the directory is crawled, **Then** no chunks from `.venv/` or `test.log` are added to ChromaDB.

---

### User Story 3 - Code-Aware Chunking (Priority: P3)
As a developer, I want the chunker to split code blocks based on syntax (e.g., Python class/function boundaries) rather than simple character count, so that the context of code blocks is preserved.

**Why this priority**: Improves response quality from the LLM, as entire functions are retrieved together instead of truncated code snippets.

**Independent Test**: Parse a file with a large class definition and confirm that chunk boundaries align with function definitions where possible.

**Acceptance Scenarios**:
1. **Given** a Python script with multiple functions, **When** chunked, **Then** the chunk boundaries align with line boundaries and function start/end tags where appropriate.

---

## Edge Cases

- **Empty Files / Directories:** If a directory is empty or contains no supported files, the system must show a status message "No supported files found" instead of crashing.
- **Large File Handling:** If a file exceeds a threshold (e.g., 5MB), the system should skip or stream process it to avoid memory exhaustion, logging a warning.
- **Permission Errors:** If a file cannot be read due to permissions, log the warning and skip it, continuing ingestion for the remaining files.

---

## Requirements

### Functional Requirements
- **FR-001:** System MUST accept an absolute directory path as input.
- **FR-002:** System MUST crawl the directory recursively and find files with extensions: `.py`, `.md`, `.txt`, `.json`, `.js`.
- **FR-003:** System MUST read and respect local `.gitignore` specifications from the directory root.
- **FR-004:** System MUST parse files and split them using a code-aware chunking strategy (e.g., `RecursiveCharacterTextSplitter` with code separators).
- **FR-005:** System MUST connect to a local Ollama server to generate embeddings via `nomic-embed-text`.
- **FR-006:** System MUST save generated embeddings into a local ChromaDB collection persisted on disk.
- **FR-007:** System MUST display a status summary after ingestion (number of files scanned, ignored, chunked, and total vectors created).

### Key Entities
- **WorkspaceCollection:** Represents the indexed folder, metadata (path, scan timestamp), and its corresponding ChromaDB collection.
- **DocumentChunk:** Represents a single chunk of text/code with attributes: `content`, `source_file`, `start_line`, `end_line`, and `embedding_vector`.

---

## Success Criteria

### Measurable Outcomes
- **SC-001:** Ingestion of a codebase with 50 files must complete in under 30 seconds (assuming Ollama is running and responsive).
- **SC-002:** The system must filter out 100% of the paths specified in `.gitignore`.
- **SC-003:** The vector index must be persisted so that subsequent app launches do not require re-ingestion unless explicitly triggered.

---

## Assumptions
- The user has Ollama running locally at `http://localhost:11434` with the `nomic-embed-text` model pulled.
- The user inputs a path to which the Python process has read permissions.
