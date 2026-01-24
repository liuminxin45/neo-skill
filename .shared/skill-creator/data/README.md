# .shared/skill-creator/data

本目录存放 `skill-creator` 使用的结构化数据索引。

## 文件类型

- **domains.json**：定义 domain/stack 到数据文件的映射与描述。
- **\*.csv**：各类模式库与规则库（workflow/output/trigger/resource/validation 等）。

## 用途

- 被 `.shared/skill-creator/scripts/search.py` 与 `validate.py` 等脚本读取。

## 约定

- 数据应保持字段稳定、可增量扩展；修改字段需同步更新脚本解析逻辑。
