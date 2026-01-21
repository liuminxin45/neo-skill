deterministic scripts（给 assistant/CI 调用）。

- generate.py：从 skills/<skill>/skillspec.json 生成多端输出
- validate.py：校验 skillspec.json + 生成产物（Claude frontmatter strict 等）
- package.py：打包 Claude .skill 或 repo zip
