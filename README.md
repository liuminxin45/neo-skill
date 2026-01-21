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

**场景 2：在其他项目中使用 neo-skill 的 skill**
1. 将 neo-skill 仓库克隆到你的项目中（例如 `vendor/neo-skill/`）
2. 根据你使用的 IDE，复制对应的入口文件到项目根目录：
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
# 或
omni-skill do

# 指定 skill 名称
omni-skill init --skill coding-standards
# 或指定 spec 路径
omni-skill init --spec skills/coding-standards/skillspec.json
```

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

### 无安装回退方案
```bash
python -m omni_skill.cli init
python -m omni_skill.cli do
```

### 直接调用 skill-creator
```bash
# 从仓库根目录执行
python -m skill_creator.cli generate skills/skill-creator/skillspec.json
python -m skill_creator.cli validate skills/skill-creator/skillspec.json
python -m skill_creator.cli package --target claude --skill skill-creator
```

或使用便捷脚本：

```bash
python .shared/skill-creator/scripts/generate.py skills/skill-creator/skillspec.json
python .shared/skill-creator/scripts/validate.py skills/skill-creator/skillspec.json
python .shared/skill-creator/scripts/package.py --target claude --skill skill-creator
```

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
