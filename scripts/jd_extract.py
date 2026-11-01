"""Structured, short JD evidence from public ATS descriptions; full posting stays at employer URL."""
import html,re
from html.parser import HTMLParser
KEY_RESP=("responsib","what you'll do","what you will do","you will","drive ","manage ","lead ","develop ","collaborat","partner with","coordinate","analy","report","process","stakeholder","implement","deliver")
KEY_QUAL=("qualif","requirement","experience","years","proficien","knowledge","skill","bachelor","degree","must have","preferred","expertise","certif")
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.current=[];self.blocks=[]
 def handle_data(self,data):self.current.append(data)
 def handle_endtag(self,tag):
  if tag.lower() in ("p","li","h2","h3","h4"):
   x=html.unescape(" ".join(self.current))
   x=re.sub(r"\\s+"," ",x).strip()
   if x:self.blocks.append(x)
   self.current=[]
def extract(description,source_url):
 p=Parser();p.feed(description or "");parts=p.blocks or re.split(r"(?<=[.!?])\\s+",html.unescape(re.sub(r"<[^>]+>"," ",description or "")))
 parts=[re.sub(r"\\s+"," ",t).strip() for t in parts if len(t.strip())>=30]
 # Only capture brief selective evidence; do not republish the complete copyrighted JD.
 resp=[x[:280] for x in parts if any(k in x.lower() for k in KEY_RESP)][:6]
 quals=[x[:280] for x in parts if any(k in x.lower() for k in KEY_QUAL)][:6]
 return {"source_url":source_url,"full_description_available":len(description or "")>450,"responsibilities":resp,"qualifications":quals,"overview":(parts[0][:320] if parts else ""),"extraction_method":"keyword_selected_source_paragraphs","warning":"Summarized excerpts only; consult original employer JD for complete mandatory requirements."}
