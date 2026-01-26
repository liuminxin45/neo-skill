# skill-finder 使用指南

## 快速开始

### 1. 主动搜索模式（CLI）

```bash
# 运行 skill-finder
python -m skill_finder.cli

# 或使用 doctor 模式查看安装记录
python -m skill_finder.cli doctor
```

**交互示例**：
```
=== skill-finder ===
发现/匹配/安装第三方 skill 库

=== 需求收集（Level 1）===

你想实现什么目标？（一句话描述任务）: AI 辅助多文件代码重构
输入是什么？（文件/代码/数据/命令等） [默认: 任意]: Python 项目
运行环境？（OS/Shell/Runtime，如 Windows/Linux/Python/Node） [默认: 通用]: Linux
使用哪个 IDE/编辑器？（windsurf/cursor/vscode/generic）: windsurf

=== 匹配结果 ===
找到 1 个匹配的能力：

【1】Aider Code Editing (Aider)
- 描述: AI-powered multi-file code editing with context awareness and git integration
- 匹配原因: 匹配标签: code-refactoring; 支持 windsurf
- 置信度: 0.70
- README: https://github.com/aider-chat/aider/blob/main/README.md

选择要安装的能力 [1]: 1

=== 安装方式 ===
[1] 自动安装（默认）
[2] 手动安装（仅输出命令）
选择 [1]: 1

=== 自动安装 Aider ===
注意事项: 需要 Python 3.8+；需配置 OPENAI_API_KEY

执行命令：
pip install aider-chat

✓ 安装成功

=== 使用方式 ===
命令: aider
参数: [files...] [--model MODEL] [--message MSG]
工作目录: 项目根目录（需要 git repo）
示例:
  aider src/main.py src/utils.py
  aider --model gpt-4 --message 'refactor authentication logic'
  aider --yes --message 'add error handling to all API calls'

详细文档: https://github.com/aider-chat/aider/blob/main/README.md
```

---

### 2. 被动推荐模式（编程接口）

```python
from skill_finder.models import SearchQuery
from skill_finder.recommender import Recommender

# 创建推荐器
recommender = Recommender()

# 构建查询
query = SearchQuery(
    goal="多文件代码编辑",
    tags=["code-generation", "multi-file-editing"],
    ide="windsurf"
)

# 获取推荐
result = recommender.recommend(query)

if result.matches:
    match = result.matches[0]
    print(f"推荐: {match.unit.name}")
    print(f"置信度: {match.score:.2f}")
    print(f"README: {match.package.docs.readme}")
else:
    print(f"无推荐: {result.rejection_reason}")
```

---

### 3. 诊断与 Trace

```python
from skill_finder.models import SearchQuery
from skill_finder.doctor import Doctor

doctor = Doctor()

# 查看匹配 trace
query = SearchQuery(goal="git commit 生成", tags=["git-commit"], ide="windsurf")
trace = doctor.trace_match(query)
print(trace)

# 查看安装记录
records = doctor.show_install_records(n=5)
print(records)

# 获取修复建议
suggestion = doctor.suggest_fix("gh:aider-chat/aider")
print(suggestion)
```

**输出示例**：
```
=== skill-finder Doctor Trace ===

【匹配 Trace】
- Query: goal="git commit 生成", tags=['git-commit'], ide="windsurf"
- 粗筛命中: 1 个候选
  - Tag 'git-commit': 1 个 unit
- 精排结果:
  1. gh:aider-chat/aider#git-commit (score=0.70)
     - 匹配标签: git-commit, 支持 windsurf
- 最终返回: Top 1

【安装记录（最近 5 条）】
1. 2026-01-26 13:45:23 | gh:aider-chat/aider#code-edit | auto | ✓ success
```

---

## Registry 管理

### 添加新的 Package

1. 创建 package 文件：`data/third_party/packages/gh_owner_repo.json`

```json
{
  "package_id": "gh:owner/repo",
  "name": "Package Name",
  "description": "Package description",
  "source": {
    "type": "git",
    "repo": "owner/repo",
    "ref": "main"
  },
  "docs": {
    "readme": "https://github.com/owner/repo/blob/main/README.md"
  },
  "supported_ides": ["windsurf", "cursor"],
  "install": {
    "method": "pip",
    "auto_install_cmd": "pip install package-name",
    "manual_install_cmd": "pip install package-name",
    "uninstall_cmd": "pip uninstall -y package-name"
  },
  "units": ["gh:owner/repo#unit-a"],
  "trust_level": "trusted"
}
```

2. 创建 unit 文件：`data/third_party/units/gh_owner_repo#unit-a.json`

```json
{
  "unit_id": "gh:owner/repo#unit-a",
  "package_id": "gh:owner/repo",
  "name": "Unit Name",
  "description": "Unit description",
  "capability_tags": ["tag1", "tag2"],
  "keywords": ["keyword1", "keyword2"],
  "ide_support": ["windsurf", "cursor"],
  "entrypoints": [{
    "command": "command-name",
    "args": "[options]",
    "examples": ["command-name --help"]
  }]
}
```

3. 校验 Registry

```bash
python tools/lint_third_party_registry.py
```

4. 重建索引

```bash
python tools/build_third_party_indexes.py
```

---

## 测试

运行完整测试：

```bash
python test_skill_finder.py
```

**预期输出**：
```
skill-finder 端到端测试

=== 测试 Registry ===
✓ Package 加载成功: Aider
✓ Unit 加载成功: Aider Code Editing
✓ Tag 搜索成功: 1 个结果

=== 测试 Matcher ===
✓ 匹配成功: 1 个结果
  - Aider Code Editing (score=0.70)

=== 测试 Recommender ===
✓ 推荐成功: Aider Code Editing
  置信度: 0.70

=== 测试 Doctor ===
[trace 输出...]

==================================================
✓ 所有测试通过
==================================================
```

---

## 架构说明

### 核心模块

- **`models.py`**: 数据结构定义（Pydantic models）
- **`registry.py`**: Registry 加载与索引查询
- **`matcher.py`**: 两阶段匹配算法（粗筛 + 精排）
- **`installer.py`**: 安装执行器（auto/manual 模式）
- **`interview.py`**: 两级提问逻辑
- **`install_record.py`**: 安装记录管理
- **`recommender.py`**: 被动推荐接口（高置信度 >= 0.7）
- **`cli.py`**: 主动搜索 CLI 入口
- **`doctor.py`**: 诊断与 trace

### 匹配算法

**两阶段匹配**：
1. **粗筛**：倒排索引命中（tag/keyword/ide）
2. **精排**：置信度评分
   - Tag 覆盖率：60%
   - Keyword 匹配：30%
   - IDE 支持：10%
   - 约束过滤：降权因子

**置信门槛**：
- 主动搜索：>= 0.6（60%）
- 被动推荐：>= 0.7（70%）

**拒绝原因分类**：
- `no_candidates_by_tag`
- `candidates_but_no_ide_support`
- `candidates_but_incompatible_env`
- `insufficient_info`

---

## 安装记录

所有安装行为记录到：`~/.omni-skill/install_records.json`

**记录字段**：
- `timestamp`: 安装时间
- `unit_id`: 能力单元 ID
- `package_id`: 包 ID
- `install_mode`: auto/manual
- `executed`: true/false
- `method`: git/pip/npm
- `commands`: 执行的命令
- `result`: success/failed/skipped
- `error_summary`: 错误摘要（如有）
- `docs_links`: 文档链接

---

## 常见问题

### Q: 如何添加新的第三方 skill？
A: 创建 package + unit JSON 文件 → 运行 linter 校验 → 重建索引

### Q: 匹配不到结果怎么办？
A: 使用 `doctor.trace_match()` 查看匹配 trace，检查 tags/keywords 是否正确

### Q: 安装失败怎么办？
A: 使用 `doctor.suggest_fix(package_id)` 获取修复建议，或查看 install_records.json

### Q: 如何调整匹配阈值？
A: 修改 `Matcher(min_score=0.6)` 或 `Recommender(min_score=0.7)` 的参数

---

## 设计原则

1. **宁缺毋滥**：低于阈值必须拒绝，禁止强行匹配
2. **诚实反馈**：明确告知拒绝原因与缺口信息
3. **可追溯性**：所有安装行为记录，便于 doctor 排障
4. **轻量集成**：skill-creator 集成不打断主流程
5. **文件化索引**：不引入数据库，按需加载避免 token 膨胀
