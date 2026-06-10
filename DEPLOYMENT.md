# Deployment Guide for DeepDive AI

This guide explains how to deploy **DeepDive AI** to production using **Render** or **Streamlit Community Cloud**.

---

## Option 1: Deploying to Render (Recommended)

Render can build and run this application using the provided `Dockerfile` and `render.yaml` blueprint.

### Step-by-Step Instructions

1. **Push Changes to GitHub/GitLab:**
   Ensure all files (including `Dockerfile`, `.dockerignore`, and `render.yaml`) are committed and pushed to your repository.

2. **Log in to Render:**
   Go to [Render](https://render.com/) and log in using your GitHub or GitLab account.

3. **Deploy with Blueprint:**
   - Go to your Render Dashboard and click **New** -> **Blueprint**.
   - Connect your repository (`deepdive-ai`).
   - Render will automatically detect the `render.yaml` configuration.
   - Enter your **`GEMINI_API_KEY`** in the prompted Environment Variables section.
   - Click **Approve** to deploy.

4. **Verify Deployment:**
   - Once the build succeeds, Render will provide a public URL (e.g., `https://deepdive-ai.onrender.com`).
   - Navigate to the URL and verify that report generation works.

---

## Option 2: Deploying to Streamlit Community Cloud

Streamlit Community Cloud is a free, fast platform for hosting Streamlit applications directly from a GitHub repository.

### Step-by-Step Instructions

1. **Publish to GitHub:**
   Ensure your code is pushed to a public GitHub repository.

2. **Log in to Streamlit Cloud:**
   Navigate to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.

3. **Deploy the App:**
   - Click **New app**.
   - Select your repository, branch (usually `main`), and the main file path: `app.py`.
   - Click **Advanced settings...** before deploying to set up secrets.

4. **Configure Secrets:**
   In the **Secrets** text box, paste your `GEMINI_API_KEY` environment variable in TOML format:
   ```toml
   GEMINI_API_KEY = "your_actual_gemini_api_key"
   ```
   - Click **Save**.

5. **Deploy:**
   - Click **Deploy!**.
   - Your app will be live at a URL like `https://<your-app-name>.streamlit.app/`.

---

## Local Docker Deployment (Alternative)

If you want to run the production build locally using Docker:

```bash
# Build the Docker image
docker build -t deepdive-ai .

# Run the container (using your local .env file)
docker run --env-file .env -p 8501:8501 deepdive-ai
```
The app will be accessible at `http://localhost:8501`.
