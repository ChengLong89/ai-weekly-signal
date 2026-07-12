# AI Weekly Signal

一个零服务器成本、每周自动更新的 AI 要闻网站。每周一自动扫描 AI 实验室、研究机构、arXiv 与可靠科技媒体，去重、评分、限制单一来源占比，生成网页与 RSS，并通过 GitHub Issue 通知仓库关注者。

## 自动化

- 时间：每周一 15:15 UTC（北京时间周一 23:15；太平洋时间周一早晨）
- 手动更新：在 Actions 中运行 `Weekly AI briefing`
- 通知：自动创建一条 GitHub Issue；关注仓库并开启 Issues 通知即可收到邮件/手机推送
- 部署：仓库 Settings → Pages → Source 选择 `GitHub Actions`

## 本地更新

```bash
pip install -r requirements.txt
python scripts/update_news.py
python -m http.server 8000
```

访问 http://localhost:8000 。信源与权重可在 `scripts/update_news.py` 中调整。

## 可选：更高质量的中文摘要

当前版本完全免费，使用来源原摘要并给出结构化影响判断。后续可添加模型 API，在 GitHub Secrets 中保存密钥，由模型输出更自然的中文摘要、跨来源合并和趋势分析。
