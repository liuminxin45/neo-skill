---
description: 为 TypeScript/JavaScript（React/Vue/Node）项目建立可自动校验的 Hard Gate 编码规范：ESLint/TypeScript/Prettier + 边界约束（跨层/exports-only/禁止深层 import）+ 依赖检查（unused/ghost/版本漂移），并将架构/工程化规则尽可能落到可执行门禁（支持按仓库形态与主要改动层级自适应）。
auto_execution_mode: 3
---

# coding-standards

Role: workflow executor.

## Triggers
- 我想给仓库增加 Hard Gate 编码规范（lint/typecheck/test/depcheck + 边界）
- 帮我设置禁止跨层依赖、仅允许从 exports 导入、禁止深层 import
- 帮我把架构/工程化规范变成可自动校验的门禁
- 为 pnpm monorepo 配置 ESLint/TypeScript/Prettier + 边界检查
- 为 PR/CI 增加强制的质量门禁
- 整理代码

## Workflow
Mode: `sequential`

### Step 1 — 创建修复分支（commit id + 英文简述）
在开始修改前必须创建一个新分支，专用于修复当前（上次提交）引入的 coding-standards 问题。分支名规则：短 commit id + 英文简述（kebab-case）。如果工作区不干净，先提交/暂存/清理后再继续。
```bash
git status --porcelain
git checkout -b "$(git rev-parse --short HEAD)-<english-brief-kebab-case>"
```

### Step 2 — 创建分支后：运行一次完整单测（若没有则跳过；失败先修复再继续）
在新分支创建后立即执行一次全量单测。若仓库无 test 命令（或无测试），则跳过；若失败，必须先修复到通过后再继续后续所有 step。
```bash
node -e "const fs=require('fs');const path=require('path');const {spawnSync}=require('child_process');const cwd=process.cwd();const has=(p)=>fs.existsSync(path.join(cwd,p));const run=(cmd,args)=>{const r=spawnSync(cmd,args,{stdio:'inherit',shell:true});if(r.error&&String(r.error.message||'').toLowerCase().includes('enoent'))return {missing:true};if(r.error)throw r.error;process.exitCode=(r.status==null?1:r.status);return {missing:false,code:process.exitCode};};let r=null;if(has('pnpm-workspace.yaml')){r=run('pnpm',['-r','test','--if-present']);}else if(has('pnpm-lock.yaml')){r=run('pnpm',['test','--if-present']);}else{r=run('npm',['test','--if-present']);}if(r&&r.missing){console.log('Test runner not found; skipping tests.');process.exit(0);}if(process.exitCode&&process.exitCode!==0)process.exit(process.exitCode);"
```

### Step 3 — 识别仓库形态（repo shape）并选择最小改动路径
必须识别 pnpm-workspace / pnpm+nx / pnpm+turbo / pnpm-single，并给出证据；默认选择‘兼容现状 + 最小改动’路径。规则模板见 `.windsurf/workflows/data/coding-standards/repo-shapes/*.json`，详细规则见 `skills/coding-standards/references/hard-gate.md`。

### Step 4 — 基于 git diff 识别主要改动层级（type-first）
统计变更文件命中各 layer 的次数，输出 primary_layer 与 layers_changed；跨层变更时，额外强调边界与抽象复核。层级模型模板见 `.windsurf/workflows/data/coding-standards/layers/type-first.json`，详细规则见 `skills/coding-standards/references/hard-gate.md`。

### Step 5 — Hard Gate 基线：ESLint + TypeScript + Prettier（早期接入）
目标：ESLint 覆盖 TS/JS 并按框架启用规则；TypeScript 使用 `tsc -b`；Prettier 只负责格式，避免与 ESLint 冲突。命令契约建议见 `skills/coding-standards/references/pnpm-snippets.md`。

### Step 6 — 边界约束（Hard Gate）：跨层/exports-only/禁止深层 import
必须覆盖：禁止跨层依赖；只允许从 package.json#exports 导入；禁止深层内部目录 import。工具落地二选一：eslint-plugin-boundaries 或 dependency-cruiser（随 repo shape 推荐）。细节与默认 denylist 见 `skills/coding-standards/references/hard-gate.md`。

### Step 7 — 可移植性（Hard Gate）：绝对路径/cwd 依赖/alias 一致性/环境敏感值
必须覆盖：绝对路径/用户目录、cwd 不确定性、alias 一致性、环境敏感值治理。细节见 `skills/coding-standards/references/hard-gate.md` 的“可移植性（Hard Gate）”章节。

### Step 8 — 循环依赖（Hard Gate）：模块循环 / 包循环 / 项目引用循环
必须覆盖：模块循环/包循环/TS 引用循环的检测与阻断。细节见 `skills/coding-standards/references/hard-gate.md` 的“循环依赖（Hard Gate）”章节。

### Step 9 — 安全与仓库卫生（Hard Gate）：secrets / 危险 API / 产物入库 / lock 策略
必须覆盖：secrets、危险 API、产物入库、lock 策略一致性。细节见 `skills/coding-standards/references/hard-gate.md` 的“安全与仓库卫生（Hard Gate）”章节。

### Step 10 — 架构/工程化规范（尽可能自动化，剩余项进入 review gate）
默认按 type-first；层内职责边界采用‘目录即职责 + 依赖反推职责’；命名与一致性按约定；复杂度门槛：单函数 60 行、圈复杂度 15、鼓励早返回减少嵌套（保留必要 try-catch）；错误/日志/注释/文档按约定。详见 `skills/coding-standards/references/hard-gate.md`。

### Step 11 — 依赖检查（Hard Gate）：unused / ghost / 版本漂移
必须覆盖：未使用依赖；幽灵依赖/越界依赖；版本漂移。推荐组合：depcheck/knip + import/no-extraneous-dependencies + syncpack。落地建议见 `skills/coding-standards/references/pnpm-snippets.md`。

### Step 12 — CI PR gate 绑定 + 汇总输出（可执行清单）
触发：手动运行 + 绑定到 CI PR 检查。输出必须包含：repo_shape、primary_layer、边界工具选择；Hard Gate 自动化项/仅 review 项；最小 diff 的配置文件清单；本地与 CI 可复制命令清单。输出模板见 `skills/coding-standards/references/hard-gate.md`。

### Step 13 — 提交前：再次运行一次完整单测（若没有则跳过；失败先修复到通过）
在提交变更之前，必须再跑一次全量单测，确保后续 commit 的分支处于可用状态。若失败，先修复到通过，再进入提交步骤。
```bash
node -e "const fs=require('fs');const path=require('path');const {spawnSync}=require('child_process');const cwd=process.cwd();const has=(p)=>fs.existsSync(path.join(cwd,p));const run=(cmd,args)=>{const r=spawnSync(cmd,args,{stdio:'inherit',shell:true});if(r.error&&String(r.error.message||'').toLowerCase().includes('enoent'))return {missing:true};if(r.error)throw r.error;process.exitCode=(r.status==null?1:r.status);return {missing:false,code:process.exitCode};};let r=null;if(has('pnpm-workspace.yaml')){r=run('pnpm',['-r','test','--if-present']);}else if(has('pnpm-lock.yaml')){r=run('pnpm',['test','--if-present']);}else{r=run('npm',['test','--if-present']);}if(r&&r.missing){console.log('Test runner not found; skipping tests.');process.exit(0);}if(process.exitCode&&process.exitCode!==0)process.exit(process.exitCode);"
```

### Step 14 — 提交变更并创建 PR
将本次最小 diff 的配置变更提交到刚创建的分支，并创建 PR。优先使用 GitHub CLI（gh）。如果没有 gh，需要手动在 GitHub 上从当前分支发起 PR（base=main）。
```bash
git status --porcelain
git add -A
git commit -m "chore(coding-standards): hard gate"
git push -u origin HEAD
gh pr create --fill --title "chore(coding-standards): hard gate" || echo "gh CLI not found; please create a PR manually from this branch."
```
