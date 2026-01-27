# Review Gate - 架构与代码反腐败审查

> **定位**：架构/代码反腐败审查，区别于 lint/hard-gate。关注架构决策、模块边界、依赖方向、副作用隔离、可测试性，防止"慢慢写歪"。

## 核心理念

### 目标
- 在 PR review 中显式检查架构与设计决策
- 防止架构在长期演进中"慢慢写歪"
- 明确哪些可以自动化（转为 Hard Gate），哪些需要人工 Review

### Non-negotiable
- **Review Gate 不能替代 Hard Gate**：能自动化的规则必须先自动化
- **检查点必须具体、可执行**：避免模糊的"代码质量"描述
- **持续演进**：重复出现的 Review 问题应考虑转化为 Hard Gate 规则

## 架构概览

本技能已重构为**数据驱动的 3 层架构**，参考 `ui-ux-pro-max` 的分层索引设计：

```
.shared/review-gate/
├── data/                    # 数据层：结构化知识库
│   ├── domains/            # 14 个领域分类
│   │   ├── layer/         # 分层架构
│   │   ├── dep/           # 依赖管理
│   │   ├── api/           # API 设计
│   │   ├── pure/          # 副作用隔离
│   │   ├── complex/       # 复杂度控制
│   │   ├── error/         # 错误处理
│   │   ├── obs/           # 可观测性
│   │   ├── type/          # 类型系统
│   │   ├── async/         # 异步处理
│   │   ├── ui/            # UI 优化
│   │   ├── perf/          # 性能优化
│   │   ├── sec/           # 安全检查
│   │   ├── doc/           # 文档规范
│   │   └── test/          # 测试策略
│   ├── reasoning/         # 推理层：信号到检查的路由规则
│   └── templates/         # 输出模板
├── scripts/                # 运行时层：信号分析器 + 引擎
│   ├── signals/           # 7 个信号分析器
│   └── engine/            # 路由、评分、组合、持久化
└── review-system/         # 分层覆盖配置
    ├── MASTER.md          # 全局默认
    ├── stacks/            # 技术栈级别
    ├── packages/          # 包级别
    └── paths/             # 路径级别（最高优先级）
```

详细架构说明见：[`.shared/review-gate/README.md`](../../../.shared/review-gate/README.md)

## 领域知识索引

每个领域包含 4 个标准文件：

| 领域 | 关注点 | 检查规则 | 修复方案 | 反模式 | 硬门候选 |
|------|--------|----------|----------|--------|----------|
| **layer** | 分层架构 | [checks.csv](../../../.shared/review-gate/data/domains/layer/checks.csv) | [recipes.md](../../../.shared/review-gate/data/domains/layer/recipes.md) | [anti_patterns.md](../../../.shared/review-gate/data/domains/layer/anti_patterns.md) | [hardgate_candidates.csv](../../../.shared/review-gate/data/domains/layer/hardgate_candidates.csv) |
| **dep** | 依赖管理 | [checks.csv](../../../.shared/review-gate/data/domains/dep/checks.csv) | [recipes.md](../../../.shared/review-gate/data/domains/dep/recipes.md) | [anti_patterns.md](../../../.shared/review-gate/data/domains/dep/anti_patterns.md) | [hardgate_candidates.csv](../../../.shared/review-gate/data/domains/dep/hardgate_candidates.csv) |
| **api** | API 设计 | [checks.csv](../../../.shared/review-gate/data/domains/api/checks.csv) | [recipes.md](../../../.shared/review-gate/data/domains/api/recipes.md) | [anti_patterns.md](../../../.shared/review-gate/data/domains/api/anti_patterns.md) | [hardgate_candidates.csv](../../../.shared/review-gate/data/domains/api/hardgate_candidates.csv) |
| **pure** | 副作用隔离 | [checks.csv](../../../.shared/review-gate/data/domains/pure/checks.csv) | [recipes.md](../../../.shared/review-gate/data/domains/pure/recipes.md) | [anti_patterns.md](../../../.shared/review-gate/data/domains/pure/anti_patterns.md) | [hardgate_candidates.csv](../../../.shared/review-gate/data/domains/pure/hardgate_candidates.csv) |
| **complex** | 复杂度控制 | [checks.csv](../../../.shared/review-gate/data/domains/complex/checks.csv) | [recipes.md](../../../.shared/review-gate/data/domains/complex/recipes.md) | [anti_patterns.md](../../../.shared/review-gate/data/domains/complex/anti_patterns.md) | [hardgate_candidates.csv](../../../.shared/review-gate/data/domains/complex/hardgate_candidates.csv) |
| **error** | 错误处理 | [checks.csv](../../../.shared/review-gate/data/domains/error/checks.csv) | [recipes.md](../../../.shared/review-gate/data/domains/error/recipes.md) | [anti_patterns.md](../../../.shared/review-gate/data/domains/error/anti_patterns.md) | [hardgate_candidates.csv](../../../.shared/review-gate/data/domains/error/hardgate_candidates.csv) |
| **obs** | 可观测性 | [checks.csv](../../../.shared/review-gate/data/domains/obs/checks.csv) | [recipes.md](../../../.shared/review-gate/data/domains/obs/recipes.md) | [anti_patterns.md](../../../.shared/review-gate/data/domains/obs/anti_patterns.md) | [hardgate_candidates.csv](../../../.shared/review-gate/data/domains/obs/hardgate_candidates.csv) |
| **type** | 类型系统 | [checks.csv](../../../.shared/review-gate/data/domains/type/checks.csv) | [recipes.md](../../../.shared/review-gate/data/domains/type/recipes.md) | [anti_patterns.md](../../../.shared/review-gate/data/domains/type/anti_patterns.md) | [hardgate_candidates.csv](../../../.shared/review-gate/data/domains/type/hardgate_candidates.csv) |
| **async** | 异步处理 | [checks.csv](../../../.shared/review-gate/data/domains/async/checks.csv) | [recipes.md](../../../.shared/review-gate/data/domains/async/recipes.md) | [anti_patterns.md](../../../.shared/review-gate/data/domains/async/anti_patterns.md) | [hardgate_candidates.csv](../../../.shared/review-gate/data/domains/async/hardgate_candidates.csv) |
| **ui** | UI 优化 | [checks.csv](../../../.shared/review-gate/data/domains/ui/checks.csv) | [recipes.md](../../../.shared/review-gate/data/domains/ui/recipes.md) | [anti_patterns.md](../../../.shared/review-gate/data/domains/ui/anti_patterns.md) | [hardgate_candidates.csv](../../../.shared/review-gate/data/domains/ui/hardgate_candidates.csv) |
| **perf** | 性能优化 | [checks.csv](../../../.shared/review-gate/data/domains/perf/checks.csv) | [recipes.md](../../../.shared/review-gate/data/domains/perf/recipes.md) | [anti_patterns.md](../../../.shared/review-gate/data/domains/perf/anti_patterns.md) | [hardgate_candidates.csv](../../../.shared/review-gate/data/domains/perf/hardgate_candidates.csv) |
| **sec** | 安全检查 | [checks.csv](../../../.shared/review-gate/data/domains/sec/checks.csv) | [recipes.md](../../../.shared/review-gate/data/domains/sec/recipes.md) | [anti_patterns.md](../../../.shared/review-gate/data/domains/sec/anti_patterns.md) | [hardgate_candidates.csv](../../../.shared/review-gate/data/domains/sec/hardgate_candidates.csv) |
| **doc** | 文档规范 | [checks.csv](../../../.shared/review-gate/data/domains/doc/checks.csv) | [recipes.md](../../../.shared/review-gate/data/domains/doc/recipes.md) | [anti_patterns.md](../../../.shared/review-gate/data/domains/doc/anti_patterns.md) | [hardgate_candidates.csv](../../../.shared/review-gate/data/domains/doc/hardgate_candidates.csv) |
| **test** | 测试策略 | [checks.csv](../../../.shared/review-gate/data/domains/test/checks.csv) | [recipes.md](../../../.shared/review-gate/data/domains/test/recipes.md) | [anti_patterns.md](../../../.shared/review-gate/data/domains/test/anti_patterns.md) | [hardgate_candidates.csv](../../../.shared/review-gate/data/domains/test/hardgate_candidates.csv) |

### MVP 领域（完整实现）
- **layer**：分层架构、依赖方向、跨层耦合
- **dep**：循环依赖、模块耦合、依赖图分析
- **api**：API 边界、导出设计、破坏性变更
- **pure**：副作用隔离、可测试性、依赖注入
- **complex**：复杂度、嵌套、函数长度、认知负担

### 其他领域（可插拔存根）
其他 9 个领域提供了基础结构和示例规则，可根据项目需要逐步完善。

## 使用方式

### 基本命令

```bash
# 基础审查（当前分支 vs main）
python .shared/review-gate/scripts/review.py

# 指定技术栈
python .shared/review-gate/scripts/review.py --stack react

# 指定领域
python .shared/review-gate/scripts/review.py --domain layer,dep

# 确保测试通过
python .shared/review-gate/scripts/review.py --ensure-tests-pass

# 持久化覆盖规则
python .shared/review-gate/scripts/review.py --persist path --domain layer
```

### 工作流

1. **创建审查分支** → `review-gate/<timestamp>`
2. **可选：运行测试** → 确保基线通过
3. **收集信号**：
   - Diff 变更集
   - 依赖子图
   - 层级分类
   - API 表面变更
   - 副作用扫描
   - 复杂度扫描
4. **路由与评分**：
   - 根据推理规则路由到检查项
   - 应用分层覆盖（paths > packages > stacks > MASTER）
   - 评分并排序
5. **生成报告**：
   - Markdown 报告（按领域分组）
   - JSON 结构化输出
6. **可选：最小化修复** → 自动应用简单修复
7. **可选：重新测试** → 验证修复未破坏功能

详细工作流见：[`.shared/review-gate/README.md#workflow`](../../../.shared/review-gate/README.md#workflow)

## 分层覆盖系统

支持 4 级覆盖配置，优先级从高到低：

1. **paths** → `review-system/paths/<path-hash>.md`（最高优先级）
2. **packages** → `review-system/packages/<pkg-name>.md`
3. **stacks** → `review-system/stacks/<stack>.md`
4. **MASTER** → `review-system/MASTER.md`（全局默认）

覆盖配置格式：
```markdown
# Override: <scope>

## Enabled Domains
- layer
- dep

## Disabled Checks
- layer-001  # 理由：特殊架构需求
- dep-002    # 理由：遗留代码豁免

## Custom Weights
- api-001: 0.8  # 降低优先级
- pure-001: 1.5 # 提高优先级
```

## 输出格式

### Markdown 报告
```markdown
# Review Gate Report

## Summary
- Total Findings: 12
- Critical: 2
- High: 5
- Medium: 3
- Low: 2

## Findings by Domain

### layer (5 findings)
#### [CRITICAL] layer-001: Upward dependency detected
...
```

### JSON 输出
```json
{
  "summary": {...},
  "findings": [
    {
      "id": "finding-001",
      "domain": "layer",
      "check_id": "layer-001",
      "severity": "critical",
      "confidence": 0.95,
      "evidence": {...}
    }
  ]
}
```

## 与 skill-creator 的一致性

本技能遵循 `skill-creator` 约定：

- **目录结构**：`skills/review-gate/` 存放 canonical 定义，`.shared/review-gate/` 存放共享资源
- **数据驱动**：使用 CSV/JSON 结构化数据，支持搜索和校验
- **确定性脚本**：Python 脚本实现确定性工作流
- **分层索引**：3 层架构（数据/推理/运行时）
- **可扩展性**：领域可插拔，规则可覆盖

## 与 Hard Gate 的协同

- **优先自动化**：可自动化的检查应转化为 Hard Gate 规则
- **持续演进**：定期回顾重复问题，考虑自动化
- **互为补充**：Hard Gate 保证基线，Review Gate 关注架构决策

## 快速参考

| 需求 | 查看 |
|------|------|
| 完整架构说明 | [`.shared/review-gate/README.md`](../../../.shared/review-gate/README.md) |
| 领域检查规则 | [`.shared/review-gate/data/domains/*/checks.csv`](../../../.shared/review-gate/data/domains/) |
| 修复方案 | [`.shared/review-gate/data/domains/*/recipes.md`](../../../.shared/review-gate/data/domains/) |
| 推理规则 | [`.shared/review-gate/data/reasoning/review-reasoning.csv`](../../../.shared/review-gate/data/reasoning/review-reasoning.csv) |
| 覆盖配置 | [`.shared/review-gate/review-system/`](../../../.shared/review-gate/review-system/) |
| CLI 入口 | [`.shared/review-gate/scripts/review.py`](../../../.shared/review-gate/scripts/review.py) |

---

**注**：本文档为导航索引，具体规则和实现请查看对应的数据文件和脚本。
