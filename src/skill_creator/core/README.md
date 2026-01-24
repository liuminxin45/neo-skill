# Core Module

核心模块（不变量，不可禁用）。

## 模块说明

### types.py
核心数据结构定义：
- `QuestionSpec`: 受约束问题规格
- `InterviewState`: 提问状态机
- `GapScore` + `SlotGap`: 缺口评分
- `Plan` + `LibraryRecommendation`: Implementation Plan
- `SkillDraft`: Skill 草稿
- `ValidationResult`: 校验结果
- `SearchQuery` + `SearchResult`: 多层索引检索契约
- `SkillCreatorContext`: 全局上下文

### search.py
多层索引与按需加载：
- `IndexManager`: 索引管理器
- `search_data_packs()`: 便捷搜索函数
- 支持基于 task_type + capability_tags + keywords 检索
- 只加载 top-k 文件（默认 3-5）

### router.py
Router/Tagger（中等粒度 tags）：
- `Router`: 分析用户请求，产出 task_type + capability_tags
- Coarse tags: ~30 个（稳定）
- 基于规则 + 同义词表

### interview.py
Two-Level Interview Engine：
- `InterviewEngine`: 提问引擎
- Level 1: 固定 5-7 问
- Gap Scoring: 缺口评分
- Level 2: 缺口驱动，最多 2 轮，每轮≤3问

### orchestrator.py
Plan Orchestrator：
- `PlanOrchestrator`: Plan 编排器
- 聚合 providers 推荐
- 生成 Implementation Plan
- 选择 Output Pack（必需）

### builder.py
Skill Builder：
- `SkillBuilder`: Skill 构建器
- 基于 Plan + Output Pack 生成 SkillDraft
- 优先使用 recipe，否则使用 pack 的 workflow_pattern

### validator.py
Schema + Dry-run Validator：
- `Validator`: 校验器（不可禁用）
- Schema 校验（字段完整性、类型正确性）
- Dry-run 仿真（用验收用例走一遍工作流）
- 发现缺口时返回 missing_gaps

### engine.py
主引擎：
- `SkillCreatorEngine`: 整合所有 Core + Providers
- `create_skill()`: 创建 skill 的完整流程
- `get_doctor_report()`: 生成 doctor/debug 报告

## 设计原则

1. **不可禁用**: Core 层的所有能力都是不变量
2. **强制执行**: Two-Level Interview、Output Packs、Schema + Dry-run 等
3. **可追溯**: 完整 trace 支持 debug
4. **解耦**: 各模块职责清晰，避免循环依赖
