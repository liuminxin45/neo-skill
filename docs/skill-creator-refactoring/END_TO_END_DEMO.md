# 端到端演示：RSS 抓取 + 邮件通知

## 场景描述

用户需求：**"每天抓取一个 RSS feed 并发送邮件通知"**

## 完整对话流程

### Step 1: Router/Tagger 分析

```python
from skill_creator.core.engine import SkillCreatorEngine
from pathlib import Path

engine = SkillCreatorEngine(Path(".shared/skill-creator/data_packs"))
ctx = engine.create_skill("每天抓取一个 RSS feed 并发送邮件通知")

# 输出:
# task_type: "rss_monitoring"
# capability_tags: ["rss", "email_smtp", "scheduler_local"]
```

### Step 2: Level 1 提问（固定 5-7 问）

**系统展示 Level 1 问题：**

---

**1. 这个 skill 的一句话目标是什么（动词开头，面向可重复任务）？** (必答)

**用户回答**: 每天抓取指定 RSS feed 的新文章并通过邮件发送摘要

---

**2. 需要哪些输入（URL/文件/配置等），从哪里来？请至少给 1 个示例。** (必答)

**用户回答**: 
- RSS feed URL: https://example.com/blog/feed.xml
- 收件人邮箱: user@example.com
- SMTP 配置: smtp.gmail.com

---

**3. 期望输出是什么形态？** (必答)
  - ✓ A. 纯文本消息（邮件/IM）（推荐：是，原因：最简单，适合通知类任务）
  - B. Markdown 报告
  - C. JSON 结果
  - D. 代码片段/脚本
  - E. 其他（请说明）

**用户回答**: A

---

**4. 运行环境有哪些约束（本地/CI/联网/权限/代理等）？** (选答) (默认: 本地环境，可联网)

**用户回答**: 本地环境，可联网，需要 SMTP 凭证

---

**5. 硬约束有哪些（频率/合规/不可做的事）？** (选答) (默认: 无特殊约束)

**用户回答**: 每天执行一次，不要重复发送已发送的文章

---

**6. 请提供至少 2 条验收用例（必须包含'无数据'或'失败'场景之一）** (必答)

**用户回答**:
1. feed 有 3 篇新文章时，成功发送包含 3 篇文章摘要的邮件
2. feed 无新文章时，不发送邮件
3. feed 抓取失败时，记录错误日志但不崩溃

---

### Step 3: Gap Scoring

```python
# 系统自动评分
gap_score = engine.interview_engine.score_gaps(ctx.interview_state)

# 结果:
# gaps: []  # 无主要缺口
# should_continue_level2: False
# stop_reason: "满足生成阈值：output 可模板化，acceptance ≥ 2，无矛盾约束"
```

**无需 Level 2 提问，直接进入生成阶段。**

---

### Step 4: Providers 推荐

系统并行调用 Providers：

#### Recipe Provider
```json
{
  "provider_name": "recipe",
  "items": [{
    "id": "rss_to_email",
    "name": "RSS Feed to Email",
    "confidence": 0.95
  }],
  "trace": {
    "search_result": {
      "candidates_count": 1,
      "top_score": 19,
      "loaded_files": [".shared/skill-creator/data_packs/recipes/rss_to_email.json"]
    }
  }
}
```

#### Tool Catalog Provider
```json
{
  "provider_name": "tools",
  "items": [
    {
      "id": "feedparser",
      "name": "feedparser",
      "purpose": "解析 RSS/Atom feed",
      "pypi_link": "https://pypi.org/project/feedparser/",
      "docs_link": "https://feedparser.readthedocs.io/"
    },
    {
      "id": "schedule",
      "name": "schedule",
      "purpose": "简单的任务调度"
    }
  ],
  "confidence": 0.87
}
```

#### Checklist Provider
```json
{
  "provider_name": "checklists",
  "items": [
    {"id": "automation_basic"},
    {"id": "web_scraping_basic"},
    {"id": "notification_basic"}
  ],
  "confidence": 1.0
}
```

---

### Step 5: Plan 生成并展示

**系统展示 Implementation Plan：**

```markdown
# Implementation Plan

## 方案概述

**目标**: 每天抓取指定 RSS feed 的新文章并通过邮件发送摘要

**方案**: 采用成熟蓝图 `rss_to_email`，包含经过验证的步骤序列和配置模板。

**输出形式**: 纯文本消息（适合邮件/IM 通知）

## Output Pack: `plain_text_message`

## 蓝图: `rss_to_email`

## 推荐库栈

### feedparser
- **用途**: 解析 RSS/Atom feed
- **理由**: 成熟稳定，支持多种 feed 格式，自动处理编码和格式差异
- **PyPI**: https://pypi.org/project/feedparser/
- **文档**: https://feedparser.readthedocs.io/
- **Fallback**: 使用 requests + xml.etree.ElementTree 手动解析 XML

### smtplib
- **用途**: 发送邮件
- **理由**: Python 内置库，无需额外依赖
- **PyPI**: https://docs.python.org/3/library/smtplib.html
- **文档**: https://docs.python.org/3/library/smtplib.html

### schedule
- **用途**: 简单的任务调度
- **理由**: 轻量级，API 简洁，适合简单的定时任务
- **PyPI**: https://pypi.org/project/schedule/
- **文档**: https://schedule.readthedocs.io/
- **Fallback**: 使用系统 cron (Linux/Mac) 或 Task Scheduler (Windows)

## 假设
- 假设可以联网访问外部资源
- 假设在本地环境运行，可以读写文件
- 假设有可用的 SMTP 服务器和凭证
- 假设可以长期运行或由系统调度器触发
- 假设输入源稳定可访问: https://example.com/blog/feed.xml

## 风险
- 网络请求可能超时或失败
- 目标网站结构变化可能导致解析失败
- SMTP 凭证可能过期或被封禁
- 进程意外退出会导致调度停止

## 应用的 Checklist
- automation_basic
- web_scraping_basic
- notification_basic

---
**如无异议，将继续生成 skill。如需调整库栈或禁用某项，请告知。**
```

**用户**: （无异议，默认继续）

---

### Step 6: Skill 生成

```python
# 系统生成 SkillDraft
skill_draft = engine.skill_builder.build_skill(ctx, ctx.plan)
```

**生成的 Skill：**

```json
{
  "name": "rss-feed-email-daily",
  "description": "每天抓取指定 RSS feed 的新文章并通过邮件发送摘要。约束: 每天执行一次，不要重复发送已发送的文章",
  "triggers": [
    "每天抓取指定 RSS feed 的新文章并通过邮件发送摘要",
    "帮我每天抓取指定 RSS feed 的新文章并通过邮件发送摘要",
    "自动每天抓取指定 RSS feed 的新文章并通过邮件发送摘要",
    "抓取 RSS",
    "监控 feed"
  ],
  "output_pack": "plain_text_message",
  "workflow_steps": [
    {
      "id": "fetch_feed",
      "title": "抓取 RSS Feed",
      "kind": "action",
      "commands": [],
      "notes": "使用 feedparser 解析 RSS/Atom feed。处理网络超时、解析错误、空 feed 等情况"
    },
    {
      "id": "filter_new",
      "title": "过滤新条目",
      "kind": "action",
      "commands": [],
      "notes": "与上次抓取结果对比，找出新条目。需要持久化上次抓取的条目 ID 或时间戳"
    },
    {
      "id": "format_email",
      "title": "格式化邮件内容",
      "kind": "action",
      "commands": [],
      "notes": "将新条目格式化为邮件正文。包含标题、链接、摘要、发布时间"
    },
    {
      "id": "send_email",
      "title": "发送邮件",
      "kind": "action",
      "commands": [],
      "notes": "通过 SMTP 发送邮件。处理发送失败、凭证错误等情况"
    }
  ],
  "applied_recipe": "rss_to_email",
  "applied_checklists": ["automation_basic", "web_scraping_basic", "notification_basic"],
  "libraries_used": ["feedparser", "smtplib", "schedule"]
}
```

---

### Step 7: 校验（Schema + Dry-run）

```python
validation_result = engine.validator.validate(ctx, skill_draft)
```

**校验结果：**

```
=== Dry-run 仿真 ===

✓ 验收用例: 3 条
✓ 包含失败/无数据场景
✓ workflow steps: 4 个

模拟执行验收用例:
  1. feed 有 3 篇新文章时，成功发送包含 3 篇文章摘要的邮件
     → 预期可通过 workflow 实现
  2. feed 无新文章时，不发送邮件
     → 预期可通过 workflow 实现
  3. feed 抓取失败时，记录错误日志但不崩溃
     → 预期可通过 workflow 实现

✓ 校验通过
```

---

### Step 8: 最终产物

**生成的 Skill 文件结构：**

```
skills/rss-feed-email-daily/
├── skillspec.json          # 完整的 skill 定义
├── references/
│   ├── config-template.md  # 配置模板（feed_url, email_to, smtp_server 等）
│   └── checklists.md       # 应用的 checklist 详情
└── scripts/
    └── rss_monitor.py      # 实现脚本（基于 feedparser + smtplib + schedule）
```

**skillspec.json 内容：**
```json
{
  "version": 1,
  "name": "rss-feed-email-daily",
  "description": "每天抓取指定 RSS feed 的新文章并通过邮件发送摘要。约束: 每天执行一次，不要重复发送已发送的文章",
  "triggers": [...],
  "workflow": {
    "type": "sequential",
    "steps": [...]
  },
  "output_pack": "plain_text_message",
  "libraries": ["feedparser", "smtplib", "schedule"],
  "references": ["references/config-template.md", "references/checklists.md"],
  "scripts": ["scripts/rss_monitor.py"]
}
```

---

## Doctor Trace 示例

```bash
python -m skill_creator.doctor --context-id abc123
```

**输出：**

```markdown
# Skill Creator Doctor Report

## 1. Routing
- **User Request**: 每天抓取一个 RSS feed 并发送邮件通知
- **Task Type**: rss_monitoring
- **Capability Tags**: rss, email_smtp, scheduler_local

## 2. Interview
- **Level 1 Questions**: 6 个
- **Gap Scoring**: 0 个缺口 (0 个主要)
- **Continue Level 2**: False

## 3. Providers Recommendations

### Recipe
- **Items**: 1
- **Confidence**: 0.95
- **Trace**: {'search_result': {'candidates_count': 1, 'top_score': 19, 'loaded_files': ['.shared/skill-creator/data_packs/recipes/rss_to_email.json']}}

### Tools
- **Items**: 3
- **Confidence**: 0.87
- **Trace**: {'search_result': {'candidates_count': 3, 'loaded_files': ['...feedparser.json', '...schedule.json']}}

### Checklists
- **Items**: 3
- **Confidence**: 1.00
- **Trace**: {'minimal_checklists_count': 3, 'extended_checklists_count': 0}

## 4. Plan
- **Output Pack**: plain_text_message
- **Recipe**: rss_to_email
- **Libraries**: 3
  - feedparser: 解析 RSS/Atom feed
  - smtplib: 发送邮件
  - schedule: 简单的任务调度
- **Checklists**: automation_basic, web_scraping_basic, notification_basic

## 5. Skill Draft
- **Name**: rss-feed-email-daily
- **Triggers**: 5
- **Workflow Steps**: 4

## 6. Validation
- **Passed**: True
- **Issues**: 0

## 7. Full Trace
```json
{
  "routing": {
    "task_type": "rss_monitoring",
    "capability_tags": ["rss", "email_smtp", "scheduler_local"]
  },
  "level1_questions": {
    "count": 6,
    "questions": [...]
  },
  "gap_scoring": {
    "should_continue_level2": false,
    "gaps_count": 0,
    "major_gaps": 0
  },
  "provider_recipe": {
    "items_count": 1,
    "confidence": 0.95
  },
  "provider_tools": {
    "items_count": 3,
    "confidence": 0.87
  },
  "provider_checklists": {
    "items_count": 3,
    "confidence": 1.0
  },
  "plan_generation": {
    "output_pack": "plain_text_message",
    "recipe_id": "rss_to_email",
    "libraries_count": 3,
    "checklists_count": 3
  },
  "skill_building": {
    "name": "rss-feed-email-daily",
    "workflow_steps_count": 4,
    "triggers_count": 5
  },
  "validation": {
    "passed": true,
    "issues_count": 0,
    "errors_count": 0,
    "warnings_count": 0
  }
}
```
```

---

## 关键特性展示

### ✓ Two-Level Interview
- Level 1: 6 个固定问题，覆盖核心槽位
- Gap Scoring: 自动评估是否需要 Level 2
- 本例无缺口，直接进入生成

### ✓ Output Packs（不可禁用）
- 自动选择 `plain_text_message` pack
- 基于用户选择 "A. 纯文本消息"

### ✓ Providers（可插拔，安全降级）
- Recipe Provider: 命中 `rss_to_email` 蓝图（confidence 0.95）
- Tool Catalog: 推荐 3 个库（含链接和用途说明）
- Checklist Provider: 应用 3 个基本 checklist

### ✓ Plan 阶段（不可禁用）
- 展示方案、库栈、假设、风险
- 用户不反对则默认继续（无需显式确认）

### ✓ Schema + Dry-run（不可禁用）
- 校验字段完整性、kebab-case、triggers 数量
- 用验收用例仿真工作流
- 通过后产出最终 skill

### ✓ 多层索引 + 按需加载
- 只加载命中的 recipe/tools 文件（3 个文件）
- 未加载整个模板库（避免 token 膨胀）

### ✓ Doctor/Debug
- 完整 trace：路由 → 提问 → 推荐 → Plan → 生成 → 校验
- 可追溯每个决策的依据和加载的文件
