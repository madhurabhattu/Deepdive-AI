# DeepDive AI — User Manual

**Version:** 1.0.0  
**Last Updated:** 2026-06-10

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Requirements](#2-system-requirements)
3. [Installation](#3-installation)
4. [Environment Setup](#4-environment-setup)
5. [Running Locally](#5-running-locally)
6. [Using the Application](#6-using-the-application)
7. [Downloading Reports](#7-downloading-reports)
8. [Running with Docker](#8-running-with-docker)
9. [Troubleshooting](#9-troubleshooting)
10. [FAQ](#10-faq)

---

## 1. Project Overview

**DeepDive AI** is an AI-powered research report generator built with [Streamlit](https://streamlit.io) and the [Google Gemini API](https://ai.google.dev/). It allows users to enter any research topic and receive a fully structured, professional report in seconds — complete with:

| Output Section        | Description                                              |
|-----------------------|----------------------------------------------------------|
| **Executive Summary** | A concise professional overview of the topic             |
| **Key Insights**      | The most important findings and takeaways                |
| **Statistics & Data** | Relevant numbers, metrics, and supporting data points    |
| **References**        | Credible sources with descriptions and URLs              |
| **PDF Report**        | Downloadable multi-page professionally formatted PDF     |
| **PowerPoint Deck**   | Ready-to-present PPTX slide deck (5+ slides)            |

DeepDive AI is designed for researchers, students, educators, analysts, and professionals who need a fast starting point for any research topic.

---

## 2. System Requirements

| Requirement        | Minimum Version  |
|--------------------|------------------|
| **Python**         | 3.10 or higher   |
| **pip**            | 22.0 or higher   |
| **Internet**       | Required (API calls to Google Gemini) |
| **RAM**            | 512 MB free      |
| **Disk space**     | 200 MB (for dependencies + generated output) |

> **Supported OS:** macOS, Linux, Windows 10/11

---

## 3. Installation

### Step 1 — Clone the Repository

```bash
git clone https://code.swecha.org/madhura1/deepdive-ai.git
cd deepdive-ai
```

### Step 2 — Create a Virtual Environment

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the beginning of your terminal prompt.

### Step 3 — Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- `streamlit` — UI framework
- `google-generativeai` — Gemini AI SDK
- `python-dotenv` — Loads `.env` file
- `reportlab` — PDF generation
- `python-pptx` — PowerPoint generation
- `pytest`, `pytest-mock` — Testing framework

---

## 4. Environment Setup

### Obtain a Google Gemini API Key

1. Visit [https://ai.google.dev/](https://ai.google.dev/)
2. Sign in with your Google account
3. Click **"Get API key"**
4. Create a new project or select an existing one
5. Copy the generated API key

> ⚠️ **Keep your API key secret.** Never commit it to version control.

### Configure the `.env` File

```bash
cp .env.example .env
```

Open `.env` in a text editor and replace the placeholder value:

```dotenv
# DeepDive AI — Environment Variables
GEMINI_API_KEY=your_actual_api_key_here
```

Save and close the file. The application loads this key automatically at startup via `python-dotenv`.

---

## 5. Running Locally

Ensure your virtual environment is activated and `.env` is configured, then run:

```bash
streamlit run app.py
```

Streamlit will print a local URL to the terminal:

```
  You can now view your Streamlit app in your browser.

  Local URL:  http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Open the **Local URL** in your browser. The application landing page will appear.

### Stopping the Application

Press `Ctrl + C` in the terminal to stop the Streamlit server.

---

## 6. Using the Application

### Navigation

The application has a **sidebar** on the left with navigation links:

| Page             | Description                                |
|------------------|--------------------------------------------|
| **Home (🏠)**    | Landing page with feature overview         |
| **Research (🔬)**| Main page to generate research reports     |

### Generating a Report

1. Click **🔬 Research** in the sidebar.
2. In the **"Research Topic"** input box, type your topic.
   - Example: `"Impact of AI on Healthcare"`
   - Example: `"History of Quantum Computing"`
   - Example: `"Climate Change and Renewable Energy"`
3. Click the **🚀 Generate Report** button.
4. Wait for the AI to process your request (typically **5–20 seconds** depending on topic complexity and API response time).
5. The report sections will appear below:
   - **Executive Summary**
   - **Key Insights** (bulleted list)
   - **Statistics & Data** (bulleted list)
   - **References & Citations** (links and descriptions)

> 💡 **Tips for better results:**
> - Be specific: `"Machine Learning in Drug Discovery 2024"` gives richer content than just `"AI"`.
> - Avoid extremely short (1-word) topics for best quality.
> - English-language topics produce the most reliable results.

---

## 7. Downloading Reports

After a report is generated, two download buttons appear at the bottom of the report:

### Download as PDF

Click **⬇️ Download PDF** to save a professionally formatted multi-page PDF to your local machine. The PDF includes:
- A title page with the topic and generation date
- All report sections with clear headings
- References with URLs

### Download as PowerPoint

Click **⬇️ Download PPT** to save a PPTX presentation. The deck includes:
- Title slide
- Executive Summary slide
- Key Insights slide
- Statistics & Data slide
- References slide

> Generated files are also saved locally in the `output/` directory.

---

## 8. Running with Docker

If you prefer to run the application in a containerised environment:

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running

### Build the Image

```bash
docker build -t deepdive-ai .
```

### Run the Container

```bash
docker run -p 8501:8501 --env-file .env deepdive-ai
```

Open `http://localhost:8501` in your browser.

> The `--env-file .env` flag passes your API key securely to the container without baking it into the image.

---

## 9. Troubleshooting

### ❌ "GEMINI_API_KEY not found" or "Invalid API key"

**Cause:** The `.env` file is missing or the key is incorrect.

**Fix:**
1. Ensure `.env` exists in the project root (not `.env.example`).
2. Verify the key starts with `AIza...`.
3. Re-run `streamlit run app.py`.

---

### ❌ Application does not start — `ModuleNotFoundError`

**Cause:** Dependencies are not installed or the wrong Python environment is active.

**Fix:**
```bash
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
streamlit run app.py
```

---

### ❌ "Port 8501 is already in use"

**Cause:** Another Streamlit instance or another process is using port 8501.

**Fix:** Run on a different port:
```bash
streamlit run app.py --server.port 8502
```

Or kill the process occupying 8501:
```bash
# macOS / Linux
lsof -i :8501 | grep LISTEN
kill -9 <PID>
```

---

### ❌ Report generation times out or returns empty content

**Cause:** Network connectivity issue or Gemini API rate limit reached.

**Fix:**
1. Check your internet connection.
2. Wait 30–60 seconds and try again.
3. Verify your API key has sufficient quota at [https://console.cloud.google.com/](https://console.cloud.google.com/).

---

### ❌ PDF / PPT download button does not appear

**Cause:** Report generation may have partially failed or a dependency is missing.

**Fix:**
1. Check the terminal output for errors.
2. Reinstall dependencies: `pip install -r requirements.txt`.
3. Regenerate the report.

---

### ❌ Tests fail with `pytest`

**Fix:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v --tb=long
```

Check the output for specific failure messages and ensure `GEMINI_API_KEY` is set if any integration tests require it.

---

## 10. FAQ

**Q: Is my research topic data stored anywhere?**  
A: No. Your topic is sent directly to the Google Gemini API for processing. DeepDive AI does not store, log, or transmit your queries to any third party other than Google.

**Q: Can I use this offline?**  
A: No. The application requires an active internet connection to call the Google Gemini API.

**Q: What languages are supported?**  
A: English is the primary supported language. The Gemini API supports many languages, but report quality may vary for non-English topics.

**Q: How many reports can I generate?**  
A: The number of reports is limited by your Google Gemini API quota. Free-tier keys have a rate limit; see [Google AI Studio quotas](https://ai.google.dev/pricing) for details.

**Q: Can I modify the report format?**  
A: Yes, for developers. The PDF and PowerPoint templates live in `utils/pdf_generator.py` and `utils/ppt_generator.py` respectively. Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

*For additional help, please open an issue on the project repository.*
