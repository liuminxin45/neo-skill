---
description: 对话式收集需求（最多 10 个关键问题），生成可在 Claude/Windsurf/Cursor/GitHub Skills 等多 AI Assistant 运行的技能包（SKILL.md + references/scripts/assets），并输出 Claude .skill 打包文件。
auto_execution_mode: 3
---

# skill-creator

Role: skill generator.

Non-negotiable:
- Follow the canonical SkillSpec at skills/<skill>/skillspec.json
- Generate Claude/Windsurf/Cursor/GitHub Skills outputs
- Run validation before packaging
- Use index-style workflow steps: keep steps short and store detailed rules/templates in references/ or assets/ (knowledge base)

## Triggers
- 我想做一个 skill（Claude/Windsurf/Cursor 都能用）
- 帮我生成 SKILL.md
- 把我的 prompt 工作流变成 skill
- 帮我在已有 skill 的基础上补充/重构 workflow steps
- 做一个 skill 库/skill creator
- 打包成 Claude .skill

## Workflow
Mode: `sequential`

### Step 1 — 对话式收集需求（<=10 问）
只问缺失信息；最多 10 个问题；问完就进入生成阶段。

### Step 2 — 落地 SkillSpec（单一真源）
把收集到的信息写入 skills/<name>/skillspec.json；确定 references/scripts/assets 需要哪些内容（progressive disclosure）。

### Step 3 — 对话式补充/重构 workflow steps（归类/增删/合并）
当目标是‘更新已有 skill’时：先读取现有 skills/<skill>/skillspec.json，提取现有 workflow.steps 与每步意图；再把用户新增需求归类到已有 step（必要时新增 step）；允许删除或合并 step（必须给出理由与安全检查）；最后输出一个可落盘的变更摘要 + 最终 workflow.steps。协议与输出模板见 `skills/skill-creator/references/workflow-step-editing.md`。

### Step 4 — 生成多 Assistant 入口文件
输出：.claude/.windsurf/.cursor/.github 对应入口 + resources 拷贝。
```bash
python3 .shared/skill-creator/scripts/generate.py skills/<skill>/skillspec.json
```

### Step 5 — 校验（spec + Claude frontmatter strict + 目录噪声）
Claude strict：frontmatter 仅允许 name/description；skill bundle 内禁止 README/CHANGELOG 等无关文档。
```bash
python3 .shared/skill-creator/scripts/validate.py skills/<skill>/skillspec.json
```

### Step 6 — 打包分发（Claude .skill + 仓库 zip）
Claude：zip 根是 skill 文件夹；仓库 zip 便于直接丢进 IDE。
```bash
python3 .shared/skill-creator/scripts/package.py --target claude --skill <skill>
python3 .shared/skill-creator/scripts/package.py --target repo
```

## Deterministic tools
```bash
# Generate outputs for all targets
python3 .shared/skill-creator/scripts/generate.py skills/<skill>/skillspec.json
# Validate outputs
python3 .shared/skill-creator/scripts/validate.py skills/<skill>/skillspec.json
# Package Claude .skill
python3 .shared/skill-creator/scripts/package.py --target claude --skill <skill>
```