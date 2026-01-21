# skill-creator

对话式收集需求（最多 10 个关键问题），生成可在 Claude/Windsurf/Cursor/GitHub Skills 等多 AI Assistant 运行的技能包（SKILL.md + references/scripts/assets），并输出 Claude .skill 打包文件。

## When to use
- 我想做一个 skill（Claude/Windsurf/Cursor 都能用）
- 帮我生成 SKILL.md
- 把我的 prompt 工作流变成 skill
- 帮我在已有 skill 的基础上补充/重构 workflow steps
- 做一个 skill 库/skill creator
- 打包成 Claude .skill

## Command
Run these deterministic steps in the repository:
```bash
python3 .shared/skill-creator/scripts/generate.py skills/<skill>/skillspec.json
python3 .shared/skill-creator/scripts/validate.py skills/<skill>/skillspec.json
python3 .shared/skill-creator/scripts/package.py --target claude --skill <skill>
```

## Workflow
Mode: `sequential`

### 1. 对话式收集需求（<=10 问）
### 2. 落地 SkillSpec（单一真源）
### 3. 对话式补充/重构 workflow steps（归类/增删/合并）
### 4. 生成多 Assistant 入口文件
```bash
python3 .shared/skill-creator/scripts/generate.py skills/<skill>/skillspec.json
```
### 5. 校验（spec + Claude frontmatter strict + 目录噪声）
```bash
python3 .shared/skill-creator/scripts/validate.py skills/<skill>/skillspec.json
```
### 6. 打包分发（Claude .skill + 仓库 zip）
```bash
python3 .shared/skill-creator/scripts/package.py --target claude --skill <skill>
python3 .shared/skill-creator/scripts/package.py --target repo
```