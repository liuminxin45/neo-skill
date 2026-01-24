# Neo-Skill 架构规则（强制约束）

## 版本：2.0
## 生效日期：2026-01-24

---

## 0. 核心原则

本架构采用**分层索引 + 文件化数据包**体系，确保：
- **输出一致性**：Output Packs 不变量
- **低 Token 消耗**：按需加载 top_k 文件
- **可扩展性**：新增能力不触发大重构
- **可迁移性**：安装后自包含，不依赖源仓库

---

## 1. 强约束：禁止单文件脚本（Monolith）

### 1.1 规则

**禁止**生成任何"单文件可执行脚本"作为最终 skill 产物。

**原因**：
- 违反分层索引原则
- 破坏可扩展性
- 难以维护和复用
- 无法利用数据包体系

### 1.2 允许的形态

✅ **Structured Skill**（唯一允许）：
- 分层索引文件（index.json）
- 被索引的数据文件（items/*.json）
- Skill 主文档（{{skill-id}}.md）
- 运行时依赖的最小闭包

❌ **Monolith Script**（严格禁止）：
- 单个 Python/Shell 脚本包含所有逻辑
- 不使用索引系统
- 硬编码数据和逻辑

### 1.3 AI 指令

skill-creator 必须明确告知 AI：
- **不得输出 Monolith**
- **不得建议 Monolith 作为解决方案**
- **即使更简单也必须使用分层索引结构**

### 1.4 扩展点（预留但不实现）

架构预留 `Renderer` 接口用于未来扩展，但当前版本：
- **只实现 Structured Renderer**
- **不实现 Monolith Renderer**

---

## 2. 路径空间：Source Space vs Install Space

### 2.1 术语定义

#### Source Space（源文件空间）
- **定义**：skill-creator/开发仓库里的模板与数据源路径
- **用途**：仅用于构建/安装阶段
- **位置**：
  - `skills/{{skill-id}}/` - skill 源文件
  - `.shared/skill-creator/data_packs/` - 数据包源
  - `src/skill_creator/` - 生成器源码
- **禁止**：运行时依赖 Source Space 路径

#### Install Space（安装后运行空间）
- **定义**：{{agent-id}} 目录下的已物化文件路径
- **用途**：仅用于运行时
- **位置**：
  - `.windsurf/workflows/{{skill-id}}.md` - Windsurf skill
  - `.windsurf/workflows/data/{{skill-id}}/` - Windsurf 数据
  - `.claude/skills/{{skill-id}}/` - Claude skill
  - `.cursor/commands/{{skill-id}}.md` - Cursor skill
  - `.github/skills/{{skill-id}}/` - GitHub skill
- **要求**：所有索引路径必须指向 Install Space

### 2.2 路径占位符规范

#### Install Root 占位符

Skill 文档中的索引路径必须使用占位符：

```markdown
# Windsurf
{{install_root}}/.windsurf/workflows/data/{{skill-id}}/

# Claude
{{install_root}}/.claude/skills/{{skill-id}}/resources/

# Cursor
{{install_root}}/.cursor/commands/data/{{skill-id}}/

# GitHub
{{install_root}}/.github/skills/{{skill-id}}/
```

#### 禁止的路径形式

❌ **绝对路径**：`/home/user/neo-skill/skills/...`
❌ **相对路径**：`../skills/...`, `../../data/...`
❌ **源仓库路径**：`skills/{{skill-id}}/...`, `.shared/...`

### 2.3 根因说明

**问题**：新增 skill 后，AI 在 skill 文档中写的索引路径指向"install 之前的源文件目录"。

**后果**：
- 部署产物不自包含
- 隔离性差
- 迁移/发布不可靠
- 运行时依赖源仓库

**正确做法**：
1. 定义两个路径空间（Source vs Install）
2. install 时物化/拷贝依赖闭包到 Install Space
3. skill 文档只引用 Install Space 路径
4. 运行时索引解析器以 Install Space 为 root

---

## 3. 依赖闭包（Dependency Closure）

### 3.1 定义

每个 skill 的运行期依赖闭包包括：

1. **Skill 主文档**：`{{skill-id}}.md`
2. **索引文件**：skill 引用的 `index.json` 等
3. **索引命中的 items**：top_k 或固定集合的数据文件
4. **必需不变量**：
   - Universal schema
   - Output packs
   - Minimal checklists
5. **三方库声明**：`requirements.txt` 片段或元数据
6. **References/Scripts/Assets**：skill 特定的资源文件

### 3.2 最小闭包原则

**要求**：
- ✅ 只拷贝该 skill 需要的最小闭包
- ❌ 不原封不动复制整个源目录
- ❌ 不拷贝未被引用的文件

**策略**：
- 按索引层级递归解析
- 收集所有被引用的文件
- 去重并验证完整性
- 只拷贝收集到的文件

### 3.3 闭包解析算法

```
1. 从 skill 主文档开始
2. 解析文档中的索引引用
3. 加载索引文件，解析 items
4. 递归解析 items 中的嵌套引用
5. 收集所有文件路径（Source Space）
6. 映射到 Install Space 路径
7. 验证闭包完整性
8. 返回拷贝清单
```

---

## 4. Install 流程

### 4.1 高层流程

```
┌─────────────────────────────────────┐
│ 1. 解析 skill 依赖闭包              │
│    - 从 skillspec.json 开始         │
│    - 递归解析索引引用               │
│    - 收集所有依赖文件               │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 2. 物化/拷贝到 Install Space        │
│    - 创建目标目录结构               │
│    - 拷贝最小闭包文件               │
│    - 保持相对路径结构               │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 3. 生成 Install Manifest            │
│    - 记录拷贝的文件映射             │
│    - 记录版本/哈希                  │
│    - 记录 install_root              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 4. 校验                             │
│    - 禁止 source path 泄漏          │
│    - 索引可解析                     │
│    - 必要不变量齐全                 │
└─────────────────────────────────────┘
```

### 4.2 Install Manifest 格式

```json
{
  "version": "1.0",
  "skill_id": "review-gate",
  "install_root": ".windsurf/workflows/data/review-gate",
  "installed_at": "2026-01-24T12:00:00Z",
  "files": [
    {
      "source": "skills/review-gate/skillspec.json",
      "target": ".windsurf/workflows/data/review-gate/skillspec.json",
      "hash": "sha256:..."
    }
  ],
  "dependencies": {
    "libraries": ["requests", "pyyaml"],
    "data_packs": ["universal/output_packs", "universal/minimal_checklists"]
  }
}
```

### 4.3 校验规则

**必须通过**：
- ✅ 所有索引路径指向 Install Space
- ✅ 所有被引用的文件存在
- ✅ 必要不变量文件齐全
- ✅ 没有 source path 泄漏

**如果失败**：
- ❌ 报错并提示重新 install
- ❌ 不允许 silent fallback 到源路径

---

## 5. Skill 文档索引写法规范

### 5.1 正确示例

```markdown
# Review Gate Skill

## Data Packs

This skill uses the following data packs:

- Checklists: `{{install_root}}/.windsurf/workflows/data/review-gate/checklists/`
- Templates: `{{install_root}}/.windsurf/workflows/data/review-gate/templates/`

## Usage

Load checklist index:
```python
import json
from pathlib import Path

install_root = Path.cwd()  # 或从环境变量获取
checklist_index = install_root / ".windsurf/workflows/data/review-gate/checklists/index.json"

with open(checklist_index) as f:
    checklists = json.load(f)
```
```

### 5.2 错误示例（禁止）

```markdown
# ❌ 错误：引用源仓库路径
- Checklists: `skills/review-gate/checklists/`
- Templates: `../data/templates/`

# ❌ 错误：绝对路径
- Checklists: `/home/user/neo-skill/skills/review-gate/checklists/`

# ❌ 错误：相对路径
- Checklists: `../../skills/review-gate/checklists/`
```

---

## 6. 三方库规则

### 6.1 自动采用，无需确认

**规则**：
- ✅ 系统/AI 自动判断需要使用三方库时，**不得要求用户确认**
- ✅ 不要求用户选择 A/B/C 或进行额外交互
- ✅ 选择策略必须可解释、可追溯、可复现

**原因**：
- 降低交互负担
- 提高自动化程度
- 保持生成流程流畅

### 6.2 结果汇报（强制）

**必须在最终输出中列出**：

```markdown
## 使用的第三方库

### 1. requests
- **版本策略**：>=2.28.0
- **用途**：发起 HTTP 请求获取 RSS feed
- **安装方式**：`pip install requests>=2.28.0`
- **文档链接**：
  - PyPI: https://pypi.org/project/requests/
  - GitHub: https://github.com/psf/requests
  - Docs: https://requests.readthedocs.io/

### 2. feedparser
- **版本策略**：>=6.0.0
- **用途**：解析 RSS/Atom feed 格式
- **安装方式**：`pip install feedparser>=6.0.0`
- **文档链接**：
  - PyPI: https://pypi.org/project/feedparser/
  - Docs: https://feedparser.readthedocs.io/

### Fallback 方案（可选）
- 如果不使用 `feedparser`，可使用标准库 `xml.etree.ElementTree` 手动解析 XML
- 如果不使用 `requests`，可使用标准库 `urllib` 发起 HTTP 请求
```

### 6.3 最小闭包与可迁移性

**要求**：
- ✅ 三方库声明必须包含在 Install Space
- ✅ 生成 `requirements.txt` 或等价文件
- ✅ 安装后依然满足最小闭包原则
- ✅ 可迁移到其他环境

---

## 7. Doctor/Debug 诊断

### 7.1 诊断命令

```bash
omni-skill doctor --skill <skill-id>
```

### 7.2 诊断输出要求

```
=== Skill Diagnostic Report ===

Skill ID: review-gate
Install Root: .windsurf/workflows/data/review-gate
Installed At: 2026-01-24T12:00:00Z

--- Dependency Closure ---
✓ Skill document: .windsurf/workflows/review-gate.md
✓ Skillspec: .windsurf/workflows/data/review-gate/skillspec.json
✓ Checklists index: .windsurf/workflows/data/review-gate/checklists/index.json
✓ Checklist items: 5 files
✓ Universal schema: .windsurf/workflows/data/review-gate/universal/schema.json

Total files: 12

--- Path Validation ---
✓ No source path leakage detected
✓ All index paths point to Install Space
✓ All referenced files exist

--- Dependencies ---
Libraries:
  - requests>=2.28.0
  - pyyaml>=6.0

Data Packs:
  - universal/output_packs
  - universal/minimal_checklists

--- Issues ---
None

=== Diagnostic Complete ===
```

### 7.3 错误检测

**必须检测**：
- ❌ Source path 泄漏（引用了 `skills/` 或 `.shared/` 路径）
- ❌ 缺失文件（索引引用的文件不存在）
- ❌ 必要不变量缺失（universal schema、output packs 等）
- ❌ 循环依赖
- ❌ 路径越界（引用了 Install Space 之外的路径）

---

## 8. 明确不做项

### 8.1 禁止事项

❌ **不实现单文件脚本（Monolith）**
- 即使更简单也禁止
- 不提供 Monolith Renderer

❌ **不在运行期依赖源仓库路径**
- 运行时只依赖 Install Space
- 不允许 fallback 到 Source Space

❌ **不复制整个源目录**
- 必须最小闭包
- 只拷贝被引用的文件

❌ **不在生成过程中要求用户确认三方库选型**
- 自动采用
- 结果汇报时告知

---

## 9. 验收标准

### 9.1 功能验收

✅ **新增 skill 后，install 产物自包含**
- 运行时不依赖源路径
- 可迁移到其他环境

✅ **{{skill-id}}.md 的索引路径只指向 install_root**
- 使用占位符
- 不引用源路径

✅ **缺失依赖会在 install 或 doctor 阶段明确报错**
- 不允许 silent fallback
- 提供清晰的错误信息

✅ **只拷贝最小闭包文件**
- 不会把整个 skills/ 或 data/ 原样搬过去
- 按需拷贝

✅ **若使用三方库：不做用户确认**
- 自动采用
- 最终汇报完整列出库/用途/安装方式/链接
- 安装后依然满足最小闭包与可迁移性

### 9.2 质量验收

✅ **可追溯性**
- Install manifest 记录完整
- Doctor 输出清晰

✅ **可复现性**
- 相同输入产生相同输出
- 版本/哈希可验证

✅ **可维护性**
- 代码结构清晰
- 文档完整

---

## 10. 术语表

| 术语 | 定义 |
|------|------|
| **Source Space** | 源文件空间，仅用于构建/安装阶段 |
| **Install Space** | 安装后运行空间，仅用于运行时 |
| **Dependency Closure** | 依赖闭包，skill 运行时需要的所有文件 |
| **Install Root** | 安装根目录，Install Space 的根路径 |
| **Install Manifest** | 安装清单，记录拷贝的文件映射和元数据 |
| **Monolith** | 单文件脚本，严格禁止 |
| **Structured Skill** | 分层索引 + 文件化数据包，唯一允许的形态 |
| **Minimal Closure** | 最小闭包，只拷贝必需的文件 |

---

## 11. 版本历史

- **v2.0** (2026-01-24): 新增 Source/Install Space 规则，禁止 Monolith，三方库自动采用
- **v1.0** (2026-01-23): 初始版本，基础架构规则

---

**本规则为强制约束，所有 skill-creator 生成的 skill 必须遵守。**
