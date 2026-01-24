# Universal Data Pack

必需数据包（不可删除），包含 skill-creator 的核心资源。

## 文件说明

### questions.level1.json
Level 1 固定问题集（5-7问），覆盖核心槽位：
- goal: 目标
- input: 输入来源
- output: 输出形态
- environment: 运行环境
- constraints: 硬约束
- acceptance: 验收用例

### schema.skill.json
Skill 输出的 schema 定义，用于校验：
- required_fields: 必需字段
- field_types: 字段类型
- workflow_step_schema: workflow step 的 schema
- validation_rules: 校验规则

## 子目录

### output_packs/
输出格式包（5个，必需且不可禁用）：
- **plain_text_message**: 纯文本消息（邮件/IM）
- **markdown_report**: Markdown 报告
- **json_result**: JSON 结果
- **code_snippet**: 代码片段/脚本
- **generic**: 通用格式（兜底）

每个 pack 包含：
- output_structure: 输出结构定义
- workflow_pattern: 工作流模式
- recommended_libraries: 推荐库
- acceptance_template: 验收模板

### minimal_checklists/
最小 checklist（3个，必需）：
- **automation_basic**: 自动化任务基本可靠性检查
- **web_scraping_basic**: 网页抓取基本可靠性检查
- **notification_basic**: 通知发送基本可靠性检查

每个 checklist 包含：
- rules: 规则列表（id, title, description, severity, example）

## 设计原则

1. **不可禁用**: universal 数据包是不变量，必须存在
2. **安全降级**: 其他数据包缺失时，使用 universal 中的资源
3. **可扩展**: 可以添加新的 output_packs 和 checklists
