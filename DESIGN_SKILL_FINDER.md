# skill-finder 完整工程设计文档

## 一、总体架构

### 1.1 目录结构
```
neo-skill/
├── skills/skill-finder/              # Skill 定义
│   ├── skillspec.json
│   └── references/
│       ├── matching-algorithm.md
│       ├── install-modes.md
│       ├── interview-protocol.md
│       └── registry-schema.md
│
├── src/skill_finder/                 # 核心模块
│   ├── __init__.py
│   ├── models.py                     # ✓ 已创建
│   ├── cli.py                        # 主动搜索入口
│   ├── recommender.py                # 被动推荐接口
│   ├── matcher.py                    # 匹配算法
│   ├── installer.py                  # 安装执行器
│   ├── registry.py                   # Registry 加载
│   ├── interview.py                  # 两级提问
│   ├── install_record.py             # 安装记录
│   └── doctor.py                     # 诊断 trace
│
├── data/third_party/                 # Registry 数据
│   ├── packages/
│   │   └── gh_aider-chat_aider.json
│   ├── units/
│   │   ├── gh_aider-chat_aider#code-edit.json
│   │   └── gh_aider-chat_aider#git-commit.json
│   └── indexes/
│       ├── units.by_tag.json
│       ├── units.by_keyword.json
│       ├── units.by_ide.json
│       ├── packages.all.json
│       └── units.all.json
│
└── tools/
    ├── lint_third_party_registry.py
    └── build_third_party_indexes.py
```

---

## 二、核心数据结构（已实现）

参见 `src/skill_finder/models.py`：
- **SkillPackage**: 安装载体（package 级）
- **SkillUnit**: 能力单元（匹配维度）
- **InstallerSpec**: 安装规范（auto/manual 两种模式）
- **SearchQuery/SearchResult**: 搜索接口
- **InstallRecord**: 安装记录（可追溯）

---

## 三、Registry 文件格式

### 3.1 Package 样例
```json
{
  "package_id": "gh:aider-chat/aider",
  "name": "Aider",
  "description": "AI pair programming in terminal",
  "source": {"type": "git", "repo": "aider-chat/aider", "ref": "main"},
  "docs": {
    "readme": "https://github.com/aider-chat/aider/blob/main/README.md",
    "homepage": "https://aider.chat"
  },
  "supported_ides": ["windsurf", "cursor", "generic"],
  "install": {
    "method": "pip",
    "auto_install_cmd": "pip install aider-chat",
    "manual_install_cmd": "pip install aider-chat",
    "uninstall_cmd": "pip uninstall -y aider-chat",
    "notes": "需要 Python 3.8+；需配置 OPENAI_API_KEY"
  },
  "units": ["gh:aider-chat/aider#code-edit", "gh:aider-chat/aider#git-commit"],
  "trust_level": "trusted"
}
```

### 3.2 Unit 样例
```json
{
  "unit_id": "gh:aider-chat/aider#code-edit",
  "package_id": "gh:aider-chat/aider",
  "name": "Aider Code Editing",
  "description": "AI-powered multi-file code editing",
  "capability_tags": ["code-generation", "code-refactoring", "multi-file-editing"],
  "keywords": ["aider", "ai coding", "refactor"],
  "ide_support": ["windsurf", "cursor", "generic"],
  "entrypoints": [{
    "command": "aider",
    "args": "[files...] [--model MODEL]",
    "cwd": "git repo root",
    "examples": ["aider src/main.py", "aider --model gpt-4 --message 'refactor'"]
  }],
  "usage_notes": "终端运行，对话式编辑多文件。自动追踪依赖，生成 git commit。"
}
```

### 3.3 索引样例
```json
// data/third_party/indexes/units.by_tag.json
{
  "code-generation": ["gh:aider-chat/aider#code-edit"],
  "code-refactoring": ["gh:aider-chat/aider#code-edit"],
  "git-commit": ["gh:aider-chat/aider#git-commit"]
}
```

---

## 四、匹配算法流程

### 4.1 两阶段匹配
```
输入: SearchQuery (goal, tags, keywords, ide, env, constraints)
  ↓
【阶段 1: 粗筛】
  - 倒排索引命中: units.by_tag + units.by_keyword + units.by_ide
  - 返回候选 unit_id 列表
  ↓
【阶段 2: 精排】
  - Tag 覆盖率 (权重 0.6)
  - Keyword 匹配 (权重 0.3)
  - IDE 支持 (权重 0.1，不支持降权 0.2)
  - 约束过滤 (env/constraints 冲突降权 0.3-0.5)
  ↓
【置信门槛】
  - score >= 0.6: 返回 Top 1-3
  - score < 0.6: 拒绝并分类原因
    - no_candidates_by_tag
    - candidates_but_no_ide_support
    - candidates_but_incompatible_env
    - insufficient_info
```

### 4.2 拒绝原因分类（必须）
- **no_candidates_by_tag**: 未找到匹配的能力标签或关键词
- **candidates_but_no_ide_support**: 找到候选但均不支持目标 IDE
- **candidates_but_incompatible_env**: 找到候选但不满足环境/约束
- **insufficient_info**: 候选置信度不足，需补充信息

---

## 五、安装流程

### 5.1 两种安装模式
```
【模式 1: 自动安装（默认）】
  1. 执行 package.install.auto_install_cmd
  2. 捕获 stdout/stderr
  3. 记录结果 (success/failed)
  4. 写入 install_record (executed=true)
  5. 输出使用方式 + README 链接

【模式 2: 手动安装】
  1. 输出 package.install.manual_install_cmd
  2. 输出 install.notes（如有）
  3. 记录 (executed=false, result=skipped)
  4. 任务结束，不执行安装
```

### 5.2 install_record 结构
```json
{
  "timestamp": "2026-01-26T12:30:00",
  "unit_id": "gh:aider-chat/aider#code-edit",
  "package_id": "gh:aider-chat/aider",
  "install_mode": "auto",
  "executed": true,
  "method": "pip",
  "commands": "pip install aider-chat",
  "result": "success",
  "error_summary": null,
  "docs_links": {"readme": "https://..."}
}
```

存储位置: `~/.omni-skill/install_records.json`

---

## 六、两级提问协议

### 6.1 Level 1（固定 3-4 问）
1. **goal** (必答): 你想实现什么目标？
2. **input** (选答): 输入是什么？
3. **env** (选答): 运行环境？
4. **ide** (必答): 使用哪个 IDE？

### 6.2 Level 2（缺口驱动，最多 1-2 问）
- 仅当 Level 1 信息不足时触发
- 示例：goal 太模糊 → 追问细节
- 示例：未提约束 → 询问硬约束

---

## 七、skill-creator 集成

### 7.1 集成点
```python
# skill-creator workflow 修改点
def run():
    ctx = collect_level1()  # 现有流程
    
    # === 新增：调用 skill-finder ===
    from skill_finder.recommender import Recommender
    rec = Recommender().recommend(SearchQuery(
        goal=ctx["goal"],
        tags=ctx["tags"],
        ide=ctx["ide"],
        constraints=ctx["constraints"]
    ))
    
    # === Plan 中轻量展示 ===
    if rec.matches:
        print("\n【第三方能力推荐】")
        top = rec.matches[0]
        print(f"- {top.unit.name} ({top.package.name})")
        print(f"- 匹配原因: {', '.join(top.reasons)}")
        print(f"- README: {top.package.docs.readme}")
        print(f"- 可用 skill-finder 安装（默认自动/可选手动）")
        
        choice = input("\n是否安装？(y/n, 默认 n): ")
        if choice.lower() == 'y':
            # 执行安装
            from skill_finder.installer import Installer
            Installer().install(top, mode="auto")
            return  # 结束，不生成自研 skill
    
    # 用户选择不安装或无推荐 → 继续自研 skill
    generate_plan(ctx)
```

### 7.2 不打断主流程
- 推荐仅在 Plan 阶段轻量展示
- 用户选择安装才执行
- 否则继续生成自研 skill

---

## 八、Doctor / Debug

### 8.1 skill-finder doctor 输出
```
=== skill-finder Doctor Trace ===

【匹配 Trace】
- Query: goal="AI 代码编辑", tags=["code-generation"], ide="windsurf"
- 粗筛命中: 3 个候选 (units.by_tag["code-generation"])
- 精排结果:
  1. gh:aider-chat/aider#code-edit (score=0.85)
     - 匹配标签: code-generation, multi-file-editing
     - 支持 windsurf
  2. gh:cursor-sh/cursor-rules#code-style (score=0.45) [低于阈值]
- 最终返回: Top 1

【安装记录（最近 5 条）】
1. 2026-01-26 12:30 | gh:aider-chat/aider#code-edit | auto | success
2. 2026-01-25 10:15 | gh:some/tool#unit | auto | failed (pip timeout)
3. 2026-01-24 09:00 | gh:other/lib#feature | manual | skipped

【冲突/异常建议】
- 若安装失败，尝试重装: pip uninstall -y aider-chat && pip install aider-chat
```

### 8.2 skill-creator doctor 增强
```
【自研 Skill 诊断】
- install_root: ~/.claude/skills/my-skill/
- 拷贝闭包: 15 个文件
- 源路径泄漏检查: 无泄漏 ✓
```

---

## 九、Linter & Index Builder

### 9.1 Linter 校验点
```bash
python tools/lint_third_party_registry.py

【校验项】
✓ Package 字段完整性 (package_id, name, install.*)
✓ Unit 字段完整性 (unit_id, package_id, capability_tags, entrypoints)
✓ package_id 格式: gh:owner/repo | pip:pkg | npm:pkg
✓ unit_id 格式: <package_id>#<unit-name>
✓ unit.package_id 引用存在
✓ package.units 引用存在
✓ docs.readme 链接格式 (http/https)
✓ trust_level 枚举值合法
✓ entrypoints.command 非空
✗ 错误: units/gh_xxx#yyy.json 的 package_id 不存在
```

### 9.2 Index Builder
```bash
python tools/build_third_party_indexes.py

【输出】
- data/third_party/indexes/units.by_tag.json
- data/third_party/indexes/units.by_keyword.json
- data/third_party/indexes/units.by_ide.json
- data/third_party/indexes/packages.all.json
- data/third_party/indexes/units.all.json

【逻辑】
- 扫描 packages/*.json + units/*.json
- 大小写归一、去重
- 可重复构建（幂等）
```

---

## 十、端到端示例

### 10.1 主动搜索 - 自动安装成功
```
$ python -m skill_finder.cli

=== 需求收集（Level 1）===
你想实现什么目标？: AI 辅助多文件代码重构
输入是什么？ [默认: 任意]: Python 项目
运行环境？ [默认: 通用]: Linux
使用哪个 IDE？: windsurf

=== 匹配结果 ===
找到 1 个匹配的能力：

【1】Aider Code Editing (Aider)
- 描述: AI-powered multi-file code editing
- 匹配原因: 匹配标签 code-generation, code-refactoring; 支持 windsurf
- 置信度: 0.85
- README: https://github.com/aider-chat/aider/blob/main/README.md

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
命令: aider [files...] [--model MODEL]
工作目录: git repo root
示例:
  aider src/main.py
  aider --model gpt-4 --message 'refactor authentication logic'

详细文档: https://github.com/aider-chat/aider/blob/main/README.md
```

### 10.2 主动搜索 - 手动安装
```
选择 [1]: 2

=== 手动安装 Aider ===
pip install aider-chat

注意事项：
需要 Python 3.8+；需配置 OPENAI_API_KEY

已记录安装指令。请手动执行上述命令。
```

### 10.3 主动搜索 - 未找到
```
你想实现什么目标？: 自动生成 PPT
...

=== 匹配结果 ===
✗ 未找到匹配的第三方能力

拒绝原因: 未找到匹配的能力标签或关键词
建议: 尝试使用 skill-creator 创建自研 skill
```

### 10.4 被动推荐（skill-creator 集成）
```
$ /skill-creator

... Level 1 收集 ...

=== Plan ===

【第三方能力推荐】
- Aider Code Editing (Aider)
- 匹配原因: 匹配标签 code-generation, multi-file-editing; 支持 windsurf
- README: https://github.com/aider-chat/aider/blob/main/README.md
- 可用 skill-finder 安装（默认自动/可选手动）

是否安装？(y/n, 默认 n): n

继续生成自研 skill...
```

### 10.5 Doctor Trace - 安装失败
```
$ python -m skill_finder.doctor

=== 安装记录 ===
2026-01-26 14:20 | gh:some/tool#unit | auto | failed
错误摘要: pip: command not found

【建议】
- 检查 Python/pip 是否安装
- 尝试手动安装: pip install some-tool
- 或使用 manual 模式获取完整指令
```

---

## 十一、明确非目标

1. **不实现 Monolith 单文件脚本**（自研 skill）
2. **不保证第三方 skill 间绝对不冲突**（冲突按重装策略处理）
3. **不强制把第三方 skill 统一到 omni-skill 指令体系**
4. **不抓取并注入 README 全文**（只存链接 + 可选微摘要）
5. **不强行匹配**；无结果必须直说
6. **不引入 SQL/数据库**（文件化索引）
7. **不做隔离安装**（全局安装，doctor 提供重装建议）

---

## 十二、下一步实施清单

### 核心模块
- [x] `src/skill_finder/models.py`
- [ ] `src/skill_finder/registry.py`
- [ ] `src/skill_finder/matcher.py`
- [ ] `src/skill_finder/installer.py`
- [ ] `src/skill_finder/interview.py`
- [ ] `src/skill_finder/install_record.py`
- [ ] `src/skill_finder/recommender.py`
- [ ] `src/skill_finder/cli.py`
- [ ] `src/skill_finder/doctor.py`

### Registry 数据
- [ ] `data/third_party/packages/gh_aider-chat_aider.json`
- [ ] `data/third_party/units/gh_aider-chat_aider#code-edit.json`
- [ ] `data/third_party/units/gh_aider-chat_aider#git-commit.json`
- [ ] `data/third_party/indexes/*.json`

### 工具
- [ ] `tools/lint_third_party_registry.py`
- [ ] `tools/build_third_party_indexes.py`

### 文档
- [ ] `skills/skill-finder/references/matching-algorithm.md`
- [ ] `skills/skill-finder/references/install-modes.md`
- [ ] `skills/skill-finder/references/interview-protocol.md`
- [ ] `skills/skill-finder/references/registry-schema.md`

### 集成
- [ ] 修改 `src/skill_creator/workflow.py` 集成推荐接口

---

**设计完成时间**: 2026-01-26  
**架构原则**: 简单、鲁棒、可扩展、宁缺毋滥、禁止欺骗
