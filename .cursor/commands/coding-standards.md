# coding-standards

为 TypeScript/JavaScript（React/Vue/Node）项目建立可自动校验的 Hard Gate 编码规范：ESLint/TypeScript/Prettier + 边界约束（跨层/exports-only/禁止深层 import）+ 依赖检查（unused/ghost/版本漂移），并将架构/工程化规则尽可能落到可执行门禁（支持按仓库形态与主要改动层级自适应）。

## When to use
- 我想给仓库增加 Hard Gate 编码规范（lint/typecheck/test/depcheck + 边界）
- 帮我设置禁止跨层依赖、仅允许从 exports 导入、禁止深层 import
- 帮我把架构/工程化规范变成可自动校验的门禁
- 为 pnpm monorepo 配置 ESLint/TypeScript/Prettier + 边界检查
- 为 PR/CI 增加强制的质量门禁
- 整理代码

## Command
Run these deterministic steps in the repository:
```bash
omni-skill init --cursor
omni-skill do --agent
```

## Workflow
Mode: `sequential`

### 1. 识别仓库形态（repo shape）并选择最小改动路径
### 2. 基于 git diff 识别主要改动层级（type-first）
### 3. Hard Gate 基线：ESLint + TypeScript + Prettier（早期接入）
### 4. 边界约束（Hard Gate）：跨层/exports-only/禁止深层 import
### 5. 可移植性（Hard Gate）：绝对路径/cwd 依赖/alias 一致性/环境敏感值
### 6. 循环依赖（Hard Gate）：模块循环 / 包循环 / 项目引用循环
### 7. 安全与仓库卫生（Hard Gate）：secrets / 危险 API / 产物入库 / lock 策略
### 8. 架构/工程化规范（尽可能自动化，剩余项进入 review gate）
### 9. 依赖检查（Hard Gate）：unused / ghost / 版本漂移
### 10. CI PR gate 绑定 + 汇总输出（可执行清单）