# Recipes（蓝图库）

可选增强数据包，提供成熟方案骨架。

## 当前 Recipes

### rss_to_email
抓取 RSS/Atom feed 并发送邮件通知的成熟方案。

**适用场景**:
- task_types: rss_monitoring, notification, scheduled_task
- tags: rss, email_smtp, scheduler_local

**包含内容**:
- 4 步 workflow（fetch_feed → filter_new → format_email → send_email）
- 推荐库栈（feedparser, smtplib, schedule）
- 配置键（feed_url, email_to, smtp_server 等）
- 验收模板（3条）
- 假设和风险清单

## Recipe 文件结构

```json
{
  "id": "recipe_id",
  "name": "Recipe Name",
  "description": "...",
  "task_types": ["..."],
  "tags": ["..."],
  "workflow_steps": [...],
  "recommended_libraries": [...],
  "config_keys": [...],
  "acceptance_template": [...],
  "assumptions": [...],
  "risks": [...]
}
```

## 添加新 Recipe

1. 创建 `{recipe_id}.json` 文件
2. 更新 `index.json`，添加索引条目：
   ```json
   {
     "recipe_id": {
       "file": "recipe_id.json",
       "task_types": ["..."],
       "tags": ["..."],
       "keywords": ["..."]
     }
   }
   ```
3. 无需修改代码，系统会自动检索

## 设计原则

- **成熟验证**: 只添加经过验证的方案
- **完整性**: 包含完整的 workflow + libraries + config
- **可选性**: Recipe 缺失时安全降级为 generic recipe
