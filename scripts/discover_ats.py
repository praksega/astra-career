#!/usr/bin/env python3
"""Astra public ATS discovery. No credentials. No speculative match scores."""
import concurrent.futures, datetime as dt, json, pathlib, re, urllib.request, urllib.error, html
ROOT=pathlib.Path(__file__).resolve().parents[1]
try:
 from scripts.jd_evidence import evaluate
 from scripts.preliminary_scoring import assess
 from scripts.jd_extract import extract
except ModuleNotFoundError:
 from jd_evidence import evaluate
 from preliminary_scoring import assess
 from jd_extract import extract
# Employer board slugs are candidates, not guarantees; failed/empty boards are logged.
GREENHOUSE=["instawork","reddit","figma","notion","airtable","rippling","razorpay","browserstack","meesho","phonepe","slice","postman","freshworks","plaid","stripe","databricks","mongodb","coursera","canva","zoom","duolingo","okta","twilio","asana","brex","coinbase","roblox","gusto","square","elastic","udemy","miro","wise","deliveroo","hubspot"]
LEVER=["Loop%20AI","cred","gojek","groww","mindtickle","hackerone","atlassian","zomato","urbancompany","porter","swiggy","sharechat","clevertap","whatfix","innovaccer","highradius","browserstack","chargebee","upgrad","ninjacart","cars24"]
CITIES=("hyderabad","bengaluru","bangalore","pune")
ROLES=("product operation","product ops","business operation","strategy operation","strategy and operation","process excellence","continuous improvement","process improvement","business analyst","product analyst","program manager","programme manager","project manager","project operation","business transformation","operations analyst","operational excellence","recruitment operations","talent acquisition operations","ta operations","performance analyst","product owner","business intelligence","business process","strategy associate","strategy analyst","business excellence","operations excellence","process analyst","business systems","revenue operations","sales operations","customer operations","workforce operations","workforce analyst","operations manager","operations specialist","program specialist","program analyst","project analyst","business intelligence analyst","business performance","implementation specialist","implementation manager","product specialist","project coordinator")
EXCLUSIONS=("software engineer","backend engineer","frontend engineer","data engineer","machine learning engineer","cloud engineer","devops engineer","mobile developer","technical architect","account executive","sales executive","site reliability")
# A precise title match is best, but responsibilities can recover less-obvious role titles.
DUTY_TERMS=("stakeholder management","process improvement","operational efficiency","continuous improvement","reporting dashboards","process automation","workflow automation","business operations","performance metrics","cross-functional coordination","business process improvement","program management","operational excellence","process optimization","process optimisation","requirements gathering","business analytics")
def candidate_signals(title,description):
    title_l=title.lower()
    if any(x in title_l for x in EXCLUSIONS):return [],"excluded_specialist_title"
    title_hits=[x for x in ROLES if x in title_l]
    body_l=description.lower()
    duty_hits=[x for x in DUTY_TERMS if x in body_l]
    # Do not admit unrelated generic jobs just because JD lists stakeholder management.
    generic_title=any(x in title_l for x in ("analyst","operations","strategy","program","project","process","product","business","implementation","transformation"))
    if title_hits:return title_hits+duty_hits[:4],"title_and_jd" if duty_hits else "title"
    if generic_title and len(set(duty_hits))>=3:return duty_hits[:6],"jd_responsibilities"
    return [],"role_not_relevant"
def fetch(source,slug):
    url=(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true" if source=="greenhouse" else f"https://api.lever.co/v0/postings/{slug}?mode=json")
    req=urllib.request.Request(url,headers={"User-Agent":"AstraCareerResearch/1.0 (public vacancies; github.com/praksega/astra-career)","Accept":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=14) as resp: data=json.load(resp)
        items=data.get("jobs",[]) if source=="greenhouse" else data
        if not isinstance(items,list):raise ValueError("unexpected JSON shape")
        return {"source":source,"board":slug,"status":"ok","count":len(items)},[(source,slug,x) for x in items]
    except (urllib.error.URLError,TimeoutError,ValueError,json.JSONDecodeError,OSError) as e:
        return {"source":source,"board":slug,"status":"error","error":type(e).__name__,"count":0},[]
def normalize(src,slug,x):
    if src=="greenhouse":
        title=x.get("title") or ""; location=((x.get("location") or {}).get("name") or "")
        url=x.get("absolute_url") or "";ident=str(x.get("id") or "")
        stamp=x.get("first_published") or x.get("updated_at")
        date_verified=bool(x.get("first_published"))
        description=html.unescape(re.sub("<[^>]*>"," ",(x.get("content") or "")))
    else:
        title=x.get("text") or "";location=(x.get("categories") or {}).get("location") or ""
        url=x.get("hostedUrl") or ""; ident=str(x.get("id") or "")
        stamp=x.get("createdAt")
        date_verified=bool(stamp)
        description=html.unescape(re.sub("<[^>]*>"," ",(x.get("descriptionPlain") or x.get("description") or "")))
    if not (ident and url.startswith("https://")):return None
    if src=="lever" and isinstance(stamp,(int,float)):stamp=dt.datetime.fromtimestamp(stamp/1000,dt.timezone.utc).isoformat()
    loc_l=location.lower()
    # Evaluate every complete available JD at approved locations before role filtering.
    place_ok=any(c in loc_l for c in CITIES) or ("remote" in loc_l and "india" in loc_l)
    if not place_ok:return None
    keywords,reason=candidate_signals(title,description)
    if not keywords:return None
    return {"id":src+":"+ident,"company_board":slug,"title":title,"location":location,"url":url,"source":src,"source_date":stamp,"date_source":"first_published" if src=="greenhouse" and date_verified else "createdAt" if src=="lever" and date_verified else "updated_at/unverified","posting_date_verified":date_verified,"matched_keywords":keywords,"matching_method":reason,"description_characters":len(description),"jd_text_available_for_scoring":len(description)>=500,"_full_description":description,"description_excerpt":description[:1200],"jd_details":extract(description,url),"status":"unscored_candidate","jd_evidence":evaluate(title,description,location)}
def run():
    targets=[("greenhouse",s) for s in GREENHOUSE]+[("lever",s) for s in LEVER]
    sources=[];raw=0;rows=[];seen=set();location_eligible_reviewed=0;complete_jd_location_reviewed=0;rejection_counts={"unrelated_or_unapproved_location":0,"invalid_record":0};full_content_candidates=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for meta,items in pool.map(lambda t:fetch(*t),targets):
            sources.append(meta);raw+=len(items)
            for src,slug,item in items:
                loc=((item.get("location") or {}).get("name","") if src=="greenhouse" else (item.get("categories") or {}).get("location","")) if isinstance(item,dict) else ""
                eligible=any(city in str(loc).lower() for city in CITIES) or ("remote" in str(loc).lower() and "india" in str(loc).lower())
                if eligible:
                    location_eligible_reviewed+=1
                    raw_jd=(item.get("content") or "") if src=="greenhouse" else (item.get("descriptionPlain") or item.get("description") or "")
                    if len(raw_jd)>=500:complete_jd_location_reviewed+=1
                try:r=normalize(src,slug,item)
                except (ValueError,TypeError,AttributeError):rejection_counts["invalid_record"]+=1;continue
                if not r:rejection_counts["unrelated_or_unapproved_location"]+=1;continue
                if r["id"] not in seen:
                    seen.add(r["id"]);rows.append(r)
                    if r["description_characters"]>=500:full_content_candidates+=1
    now=dt.datetime.now(dt.timezone.utc)
    for row in rows:
        row["verification_status"]="REVIEW_REQUIRED"
        row["verification_reasons"]=["mandatory_requirements_not_verified","compensation_not_verified","minimum_80_percent_requirement_coverage_not_established"]
        row.pop("_full_description",None) # Do not republish entire employer JD
    rows.sort(key=lambda x:(bool(x.get("posting_date_verified")),str(x.get("source_date") or "")),reverse=True)
    report={"schema_version":1,"run_at_utc":now.isoformat(),"engine":"github_actions_public_ats_v1","source_boards_attempted":len(targets),"source_boards_succeeded":sum(x["status"]=="ok" for x in sources),"source_boards_failed":sum(x["status"]!="ok" for x in sources),"raw_listings_seen":raw,"location_eligible_jds_screened":location_eligible_reviewed,"location_eligible_jds_with_500_plus_chars":complete_jd_location_reviewed,"unique_role_location_candidates":len(rows),"full_jds_with_accessible_text":full_content_candidates,"jd_evidence_maps_generated":sum("jd_evidence" in x for x in rows),"human_or_evidence_scored_full_jds":0,"scored_strong":0,"scored_possible":0,"verified_matches":0,"review_required":len(rows),"rejection_counts":rejection_counts,"coverage_target":200,"coverage_status":"INSUFFICIENT_RELEVANT_COVERAGE" if len(rows)<30 else "CANDIDATES_DISCOVERED_UNSCORED","notes":"All location-eligible available ATS descriptions are checked for role relevance before selecting candidates. Candidate titles and JD duties are screened; all remain REVIEW_REQUIRED until individual mandatory requirements are verified; no heuristic numeric scores are asserted. Accessible JD text is not a full evidence-based assessment. No hiring or current freshness guarantee.","boards":sources,"potential_fit_reviews":sum(x["jd_evidence"]["capability_categories_matched"]>=4 for x in rows)}
    (ROOT/"data"/"discovered_candidates.json").write_text(json.dumps({"schema_version":1,"updated_at":now.isoformat(),"candidates":rows},indent=2)+"\n")
    out=ROOT/"data"/"run_reports";out.mkdir(parents=True,exist_ok=True)
    (out/"ats_discovery_latest.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="boards"},indent=2))
if __name__=="__main__":run()
