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
# 初始化技能
omni-skill init --ai claude

# 生成技能输出
skill-creator generate skills/skill-name/skillspec.json

# 验证技能
skill-creator validate skills/skill-name/skillspec.json
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

**初始化技能文件**
```bash
# 初始化指定 AI 助手的技能文件
omni-skill init --ai claude
omni-skill init --ai windsurf
omni-skill init --ai all  # 初始化所有支持的 AI 助手

# 更新（基于上次 init 的配置）
omni-skill update
```

**生成和验证技能**
```bash
# 生成技能输出
skill-creator generate skills/skill-name/skillspec.json

# 验证技能
skill-creator validate skills/skill-name/skillspec.json

# 打包 Claude 技能
skill-creator package --target claude --skill skill-name
```

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
