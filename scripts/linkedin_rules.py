"""Strict validation for public LinkedIn hiring leads. No scraping or timestamp inference."""
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
import re

CITIES=("bengaluru","bangalore","hyderabad","pune","remote india","remote - india","india remote")
ROLES=("product operations","business operations","strategy & operations","strategy and operations","process improvement","continuous improvement","business analyst","product analyst","program manager","programme manager","project manager","project operations","operational excellence","operations analyst","analytics","business transformation","recruitment operations","talent acquisition operations","ta operations","performance analyst","product owner")
LINKEDIN_HOSTS={"linkedin.com","www.linkedin.com","in.linkedin.com"}
def canonical(url):
    try:
        p=urlparse(url)
        host=p.hostname.lower() if p.hostname else ""
        if host not in LINKEDIN_HOSTS or p.scheme!="https":return None
        path=p.path.rstrip("/")
        match=re.search(r"(?:/posts/[^/]*activity-|/feed/update/urn:li:activity:)(\d{12,})",path)
        return "activity:"+match.group(1) if match else ("url:"+path.lower() if "/posts/" in path or "/feed/update/" in path else None)
    except (TypeError,ValueError,AttributeError):return None
def validate(item,now=None):
    if not isinstance(item,dict):return False,"invalid_record"
    key=canonical(item.get("url"))
    if not key:return False,"not_individual_linkedin_post"
    stamp=item.get("posted_at")
    if not isinstance(stamp,str):return False,"missing_verified_timestamp"
    try: dt=datetime.fromisoformat(stamp.replace("Z","+00:00"))
    except ValueError:return False,"invalid_timestamp"
    if dt.tzinfo is None:return False,"timezone_missing"
    now=now or datetime.now(timezone.utc)
    age=now-dt.astimezone(timezone.utc)
    if age<timedelta(0) or age>timedelta(hours=24):return False,"outside_24h"
    if item.get("timestamp_verified") is not True or not item.get("timestamp_evidence_url"):
        return False,"timestamp_evidence_missing"
    content=" ".join(str(item.get(k) or "") for k in ("role","summary","location")).lower()
    if not any(t in content for t in CITIES):return False,"location_not_relevant"
    if not any(t in content for t in ROLES):return False,"role_not_relevant"
    return True,key
def filtered(posts,now=None):
    seen=set();valid=[];rejected={}
    for item in sorted(posts,key=lambda x:str(x.get("posted_at") or ""),reverse=True):
        ok,reason=validate(item,now)
        if not ok:
            rejected[reason]=rejected.get(reason,0)+1;continue
        if reason in seen:
            rejected["duplicate"]=rejected.get("duplicate",0)+1;continue
        seen.add(reason);valid.append(item)
    return valid,rejected
