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

### 1. 创建修复分支（commit id + 英文简述）
```bash
git status --porcelain
git checkout -b "$(git rev-parse --short HEAD)-<english-brief-kebab-case>"
```
### 2. 创建分支后：运行一次完整单测（若没有则跳过；失败先修复再继续）
```bash
node -e "const fs=require('fs');const path=require('path');const {spawnSync}=require('child_process');const cwd=process.cwd();const has=(p)=>fs.existsSync(path.join(cwd,p));const run=(cmd,args)=>{const r=spawnSync(cmd,args,{stdio:'inherit',shell:true});if(r.error&&String(r.error.message||'').toLowerCase().includes('enoent'))return {missing:true};if(r.error)throw r.error;process.exitCode=(r.status==null?1:r.status);return {missing:false,code:process.exitCode};};let r=null;if(has('pnpm-workspace.yaml')){r=run('pnpm',['-r','test','--if-present']);}else if(has('pnpm-lock.yaml')){r=run('pnpm',['test','--if-present']);}else{r=run('npm',['test','--if-present']);}if(r&&r.missing){console.log('Test runner not found; skipping tests.');process.exit(0);}if(process.exitCode&&process.exitCode!==0)process.exit(process.exitCode);"
```
### 3. 识别仓库形态（repo shape）并选择最小改动路径
### 4. 基于 git diff 识别主要改动层级（type-first）
### 5. Hard Gate 基线：ESLint + TypeScript + Prettier（早期接入）
### 6. 边界约束（Hard Gate）：跨层/exports-only/禁止深层 import
### 7. 可移植性（Hard Gate）：绝对路径/cwd 依赖/alias 一致性/环境敏感值
### 8. 循环依赖（Hard Gate）：模块循环 / 包循环 / 项目引用循环
### 9. 安全与仓库卫生（Hard Gate）：secrets / 危险 API / 产物入库 / lock 策略
### 10. 架构/工程化规范（尽可能自动化，剩余项进入 review gate）
### 11. 依赖检查（Hard Gate）：unused / ghost / 版本漂移
### 12. CI PR gate 绑定 + 汇总输出（可执行清单）
### 13. 提交前：再次运行一次完整单测（若没有则跳过；失败先修复到通过）
```bash
node -e "const fs=require('fs');const path=require('path');const {spawnSync}=require('child_process');const cwd=process.cwd();const has=(p)=>fs.existsSync(path.join(cwd,p));const run=(cmd,args)=>{const r=spawnSync(cmd,args,{stdio:'inherit',shell:true});if(r.error&&String(r.error.message||'').toLowerCase().includes('enoent'))return {missing:true};if(r.error)throw r.error;process.exitCode=(r.status==null?1:r.status);return {missing:false,code:process.exitCode};};let r=null;if(has('pnpm-workspace.yaml')){r=run('pnpm',['-r','test','--if-present']);}else if(has('pnpm-lock.yaml')){r=run('pnpm',['test','--if-present']);}else{r=run('npm',['test','--if-present']);}if(r&&r.missing){console.log('Test runner not found; skipping tests.');process.exit(0);}if(process.exitCode&&process.exitCode!==0)process.exit(process.exitCode);"
```
### 14. 提交变更并创建 PR
```bash
git status --porcelain
git add -A
git commit -m "chore(coding-standards): hard gate"
git push -u origin HEAD
gh pr create --fill --title "chore(coding-standards): hard gate" || echo "gh CLI not found; please create a PR manually from this branch."
```