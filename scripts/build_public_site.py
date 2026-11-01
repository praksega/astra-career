"""Build a PUBLIC-safe Astra Pages site; never publish applications, private documents, or raw JSON."""
import json,html,pathlib,datetime as dt
from linkedin_rules import filtered, canonical
from manual_intake import manual_valid
root=pathlib.Path(__file__).resolve().parents[1]
jobs=json.loads((root/"data/jobs.json").read_text(encoding="utf-8")).get("jobs",[])
posts=json.loads((root/"data/linkedin_posts.json").read_text(encoding="utf-8")).get("posts",[])
manual=json.loads((root/"data/manual_linkedin_intake.json").read_text(encoding="utf-8")).get("posts",[])
discovery=json.loads((root/"data/discovered_candidates.json").read_text(encoding="utf-8")).get("candidates",[])
audit_path=root/"data/run_reports/workflow_latest.json"
audit=json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else {"status":"NOT_RUN"}
out=root/"public_site";out.mkdir(exist_ok=True)
e=lambda x:html.escape(str(x if x is not None else ""),quote=True)
strong_cards=[]
possible_cards=[]
for j in jobs:
    score=j.get("score")
    if not isinstance(score,(int,float)) or score<=70:continue
    if j.get("score_status") not in ("verified","verified_requirements"):continue
    try:
        posted=dt.date.fromisoformat(str(j.get("date_posted") or ""))
        age=(dt.datetime.now(dt.timezone.utc).date()-posted).days
        if age<0 or age>5:continue
    except (ValueError,TypeError):continue
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
discovery_cards=[]
summary={"strong":0,"possible":0,"below_threshold":0,"unscored":0}
for job in discovery:
    a=job.get("preliminary_assessment") or {}
    tier=a.get("preliminary_tier","unscored")
    summary[tier]=summary.get(tier,0)+1
for job in discovery[:100]:
    url=str(job.get("url") or "")
    if not url.startswith("https://"):continue
    assessment=job.get("preliminary_assessment") or {}
    preliminary=assessment.get("preliminary_score")
    tier=assessment.get("preliminary_tier","unscored")
    flags=", ".join(assessment.get("review_flags") or [])
    discovery_cards.append(f'<article><h2>{e(job.get("title"))} — {e(job.get("company_board"))}</h2><p>{e(job.get("location"))} · Source: {e(job.get("source"))} · Date: {e(job.get("source_date") or "Unknown")} ({e(job.get("date_source"))})</p><p><b>Preliminary fit: {e(str(preliminary)+"/100" if preliminary is not None else "not scored")} — {e(tier)}</b> · Rule-based estimate, NOT an ATS score or verified match.</p><p><small>Review required: {e(flags or "Qualification and compensation validation")}. Job availability not guaranteed.</small></p><a href="{e(url)}" rel="noopener noreferrer" target="_blank">Employer job page</a></article>')
audit_status=e(audit.get("status","NOT_RUN"))
audit_time=e(audit.get("timestamp_utc","No completed execution"))
audit_counts=e(audit.get("candidate_count","Unknown"))
audit_block='<section><h2>Latest 8 AM Discovery Execution</h2><p><strong>'+audit_status+'</strong> · '+audit_time+' · Candidates: '+audit_counts+'</p><p><a href="https://github.com/praksega/astra-career/blob/main/data/run_reports/workflow_latest.json">View independent run audit</a></p></section>'
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Astra Opportunities</title><style>body{background:#f4f6fa;color:#15253f;font:16px/1.55 system-ui;margin:0}main{max-width:1000px;margin:auto;padding:28px}header{background:#172b4b;color:#fff;border-radius:16px;padding:25px}.top{display:flex;justify-content:space-between;gap:20px}article{background:white;margin:14px 0;padding:18px;border:1px solid #e1e5ef;border-radius:12px}a{color:#1967b1}h2{font-size:18px;margin:0 0 8px}p{color:#56647a}</style></head><body><main><header><small>ASTRA · PUBLIC JOB DISCOVERY VIEW</small><h1>Career Opportunities</h1><p style="color:#cfdbf0">Selected openings and provisional match assessments</p></header>'''+audit_block+'''<h2>Strong Matches (86–100)</h2>'''+(''.join(strong_cards) or '<p>No strong matches recorded.</p>')+'<h2>Possible Matches (71–85) — up to 20</h2>'+(''.join(possible_cards[:20]) or '<p>No possible matches recorded yet.</p>')+'<h2>ATS discovery — Preliminary scored candidates ('+str(len(discovery))+')</h2><p>Rule-based strong: '+str(summary['strong'])+' · Possible: '+str(summary['possible'])+' · Below threshold: '+str(summary['below_threshold'])+' · Unscored: '+str(summary['unscored'])+'. These are NOT independently verified match ratings.</p>'+(''.join(discovery_cards) or '<p>No ATS discovery candidates yet; see GitHub Actions diagnostics.</p>')+'<h2>Verified LinkedIn Hiring Posts — Last 24 Hours ('+str(len(post_cards))+')</h2>'+(''.join(post_cards) or '<p>No verified relevant posts recorded yet.</p>')+'<h2>Manual LinkedIn Leads — Date Unverified ('+str(len(manual_cards))+')</h2><p><a href="intake.html">Add recruiter hiring posts</a></p>'+(''.join(manual_cards) or '<p>No manually imported relevant posts yet.</p>')+'''<p><small>Private resume, cover letters, application statuses and personal information are intentionally not published. Job data is a snapshot; check official posting for status.</small></p></main></body></html>'''
(out/"index.html").write_text(page,encoding="utf-8")
(out/".nojekyll").write_text("",encoding="utf-8")
(out/"intake.html").write_text((root/"scripts/intake_template.html").read_text(encoding="utf-8").replace("__ASTRA_EXISTING_POSTS__",json.dumps(manual,ensure_ascii=True).replace("<","\\u003c")),encoding="utf-8")
print("Public strong cards:",len(strong_cards),"possible cards shown:",min(20,len(possible_cards)),"LinkedIn displayed:",len(post_cards),"excluded:",excluded_posts,"manual_relevant:",len(manual_cards),"manual_excluded:",manual_rejected)
