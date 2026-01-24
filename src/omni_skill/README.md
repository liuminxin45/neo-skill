# src/omni_skill

本目录存放 `omni-skill` 命令对应的 Python 模块。

## 职责

- 将本仓库作为“技能初始化器”：把 `skills/`（canonical）及必要的生成/辅助目录同步到目标工作目录。
- 支持按 AI 助手类型选择性同步（例如 `claude`/`windsurf`/`cursor` 等）。

## 约定

- 同步规则与生成行为应保持确定性（同输入得到同输出）。

## Commands

### `omni-skill init --ai <target>`
Initialize skills for target AI assistants.

**Usage:**
```bash
omni-skill init --ai windsurf
omni-skill init --ai claude
omni-skill init --ai all
```

**What it does:**
1. Syncs skills/ and .shared/ from npm package to current directory
2. Installs all skills (generates outputs for **specified AI targets only**)
3. Writes VERSION files for each AI target
4. Saves init state to .neo-skill.json

**Example:**
- `omni-skill init --ai windsurf` → Only generates `.windsurf/workflows/`
- `omni-skill init --ai claude` → Only generates `.claude/skills/`
- `omni-skill init --ai all` → Generates all targets (.windsurf, .claude, .cursor, .github)

### `omni-skill install <path>`
Install skill(s) from a local directory.

**Usage:**
```bash
# Install a single skill
omni-skill install ./skills/my-new-skill

# Install all skills from a directory
omni-skill install ./skills
```

**What it does:**
1. Copies skill(s) to current directory's skills/ folder
2. Generates outputs for **all AI targets** (.windsurf, .claude, .cursor, .github)

**Note:** Unlike `init`, the `install` command always generates outputs for all AI targets to ensure maximum compatibility.

### `omni-skill install-skill <skill-id>`
Install skill with dependency closure (new architecture).

**Usage:**
```bash
omni-skill install-skill review-gate --target windsurf
omni-skill install-skill skill-creator --target claude
```

**What it does:**
1. Resolves skill dependency closure (minimal files)
2. Materializes files to Install Space
3. Generates install manifest
4. Validates paths (no source path leakage)

**Architecture:**
- Uses Source Space (skills/) for build
- Copies to Install Space (.windsurf/, .claude/, etc.) for runtime
- Only copies minimal closure (not entire source directory)

### `omni-skill doctor --skill <skill-id>`
Diagnose skill installation and dependencies.

**Usage:**
```bash
omni-skill doctor --skill review-gate --target windsurf
```

**What it checks:**
- Install manifest exists
- All referenced files exist
- No source path leakage
- Index files are valid
- Dependency closure is complete

**Output:**
```
=== Skill Diagnostic Report ===
Skill ID: review-gate
Install Root: .windsurf/workflows/data/review-gate

--- Path Validation ---
✓ No source path leakage detected
✓ All index paths point to Install Space
✓ All referenced files exist

=== Diagnostic Complete ===
```

### `omni-skill update`
Update npm package and re-initialize skills.

**Usage:**
```bash
omni-skill update
```

**What it does:**
1. Runs `npm install neo-skill@latest`
2. Re-runs `omni-skill init` with saved AI targets
