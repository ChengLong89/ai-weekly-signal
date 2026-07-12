"""Collect, rank and publish the week's AI news. Runs unattended in GitHub Actions."""
from __future__ import annotations
import json, os, re, hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import feedparser, requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
NOW=datetime.now(timezone.utc); CUTOFF=NOW-timedelta(days=8)
FEEDS=[
 ("OpenAI","https://openai.com/news/rss.xml",10),("Google DeepMind","https://deepmind.google/blog/rss.xml",10),
 ("Anthropic","https://www.anthropic.com/rss.xml",10),("Google AI","https://blog.google/technology/ai/rss/",9),
 ("Microsoft Research","https://www.microsoft.com/en-us/research/feed/",8),("Hugging Face","https://huggingface.co/blog/feed.xml",8),
 ("MIT AI News","https://news.mit.edu/rss/topic/artificial-intelligence2",8),("TechCrunch AI","https://techcrunch.com/category/artificial-intelligence/feed/",6),
 ("VentureBeat AI","https://venturebeat.com/category/ai/feed/",5),("arXiv AI","https://export.arxiv.org/rss/cs.AI",7),
 ("arXiv ML","https://export.arxiv.org/rss/cs.LG",7),("arXiv CL","https://export.arxiv.org/rss/cs.CL",7)]
KEYWORDS={"model":("model","模型","gpt","claude","gemini","llama","parameter"),"training":("train","learning method","distillation","alignment","rlhf","optimization","训练"),"research":("paper","research","benchmark","arxiv","论文","study"),"product":("launch","release","available","agent","api","product"),"policy":("policy","regulation","funding","acquisition","law","safety")}
IMPACT=("new model","state-of-the-art","sota","open source","reasoning","multimodal","agent","breakthrough","training","safety","benchmark","released")
def clean_url(u):
 p=urlsplit(u); return urlunsplit((p.scheme,p.netloc,p.path,"",""))
def text(v): return BeautifulSoup(v or "","html.parser").get_text(" ",strip=True)
def parsed_date(e):
 t=e.get("published_parsed") or e.get("updated_parsed")
 return datetime(*t[:6],tzinfo=timezone.utc) if t else NOW
def category(s):
 s=s.lower(); scores={k:sum(w in s for w in ws) for k,ws in KEYWORDS.items()}; return max(scores,key=scores.get) if max(scores.values()) else "other"
def summarize(raw,limit=240):
 s=re.sub(r"\s+"," ",text(raw)); parts=re.split(r"(?<=[.!?。！？])\s+",s); out=""
 for p in parts:
  if len(out)+len(p)>limit: break
  out+=(" " if out else "")+p
 return out or s[:limit]
def why(cat, source):
 reasons={"model":"它可能改变当前模型能力边界、使用成本或开发者的技术选择。","training":"它提供了可能提升效率、稳定性或能力的新训练路径。","research":"它为后续研究提供了新证据、评测方法或可复现的技术方向。","product":"它把 AI 能力推向实际工作流，可能改变产品体验与市场格局。","policy":"它可能影响 AI 的投资、治理、开放程度或商业化节奏。","other":"它反映了本周值得持续追踪的 AI 行业信号。"}
 return f"{reasons.get(cat,reasons['other'])} 信息来自 {source}，可由原文核验。"
def collect():
 rows=[]
 headers={"User-Agent":"AIWeeklySignal/1.0 (+GitHub Pages weekly digest)"}
 for source,url,authority in FEEDS:
  try:
   body=requests.get(url,headers=headers,timeout=25).content; feed=feedparser.parse(body)
   for e in feed.entries[:35]:
    dt=parsed_date(e)
    if dt<CUTOFF: continue
    title=text(e.get("title")); raw=e.get("summary") or e.get("description") or ""; combined=f"{title} {text(raw)}".lower()
    relevance=sum(k in combined for k in ("ai","artificial intelligence","machine learning","model","llm","neural","robot"))
    if not relevance and "arxiv" not in source.lower(): continue
    score=min(99,45+authority*3+min(15,sum(k in combined for k in IMPACT)*3)+min(8,relevance*2))
    cat=category(combined)
    rows.append({"id":hashlib.sha1(clean_url(e.link).encode()).hexdigest()[:12],"title":title,"summary":summarize(raw),"why_it_matters":why(cat,source),"source":source,"date":dt.date().isoformat(),"url":clean_url(e.link),"category":cat,"score":score})
  except Exception as ex: print(f"WARN {source}: {ex}")
 dedup={};
 for r in rows:
  key=re.sub(r"\W+","",r["title"].lower())[:70]
  if key not in dedup or r["score"]>dedup[key]["score"]: dedup[key]=r
 ranked=sorted(dedup.values(),key=lambda x:(x["score"],x["date"]),reverse=True)
 selected=[]; source_counts={}
 for item in ranked:
  if source_counts.get(item["source"],0)>=3: continue
  selected.append(item); source_counts[item["source"]]=source_counts.get(item["source"],0)+1
  if len(selected)==16: break
 return selected
def main():
 items=collect(); data={"generated_at":NOW.isoformat(),"week_label":f"{NOW.year} · 第 {NOW.isocalendar().week} 周","sources_scanned":len(FEEDS),"items":items}
 (ROOT/"data").mkdir(exist_ok=True); (ROOT/"data/latest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
 rss=['<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>AI Weekly Signal</title><link>https://github.com/</link><description>每周 AI 要闻</description>']
 for x in items: rss.append(f'<item><title><![CDATA[{x["title"]}]]></title><link>{x["url"]}</link><description><![CDATA[{x["summary"]}]]></description><pubDate>{x["date"]}</pubDate></item>')
 rss.append("</channel></rss>"); (ROOT/"feed.xml").write_text("".join(rss),encoding="utf-8")
 print(f"Published {len(items)} items")
if __name__=="__main__": main()
