# Skill Creator 重构设计文档

## 概述

本次重构以"文件化 + 多层索引 + 按需加载"为核心设计，实现了一个稳定、低 token、低交互负担的 skill 生成系统。

## 文档列表

- [ARCHITECTURE.md](./ARCHITECTURE.md) - 架构设计详解
- [DIRECTORY_STRUCTURE.md](./DIRECTORY_STRUCTURE.md) - 目录结构说明
- [END_TO_END_DEMO.md](./END_TO_END_DEMO.md) - 端到端演示
- [LIBRARY_RECOMMENDATION.md](./LIBRARY_RECOMMENDATION.md) - 三方库自动推荐机制
- [SUMMARY.md](./SUMMARY.md) - 重构总结邮件场景完整对话
   - Doctor trace 示例

## 核心文档

1. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - 完整架构说明
   - 模块划分（Core + Providers + Data Packs）
   - 数据流
   - 不变量与安全降级机制

2. **[END_TO_END_DEMO.md](./END_TO_END_DEMO.md)** - 端到端演示
   - RSS 抓取 + 邮件场景完整对话
   - Doctor trace 示例

3. **[DIRECTORY_STRUCTURE.md](./DIRECTORY_STRUCTURE.md)** - 目录结构
   - 完整文件树
   - 数据包说明
   - 扩展方式

## 快速开始

```python
from skill_creator.core.engine import SkillCreatorEngine
from pathlib import Path

# 初始化引擎
engine = SkillCreatorEngine(Path(".shared/skill-creator/data_packs"))

# 创建 skill
ctx = engine.create_skill("每天抓取 RSS 并发邮件")

# 查看 doctor 报告
print(engine.get_doctor_report(ctx))
```

## 核心特性

### ✓ 不变量（不可禁用）
- Two-Level Interview (Level1 → Gap → Level2)
- QuestionSpec 受约束问题规格
- Output Packs 输出格式包
- Schema + Dry-run 校验
- Plan 生成前展示

### ✓ 可选增强（安全降级）
- Recipe/Blueprint 蓝图库
- Tool Catalog 库推荐
- Extended Checklist 扩展规则
- Acceptance Templates 验收模板
- Profiles 环境 profile

### ✓ 多层索引 + 按需加载
- 基于 task_type + capability_tags + keywords 检索
- 只加载 top-k 文件（默认 3-5）
- 完整 trace 可追溯

## 已实现模块

### Core 层
- ✅ types.py - 数据结构
- ✅ search.py - 多层索引
- ✅ router.py - Router/Tagger
- ✅ interview.py - Interview Engine
- ✅ orchestrator.py - Plan Orchestrator
- ✅ builder.py - Skill Builder
- ✅ validator.py - Validator
- ✅ engine.py - 主引擎

### Providers 层
- ✅ recipe_provider.py
- ✅ tool_catalog_provider.py
- ✅ checklist_provider.py

### Data Packs
- ✅ universal/ (完整)
- ✅ recipes/ (示例)
- ✅ tools/ (示例)

## 待扩展

- [ ] domains/ - 领域知识
- [ ] tasks/ - 任务模式
- [ ] checklists_ext/ - 扩展 checklist
- [ ] acceptance_templates/ - 验收模板
- [ ] profiles/ - 环境 profile
- [ ] CLI 集成
- [ ] 实际代码生成器

## 设计原则

1. **不变量优先**: 关键能力不可禁用
2. **安全降级**: 增强能力缺失时仍可工作
3. **按需加载**: 严控 token 消耗
4. **可追溯**: 完整 trace 支持 debug
5. **可扩展**: 新增能力不触发大重构
