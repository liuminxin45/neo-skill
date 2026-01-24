# .shared/skill-creator/scripts

本目录存放 `skill-creator` 的确定性工具脚本。

## 包含内容

- **search.py**：基于 `.shared/skill-creator/data` 的多域检索与推荐。
- **generate.py**：从 `skills/<skill>/skillspec.json` 生成各 target 输出。
- **validate.py**：校验 spec 与生成输出（含 Claude 严格 frontmatter）。
- **package.py**：打包 Claude `.skill` 或仓库 zip。

## 约定

- 脚本应可直接运行（`python3 ...`），并尽量避免非确定性行为。
- 输入输出路径应清晰，并与仓库目录规范一致。
