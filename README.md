# Astra Career — public job discovery dashboard

Website: https://praksega.github.io/astra-career/

This is a PUBLIC repository. Only public-safe job metadata is stored here in [data/jobs.json](data/jobs.json). The GitHub Pages workflow [publish-pages.yml](.github/workflows/publish-pages.yml) renders the public dashboard. The old snapshot workflow is disabled.

## Scheduled workflow
- 08:00 Asia/Kolkata: ChatGPT Astra Daily Recruiter, configured to add **public-safe** qualified job details only, after verification.
- 09:00 Asia/Kolkata: ChatGPT Astra Application Studio, configured to create individual application documents when tools permit, but **never commit personal documents to this public repository**.
- Both scheduled tasks are enabled; successful unattended end-to-end runs still need verification.

## Private data policy
Application submissions/dates, interview notes, personal contact data, Master Resume, resumes, cover letters, and private document queues must live in a SEPARATE private repository or private authenticated storage. No private storage has yet been connected; therefore private application-history synchronization is not operational. See [SECURITY.md](SECURITY.md).

## Limitations
The GitHub Pages site is read-only and public, not an authenticated application tracker. GitHub history can retain prior commits even after files are removed. Do not upload personal documents to this repository.
