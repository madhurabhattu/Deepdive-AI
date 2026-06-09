# Implementation Plan: Workspace Ingestion

**Branch**: `001-workspace-ingestion` | **Date**: 2026-06-09 | **Spec**: [spec.md](file:///Users/madhurabhattu/DeepDive-AI/specs/001-workspace-ingestion/spec.md)

**Input**: Feature specification from `/specs/001-workspace-ingestion/spec.md`

## Summary
Build a robust directory crawler and parsing subsystem in Python that reads local source files, filters them using gitignore schemas, chunks them with LangChain's code splitters, generates embeddings via a local Ollama server, and indexes them into ChromaDB. We will expose this functionality through a Streamlit UI on the Ingestion page.

---

## Technical Context

* **Language/Version:** Python 3.10+
* **Primary Dependencies:** Streamlit, LangChain, ChromaDB, Ollama Python Client, Pathspec (for gitignore checks)
* **Storage:** Local ChromaDB (persisted under `db/` or `.chroma/` in workspace)
* **Testing:** Pytest (tests co-located in `tests/` or alongside logic)
* **Target Platform:** macOS / Linux desktop environment
* **Project Type:** Streamlit Multi-Page Web App
* **Performance Goals:** Ingest and index 100 code files (<1MB total) in <45 seconds.
* **Constraints:** Complete offline execution, zero external HTTP calls (except localhost Ollama).

---

## Constitution Check

* **Offline & Privacy-First:** Checked. Only calls `localhost:11434` for Ollama embeddings.
* **AST / Code Chunking:** Checked. Uses LangChain's `RecursiveCharacterTextSplitter.from_language` to parse Python/JavaScript files.
* **UI/Logic Separation:** Checked. Ingestion code will reside in `utils/parser.py` and `utils/vectorstore.py`, not inside the Streamlit page view.
* **Traceable Citations:** Checked. Line numbers and file paths will be stored as metadata in each vector record.
* **Test Coverage:** Checked. Unit tests will target parser and vector store modules.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-workspace-ingestion/
├── spec.md              # Requirements and User Stories
├── plan.md              # Technical design and architecture (This file)
└── tasks.md             # Actionable engineering tasks
```

### Source Code & Test Layout

We will use the following structures for implementation:

```text
app.py                         # Landing page redirecting to pages
pages/
└── 1_📂_Ingestion.py          # UI for inputting directory, starting scan, displaying progress

utils/
├── __init__.py
├── parser.py                  # Directory crawler, gitignore filter, file reader, chunk splitter
└── vectorstore.py             # ChromaDB client connector, Ollama embedding generator

tests/
├── test_parser.py             # Unit tests for crawler, gitignore filter, and splitters
└── test_vectorstore.py        # Unit tests for database inserts and retrieves
```

---

## Technical Design Details

### 1. File Crawling and Gitignore Filtering (`utils/parser.py`)
- We will use `pathspec` to read and match paths against `.gitignore` directives.
- We will recursively walk the given root path, building a list of paths relative to the root, checking them against the loaded `PathSpec`.
- Supported files: `.py`, `.js`, `.json`, `.md`, `.txt`.

### 2. Chunking strategy (`utils/parser.py`)
- For Python files (`.py`), we will use `RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON, chunk_size=800, chunk_overlap=100)`.
- For other text-based files, we will use default splitters.
- Metadata to collect per chunk:
  ```json
  {
    "source": "relative/path/to/file.py",
    "filename": "file.py",
    "start_line": 12,
    "end_line": 25
  }
  ```

### 3. Vector Database Indexing (`utils/vectorstore.py`)
- We will instantiate ChromaDB's persistent client: `chromadb.PersistentClient(path="./.chromadb")`.
- We will initialize the embedding function using `OllamaEmbeddings(model="nomic-embed-text")`.
- Collection name will default to `deepdive_workspace`.
- Document content, metadata, and embeddings will be batched and upserted in sizes of 100 records to prevent HTTP timeouts.

---

## Complexity Tracking
*No constitution checks are violated. The architecture remains minimal and modular.*
