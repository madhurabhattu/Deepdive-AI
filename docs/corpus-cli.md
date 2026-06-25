# DeepDive AI — Corpus CLI Integration Roadmap

> [!NOTE]
> This document is **informational and future-facing**. The Corpus CLI is not currently integrated into the DeepDive AI code backend. This guide serves as a technical proposal and operational manual for future implementation.

---

## 1. Purpose of Corpus CLI

The **Corpus CLI** is a command-line toolchain developed by the Swecha/FOSS community to collect, validate, package, and upload digital text corpora. In projects focusing on regional Indian languages, the Corpus CLI enables developers to feed local language data (such as articles, translations, scanned textbooks, and speech scripts) directly into central repositories.

For **DeepDive AI**, integration with the Corpus CLI will allow:
* Ingesting high-quality regional language corpora to feed our local Document Q&A RAG indexes.
* Uploading anonymized user research reports (with consent) to Swecha's central corpus repository to assist in open LLM training.

---

## 2. Installation Instructions

The Corpus CLI can be installed locally via `pip` or by downloading pre-built binaries.

```bash
# Clone the Corpus Toolchain repository
git clone https://code.swecha.org/corpus/corpus-cli.git
cd corpus-cli

# Install in virtual environment
source .venv/bin/activate
pip install .
```

Verify installation:
```bash
corpus-cli --version
```

---

## 3. Example Commands

Here are standard operations performed with the Corpus CLI toolset:

### Ingesting & Validating Text Data
Ensure texts are formatted in UTF-8 and contain clean syntax:
```bash
corpus-cli validate --dir ./raw_telugu_data/ --lang te
```

### Packaging a Dataset Corpus
Package folders of text or PDF files into a standardized compressed archive:
```bash
corpus-cli package --input ./validated_data/ --output ./packages/telugu_history.zip
```

### Uploading to Swecha Central Registry
Publish the packaged corpus to the central repository:
```bash
corpus-cli upload --package ./packages/telugu_history.zip --token <SWECHA_CORPUS_TOKEN>
```

---

## 4. Proposed Data Ingestion/Upload Workflow

When integrated, DeepDive AI will utilize the following workflow:

```
  ┌────────────────────────────────────────────────────────┐
  │ 1. User generates report or indexes document locally   │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 2. Check for explicit data upload consent               │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ 3. DeepDive runs automated validations & packages UTF-8│
  └───────────────────────────┬────────────────────────────┘
                              ▼
  │ 4. Calls Corpus CLI library to upload package to cloud  │
  └────────────────────────────────────────────────────────┘
```

1. **Consent Trigger:** A checkbox asks: *"Share this generated report with Swecha's Open Corpus project?"*
2. **Background Ingestion:** If checked, the app writes the validated `ResearchReport` JSON schema to a queue folder.
3. **Packaging:** A background task invokes the Corpus CLI python API to package the queue folder.
4. **Transmission:** The package is uploaded using a pre-configured project runner API token.

---

## 5. Potential Integration Opportunities

1. **RAG Dataset Library:** A new page in the Streamlit UI called **"Community Ingestion"** where users can browse public corpora uploaded via the Corpus CLI and download them directly into their local FAISS vector store.
2. **Fine-Tuning Loop:** Feed reports written in regional languages back into the fine-tuning pipeline to continuously improve translation prompts.
