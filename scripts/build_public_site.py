"""Build a PUBLIC-safe Astra Pages site; never publish applications, private documents, or raw JSON."""
import json,html,pathlib
from linkedin_rules import filtered, canonical
from manual_intake import manual_valid
root=pathlib.Path(__file__).resolve().parents[1]
jobs=json.loads((root/"data/jobs.json").read_text(encoding="utf-8")).get("jobs",[])
posts=json.loads((root/"data/linkedin_posts.json").read_text(encoding="utf-8")).get("posts",[])
manual=json.loads((root/"data/manual_linkedin_intake.json").read_text(encoding="utf-8")).get("posts",[])
out=root/"public_site";out.mkdir(exist_ok=True)
e=lambda x:html.escape(str(x if x is not None else ""),quote=True)
strong_cards=[]
possible_cards=[]
for j in jobs:
    score=j.get("score")
    if not isinstance(score,(int,float)) or score<=70:continue
    tier="strong" if score>85 else "possible"
    url=str(j.get("url",""))
    if not url.startswith("https://"):continue
    card=f'<article><div class="top"><h2>{e(j.get("company"))} — {e(j.get("title"))}</h2><b>{e(j.get("score","?"))}/100</b></div><p>{e(j.get("location"))} · Fit: {e(j.get("score_status","unverified"))}</p><p>Posting date: {e(j.get("date_posted") or "Not verified")} · First shown: {e(j.get("first_shown_date") or "Unknown")}</p><a href="{e(url)}" rel="noopener noreferrer" target="_blank">Official job posting</a></article>'
    (strong_cards if tier=="strong" else possible_cards).append(card)
post_cards=[]
valid_posts, excluded_posts=filtered(posts)
for item in valid_posts:
    url=str(item.get("url",""))
    if not url.startswith("https://www.linkedin.com/") and not url.startswith("https://in.linkedin.com/"):continue
    post_cards.append(f'<article><h2>{e(item.get("company") or item.get("source_name") or "LinkedIn hiring post")}</h2><p>{e(item.get("summary") or item.get("role") or "")}</p><p>{e(item.get("location") or "")} · Posted: {e(item.get("posted_at") or "Unverified")}</p><p><small>Community hiring lead — not an independently verified job or match score.</small></p><a href="{e(url)}" rel="noopener noreferrer" target="_blank">Original LinkedIn post</a></article>')
manual_cards=[]
manual_valid_posts, manual_rejected=manual_valid(manual)
verified_keys={canonical(p.get("url")) for p in valid_posts}
for item in manual_valid_posts:
    if canonical(item.get("url")) in verified_keys:continue
    url=str(item.get("url") or "")
    manual_cards.append(f'<article><h2>{e(item.get("company") or "Recruiter post")} — {e(item.get("role"))}</h2><p>{e(item.get("location"))}</p><p><small>Manually submitted lead · Original posting time not verified · Not counted as fresh</small></p><a href="{e(url)}" target="_blank" rel="noopener noreferrer">View LinkedIn post</a></article>')
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Astra Opportunities</title><style>body{background:#f4f6fa;color:#15253f;font:16px/1.55 system-ui;margin:0}main{max-width:1000px;margin:auto;padding:28px}header{background:#172b4b;color:#fff;border-radius:16px;padding:25px}.top{display:flex;justify-content:space-between;gap:20px}article{background:white;margin:14px 0;padding:18px;border:1px solid #e1e5ef;border-radius:12px}a{color:#1967b1}h2{font-size:18px;margin:0 0 8px}p{color:#56647a}</style></head><body><main><header><small>ASTRA · PUBLIC JOB DISCOVERY VIEW</small><h1>Career Opportunities</h1><p style="color:#cfdbf0">Selected openings and provisional match assessments</p></header><h2>Strong Matches (86–100)</h2>'''+(''.join(strong_cards) or '<p>No strong matches recorded.</p>')+'<h2>Possible Matches (71–85) — up to 20</h2>'+(''.join(possible_cards[:20]) or '<p>No possible matches recorded yet.</p>')+'<h2>Verified LinkedIn Hiring Posts — Last 24 Hours ('+str(len(post_cards))+')</h2>'+(''.join(post_cards) or '<p>No verified relevant posts recorded yet.</p>')+'<h2>Manual LinkedIn Leads — Date Unverified ('+str(len(manual_cards))+')</h2><p><a href="intake.html">Add recruiter hiring posts</a></p>'+(''.join(manual_cards) or '<p>No manually imported relevant posts yet.</p>')+'''<p><small>Private resume, cover letters, application statuses and personal information are intentionally not published. Job data is a snapshot; check official posting for status.</small></p></main></body></html>'''
(out/"index.html").write_text(page,encoding="utf-8")
(out/".nojekyll").write_text("",encoding="utf-8")
(out/"intake.html").write_text((root/"scripts/intake_template.html").read_text(encoding="utf-8").replace("__ASTRA_EXISTING_POSTS__",json.dumps(manual,ensure_ascii=True).replace("<","\\u003c")),encoding="utf-8")
print("Public strong cards:",len(strong_cards),"possible cards shown:",min(20,len(possible_cards)),"LinkedIn displayed:",len(post_cards),"excluded:",excluded_posts,"manual_relevant:",len(manual_cards),"manual_excluded:",manual_rejected)
