# Install Space 路径使用示例

## 正确的 Skill 文档写法

### Windsurf Workflow 示例

```markdown
# Review Gate Skill

## Data Packs

This skill uses the following data packs (Install Space paths):

- Checklists: `{{install_root}}/.windsurf/workflows/data/review-gate/checklists/`
- Templates: `{{install_root}}/.windsurf/workflows/data/review-gate/templates/`
- Universal Schema: `{{install_root}}/.windsurf/workflows/data/review-gate/universal/schema.json`

## Usage

Load checklist index from Install Space:

```python
import json
from pathlib import Path

# Install root is current working directory
install_root = Path.cwd()

# Use Install Space path
checklist_index = install_root / ".windsurf/workflows/data/review-gate/checklists/index.json"

with open(checklist_index) as f:
    checklists = json.load(f)
```
```

### Claude Skill 示例

```markdown
# Review Gate Skill

## Resources (Install Space)

This skill uses the following resources:

- Checklists: `{{install_root}}/.claude/skills/review-gate/resources/checklists/`
- Templates: `{{install_root}}/.claude/skills/review-gate/resources/templates/`

## Usage

```python
from pathlib import Path

install_root = Path.cwd()
checklist_dir = install_root / ".claude/skills/review-gate/resources/checklists"

for checklist_file in checklist_dir.glob("*.json"):
    print(f"Found checklist: {checklist_file.name}")
```
```

## 错误示例（禁止）

### ❌ 错误 1：引用 Source Space 路径

```markdown
# 错误：引用源仓库路径
- Checklists: `skills/review-gate/checklists/`
- Templates: `.shared/skill-creator/data/templates/`
```

### ❌ 错误 2：使用相对路径

```markdown
# 错误：相对路径
- Checklists: `../data/checklists/`
- Templates: `../../templates/`
```

### ❌ 错误 3：使用绝对路径

```markdown
# 错误：绝对路径
- Checklists: `/home/user/neo-skill/skills/review-gate/checklists/`
- Templates: `C:/Users/user/neo-skill/data/templates/`
```

## Install Root 占位符

所有 skill 文档必须使用 `{{install_root}}` 占位符：

| Target | Install Root Path |
|--------|-------------------|
| Windsurf | `{{install_root}}/.windsurf/workflows/data/{{skill-id}}/` |
| Claude | `{{install_root}}/.claude/skills/{{skill-id}}/resources/` |
| Cursor | `{{install_root}}/.cursor/commands/data/{{skill-id}}/` |
| GitHub | `{{install_root}}/.github/skills/{{skill-id}}/` |

## 运行时路径解析

在运行时，`{{install_root}}` 应该被解析为当前工作目录：

```python
import os
from pathlib import Path

# 方法 1：使用当前工作目录
install_root = Path.cwd()

# 方法 2：从环境变量获取
install_root = Path(os.getenv('INSTALL_ROOT', Path.cwd()))

# 方法 3：从配置文件获取
# install_root = Path(config.get('install_root'))
```

## 验证

使用 `omni-skill doctor` 命令验证路径正确性：

```bash
omni-skill doctor --skill review-gate --target windsurf
```

输出示例：

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
