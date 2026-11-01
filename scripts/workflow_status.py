#!/usr/bin/env python3
"""Produce an auditable per-run GitHub Actions status. Never equate an empty output with success."""
import datetime as dt,json,os,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 out=ROOT/"data"/"run_reports";out.mkdir(parents=True,exist_ok=True)
 now=dt.datetime.now(dt.timezone.utc).isoformat()
 steps={name:os.environ.get(name,"unknown") for name in ("TEST_RESULT","DISCOVERY_RESULT","SCORING_RESULT")}
 status="SUCCESS" if all(x=="success" for x in steps.values()) else "FAILED" if "failure" in steps.values() else "INCOMPLETE"
 data={"schema_version":1,"timestamp_utc":now,"run_id":os.environ.get("GITHUB_RUN_ID"),"attempt":os.environ.get("GITHUB_RUN_ATTEMPT"),"commit":os.environ.get("GITHUB_SHA"),"workflow":os.environ.get("GITHUB_WORKFLOW"),"status":status,"steps":steps,"report_present":False,"candidates_present":False}
 p=out/"ats_discovery_latest.json";q=ROOT/"data"/"discovered_candidates.json"
 try:
  d=json.loads(p.read_text()); data["discovery_report_time"]=d.get("run_at_utc")
  data["raw_listings_seen"]=d.get("raw_listings_seen")
  data["candidate_count"]=d.get("unique_role_location_candidates")
  data["report_present"]=bool(d.get("run_at_utc"))
  rows=json.loads(q.read_text()).get("candidates",[])
  data["candidates_present"]=bool(rows) and all(isinstance(x,dict) for x in rows)
  data["candidate_scored_count"]=sum(bool(x.get("preliminary_assessment")) for x in rows)
  if status=="SUCCESS" and (not data["report_present"] or d.get("run_at_utc")!=os.environ.get("EXPECTED_DISCOVERY_TIME")):status="INCOMPLETE"
  if status=="SUCCESS" and data["candidate_scored_count"]!=len(rows):status="INCOMPLETE"
 except (OSError,ValueError,TypeError) as e:data["data_error"]=str(e);status="INCOMPLETE" if status=="SUCCESS" else status
 data["status"]=status
 (out/"workflow_latest.json").write_text(json.dumps(data,indent=2)+"\n")
 print(json.dumps(data,indent=2))
if __name__=="__main__":main()
