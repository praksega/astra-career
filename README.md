# Astra Career — GitHub-backed daily recruiter

The private GitHub repository is Astra's versioned tracking store.

## Daily task
An existing **ChatGPT Astra Daily Recruiter** is enabled for **08:00 Asia/Kolkata every day**, starting 2026-10-31. The task has been updated to attempt GitHub read/merge/commit on each run. **A successful scheduled GitHub write has not yet been observed.**

## Stored data
- [Jobs and previously shown opportunities](data/jobs.json)
- [Confirmed submitted applications](data/applications.json) — only after explicit user confirmation
- [Daily search run history](data/run_history.json)

## Automation architecture
ChatGPT scheduled task → GitHub connector → private JSON tracking files. This does not require a hosted backend for tracking. GitHub Actions is intentionally manual-only, preventing duplicate runs.

## Limitations
- This is a versioned JSON ledger, **not** a live SQLite or hosted web dashboard. The prior local Astra dashboard will not synchronize without an importer or separately added GitHub file reader.
- Scheduled task access to GitHub must be confirmed by its first completed run. If tools are not accessible in scheduled runs, the task must report that GitHub was not updated.
- Generated DOCX/PDF documents require available file tooling; the existing GitHub text-file tool cannot upload binaries automatically. Files should only be linked when truly created and accessible.
- GitHub is private, but repository collaborators can access the records; do not store passwords or API keys here.

Read [DATA_WORKFLOW.md](DATA_WORKFLOW.md) for update rules.
