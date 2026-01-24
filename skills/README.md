# skills

本目录存放技能的 canonical 定义（可编辑的单一真源）。

## 结构

- `skills/<skill>/skillspec.json`：技能规格（唯一真源）。
- `skills/<skill>/references/**`：引用资料、规则说明、长文档（用于降低主文档上下文占用）。
- `skills/<skill>/scripts/**`：确定性脚本（可选）。
- `skills/<skill>/assets/**`：数据与资源（可选）。

## 约定

- 生成物（如 `.windsurf/.claude/.cursor/.github/skills`）不是编辑入口。
- 每个 skill 名称应为 kebab-case，并与目录名保持一致。
