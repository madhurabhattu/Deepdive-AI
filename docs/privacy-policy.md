# DeepDive AI — Privacy Policy

**Last Updated:** June 2026

DeepDive AI is committed to protecting your privacy. This privacy policy describes how we collect, process, and handle your data when you use the DeepDive AI Research Report Generator and local Document Q&A application.

---

## 1. Local-First Processing (GDPR Transparency)

DeepDive AI is built with a **local-first and privacy-by-default architecture**. 

* **No Server-Side Tracking:** We do not deploy telemetry, analytics trackers, or profiling scripts on the core Streamlit application.
* **100% Offline Mode (Ollama):** If you configure the application to run with **Ollama Local**, all AI inference (text generation and vector embedding extraction) occurs entirely on your own local physical hardware. No network requests are sent, and no data is shared.
* **Local Caching:** When you upload documents for local Q&A search, the text chunks and vector embeddings are stored in a local SQLite cache database ([embeddings_cache.db](file:///Users/madhurabhattu/DeepDive-AI/data/embeddings_cache.db)) on your own machine. This data never leaves your environment.

---

## 2. Cloud AI Processing (Google Gemini API)

If you explicitly choose to configure and use the **Google Gemini API** cloud backend:
* **BYOK (Bring Your Own Key):** You supply your own API credentials via the Streamlit UI sidebar, Streamlit secrets, or local environment variables.
* **Data Transmission:** Only your research topic inputs are transmitted to Google's API servers to generate the reports.
* **Provider Terms:** The data sent to the Gemini API is governed by the [Google APIs Terms of Service](https://developers.google.com/terms) and [Google's Privacy Policy](https://policies.google.com/privacy). DeepDive AI does not intercept, log, or persist these payloads.

---

## 3. Community Reviews & Ratings Data

DeepDive AI offers a sidebar feedback form allowing users to submit ratings and reviews.

* **Voluntary Information:** We only collect your name, rating (1-5 stars), optional comment, and timestamp when you submit a review.
* **Explicit Consent:** In compliance with GDPR principles, you must select the **Consent Checkbox** before submission. By selecting the checkbox, you grant permission to save your name and comments in [reviews.json](file:///Users/madhurabhattu/DeepDive-AI/data/reviews.json), which is stored locally in the project repository.
* **Public Visibility:** If the repository is shared, committed, or pushed to open-source platforms (e.g. Swecha GitLab), the reviews contained in `reviews.json` will be publicly visible to other developers and users.
* **Data Rectification & Erasure:** If you wish to modify or erase your submitted review, you can do so directly by opening [reviews.json](file:///Users/madhurabhattu/DeepDive-AI/data/reviews.json) in a text editor and deleting your entry, or by opening an issue requesting maintainers to remove it.

---

## 4. Data Security

We implement appropriate controls to safeguard your data:
* **Atomic JSON writes:** All review data writes are handled using atomic operations to prevent corruption.
* **BYOK Session Security:** API keys entered into the Streamlit sidebar are stored strictly in session memory and are never persisted to disk or sent to any telemetry endpoints.

---

## 5. Contact Information

If you have questions about this privacy policy, local data storage, or wish to request data deletion, please contact:
* **Swecha Community Support:** [https://swecha.org/contact](https://swecha.org/contact)
* **GitLab Issue Board:** Open an issue at [https://code.swecha.org/madhura1/deepdive-ai/-/issues](https://code.swecha.org/madhura1/deepdive-ai/-/issues) using the `documentation_issue` template.
