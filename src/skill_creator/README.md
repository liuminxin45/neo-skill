# src/skill_creator

本目录存放 `skill-creator` 命令对应的 Python 包（核心生成器）。

## 职责

- 读取 `skills/<skill>/skillspec.json`（single source of truth）。
- 生成多目标输出（Windsurf 为主，Claude/Cursor/GitHub 为兼容）。
- 校验 spec 与生成物。
- 打包 Claude `.skill`（zip）。

## 子目录

- **spec/**：SkillSpec 数据模型、渲染入口与校验。
- **targets/**：不同目标平台的渲染器（Windsurf/Claude/Cursor/GitHub）。
- **packaging/**：打包与 zip 工具。
- **util/**：文件、frontmatter 等通用工具。

## 约定

- 生成文件属于派生物，不应作为编辑入口；编辑入口始终是 `skills/` 下的 canonical 文件。
