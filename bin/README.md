# bin

本目录存放 Node.js 命令行入口（thin wrapper）。

## 包含内容

- **omni-skill.js**：启动 `python -m omni_skill.cli`，负责初始化/同步/生成技能输出。
- **skill-creator.js**：启动 `python -m skill_creator.cli`，负责生成/校验/打包技能。

## 约定

- 这里仅做启动与环境变量拼装（例如 `PYTHONPATH`），不承载核心业务逻辑。
- 核心实现应位于 `src/` 的 Python 包中。
