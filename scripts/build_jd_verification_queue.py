"""Create a requirement-verification queue; do not score without verified JD evidence."""
import datetime as dt,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def run():
 p=ROOT/"data"/"discovered_candidates.json"
 d=json.loads(p.read_text())
 items=[]
 now=dt.datetime.now(dt.timezone.utc)
 for j in d.get("candidates",[]):
  try:
   stamp=dt.datetime.fromisoformat(str(j.get("source_date") or "").replace("Z","+00:00"))
   age_days=(now-stamp.astimezone(dt.timezone.utc)).total_seconds()/86400 if stamp.tzinfo else None
  except (ValueError,TypeError,OverflowError):age_days=None
  fresh=bool(j.get("posting_date_verified")) and age_days is not None and 0<=age_days<=5
  specialized=(j.get("jd_evidence") or {}).get("potential_unverified_requirements",[])
  blockers=[]
  if not fresh:blockers.append("original_posting_not_verified_within_5_days")
  if specialized:blockers.append("specialized_experience_not_confirmed")
  if not j.get("jd_text_available_for_scoring"):blockers.append("incomplete_jd")
  blockers.extend(["mandatory_requirements_not_individually_verified","salary_not_confirmed"])
  items.append({"job_id":j.get("id"),"company":j.get("company_board"),"title":j.get("title"),"url":j.get("url"),
   "posting_date":j.get("source_date"),"posting_date_verified":bool(j.get("posting_date_verified")),
   "jd_source_available":bool(j.get("jd_text_available_for_scoring")),
   "jd_responsibilities":(j.get("jd_details") or {}).get("responsibilities",[]),
   "jd_qualifications":(j.get("jd_details") or {}).get("qualifications",[]),
   "candidate_evidence":(j.get("jd_evidence") or {}).get("evidence",[]),
   "potential_gaps":(j.get("jd_evidence") or {}).get("potential_unverified_requirements",[]),
   "requirements_verified":False,"verified_score":None,"status":"REVIEW_REQUIRED","fresh_within_5_days":fresh,"days_since_posting":round(age_days,2) if age_days is not None else None,"verification_blockers":blockers,
   "blocking_checks":["all_mandatory_requirements","minimum_80_percent_evidence_coverage","seniority","specialized_skills","salary_fixed_at_least_12LPA_or_unknown","posting_date_within_5_days","official_link"]})
 result={"schema_version":1,"updated_at":d.get("updated_at"),"status":"REVIEW_REQUIRED" if items else "NO_CANDIDATES","total":len(items),"verified":0,"fresh_for_review":sum(j["fresh_within_5_days"] for j in items),"older_or_unverified":sum(not j["fresh_within_5_days"] for j in items),"jobs":items,
 "note":"This queue does not certify eligibility or generate numeric scores. Verified scores require individual requirement evidence and genuine missing-skill handling."}
 (ROOT/"data"/"jd_verification_queue.json").write_text(json.dumps(result,indent=2)+"\n")
 print("JD verification queue:",len(items),"verified:",0)
if __name__=="__main__":run()
