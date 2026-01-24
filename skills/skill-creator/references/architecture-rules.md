# Skill Creator 架构规则（强制约束）

## 重要提示：AI 必须遵守以下规则

---

## 1. 禁止单文件脚本（Monolith）

### 规则

**严格禁止**生成任何"单文件可执行脚本"作为最终 skill 产物。

### 原因

- 违反分层索引原则
- 破坏可扩展性
- 难以维护和复用
- 无法利用数据包体系

### 允许的形态

✅ **Structured Skill**（唯一允许）：
- 分层索引文件（index.json）
- 被索引的数据文件（items/*.json）
- Skill 主文档（{{skill-id}}.md）
- 运行时依赖的最小闭包

❌ **Monolith Script**（严格禁止）：
- 单个 Python/Shell 脚本包含所有逻辑
- 不使用索引系统
- 硬编码数据和逻辑

### AI 指令

**不得输出 Monolith**
**不得建议 Monolith 作为解决方案**
**即使更简单也必须使用分层索引结构**

---

## 2. Install Space 路径规范

### 路径空间定义

#### Source Space（源文件空间）
- 仅用于构建/安装阶段
- 位置：`skills/`, `.shared/`, `src/`
- **禁止**：运行时依赖

#### Install Space（安装后运行空间）
- 仅用于运行时
- 位置：`.windsurf/`, `.claude/`, `.cursor/`, `.github/`
- **要求**：所有索引路径必须指向此空间

### 路径写法规范

✅ **正确**：使用 Install Space 占位符
```markdown
- Data: `{{install_root}}/.windsurf/workflows/data/{{skill-id}}/`
- Index: `{{install_root}}/.windsurf/workflows/data/{{skill-id}}/index.json`
```

❌ **错误**：引用 Source Space 路径
```markdown
- Data: `skills/{{skill-id}}/data/`
- Index: `.shared/skill-creator/data_packs/`
- Relative: `../data/`, `../../skills/`
```

### 验证

使用 `omni-skill doctor --skill <skill-id>` 验证路径正确性。

---

## 3. 三方库规则

### 自动采用，无需确认

**规则**：
- ✅ 自动判断并采用三方库
- ❌ 不要求用户确认
- ❌ 不要求用户选择 A/B/C

### 结果汇报（强制）

**必须在最终输出中列出**：

```markdown
## 使用的第三方库

### 1. requests
- **版本策略**：>=2.28.0
- **用途**：发起 HTTP 请求
- **安装方式**：`pip install requests>=2.28.0`
- **文档链接**：
  - PyPI: https://pypi.org/project/requests/
  - Docs: https://requests.readthedocs.io/

### 2. feedparser
- **版本策略**：>=6.0.0
- **用途**：解析 RSS/Atom feed
- **安装方式**：`pip install feedparser>=6.0.0`
- **文档链接**：
  - PyPI: https://pypi.org/project/feedparser/
  - Docs: https://feedparser.readthedocs.io/

### Fallback 方案（可选）
- 如果不使用 `requests`，可使用标准库 `urllib`
```

---

## 4. 依赖闭包原则

### 最小闭包

**要求**：
- ✅ 只拷贝该 skill 需要的最小闭包
- ❌ 不原封不动复制整个源目录
- ❌ 不拷贝未被引用的文件

### 闭包内容

每个 skill 的依赖闭包包括：
1. Skill 主文档（{{skill-id}}.md）
2. 索引文件（index.json 等）
3. 索引命中的 items
4. 必需不变量（universal schema, output packs, minimal checklists）
5. 三方库声明（requirements.txt）
6. References/Scripts/Assets

---

## 5. 生成流程

### 步骤

1. **分析需求**：提取任务类型、输出形态、约束条件
2. **收集信息**：对话式收集（≤10 问）
3. **设计系统**：分层索引 + 文件化数据包
4. **生成 SkillSpec**：写入 `skills/<name>/skillspec.json`
5. **生成输出**：为所有 AI 目标生成文档
6. **验证**：Schema 校验 + Dry-run

### 禁止事项

❌ 不生成单文件脚本
❌ 不在文档中引用 Source Space 路径
❌ 不要求用户确认三方库选型
❌ 不复制整个源目录

---

## 6. 验收标准

### 功能验收

✅ Skill 产物自包含
✅ 索引路径只指向 Install Space
✅ 使用分层索引结构
✅ 只拷贝最小闭包文件

### 质量验收

✅ 可追溯性：Install manifest 记录完整
✅ 可复现性：相同输入产生相同输出
✅ 可维护性：代码结构清晰，文档完整

---

## 7. 示例

### 正确的 Skill 结构

```
skills/review-gate/
├── skillspec.json          # Skill 定义
├── references/             # 规则文档
│   └── checklist-rules.md
├── scripts/                # 确定性脚本
│   └── validate.py
└── assets/                 # 数据文件
    └── templates/
```

### 正确的索引引用

```json
{
  "version": "1.0",
  "items": {
    "checklist-1": {
      "file": "{{install_root}}/.windsurf/workflows/data/review-gate/checklists/checklist-1.json"
    }
  }
}
```

---

**本规则为强制约束，所有 AI 生成的 skill 必须遵守。**

详见：`docs/ARCHITECTURE_RULES.md`
