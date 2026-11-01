"""Astra rule-based preliminary match assessment; not a real ATS score or eligibility decision."""
from datetime import datetime,timezone,timedelta
import re
from scripts.jd_evidence import evaluate

WEIGHTS={"responsibilities":30,"evidenced_skills":25,"seniority":15,"industry":10,"location":15,"compensation":5}
SENIOR=("head of","director","vice president","vp ","principal","staff ","distinguished")
SPECIALISMS=("xactly","salesforce administrator","sap fico","netsuite administrator","workday","icims","taleo","servicenow","kubernetes","cloud security","identity engineering","commission systems","cpa","chartered accountant","pmp required")
def parse_date(value):
 try:
  if not value:return None
  d=datetime.fromisoformat(str(value).replace("Z","+00:00"))
  return d.astimezone(timezone.utc) if d.tzinfo else None
 except (ValueError,TypeError,OverflowError):return None

def assess(job,now=None):
 now=now or datetime.now(timezone.utc)
 title=str(job.get("title") or "")
 location=str(job.get("location") or "")
 desc=str(job.get("_full_description") or job.get("description_excerpt") or "")
 evidence=job.get("jd_evidence") or evaluate(title,desc,location)
 categories=int(evidence.get("capability_categories_matched") or 0)
 lower=(title+" "+desc).lower()
 # This is a limited preliminary score: missing full JD, hard requirements and compensation remain UNKNOWN.
 resp=round(30*min(categories,6)/6)
 skills=round(25*min(categories,7)/7)
 seniority=6 if any(t in lower[:len(title)] for t in SENIOR) else 11 if any(t in title.lower() for t in ("senior","sr.","lead","manager")) else 13
 specialized=[t for t in SPECIALISMS if t in lower]
 if specialized:skills=max(0,skills-9);seniority=min(seniority,10)
 industry=6 # Unknown sector depth; never award full sector fit automatically.
 geography=15 if any(t in location.lower() for t in ("bengaluru","bangalore","hyderabad","pune")) else 10
 compensation=0 # Unknown salary is not evidence of salary alignment.
 score=min(100,resp+skills+seniority+industry+geography+compensation)
 date=parse_date(job.get("source_date")) if job.get("posting_date_verified") else None
 age=(now-date).total_seconds()/86400 if date else None
 fresh=date is not None and 0<=age<=5
 # Restrict auto promotion when important evidence is unavailable; high score is not sufficient.
 review=[]
 if len(desc)<500:review.append("full_JD_missing_or_incomplete")
 if specialized:review.append("specialized_requirements_unverified")
 if evidence.get("potential_unverified_requirements"):review.append("mandatory_platform_or_license_gap_review")
 if not date:review.append("original_posting_date_unverified")
 elif not fresh:review.append("posting_older_than_5_days")
 review.append("salary_not_verified")
 review.append("mandatory_requirements_not_individually_validated")
 tier="strong" if score>=86 else "possible" if score>=71 else "below_threshold"
 return {"preliminary_score":score,"preliminary_tier":tier,"score_status":"RULE_BASED_ESTIMATE_NOT_ATS_SCORE","rubric":{"responsibilities":resp,"evidenced_skills":skills,"seniority":seniority,"industry":industry,"location":geography,"compensation":compensation},"fresh_within_5_days":fresh,"age_days":round(age,1) if age is not None else None,"evidence_coverage_proxy_pct":int(evidence.get("capability_evidence_coverage_pct") or 0),"review_flags":review,"verified_for_main_match_tiers":False}
