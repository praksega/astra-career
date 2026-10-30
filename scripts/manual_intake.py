"""Validate manual LinkedIn links for role/city relevance, without asserting post age."""
from linkedin_rules import ROLES, CITIES, canonical

def manual_valid(posts):
    seen=set(); good=[]; rejected={}
    for item in posts:
        if not isinstance(item,dict):
            reason="invalid"; key=None
        else:
            key=canonical(item.get("url"))
            text=" ".join(str(item.get(k) or "") for k in ("role","location","summary")).lower()
            reason=("invalid_link" if not key else
                    "role_not_relevant" if not any(r in text for r in ROLES) else
                    "location_not_relevant" if not any(c in text for c in CITIES) else
                    "duplicate" if key in seen else None)
        if reason:
            rejected[reason]=rejected.get(reason,0)+1
        else:
            seen.add(key);good.append(item)
    return good,rejected
