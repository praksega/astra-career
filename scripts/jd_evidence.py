"""Explainable preliminary JD fit: evidence only, not employer ATS score."""
import re
CAPABILITIES={
 "reporting_analytics":("reporting","dashboard","metrics","kpi","power bi","sql","excel","business intelligence"),
 "process_improvement":("process improvement","continuous improvement","operational excellence","process excellence","process optimization","process optimisation","standardization"),
 "automation":("automation","workflow automation","process automation","ai tools"),
 "stakeholders":("stakeholder","cross-functional","collaborat","vendor management","employer engagement"),
 "program_delivery":("program management","project management","project coordination","implementation","agile","roadmap"),
 "operations":("business operations","product operations","recruitment operations","workforce operations","operational performance","operations"),
 "documentation":("documentation","sop","standard operating procedure","requirements gathering","user acceptance testing","uat"),
}
# Each category below corresponds to documented SERCO/Xeality experience; evidence is not tied to a specific ATS.
VERIFIED={"reporting_analytics":"SERCO: Excel, SQL, Power BI; 33 outcome KPIs",
"process_improvement":"SERCO: workflow cycle-time improvement; Xeality: vendor onboarding improvement",
"automation":"SERCO: seven operational automations",
"stakeholders":"SERCO: employer coordination; Xeality: vendor collaboration",
"program_delivery":"Xeality: product roadmap and Agile delivery; SERCO: cross-team implementation",
"operations":"SERCO: workforce operations; Xeality: product operations",
"documentation":"SERCO: SOP design, testing and deployment"}
HARD_GAPS=("workday recruiting","icims administrator","taleo administrator","servicenow administrator","sap successfactors","six sigma black belt","pmp certification","chartered accountant","cpa","medical doctor","phd required","licensed attorney")
def evaluate(title,description,location):
 text=(title+" "+description).lower()
 matches={k:[term for term in terms if term in text] for k,terms in CAPABILITIES.items()}
 matched={k:v for k,v in matches.items() if v}
 gaps=[x for x in HARD_GAPS if x in text]
 # This metric reflects capability evidence coverage only; cannot substitute for requirement-by-requirement manual review.
 coverage=round(100*len(matched)/len(CAPABILITIES)) if matched else 0
 role_strength=len(matched)
 risk="requires_review" if gaps else "no_obvious_platform_gap_detected"
 return {"score":None,"score_status":"NOT_SCORED_REQUIREMENT_VALIDATION_NEEDED",
 "capability_categories_matched":role_strength,"capability_evidence_coverage_pct":coverage,
 "evidence":[{"category":k,"jd_terms":v[:4],"candidate_evidence":VERIFIED[k]} for k,v in matched.items()],
 "potential_unverified_requirements":gaps,"gap_status":risk,
 "notes":"Capability evidence is based on verified experience; no numerical ATS score or job-fit percentage assigned until all JD requirements, seniority, education and salary are individually verified."}
