# Astra Career — private automation repository

This private repository is the deployment home for Astra's code and scheduled job runner.

## Current status
- ChatGPT Astra Daily Recruiter: scheduled daily 08:00 Asia/Kolkata (separate ChatGPT task; not a GitHub integration).
- GitHub Actions: scheduled workflow to call a separately hosted authenticated Astra backend. The workflow will **skip** until the repository secrets `ASTRA_BASE_URL` and `ASTRA_ACCESS_TOKEN` are configured.
- Database: **not hosted or synchronized yet**. GitHub alone is not a durable private application database.
- Never commit actual CVs, generated applications, API tokens, or job application history into the repository.

Next: deploy Astra to an authenticated service with persistent storage, configure secrets in GitHub Settings → Secrets and variables → Actions, run `workflow_dispatch` once, and inspect logs before treating cloud sync as operational.
