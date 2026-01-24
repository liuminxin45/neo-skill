# src

本目录存放 Python 源码（项目核心实现）。

## 包含内容

- **omni_skill/**：`omni-skill` 命令实现（初始化/同步/批量生成）。
- **skill_creator/**：`skill-creator` 命令实现（spec 校验、渲染输出、打包）。

## 约定

- `pyproject.toml` 使用 `package-dir = {"" = "src"}`，因此该目录是 Python 包的根。
- CLI 入口通过 `python -m <module>` 方式运行，避免额外打包步骤。
