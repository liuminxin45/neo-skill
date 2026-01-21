# Hard Gate 编码规范（coding-standards）

## 目标
- 防止代码质量与架构在长期演进中“慢慢写歪”。
- 把规则拆成：
  - Hard Gate（必须自动化、失败即阻断）
  - Review Gate（无法完全自动化，但必须在 PR review 中显式检查）

## Non-negotiable
- 任何 gate 都应尽早接入；默认 fail-fast。
- 不引入与现有栈冲突的强依赖；若项目已有约定，以“兼容优先、逐步收紧”为原则。
- 最小化实现原则：优先用现有命令/工具拼出可跑通的门禁，再逐步加严。
- 只在必要时新增注释：只写“为什么/约束/坑”，不写“代码在做什么”。

## 核心 Hard Gate（必须早期接入）
- ESLint（TS/JS + React/Vue/Node 适配）
- TypeScript typecheck：`tsc -b`
- Prettier：只负责格式
- 边界约束（必须覆盖）：
  - 禁止跨层依赖（type-first layer model）
  - 只允许从 public entrypoints 导入（每包仅允许从 `package.json#exports` 暴露的路径导入）
  - 禁止深层内部目录 import
- 依赖检查（必须覆盖）：
  - 未使用依赖（unused deps）
  - 幽灵/越界依赖（ghost / extraneous deps）
  - workspace 版本漂移（version drift）

## 必须能跑通的命令契约
默认目标（pnpm workspace）：
```bash
pnpm -r lint
pnpm -r typecheck
pnpm -r test
pnpm -r depcheck
```

若仓库形态不支持 `pnpm -r`：
- 允许先在 root 提供等价聚合命令（或补齐 workspace 约定）
- 但 CI PR gate 必须覆盖等价的 lint/typecheck/test/depcheck 组合

## 自动识别仓库形态（repo shape）
需要识别并输出证据（文件/字段）：
- pnpm workspace：`pnpm-workspace.yaml`
- pnpm + Nx：`pnpm-workspace.yaml` + `nx.json`
- pnpm + Turborepo：`pnpm-workspace.yaml` + `turbo.json`
- pnpm 单包：仅 `package.json`，且无 `pnpm-workspace.yaml`

输出（建议至少包含）：
- `repo_shape`：pnpm-workspace / pnpm-workspace-nx / pnpm-workspace-turbo / pnpm-single
- `recommended_boundary_tool`：eslint-plugin-boundaries 或 dependency-cruiser
- `test_runner_guess`：vitest / jest / node:test（按仓库形态与已有依赖推断）

规则模板：
- canonical：`skills/coding-standards/assets/windsurf-workflow-data/repo-shapes/*.json`
- Windsurf workflow data：`.windsurf/workflows/data/coding-standards/repo-shapes/*.json`

## 基于 git diff 的主要改动层级识别（type-first）
默认层级模型模板：
- canonical：`skills/coding-standards/assets/windsurf-workflow-data/layers/type-first.json`
- Windsurf workflow data：`.windsurf/workflows/data/coding-standards/layers/type-first.json`

要求：
- `layers_changed`：按命中变更文件计数降序
- `primary_layer`：命中最多的 layer
- 若跨多个 layer：强调边界与抽象复核，尤其是 domain/application 的耦合与副作用扩散

## 禁止深层 import（默认规则）
默认 denylist（可按 repo 调整）：
- 任意包内：禁止直接 import
  - `**/src/**`
  - `**/internal/**`
  - `**/__internal__/**`
  - `**/dist/**`
  - `**/lib/**`
- monorepo 跨包：只能
  - `@scope/pkg`
  - `@scope/pkg/<exported-subpath>`（且 subpath 必须在 exports 内）

## 可移植性（Hard Gate）：绝对路径 / cwd / alias 一致性 / 环境敏感值
### 绝对路径与本机用户目录
- 禁止在代码/配置/脚本/fixture 中写入本机绝对路径、盘符、或用户名相关路径。
  - Windows：`C:\\Users\\...`、`D:\\...`
  - macOS：`/Users/...`
  - Linux：`/home/...`
- 允许的替代方案：
  - 运行时根据 `process.cwd()` + 相对路径拼接（仅限“确定性 cwd”的场景，见下一节）。
  - 使用环境变量/配置文件注入路径（并在样例/fixture 中使用相对路径）。
  - 测试/fixture 路径优先通过 `path.resolve(__dirname, ...)` 等“以文件位置为基准”的方式生成。

### 禁止依赖不确定的运行时工作目录（cwd）
- 不允许隐式假设 `cwd` 为仓库根或某个包目录。
- 若必须依赖 `cwd`：
  - 只能依赖“明确约定的入口”（例如 root 的 `package.json` scripts），并在文档中写清约束。
  - 对外暴露的 CLI/脚本需支持通过参数传入目标路径（或在脚本内部先定位 repo root）。

### alias/路径映射一致性（TS/ESLint/测试/打包）
- `tsconfig.json` 的 `compilerOptions.paths`、ESLint import resolver、测试工具（jest/vitest）与打包工具（vite/tsup/webpack）必须保持同一套 alias 语义。
- 禁止“只在某一环节生效”的 alias，避免本地能跑、CI/打包失败或产物路径错乱。

### 环境敏感值：禁止硬编码端口/路径/URL/环境变量名
- 禁止把端口、服务地址、文件系统路径、环境名等写死在实现中（尤其是 domain/application 层）。
- 统一通过配置层注入（env/config 文件/参数），并给出迁移期白名单策略（例如仅允许在示例/开发脚本中硬编码）。

## 循环依赖（Hard Gate）：模块循环 / 包循环 / TS 引用循环
### 必须阻断的循环类型
- 包间循环（workspace packages A -> B -> A）。
- 包内模块循环（A.ts -> B.ts -> A.ts）。
- TypeScript project references 循环。

### 落地策略（不改变既有命令的前提）
- 优先复用边界工具能力：
  - dependency-cruiser：启用 `no-circular` / `circular` 相关规则。
  - eslint-plugin-boundaries：作为“边界与导入约束”，循环检测不足时用工具补齐。
- 若仓库已有构建图工具（Nx/Turbo/自研脚本），允许在现有 gate 命令链路中接入等价校验，但不引入新的“必跑命令契约”。

### 修复原则（优先级从高到低）
- 打断跨层回依赖（domain/application 不回依赖 infra/presentation）。
- 抽取纯接口/类型到 `shared/types` 或独立包，避免实现互相引用。
- 避免通过深层 `index.ts` 聚合制造隐式环（尤其是层层 re-export）。

## 安全与仓库卫生（Hard Gate）：secrets / 危险 API / 产物入库 / lock 策略
### Secrets 扫描（必须阻断）
- 禁止 token/key/私钥/证书等进入 git 历史。
- 允许采用工具：git hooks + CI 扫描（以“兼容优先”为前提选择与现有平台匹配的方案）。

### 危险 API 使用收敛
- 默认禁止（或限制）不安全/不受控 API：
  - `eval`/`Function` 动态执行。
  - 不受控的 `child_process` 执行（尤其是拼接 shell 命令）。
  - 弱随机用于安全场景（例如用 `Math.random()` 生成 token）。
- 若业务确需使用：必须有白名单与隔离边界（仅允许在 infra/cli 层），并给出替代方案。

### 禁止产物/临时文件入库
- 产物目录（按栈调整）：`dist/`、`lib/`、`build/`、`.turbo/`、`.nx/`、`coverage/`、`*.log`、`*.tmp` 等必须被忽略。
- 需要明确：哪些文件允许入库（例如类型声明/代码生成产物是否入库），并将策略固化在 `.gitignore` 与 CI 检查中。

### lock 策略（必须一致）
- 仓库只能采用一种 lock（按包管理器）：例如 pnpm -> `pnpm-lock.yaml`。
- 禁止 lock 漂移：CI 中应校验 lock 文件未被非预期修改（或严格固定安装策略）。

## 架构/工程化规范（Hard Gate + Review Gate）
### 目录组织范式
- 采用 `type-first`。

### 层内职责边界
- 两条同时成立：
  - 目录即职责
  - 依赖反推职责（禁止“为了复用”而跨职责/跨层耦合）

### 命名与一致性
- React components：`PascalCase.tsx`
- hooks：`useXxx.ts`
- utils：`xxx.ts`
- 文件名与导出符号一致：不强制，但需要巡检与统一建议

### 模块 API 设计
- 公共 API 以包级 entrypoints（exports）为准。
- 允许在包根 `index.ts` 聚合；禁止在深层目录层层 `index.ts` 造成循环依赖与耦合扩散。
- 默认倾向 named exports；default export 仅在框架强约束处使用。

### 副作用隔离（可测试性）
- domain/application 尽量保持纯：不直接依赖 network/fs/db/time/random。
- I/O 集中在 infra/adapter，通过抽象或依赖注入传入。

### 复杂度门槛（Hard Gate）
- 单函数最大行数：60
- 圈复杂度：15
- 在保留必要 try-catch 的情况下，优先早返回减少嵌套层级。

### 错误处理与日志（Hard Gate）
- 统一错误类型（例如 `AppError`/`DomainError`），禁止在非边界层随意 `throw new Error`。
- 禁止在非边界层直接 `console.*`（仅允许 entry/infra）。

### 注释与文档（Hard Gate + Review Gate）
- 禁止“解释代码做什么”的注释；只写“为什么/约束/坑”。
- 关键算法/复杂业务必须有块注释或链接到设计/issue。
- public API 需要 TSDoc/JSDoc（至少覆盖 exports 暴露的函数/类/类型）。

## 输出模板（执行本 skill 时必须给出）
- A) 识别结果：repo_shape + primary_layer + 边界工具选择
- B) Hard Gate 清单：可自动化项 vs 仅 review 项
- C) 需要新增/修改的配置文件清单（最小 diff）
- D) 可直接复制的命令清单（本地 + CI PR gate）

## CI（PR Gate）建议
- PR 必须跑 lint/typecheck/depcheck（以及项目已有的 test）。
- gate 失败必须阻断合并。
