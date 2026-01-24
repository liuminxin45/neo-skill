# Tools（库推荐库）

可选增强数据包，提供第三方库推荐信息。

## 当前 Tools

### feedparser
- **用途**: 解析 RSS/Atom feed
- **理由**: 成熟稳定，支持多种 feed 格式
- **链接**: [PyPI](https://pypi.org/project/feedparser/) | [Docs](https://feedparser.readthedocs.io/)

### requests
- **用途**: 发起 HTTP 请求
- **理由**: Python 最流行的 HTTP 库，API 简洁
- **链接**: [PyPI](https://pypi.org/project/requests/) | [Docs](https://requests.readthedocs.io/)

### beautifulsoup4
- **用途**: 解析 HTML/XML
- **理由**: 最流行的 HTML 解析库，容错性强
- **链接**: [PyPI](https://pypi.org/project/beautifulsoup4/) | [Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

### schedule
- **用途**: 简单的任务调度
- **理由**: 轻量级，API 简洁
- **链接**: [PyPI](https://pypi.org/project/schedule/) | [Docs](https://schedule.readthedocs.io/)

## Tool 文件结构

```json
{
  "id": "tool_id",
  "name": "tool_name",
  "purpose": "用途说明",
  "reason": "推荐理由",
  "pypi_link": "https://pypi.org/project/...",
  "docs_link": "https://...",
  "github_link": "https://github.com/...",
  "minimal_usage_notes": "简短使用说明（10-20行）",
  "fallback": "零依赖/离线替代方案",
  "tags": ["..."],
  "stability": "high|medium|low",
  "last_updated": "2023"
}
```

## 如何添加新工具

1. 创建工具详情文件 `{tool-name}.json`
2. 在 `index.json` 中添加索引条目
3. 确保 tags 与 capability_tags 设计一致

## 自动推荐机制

skill-creator 会**自动推荐**合适的第三方库，无需用户手动指定：

- **自动触发**：基于 `task_type` 和 `capability_tags` 自动匹配
- **智能排序**：返回 top-5 最匹配的工具库
- **多处展示**：推荐信息会在 Plan、Workflow Steps 和最终输出中展示
- **安全降级**：如果没有匹配的库，不影响 skill 生成

详见：`docs/skill-creator-refactoring/LIBRARY_RECOMMENDATION.md`
   }
   ```
3. 无需修改代码，系统会自动检索

## 设计原则

- **链接优先**: 提供 PyPI + Docs 链接，不拉取 README
- **微摘要**: minimal_usage_notes 控制在 10-20 行
- **稳定性**: 优先推荐成熟稳定的库
- **Fallback**: 提供零依赖/离线替代方案
