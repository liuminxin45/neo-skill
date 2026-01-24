# Skill Creator 重构后的目录结构

## 完整目录树

```
neo-skill/
├── src/skill_creator/
│   ├── core/                          # Core 层（不变量，不可禁用）
│   │   ├── __init__.py
│   │   ├── types.py                   # 核心数据结构定义
│   │   ├── search.py                  # 多层索引与按需加载
│   │   ├── router.py                  # Router/Tagger
│   │   ├── interview.py               # Interview Engine (Level1/2)
│   │   ├── orchestrator.py            # Plan Orchestrator
│   │   ├── builder.py                 # Skill Builder
│   │   ├── validator.py               # Validator (schema + dry-run)
│   │   └── engine.py                  # 主引擎（整合所有组件）
│   │
│   ├── providers/                     # Providers 层（可插拔增强）
│   │   ├── __init__.py
│   │   ├── base.py                    # Provider 基类
│   │   ├── recipe_provider.py         # Recipe/Blueprint Provider
│   │   ├── tool_catalog_provider.py   # Tool Catalog Provider
│   │   └── checklist_provider.py      # Checklist Provider
│   │
│   ├── cli.py                         # CLI 入口（保留原有功能）
│   └── ...
│
├── .shared/skill-creator/
│   └── data_packs/                    # Data Packs（纯文件资产）
│       │
│       ├── universal/                 # 必需数据包（不可删除）
│       │   ├── questions.level1.json
│       │   ├── schema.skill.json
│       │   ├── output_packs/
│       │   │   ├── index.json
│       │   │   ├── plain_text_message.json
│       │   │   ├── markdown_report.json
│       │   │   ├── json_result.json
│       │   │   ├── code_snippet.json
│       │   │   └── generic.json
│       │   └── minimal_checklists/
│       │       ├── index.json
│       │       ├── automation_basic.json
│       │       ├── web_scraping_basic.json
│       │       └── notification_basic.json
│       │
│       ├── recipes/                   # 可选：蓝图库
│       │   ├── index.json
│       │   └── rss_to_email.json
│       │
│       ├── tools/                     # 可选：库推荐库
│       │   ├── index.json
│       │   ├── feedparser.json
│       │   ├── requests.json
│       │   ├── beautifulsoup4.json
│       │   └── schedule.json
│       │
│       ├── domains/                   # 可选：领域知识（未实现）
│       ├── tasks/                     # 可选：任务模式（未实现）
│       ├── checklists_ext/            # 可选：扩展 checklist（未实现）
│       ├── acceptance_templates/      # 可选：验收模板（未实现）
│       └── profiles/                  # 可选：环境 profile（未实现）
│
├── docs/skill-creator-refactoring/
│   ├── ARCHITECTURE.md                # 架构说明
│   ├── END_TO_END_DEMO.md            # 端到端演示
│   └── DIRECTORY_STRUCTURE.md         # 本文件
│
└── skills/                            # 生成的 skills
    └── rss-feed-email-daily/
        ├── skillspec.json
        ├── references/
        └── scripts/
```

## 数据包文件说明

### universal/ (必需)
- **questions.level1.json**: Level 1 固定问题集（5-7问）
- **schema.skill.json**: Skill 输出的 schema 定义
- **output_packs/**: 输出格式包（5个，必需且不可禁用）
- **minimal_checklists/**: 最小 checklist（3个，必需）

### recipes/ (可选)
- **index.json**: 索引文件（task_types + tags + keywords）
- **rss_to_email.json**: RSS→邮件蓝图（含 workflow_steps + libraries + config_keys）

### tools/ (可选)
- **index.json**: 索引文件
- **{tool}.json**: 库信息（purpose + reason + links + minimal_usage_notes）

## 索引文件格式

所有 index.json 遵循统一格式：

```json
{
  "version": "1.0",
  "description": "...",
  "items": {
    "item_id": {
      "file": "item_file.json",
      "task_types": ["..."],
      "tags": ["..."],
      "keywords": ["..."]
    }
  }
}
```

## 扩展方式

### 添加新 Recipe
1. 在 `recipes/` 下创建 `{recipe_id}.json`
2. 更新 `recipes/index.json`
3. 无需修改代码

### 添加新 Tool
1. 在 `tools/` 下创建 `{tool_id}.json`
2. 更新 `tools/index.json`
3. 无需修改代码

### 添加新 Output Pack
1. 在 `universal/output_packs/` 下创建 `{pack_id}.json`
2. 更新 `universal/output_packs/index.json`
3. 无需修改代码（自动安全降级）
