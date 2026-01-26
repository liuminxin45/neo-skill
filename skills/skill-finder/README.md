# skill-finder

发现/匹配/安装第三方 skill 库。

## 功能

- **主动搜索**：通过两级提问收集需求，匹配第三方能力单元
- **被动推荐**：供 skill-creator 调用，推荐高置信度第三方 unit
- **两种安装模式**：自动安装（默认）/ 手动安装（仅输出命令）
- **可追溯性**：所有安装行为记录到 `~/.omni-skill/install_records.json`
- **诊断工具**：提供匹配 trace 和安装记录分析

## 触发方式

- "找第三方 skill"
- "有没有现成的工具"
- "推荐一个能力库"
- "安装第三方能力"
- "search for third-party skill"

## 使用方式

### CLI 模式

```bash
python -m skill_finder.cli
```

### 编程接口

```python
from skill_finder.recommender import Recommender
from skill_finder.models import SearchQuery

recommender = Recommender()
query = SearchQuery(goal="AI 代码编辑", tags=["code-generation"], ide="windsurf")
result = recommender.recommend(query)
```

## 设计原则

- **宁缺毋滥**：置信度 < 60% 必须拒绝
- **诚实反馈**：明确告知拒绝原因（4 种分类）
- **可追溯**：install_record 记录所有安装行为
- **轻量集成**：skill-creator 集成不打断主流程

## 详细文档

参见：
- `DESIGN_SKILL_FINDER.md` - 完整设计文档
- `SKILL_FINDER_USAGE.md` - 使用指南
- `references/matching-algorithm.md` - 匹配算法详解
