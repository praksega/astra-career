"""Create a requirement-verification queue; do not score without verified JD evidence."""
import datetime as dt,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def run():
 p=ROOT/"data"/"discovered_candidates.json"
 d=json.loads(p.read_text())
 items=[]
 for j in d.get("candidates",[]):
  items.append({"job_id":j.get("id"),"company":j.get("company_board"),"title":j.get("title"),"url":j.get("url"),
   "posting_date":j.get("source_date"),"posting_date_verified":bool(j.get("posting_date_verified")),
   "jd_source_available":bool(j.get("jd_text_available_for_scoring")),
   "jd_responsibilities":(j.get("jd_details") or {}).get("responsibilities",[]),
   "jd_qualifications":(j.get("jd_details") or {}).get("qualifications",[]),
   "candidate_evidence":(j.get("jd_evidence") or {}).get("evidence",[]),
   "potential_gaps":(j.get("jd_evidence") or {}).get("potential_unverified_requirements",[]),
   "requirements_verified":False,"verified_score":None,"status":"REVIEW_REQUIRED",
   "blocking_checks":["all_mandatory_requirements","minimum_80_percent_evidence_coverage","seniority","specialized_skills","salary_fixed_at_least_12LPA_or_unknown","posting_date_within_5_days","official_link"]})
 result={"schema_version":1,"updated_at":d.get("updated_at"),"status":"REVIEW_REQUIRED" if items else "NO_CANDIDATES","total":len(items),"verified":0,"jobs":items,
 "note":"This queue does not certify eligibility or generate numeric scores. Verified scores require individual requirement evidence and genuine missing-skill handling."}
 (ROOT/"data"/"jd_verification_queue.json").write_text(json.dumps(result,indent=2)+"\n")
 print("JD verification queue:",len(items),"verified:",0)
if __name__=="__main__":run()
