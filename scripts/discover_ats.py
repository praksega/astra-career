#!/usr/bin/env python3
"""Astra public ATS discovery. No credentials. No speculative match scores."""
import concurrent.futures, datetime as dt, json, pathlib, re, urllib.request, urllib.error, html
ROOT=pathlib.Path(__file__).resolve().parents[1]
# Employer board slugs are candidates, not guarantees; failed/empty boards are logged.
GREENHOUSE=["instawork","reddit","figma","notion","airtable","rippling","razorpay","browserstack","meesho","phonepe","slice","postman","freshworks","plaid","stripe","databricks","mongodb","coursera","canva","zoom"]
LEVER=["Loop%20AI","cred","gojek","groww","mindtickle","hackerone","atlassian","zomato","urbancompany","porter"]
CITIES=("hyderabad","bengaluru","bangalore","pune","india","remote")
ROLES=("product operation","product ops","business operation","strategy operation","strategy and operation","process excellence","continuous improvement","process improvement","business analyst","product analyst","program manager","programme manager","project manager","project operation","business transformation","operations analyst","operational excellence","recruitment operations","talent acquisition operations","ta operations","performance analyst","product owner","business intelligence")
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
    title_l=title.lower(); loc_l=location.lower()
    keywords=[r for r in ROLES if r in title_l]
    # Location must be recognized explicitly (do not treat all India vacancies as remote).
    place_ok=any(c in loc_l for c in CITIES[:4]) or ("remote" in loc_l and "india" in loc_l)
    if not keywords or not place_ok:return None
    return {"id":src+":"+ident,"company_board":slug,"title":title,"location":location,"url":url,"source":src,"source_date":stamp,"date_source":"first_published" if src=="greenhouse" and date_verified else "createdAt" if src=="lever" and date_verified else "updated_at/unverified","posting_date_verified":date_verified,"matched_keywords":keywords,"description_characters":len(description),"description_excerpt":description[:500],"status":"unscored_candidate"}
def run():
    targets=[("greenhouse",s) for s in GREENHOUSE]+[("lever",s) for s in LEVER]
    sources=[];raw=0;rows=[];seen=set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for meta,items in pool.map(lambda t:fetch(*t),targets):
            sources.append(meta);raw+=len(items)
            for src,slug,item in items:
                try:r=normalize(src,slug,item)
                except (ValueError,TypeError,AttributeError):continue
                if r and r["id"] not in seen:seen.add(r["id"]);rows.append(r)
    rows.sort(key=lambda x:(x["posting_date_verified"],str(x["source_date"] or "")),reverse=True)
    now=dt.datetime.now(dt.timezone.utc)
    report={"schema_version":1,"run_at_utc":now.isoformat(),"engine":"github_actions_public_ats_v1","source_boards_attempted":len(targets),"source_boards_succeeded":sum(x["status"]=="ok" for x in sources),"source_boards_failed":sum(x["status"]!="ok" for x in sources),"raw_listings_seen":raw,"unique_role_location_candidates":len(rows),"full_jds_reviewed":0,"scored_strong":0,"scored_possible":0,"coverage_target":200,"coverage_status":"DISCOVERY_PARTIAL" if raw<200 else "DISCOVERY_TARGET_MET_UNSCORED","notes":"Raw listings across employer boards are not all relevant. Candidates are role/location title matches, NOT screened 71+/86+ or confirmed fresh. Full JD evaluation remains separate.","boards":sources}
    (ROOT/"data"/"discovered_candidates.json").write_text(json.dumps({"schema_version":1,"updated_at":now.isoformat(),"candidates":rows},indent=2)+"\n")
    out=ROOT/"data"/"run_reports";out.mkdir(parents=True,exist_ok=True)
    (out/"ats_discovery_latest.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="boards"},indent=2))
if __name__=="__main__":run()
