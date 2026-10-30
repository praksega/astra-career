"""Build a PUBLIC-safe Astra Pages site; never publish applications, private documents, or raw JSON."""
import json,html,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
jobs=json.loads((root/"data/jobs.json").read_text(encoding="utf-8")).get("jobs",[])
out=root/"public_site";out.mkdir(exist_ok=True)
e=lambda x:html.escape(str(x if x is not None else ""),quote=True)
cards=[]
for j in jobs:
    url=str(j.get("url",""))
    if not url.startswith("https://"):continue
    cards.append(f'<article><div class="top"><h2>{e(j.get("company"))} — {e(j.get("title"))}</h2><b>{e(j.get("score","?"))}/100</b></div><p>{e(j.get("location"))} · Fit: {e(j.get("score_status","unverified"))}</p><p>Posting date: {e(j.get("date_posted") or "Not verified")} · First shown: {e(j.get("first_shown_date") or "Unknown")}</p><a href="{e(url)}" rel="noopener noreferrer" target="_blank">Official job posting</a></article>')
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Astra Opportunities</title><style>body{background:#f4f6fa;color:#15253f;font:16px/1.55 system-ui;margin:0}main{max-width:1000px;margin:auto;padding:28px}header{background:#172b4b;color:#fff;border-radius:16px;padding:25px}.top{display:flex;justify-content:space-between;gap:20px}article{background:white;margin:14px 0;padding:18px;border:1px solid #e1e5ef;border-radius:12px}a{color:#1967b1}h2{font-size:18px;margin:0 0 8px}p{color:#56647a}</style></head><body><main><header><small>ASTRA · PUBLIC JOB DISCOVERY VIEW</small><h1>Career Opportunities</h1><p style="color:#cfdbf0">Selected openings and provisional match assessments</p></header><h2>Tracked Opportunities</h2>'''+''.join(cards)+'''<p><small>Private resume, cover letters, application statuses and personal information are intentionally not published. Job data is a snapshot; check official posting for status.</small></p></main></body></html>'''
(out/"index.html").write_text(page,encoding="utf-8")
(out/".nojekyll").write_text("",encoding="utf-8")
print("Public cards:",len(cards))
