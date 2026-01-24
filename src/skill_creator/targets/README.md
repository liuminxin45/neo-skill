# src/skill_creator/targets

本目录存放各目标平台（target）的输出渲染器。

## 目标平台

- **windsurf.py**：生成 `.windsurf/workflows/<skill>.md`（主目标）。
- **claude.py**：生成 `.claude/skills/<skill>/SKILL.md`（兼容输出）。
- **cursor.py**：生成 `.cursor/commands/<skill>.md`（兼容输出）。
- **github_skills.py**：生成 `.github/skills/<skill>/SKILL.md`（兼容输出）。
- **common.py**：公共渲染函数。

## 公共逻辑复用

所有 target 都使用 `common.py` 中的公共函数，避免代码重复：

- `_render_steps()` - 渲染 workflow steps
- `_render_resources()` - 渲染 references/scripts/assets
- `_render_libraries()` - 渲染推荐的第三方库信息
- `_render_prerequisites()` - 渲染 Prerequisites 部分（包含三方库）
- `_render_footer()` - 渲染页脚

### 三方库信息展示

**所有 target 都会展示推荐的三方库信息**，确保用户知道需要安装哪些依赖：

- ✅ **windsurf.py** - 在 Prerequisites 部分展示（包含 Python 版本检查）
- ✅ **claude.py** - 在 Prerequisites 部分展示
- ✅ **cursor.py** - 在 Prerequisites 部分展示
- ✅ **github_skills.py** - 在 Prerequisites 部分展示

这确保了无论用户使用哪个 AI 助手，都能获得完整的依赖信息和安装指导。

## 约定

- 目标平台输出目录属于派生物（generated outputs），不应手工编辑。
