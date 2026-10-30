# Astra: GitHub as source of truth

Every 8 AM IST ChatGPT Astra scheduled task should retrieve `data/jobs.json`, `data/applications.json` and `data/run_history.json` in this private repo using the connected GitHub integration. Research up to 10 new recent (<=5 days old) verifiable matches >85, generate supporting content and update the JSON files via GitHub API (fetch existing SHA before update). Only mark `Applied` on explicit user confirmation and record date, role, company. If GitHub connector is not accessible in scheduled run, report the failure and **do not claim sync**. Preserve existing entries on every update. Do not store secrets. Make no assumption that local Astra SQLite mirrors this repository; that is a separate importer/view step.

Master resume should be stored as private user-controlled attachment or managed document; binary DOCX/PDF writes are not supported by the current UTF-8 GitHub text file action. Store their verified paths/links only if actually available.
