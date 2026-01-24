# src/omni_skill

本目录存放 `omni-skill` 命令对应的 Python 模块。

## 职责

- 将本仓库作为“技能初始化器”：把 `skills/`（canonical）及必要的生成/辅助目录同步到目标工作目录。
- 支持按 AI 助手类型选择性同步（例如 `claude`/`windsurf`/`cursor` 等）。

## 约定

- 同步规则与生成行为应保持确定性（同输入得到同输出）。
