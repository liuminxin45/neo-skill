# Data Packs

数据包目录，包含 skill-creator 的所有数据资源。

## 目录结构

```
data_packs/
├── universal/          # 必需数据包（不可删除）
│   ├── questions.level1.json
│   ├── schema.skill.json
│   ├── output_packs/
│   └── minimal_checklists/
├── recipes/            # 可选：蓝图库
├── tools/              # 可选：库推荐库
├── domains/            # 可选：领域知识（待扩展）
├── tasks/              # 可选：任务模式（待扩展）
├── checklists_ext/     # 可选：扩展 checklist（待扩展）
├── acceptance_templates/  # 可选：验收模板（待扩展）
└── profiles/           # 可选：环境 profile（待扩展）
```

## 数据包说明

### universal/（必需）
核心数据包，包含：
- **questions.level1.json**: Level 1 固定问题集（5-7问）
- **schema.skill.json**: Skill 输出的 schema 定义
- **output_packs/**: 5 个输出格式包（plain_text_message, markdown_report, json_result, code_snippet, generic）
- **minimal_checklists/**: 3 个基本 checklist（automation_basic, web_scraping_basic, notification_basic）

### recipes/（可选）
成熟方案蓝图库，每个 recipe 包含：
- workflow_steps: 步骤序列
- recommended_libraries: 推荐库栈
- config_keys: 配置键
- acceptance_template: 验收模板

### tools/（可选）
第三方库推荐库，每个 tool 包含：
- purpose: 用途说明
- reason: 推荐理由
- pypi_link + docs_link: 文档链接
- minimal_usage_notes: 最小使用说明（10-20行）

## 扩展方式

### 添加新 Recipe
1. 在 `recipes/` 下创建 `{recipe_id}.json`
2. 更新 `recipes/index.json`
3. 无需修改代码

### 添加新 Tool
1. 在 `tools/` 下创建 `{tool_id}.json`
2. 更新 `tools/index.json`
3. 无需修改代码

## 索引文件格式

所有 `index.json` 遵循统一格式：

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

## 相关文档

- [重构设计文档](../../../docs/skill-creator-refactoring/README.md)
- [端到端演示](../../../docs/skill-creator-refactoring/END_TO_END_DEMO.md)
