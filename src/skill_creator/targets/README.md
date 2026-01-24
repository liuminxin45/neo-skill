# src/skill_creator/targets

本目录存放各目标平台（target）的输出渲染器。

## 目标平台

- **windsurf.py**：生成 `.windsurf/workflows/<skill>.md`（主目标）。
- **claude.py**：生成 `.claude/skills/<skill>/SKILL.md`（兼容输出）。
- **cursor.py**：生成 `.cursor/commands/<skill>.md`（兼容输出）。
- **github_skills.py**：生成 `.github/skills/<skill>/SKILL.md`（兼容输出）。
- **common.py**：渲染共用逻辑。

## 约定

- 目标平台输出目录属于派生物（generated outputs），不应手工编辑。
