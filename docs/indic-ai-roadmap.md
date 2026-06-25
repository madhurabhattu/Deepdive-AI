# DeepDive AI — Indic AI & Model Fine-Tuning Roadmap

This document outlines the engineering roadmap to build, validate, and fine-tune localized open-weights LLMs for generating high-quality research reports in Indian languages.

---

## 1. Indic Language Goals

While DeepDive AI supports English, Hindi, Marathi, and Telugu UI translation dictionaries, LLM generations in regional languages can sometimes exhibit grammatical errors, transliteration glitches, or lack professional domain vocabulary.

Our goal is to achieve:
* **Natural Grammar:** Fluent sentence construction in Telugu, Hindi, and Marathi.
* **Domain Completeness:** Correct translation of complex scientific, economic, and technical terms.
* **Consistent JSON Formats:** Generating localized contents without breaking JSON key-value schemas.

---

## 2. Support Roadmap

```
┌────────────────────────────────────────────────────────┐
│  Phase 1: Dataset Curation & Translation Sprints       │
├────────────────────────────────────────────────────────┤
│  Phase 2: Validation, Baseline Testing & Metrics       │
├────────────────────────────────────────────────────────┤
│  Phase 3: Fine-Tuning Local LLMs & Integration         │
└────────────────────────────────────────────────────────┘
```

* **Short-Term (Q3 2026):** Improve prompting directives in `ai_client.py` and expand custom font selections to support additional Indic scripts (e.g., Kannada, Tamil).
* **Medium-Term (Q4 2026):** Collect parallel corpora of technical reports and establish baseline evaluations.
* **Long-Term (Q1 2027):** Train a lightweight quantized model (e.g., LLaMA 3 8B or Qwen 7B) on Swecha's translation corpus, optimizing it for local Ollama execution.

---

## 3. Dataset Acquisition Strategy

Fine-tuning requires clean, diverse datasets representing technical and formal language:
* **Swecha Language Corpus:** Ingesting verified local language articles and textbooks collected via the Swecha community network.
* **Public Parallel Datasets:** Curating data from open sources such as AI4Bharat, Samanantar, and Bhashini.
* **Synthetic Generation:** Utilizing advanced models (e.g., Gemini Pro) to translate standard English research databases, followed by manual community verification.

---

## 4. Translation Evaluation Metrics

To evaluate model improvements, we implement quantitative and qualitative benchmarks:

### A. Quantitative Metrics
* **BLEU (Bilingual Evaluation Understudy):** Measures n-gram overlap between model output and human-translated reference reports. Target: BLEU > 0.40.
* **ROUGE (Recall-Oriented Understudy for Gisting Evaluation):** Focuses on recall, assessing the overlap of summary components. Crucial for evaluating the Executive Summary and Key Insights sections.

### B. Qualitative Metrics (Human Evaluation)
* **Fluency:** Checking sentence structures and local grammatical agreements.
* **Accuracy:** Verifying technical terms are translated correctly (e.g., ensuring "Quantum Computing" is correctly described in Telugu without awkward phrasing).
* **Compliance:** Ensuring the output format matches the schema dataclass structure defined in `report_schema.py`.

---

## 5. Fine-Tuning Architecture Proposal

We propose using Parameter-Efficient Fine-Tuning (PEFT) with Low-Rank Adaptation (LoRA) to allow training on standard consumer GPUs:

* **Base Model:** `unsloth/llama-3-8b-Instruct-bnb-4bit` or `Qwen2-7B-Instruct`.
* **Method:** QLoRA (Quantized LoRA) to train model parameters using 4-bit quantization, minimizing VRAM requirements.
* **Training Platform:** Run training scripts using PyTorch and Hugging Face `transformers` / `peft` libraries.
* **Target Output format:** Export the adapter and merge it with the base weights to compile a `.gguf` file compatible with local Ollama runtimes.

---

## 6. Risk Assessment

| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **JSON Schema Breaking:** Model translates JSON keys into regional scripts, breaking parser. | High | Strict training mask penalizing any key translations. Enforce structural validation during generation. |
| **Hallucination in Translation:** Model invents facts or creates awkward neologisms. | Medium | Use RAG context verification. Provide clear reference URLs. |
| **GPU Hardware Constraints:** Training takes too long or exceeds memory. | Medium | Leverage Google Colab, Kaggle, or Swecha's server hubs using 4-bit QLoRA optimizations. |
