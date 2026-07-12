"""Create one GitHub feedback issue per edition and attach per-article reaction links."""
import json, os, re
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]; token=os.environ["GITHUB_TOKEN"]; repo=os.environ["GITHUB_REPOSITORY"]
headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"}; api=f"https://api.github.com/repos/{repo}"
def call(method,path,**kwargs):
 r=requests.request(method,api+path,headers=headers,timeout=30,**kwargs); r.raise_for_status(); return r.json() if r.content else {}
def main():
 latest_path=ROOT/"data/latest.json"; data=json.loads(latest_path.read_text(encoding="utf-8")); week=data["week_id"]
 try: call("POST","/labels",json={"name":"ai-weekly-feedback","color":"d8ff3e","description":"AI 周报点赞反馈"})
 except requests.HTTPError as ex:
  if ex.response.status_code!=422: raise
 issues=call("GET","/issues",params={"labels":"ai-weekly-feedback","state":"all","per_page":100})
 issue=next((x for x in issues if f"<!-- week-id:{week} -->" in (x.get("body") or "")),None)
 if not issue:
  body=f"<!-- week-id:{week} -->\n本期周报已经发布： https://{repo.split('/')[0]}.github.io/{repo.split('/')[1]}/\n\n请在喜欢的文章评论下点击 👍。下周选稿会温和参考这些反馈，同时继续保留重大新闻。"
  issue=call("POST","/issues",json={"title":f"AI 周报 · {data['week_label']} · 点赞区","body":body,"labels":["ai-weekly-feedback"]})
 comments=call("GET",f"/issues/{issue['number']}/comments",params={"per_page":100}); by_id={}
 for c in comments:
  m=re.search(r"article-id:([0-9a-f]{12})",c.get("body",""))
  if m: by_id[m.group(1)]=c
 for n,item in enumerate(data["items"],1):
  c=by_id.get(item["id"])
  if not c:
   body=f"<!-- article-id:{item['id']} -->\n### {n}. {item['title']}\n\n{item['summary']}\n\n来源：[{item['source']}]({item['url']})\n\n**喜欢这类内容？请点击本评论的 👍 reaction。**"
   c=call("POST",f"/issues/{issue['number']}/comments",json={"body":body})
  item["like_url"]=c["html_url"]; item["likes"]=c.get("reactions",{}).get("+1",0)
 for path in (latest_path,ROOT/"data/archive"/f"{week}.json"):
  path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
 print(f"Feedback issue #{issue['number']} linked to {len(data['items'])} articles")
if __name__=="__main__": main()
