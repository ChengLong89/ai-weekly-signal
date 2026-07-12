# AI Weekly Signal

一个零服务器成本、每周自动更新的 AI 要闻网站。每周一自动扫描 AI 实验室、研究机构、arXiv 与可靠科技媒体，去重、评分、限制单一来源占比，生成网页与 RSS，并通过 GitHub Issue 通知仓库关注者。

每期保存为 `data/archive/YYYY-Www.json`，网页可直接切换往期。每篇文章关联到当期反馈 Issue 的独立评论；用户在评论上点击 👍 后，下周任务会读取 reaction，为相似主题、类别与来源提供温和加分，并将偏好摘要交给 AI 主编。所有反馈均可审计，不需要额外数据库。

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

## 大模型混合编辑

设置仓库 Secret `OPENAI_API_KEY` 后，大模型会负责中文标题与摘要、分类、重要性排序、“为什么重要”和本周趋势总览。默认模型为 `gpt-5.4-mini`，可通过仓库变量 `OPENAI_MODEL` 覆盖。密钥缺失或调用失败时，系统会自动发布规则筛选版本，不中断周报。
