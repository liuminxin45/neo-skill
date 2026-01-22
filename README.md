# ai-skill-creator（多 AI 助手技能生成器）

一个确定性的 **skill-creator** 仓库。

## 功能说明
- 使用 canonical `skills/<skill>/skillspec.json` 作为单一真源（single source of truth）
- 为多个 AI 助手生成入口文件：
  - Claude: `.claude/skills/<skill>/SKILL.md` + `resources/`
  - Windsurf: `.windsurf/workflows/<skill>.md`
  - Cursor: `.cursor/commands/<skill>.md`
  - GitHub / VS Code Skills: `.github/skills/<skill>/SKILL.md` + resources
- 校验生成的 `SKILL.md` 是否符合 Claude 严格的元数据规则
- 打包 Claude `.skill`（zip 格式，符合正确的根目录结构）

## 快速开始

### 典型使用场景

**场景 1：在 neo-skill 仓库内开发/维护 skill**
```bash
# 从仓库根目录执行，一次性生成所有 IDE 的入口文件
omni-skill init

# 或指定具体的 skill
omni-skill init --skill coding-standards
```

**场景 2：在 neo-skill 仓库内一键更新并重新生成所有 IDE 入口文件**
在 neo-skill 仓库根目录执行：

```bash
omni-skill update
```

行为说明：
- 更新全局 npm 包（等价于执行 `npm install -g neo-skills@latest`）
- 自动执行一次 `omni-skill init`（同步/覆盖 `skills/`、`.shared/` 与各 IDE 输出目录，并执行 `uipro init --ai all`）

可选开关：
- 如需跳过 npm 自更新，可设置环境变量：`NEO_SKILLS_SKIP_SELF_UPDATE=1`

**场景 3：在其他项目中使用 neo-skill 的 skill**
将 neo-skill 仓库克隆到你的项目中（例如 `vendor/neo-skill/`），然后根据你使用的 IDE，复制对应的入口文件到项目根目录：
- **Windsurf**：复制 `.windsurf/workflows/<skill>.md` 和 `.windsurf/workflows/data/`
- **Cursor**：复制 `.cursor/commands/<skill>.md`
- **Claude Desktop**：复制 `.claude/skills/<skill>/`
- **GitHub / VS Code Skills**：复制 `.github/skills/<skill>/`

### 推荐用法（短命令）
> 如果 `omni-skill` 已安装为 CLI。

```bash
# 生成 + 校验（自动识别 skillspec.json）
# 会同时生成 .windsurf/.claude/.cursor/.github 所有 IDE 的入口文件
omni-skill init

# 指定 skill 名称
omni-skill init --skill coding-standards
# 或指定 spec 路径
omni-skill init --spec skills/coding-standards/skillspec.json
```

### 关于 npm 全局安装后的 init 行为（重要）

当你通过 `npm install -g neo-skills` 安装后：

- **命令来源**：你执行的 `omni-skill`/`skill-creator` 命令始终来自全局 npm 包（例如 `.../node_modules/neo-skills/bin/...`），不会被复制到项目里。
- **同步内容**：`omni-skill init` 会把 npm 包内的技能/资源内容同步到你当前项目目录（覆盖式同步，按条目替换）：
  - `skills/`
  - `.shared/skill-creator/`
  - `.claude/skills/`
  - `.windsurf/workflows/`
  - `.cursor/commands/`
  - `.github/skills/`
- **不会同步**：不会把用于执行命令的实现（如 npm 包内的 `bin/`、`src/`）拷贝到项目里，以避免出现“项目里也有一套命令实现”导致的混淆。
- **uipro 初始化**：`omni-skill init` 会自动执行 `uipro init --ai all`，用于把第三方库 skill 能力初始化/接入到你的 skill 库中。
  - 如需跳过自动执行，可设置环境变量：`NEO_SKILLS_SKIP_UIPRO_INIT=1`

**核心行为：**
- **一次生成所有 IDE 的入口文件**：`.windsurf/`、`.claude/`、`.cursor/`、`.github/` 会同时生成
- 不同 IDE 可以共存，切换 IDE 时无需重新生成
- 生成的文件都是从 canonical `skills/<skill>/skillspec.json` 渲染而来

**参数说明：**
- `init` / `do`：功能完全相同的别名（都执行 generate + validate）
- `--skill <name>`：指定 skill 名称（会查找 `skills/<name>/skillspec.json`）
- `--spec <path>`：直接指定 `skillspec.json` 的路径
- `--repo-root <path>`：指定仓库根目录（默认为当前目录）
- `--cursor` / `--agent`：可选的语义化标记（不影响实际执行，仅用于不同 AI 助手调用时的可读性）

**自动解析规则：**
1. 优先使用 `--spec` 或 `--skill` 参数
2. 其次查找当前目录的 `skillspec.json`
3. 再查找环境变量 `OMNI_SKILL_SPEC` 或 `OMNI_SKILL`
4. 默认使用 `skills/coding-standards/skillspec.json`（如果存在）
5. 如果只有一个 skill，自动使用该 skill
6. 如果有多个 skill，报错并提示可用的 skill 列表


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
