# DeepDive AI — Mobile Support & PWA Roadmap

This document outlines the roadmap for extending mobile platform support for DeepDive AI. 

> [!IMPORTANT]
> **Current Status:** Native Android or iOS applications do not currently exist. The application is hosted as a responsive Streamlit web page accessible via modern mobile web browsers.

---

## 1. Current Mobile Browser Compatibility

As a Streamlit application, the user interface uses responsive grid layouts that adapt to smaller screen form factors.

* **Supported Browsers:** Chrome Mobile, Safari Mobile, Firefox Mobile, Edge Mobile.
* **Layout Adaptation:** The navigation sidebar collapses into a top-left hamburger menu. Report sections wrap vertically. Download buttons remain clickable.
* **Limitations:**
  * File uploads for Document Q&A can be difficult to navigate on mobile filesystems.
  * Local Ollama models cannot run on mobile browser clients; users must connect to a remote server or use the cloud Gemini API.

---

## 2. Progressive Web App (PWA) Roadmap

To provide a app-like feel without the overhead of native app store deployment, we propose migrating the Streamlit page to a PWA.

### Phase 1: Service Worker Registration
* Add a `manifest.json` declaring icons, theme colors, and display configurations.
* Implement a basic service worker (`sw.js`) to cache static resources (styles, fonts, local javascript components).

### Phase 2: Web Share Integration
* Integrate the browser's Web Share API, allowing users to share generated PDFs or PowerPoints directly to WhatsApp, Telegram, or email.

---

## 3. Native Wrapper Strategy (Capacitor / Tauri)

To deploy to Google Play Store and Apple App Store, we propose wrapping the application frontend in a hybrid container:

```
  ┌────────────────────────────────────────────────────────┐
  │         Capacitor Container (Android/iOS Runtime)      │
  │  ┌──────────────────────────────────────────────────┐  │
  │  │  Streamlit WebView (UI Render & File Download)   │  │
  │  └──────────────────────────────────────────────────┘  │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │        Device Native API (FileSystem, Native Shares)   │
  └────────────────────────────────────────────────────────┘
```

### Proposed Approach:
1. **Tooling:** Use **CapacitorJS** by Ionic to wrap the responsive web address.
2. **Local Inference Fallback:** Since mobile chips are increasingly capable of running quantized LLMs, future iterations could integrate **Tauri Mobile** or local web-LLM runtimes (like ONNX runtime web) to run lightweight quantized models (e.g., Qwen 1.5B) directly on-device without any server connection.
3. **Download Handlers:** Write custom native bridge plugins to handle the PDF and PowerPoint downloads, saving them directly to the mobile device's `/Downloads` directory.
