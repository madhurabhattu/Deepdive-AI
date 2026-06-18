# Swecha GitLab Runner Setup Guide

This document explains how to set up and configure a project-specific GitLab Runner for the **DeepDive AI** repository, using Swecha's personal runner registration script.

---

## 1. Generate a Personal Access Token (PAT)

To register the runner automatically, you must generate a GitLab Personal Access Token (PAT) with appropriate API permissions:

1. Log in to your GitLab instance (e.g., [code.swecha.org](https://code.swecha.org)).
2. In the upper-right corner, click on your avatar and select **Preferences**.
3. In the left sidebar, click on **Access Tokens**.
4. Click **Add new token**:
   - **Name**: `gitlab-runner-registration`
   - **Expiration date**: Choose a suitable date or leave it empty for no expiration.
   - **Scopes**: Check the **`api`** scope checkbox.
5. Click **Create personal access token**.
6. **Copy the token value immediately** and store it securely (it will not be shown again).

---

## 2. Register and Start the GitLab Runner

Execute the Swecha setup script on your target machine/runner server. This script will download, install, register, and start a GitLab Runner instance inside a Docker container.

Run the following command in your terminal, replacing `<TOKEN>` with the Personal Access Token you generated above:

```bash
GITLAB_PAT=<TOKEN> RUNNER_EXECUTOR=docker \
bash <(curl -fsSL https://code.swecha.org/-/snippets/2749/raw/main/setup-gitlab-runner.sh)
```

### Script Execution Parameters:
- `GITLAB_PAT`: Your personal access token with the `api` scope.
- `RUNNER_EXECUTOR`: The executor type to run build steps (defaults to `docker` to build/run clean containers).

---

## 3. Verification & Monitoring

Once registration is complete, verify that the runner is online, active, and processing pipeline builds properly.

### A. Check Runner Container Status
Verify that the GitLab Runner container is active and running:
```bash
docker ps | grep gitlab-runner
```

### B. View Runner Process Logs
If pipelines are stuck or failing to start, view the runner container logs:
```bash
docker logs -f gitlab-runner
```

### C. Restart the Runner
If you need to apply configuration updates or restart the runner:
```bash
docker restart gitlab-runner
```

### D. Verify Status on GitLab UI
1. Navigate to your project repository page on GitLab.
2. Select **Settings** (left sidebar) → **CI/CD**.
3. Expand the **Runners** section.
4. Verify that your runner is listed under **Project runners** (or **Specific runners**) with a green circle indicator showing it is **online**.

### E. Check Pipeline Status
1. Navigate to **Build** → **Pipelines** or **CI/CD** → **Pipelines**.
2. Run a manual pipeline or commit a change.
3. Click on the active pipeline to view the `test_stage` and `build_stage` job execution logs.
