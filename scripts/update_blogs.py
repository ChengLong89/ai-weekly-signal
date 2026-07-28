"""Refresh the curated AI blog radar from first-party RSS/Atom feeds."""
from __future__ import annotations
import json, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import feedparser, requests

ROOT=Path(__file__).resolve().parents[1]; NOW=datetime.now(timezone.utc); CUTOFF=NOW-timedelta(days=7)
def entry_date(entry):
 value=entry.get("published_parsed") or entry.get("updated_parsed")
 return datetime(*value[:6],tzinfo=timezone.utc) if value else None
def main():
 sources=json.loads((ROOT/"data/blog_sources.json").read_text(encoding="utf-8")); output=[]
 headers={"User-Agent":"AIWeeklySignal/1.0 (+https://github.com/ChengLong89/ai-weekly-signal)"}
 for source in sources:
  item=source.copy(); item.update({"status":"unavailable","posts_this_week":0,"latest_title":"","latest_url":source["url"],"latest_date":None})
  try:
   response=requests.get(source["feed"],headers=headers,timeout=25); response.raise_for_status(); feed=feedparser.parse(response.content)
   posts=[]
   for entry in feed.entries:
    dt=entry_date(entry)
    if dt: posts.append((dt,entry))
   posts.sort(key=lambda x:x[0],reverse=True)
   if posts:
    dt,entry=posts[0]; item.update({"latest_title":entry.get("title","最新文章"),"latest_url":entry.get("link",source["url"]),"latest_date":dt.date().isoformat(),"posts_this_week":sum(d>=CUTOFF for d,_ in posts),"status":"updated" if dt>=CUTOFF else "quiet"})
   else: item["status"]="unknown"
  except Exception as ex: item["error"]=type(ex).__name__; print(f"WARN {source['name']}: {ex}")
  output.append(item); time.sleep(.1)
 output.sort(key=lambda x:(x["status"]=="updated",x["posts_this_week"],x["quality"]),reverse=True)
 data={"generated_at":NOW.isoformat(),"window_days":7,"updated_count":sum(x["status"]=="updated" for x in output),"blogs":output}
 (ROOT/"data/blogs.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8"); print(f"Blog radar: {data['updated_count']}/{len(output)} updated")
if __name__=="__main__": main()
