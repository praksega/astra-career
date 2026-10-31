"""Reproducible preliminary triage only. Scores are NOT validated fit or ATS scores."""
import json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
def preliminary(j):
 title=j.get("title","");x=title.lower()
 if re.search(r"application development|finance technology|xactly",x):responsibility=9
 elif re.search(r"fraud|marketing|risk operations",x):responsibility=14
 elif re.search(r"product operations|program manager|business analyst|product analyst|operations analyst|process excellence|partner program",x):responsibility=27
 elif re.search(r"operations manager|strategy|team lead",x):responsibility=21
 else:responsibility=15
 n=(j.get("jd_evidence") or {}).get("capability_categories_matched") or 0
 skills=round(n/7*25)
 seniority=10 if re.search(r"senior|sr\.|manager|lead",x) else 12
 specialized=-17 if re.search(r"xactly|application development|fraud|finance technology|robotics labs",x) else 0
 points=max(0,min(95,responsibility+skills+seniority+7+15+specialized))
 tier="strong_provisional" if points>=86 else "possible_provisional" if points>=71 else "below_threshold"
 return {"score":points,"tier":tier,"component_scores":{"responsibility_title_proxy":responsibility,"capability_overlap":skills,"seniority_proxy":seniority,"industry_assumption":7,"location":15,"compensation_unverified":0,"specialism_penalty":specialized},"note":"Heuristic preliminary score from job title and existing JD capability evidence map; mandatory requirements, seniority, industry, pay, and current opening not independently validated."}
def run():
 source=json.loads((ROOT/"data/discovered_candidates.json").read_text())
 rows=[dict(j,preliminary_fit=preliminary(j)) for j in source.get("candidates",[])]
 result={"schema_version":1,"updated_at":source.get("updated_at"),"basis":"Source-candidate JD excerpts and existing capability evidence map; unvalidated preliminary score only","scoring_warning":"Not an ATS score, nor evidence of >=80% JD requirement coverage. Do not promote to verified 86+ or 71–85 categories until full JD and mandatory requirements verified.","candidates":rows}
 (ROOT/"data/preliminary_fit_review.json").write_text(json.dumps(result,indent=2)+"\n")
 print("Preliminary candidate fit mapping:",len(rows))
if __name__=="__main__":run()
