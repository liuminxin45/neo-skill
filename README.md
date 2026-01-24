# neo-skill（多 AI 助手技能生成器）

一个确定性的 **skill-creator** 仓库。

**GitHub**: https://github.com/liuminxin45/neo-skill  
**npm**: https://www.npmjs.com/package/neo-skill

## 安装

```bash
# 通过 npm 安装（推荐）
npm install -g neo-skill

# 或通过 pip 安装
pip install neo-skill
```

**前置依赖**：需要安装 Python 3.8+

## 使用方式

### 命令行工具（安装后）

```bash
# 初始化技能（从 npm 包安装所有 skills）
omni-skill init --ai windsurf

# 手动安装本地创建的 skill
omni-skill install ./skills/my-new-skill

# 更新 npm 包并重新初始化
omni-skill update

# 查看帮助
omni-skill --help
```

### 直接运行 Python 模块（开发模式）

```bash
# 初始化技能
python -m omni_skill.cli init --ai claude

# 生成技能输出
python -m skill_creator.cli generate skills/skill-name/skillspec.json

# 验证技能
python -m skill_creator.cli validate skills/skill-name/skillspec.json
```

## 功能说明
- 使用 canonical `skills/<skill>/skillspec.json` 作为单一真源（single source of truth）
- 为多个 AI 助手生成入口文件：
  - Claude: `.claude/skills/<skill>/SKILL.md` + `resources/`
  - Windsurf: `.windsurf/workflows/<skill>.md`
  - Cursor: `.cursor/commands/<skill>.md`
  - GitHub / VS Code Skills: `.github/skills/<skill>/SKILL.md` + resources
- 校验生成的 `SKILL.md` 是否符合 Claude 严格的元数据规则
- 打包 Claude `.skill`（zip 格式，符合正确的根目录结构）

## 支持的 Skills

| Skill 名称 | 描述 | 来源 |
|-----------|------|------|
| **skill-creator** | 对话式收集需求，生成可在多 AI Assistant 运行的技能包 | 内置 |
| **review-gate** | 建立架构与工程化 PR Review 规范，提供可执行的 Review Checklist | 内置 |

**触发示例**：
- skill-creator: "我想做一个 skill"、"帮我生成 SKILL.md"、"把我的 prompt 工作流变成 skill"
- review-gate: "我想建立 PR Review 架构规范检查点"、"帮我生成 PR Review Checklist 模板"、"软评审代码"

## 快速开始

### 典型使用场景

### 使用场景

**1. 初始化技能（首次使用）**
```bash
# 初始化指定 AI 助手的技能文件
omni-skill init --ai windsurf
omni-skill init --ai claude
omni-skill init --ai all  # 初始化所有支持的 AI 助手
```

这会：
- 从 npm 包同步 skills/ 和 .shared/ 到当前目录
- 为所有 skills 生成 AI 助手的输出文件（.windsurf, .claude, .cursor, .github）
- 保存初始化状态到 .neo-skill.json

**2. 使用 skill-creator 创建新 skill**

在 IDE 中输入 `/skill-creator`（Windsurf）或使用其他 AI 助手的触发方式，按照对话式流程创建新 skill。

**3. 安装刚创建的 skill**
```bash
# 安装单个 skill
omni-skill install ./skills/my-new-skill

# 或安装整个 skills 目录
omni-skill install ./skills
```

这会：
- 复制 skill 到当前目录的 skills/ 文件夹
- 为该 skill 生成所有 AI 助手的输出文件

**4. 更新 npm 包**
```bash
# 更新到最新版本并重新初始化
omni-skill update
```

这会：
- 运行 `npm install neo-skill@latest`
- 重新执行 `omni-skill init`（使用保存的 AI 目标）

**在其他项目中使用**
将 neo-skill 仓库克隆到你的项目中（例如 `vendor/neo-skill/`），然后：
1. 设置 PYTHONPATH：`export PYTHONPATH=$PWD/vendor/neo-skill/src:$PYTHONPATH`
2. 运行命令：`omni-skill init --ai claude`

**支持的 AI 助手：**
claude, cursor, windsurf, antigravity, copilot, kiro, codex, qoder, roocode, gemini, trae, opencode, continue, all


## Canonical 与生成文件

### Canonical（可编辑）
- `skills/<skill>/skillspec.json`
- `skills/<skill>/references/**`
- `skills/<skill>/scripts/**`（可选）
- `skills/<skill>/assets/**`（可选）

### 生成文件（不要手动编辑）
- `.windsurf/workflows/<skill>.md`
- `.windsurf/workflows/data/<skill>/**`（从 `skills/<skill>/assets/windsurf-workflow-data` 同步）
- `.claude/skills/<skill>/**`
- `.cursor/commands/<skill>.md`
- `.github/skills/<skill>/**`
