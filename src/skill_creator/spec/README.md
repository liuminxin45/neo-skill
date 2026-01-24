# src/skill_creator/spec

本目录存放 SkillSpec 的“模型 + 渲染编排 + 校验”。

## 包含内容

- **model.py**：SkillSpec 数据模型与加载逻辑。
- **render.py**：将 spec 分发到不同 target 渲染器，并负责资源复制策略。
- **validate.py**：spec 与输出的校验规则（含 Claude frontmatter 严格模式）。

## 约定

- `skills/<skill>/skillspec.json` 是唯一真源；渲染器只消费 spec，不反向修改。
