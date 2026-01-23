# neo-skill（多 AI 助手技能生成器）

一个确定性的 **skill-creator** 仓库。

**GitHub**: https://github.com/liuminxin45/neo-skill

## 安装

```bash
# 全局安装
npm install -g neo-skill
```

**前置依赖**：需要安装 Python 3.8+（命令行执行依赖 Python）

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

**场景 1：在 neo-skill 仓库内开发/维护 skill**
```bash
# 从仓库根目录执行，初始化指定 AI 助手的技能文件
omni-skill init --ai claude
omni-skill init --ai windsurf
omni-skill init --ai all  # 初始化所有支持的 AI 助手
```

**场景 2：在 neo-skill 仓库内更新并重新生成所有 IDE 入口文件**
在 neo-skill 仓库根目录执行：

```bash
omni-skill update
```

行为说明：
- 根据上次 init 时保存的 AI 目标，重新同步/生成所有入口文件

**场景 3：在其他项目中使用 neo-skill 的 skill**
将 neo-skill 仓库克隆到你的项目中（例如 `vendor/neo-skill/`），然后根据你使用的 IDE，复制对应的入口文件到项目根目录：
- **Windsurf**：复制 `.windsurf/workflows/<skill>.md` 和 `.windsurf/workflows/data/`
- **Cursor**：复制 `.cursor/commands/<skill>.md`
- **Claude Desktop**：复制 `.claude/skills/<skill>/`
- **GitHub / VS Code Skills**：复制 `.github/skills/<skill>/`

### 推荐用法

```bash
# 初始化指定 AI 助手
omni-skill init --ai claude
omni-skill init --ai windsurf --ai cursor  # 可指定多个

# 初始化所有支持的 AI 助手
omni-skill init --ai all

# 更新（基于上次 init 的配置）
omni-skill update
```

### 关于 npm 安装后的 init 行为

当你通过 `npm install -g neo-skill` 安装后：

- **命令来源**：`omni-skill` 和 `skill-creator` 命令来自全局 npm 包（内部调用 Python）
- **同步内容**：`omni-skill init` 会把包内的技能/资源内容同步到当前项目目录（覆盖式同步）：
  - `skills/`
  - `.shared/skill-creator/`
  - 以及指定 AI 对应的目录（如 `.claude/skills/`、`.windsurf/workflows/` 等）

**核心行为：**
- 根据 `--ai` 参数生成对应 IDE 的入口文件
- 不同 IDE 可以共存，切换 IDE 时无需重新生成
- 生成的文件都是从 canonical `skills/<skill>/skillspec.json` 渲染而来

**参数说明：**
- `init`：初始化技能文件
- `update`：基于上次 init 保存的配置重新同步
- `--ai <target>`：指定目标 AI 助手（可重复使用）

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
