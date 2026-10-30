# Astra data separation

This repository is PUBLIC. Store ONLY non-sensitive job listing fields in `data/jobs.json`, plus public-safe aggregate run logs. Do not commit resumes, cover letters, master CV, personal email, phone, contact details, interview notes, salary negotiations, submission status, application history or document queue.

Private data needs a separate **private** repository (suggested `praksega/astra-career-private`) or private authenticated storage. Never embed private content in GitHub Pages, client-side JS, GitHub Actions artifacts, or public commit history.

Existing commits remain in history even after deletion; repository history should be audited before assuming previously committed material is erased. Never rely on `.gitignore` to prevent GitHub API commits.
