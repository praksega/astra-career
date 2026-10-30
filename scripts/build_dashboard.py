"""Generate a private, self-contained Astra HTML dashboard from repository JSON records."""
import json, pathlib, html
ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(name, default):
    p=ROOT/"data"/name
    try:return json.loads(p.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):return default
jobs=read("jobs.json",{"jobs":[]}).get("jobs",[])
applications=read("applications.json",{"applications":[]}).get("applications",[])
docs=read("documents.json",{"documents":[]}).get("documents",[])
runs=read("run_history.json",{"runs":[]}).get("runs",[])
def esc(x):return html.escape(str(x or ""),quote=True)
def link(url,label):
    if not isinstance(url,str) or not url.startswith(("https://","http://")):return ""
    return '<a href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">'+esc(label)+'</a>'
cards=[]
for job in sorted(jobs,key=lambda x:x.get("first_shown_date",""),reverse=True):
    jid=job.get("id")
    materials=[d for d in docs if d.get("job_id")==jid]
    links=[]
    for d in materials:
        for key,label in (("resume_docx","Resume DOCX"),("resume_pdf","Resume PDF"),("cover_letter_docx","Letter DOCX"),("cover_letter_pdf","Letter PDF")):
            if d.get(key): links.append(link(d[key],label))
    cards.append('<section class="card"><div class="head"><strong>'+esc(job.get("company"))+' — '+esc(job.get("title"))+'</strong><b>'+esc(job.get("score","?"))+'/100</b></div><p>'+esc(job.get("location",""))+' · '+esc(job.get("application_status","Not applied"))+'</p><p>First shown: '+esc(job.get("first_shown_date","—"))+' · Posted: '+esc(job.get("date_posted","Not verified"))+'</p><div class="links">'+link(job.get("url",""),"Official posting")+' '.join(['']+links)+'</div>'+(('<small>Application materials not yet generated and attached.</small>') if not links else '')+'</section>')
rows=['<tr><td>'+esc(x.get("company"))+'</td><td>'+esc(x.get("title",x.get("job_title","")))+'</td><td>'+esc(x.get("applied_at",x.get("application_date","")) )+'</td><td>'+esc(x.get("status","Applied"))+'</td></tr>' for x in applications]
style="body{font:15px/1.55 system-ui,Arial,sans-serif;margin:0;background:#f6f7fb;color:#151d31}main{max-width:1040px;margin:auto;padding:32px 20px}header{background:#12213c;color:white;padding:30px;border-radius:16px}h1{margin:4px 0}h2{margin-top:30px}.summary{display:flex;gap:16px;flex-wrap:wrap;margin-top:14px}.metric{background:#e3eafa;color:#13294e;border-radius:9px;padding:8px 13px}.card{border:1px solid #e1e5ec;background:white;padding:18px;margin:14px 0;border-radius:13px}.head{display:flex;justify-content:space-between;gap:12px}p{margin:7px 0;color:#4a5566}.links{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}a{color:#1259ad}small{color:#6a7182}table{border-collapse:collapse;width:100%;background:white}td,th{border-bottom:1px solid #e8e8e8;padding:10px;text-align:left}"
document='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Astra Career Dashboard</title><style>'''+style+'''</style></head><body><main><header><small style="color:#b4c6e8">ASTRA CAREER · PRIVATE REPOSITORY SNAPSHOT</small><h1>Career Command Center</h1><div class="summary"><span class="metric">Jobs: '''+str(len(jobs))+'''</span><span class="metric">Confirmed applications: '''+str(len(applications))+'''</span><span class="metric">Research runs: '''+str(len(runs))+'''</span></div></header><h2>Opportunities</h2>'''+(''.join(cards) or '<p>No qualifying jobs recorded yet.</p>')+'''<h2>Submitted applications</h2><table><thead><tr><th>Company</th><th>Role</th><th>Applied</th><th>Stage</th></tr></thead><tbody>'''+(''.join(rows) or '<tr><td colspan="4">No confirmed submitted applications recorded yet.</td></tr>')+'''</tbody></table><p><small>This is a read-only snapshot built from GitHub JSON files. The local Astra app does not automatically sync with this page. Keep the repository private.</small></p></main></body></html>'''
(ROOT/"dashboard.html").write_text(document,encoding="utf-8")
print("Dashboard built:",len(jobs),"jobs,",len(applications),"applications,",len(docs),"document records")
