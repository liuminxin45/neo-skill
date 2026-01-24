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
2. Installs all skills (generates outputs for all AI targets)
3. Writes VERSION files for each AI target
4. Saves init state to .neo-skill.json

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
2. Generates outputs for all AI targets (.windsurf, .claude, .cursor, .github)

### `omni-skill update`
Update npm package and re-initialize skills.

**Usage:**
```bash
omni-skill update
```

**What it does:**
1. Runs `npm install neo-skill@latest`
2. Re-runs `omni-skill init` with saved AI targets
