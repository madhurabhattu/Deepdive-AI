# DeepDive AI — Geographical Expansion Strategy

This document outlines the expansion strategy for DeepDive AI, aiming to bring local-first, privacy-respecting research tools to diverse regional languages and communities across India and eventually globally.

---

## 1. Current Target Region & Focus

Currently, DeepDive AI primarily serves users in India, with UI and report-generation capabilities focused on four primary languages:
* **English (EN):** Serves urban professionals, corporate analysts, and standard university curricula.
* **Hindi (HI):** Targets North and Central Indian states (e.g., Uttar Pradesh, Bihar, Madhya Pradesh, Rajasthan, Delhi).
* **Telugu (TE):** Targets Andhra Pradesh and Telangana, anchoring the project's native roots in the Swecha open-source ecosystem.
* **Marathi (MR):** Serves Maharashtra's vast student and industrial worker base.

The target region is characterized by high mobile browser penetration but varying internet bandwidth quality in rural areas, making our local-first Ollama capabilities particularly relevant.

---

## 2. Expansion Across Indian States

Our multi-state onboarding roadmap is structured to follow language and education corridors:

```
┌────────────────────────────────────────────────────────┐
│  Phase 1: Telugu, Marathi, Hindi Consolidation         │
├────────────────────────────────────────────────────────┤
│  Phase 2: Southern Languages Expansion (KA, KL, TN)    │
├────────────────────────────────────────────────────────┤
│  Phase 3: Eastern & Western Frontiers (WB, GJ, PB)     │
└────────────────────────────────────────────────────────┘
```

### Phase 1: Consolidation (Telangana, Andhra Pradesh, Maharashtra, Hindi Belt)
* Expand through existing Swecha networks and Swecha student chapters.
* Focus on engineering colleges in tier-2 and tier-3 cities (e.g., Warangal, Karimnagar, Nagpur, Pune).

### Phase 2: Southern Peninsular Expansion (Karnataka, Kerala, Tamil Nadu)
* **Goal:** Integrate Kannada, Malayalam, and Tamil support.
* **Outreach:** Partner with local Free Software Movements (e.g., FSUC in Karnataka, FSCG, and regional groups in Tamil Nadu).

### Phase 3: Eastern and Western Frontiers (West Bengal, Gujarat, Punjab)
* **Goal:** Integrate Bengali, Gujarati, and Punjabi.
* **Outreach:** Set up localization sprints to translate UI resource dictionaries.

---

## 3. Multilingual Onboarding Strategy

To onboarding users who prefer regional languages, we implement a friction-free localized pipeline:
1. **Auto Browser Language Detection:** Utilizing the browser's `Accept-Language` headers, the application automatically sets the UI language to the user's local language on first visit (e.g., auto-displaying Hindi labels for Hindi-configured systems).
2. **Local Font Delivery:** As detailed in [font_manager.py](file:///Users/madhurabhattu/DeepDive-AI/utils/font_manager.py), the application automatically downloads Noto Sans Devanagari and Noto Sans Telugu Unicode TTF files on-demand to guarantee clean PDF rendering without needing complex system installations.
3. **Bilingual Prompts:** When a user selects a regional language for report output, the AI client appends translation prompts directing the model to generate the summaries and citations in the target language while retaining strict English JSON keys for reliable internal processing.

---

## 4. Regional Partnerships & Alliances

Geographical expansion relies on integration with existing community frameworks:
* **Free Software Movements (FSMK, Swecha):** Provide infrastructure, compute resources for hosting mirrors, and translation volunteers.
* **Regional Language Academies & Universities:** Collaborate with Telugu and Marathi university departments to test report translation accuracy.
* **Rural Digital Centers:** Partner with rural common service centers (CSCs) to introduce DeepDive AI as an educational study tool that can run on a single desktop computer without internet.

---

## 5. College Outreach Roadmap

Colleges are the primary hubs for student onboarding:
* **Bootcamps & Hackathons:** Run workshops showcasing how local RAG (Document Q&A) lets students chat with their course textbooks locally.
* **Computer Labs Onboarding:** Work with college lab administrators to pre-configure and install Ollama and Streamlit on local laboratory computers so that students can access the application over the local area network (LAN) from their personal mobile devices.
* **Regional Translation Sprints:** Host weekend translation events where students translate UI keys and test generated reports on local historical or agricultural topics to verify translation quality.

---

## 6. International Considerations

While the focus remains on Indian regional languages, the design of DeepDive AI supports future international localization:
* **Linguistic Modularity:** The translation schema in [localization.py](file:///Users/madhurabhattu/DeepDive-AI/utils/localization.py) is modular. Support for Spanish, French, or Swahili can be added simply by defining new key-value dictionaries.
* **Unicode Compliance:** All PDF generation (using ReportLab) and PowerPoint layouts (using python-pptx) support UTF-8 formatting, making global character sets compatible out of the box.
