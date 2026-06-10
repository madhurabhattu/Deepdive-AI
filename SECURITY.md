# Security Policy

## Supported Versions

The following table shows which versions of DeepDive AI currently receive security updates.

| Version | Supported          |
|---------|--------------------|
| 1.x.x   | ✅ Actively supported |
| < 1.0   | ❌ Not supported      |

We recommend always running the latest stable release.

---

## Reporting a Vulnerability

We take the security of DeepDive AI seriously. If you believe you have found a security vulnerability, **please do not open a public issue**. Instead, follow the responsible disclosure process below.

### How to Report

Please report security vulnerabilities by **one** of the following methods:

1. **Email (preferred):** Send a detailed report to the project maintainer via the email address listed in the repository's profile or README.
2. **Private issue:** If your Git hosting platform supports confidential/private issues, open one with the label `security`.

### What to Include in Your Report

To help us triage and resolve the issue quickly, please include:

- A clear **description** of the vulnerability
- The **affected component(s)** (e.g., `utils/ai_client.py`, environment variable handling)
- **Steps to reproduce** the vulnerability
- The **potential impact** (e.g., data exposure, denial of service, privilege escalation)
- Any **proof-of-concept** code or screenshots (if applicable)
- Your **suggested fix** (optional but appreciated)

---

## Responsible Disclosure Guidelines

We follow a **coordinated vulnerability disclosure** model:

1. **Report privately** — Contact the maintainers before disclosing publicly.
2. **Allow response time** — We aim to acknowledge your report within **48 hours** and provide an initial assessment within **7 days**.
3. **Collaborate on a fix** — We will work with you to understand and resolve the issue.
4. **Agree on a disclosure timeline** — We aim to release a fix within **90 days** of the initial report. If a fix requires more time, we will notify you and agree on an extended timeline.
5. **Public disclosure** — Once a fix is released, we will publish a security advisory crediting you (with your permission).

We ask that you:
- **Do not** exploit the vulnerability beyond what is necessary to demonstrate it.
- **Do not** access, modify, or delete data belonging to other users.
- **Do not** disclose the vulnerability publicly before a patch is available.
- **Act in good faith** — we will do the same.

---

## Security Best Practices for Users

### Protecting Your API Key

- **Never commit your `.env` file** to version control. The `.gitignore` excludes it by default.
- Use `.env.example` as a template; always copy it to `.env` and fill in real values locally.
- If you suspect your `GEMINI_API_KEY` has been exposed, regenerate it immediately at [https://aistudio.google.com/](https://aistudio.google.com/).
- When running in production or shared environments, prefer injecting secrets via environment variables or a secrets manager rather than a `.env` file.

### Running in Docker

- Use `--env-file .env` to pass secrets to the container; never `COPY .env` into the Docker image.
- Do not run the container as `root` in production environments.
- Regularly pull updated base images to receive OS security patches.

### Dependencies

- Keep dependencies up to date. Run `pip list --outdated` regularly.
- Use `pip audit` or a dependency scanning tool (e.g., `safety`, Dependabot) to detect known vulnerabilities in third-party packages.

---

## Acknowledgements

We are grateful to the security researchers and community members who responsibly disclose vulnerabilities. We will credit reporters in our security advisories (with their consent).

---

*This policy is subject to change. Check back for updates.*
