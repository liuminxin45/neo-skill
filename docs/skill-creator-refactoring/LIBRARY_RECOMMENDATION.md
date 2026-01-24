# 三方库自动推荐机制

## 概述

skill-creator 在创建 skill 时会**自动推荐**合适的第三方库，无需用户手动指定。推荐的库信息会在生成过程中输出，让 AI 和用户都能看到选用了哪些库。

## 工作流程

### 1. 自动触发推荐

当用户创建 skill 时，系统会自动执行以下流程：

```
用户请求 → Router/Tagger → Interview → Providers 推荐 → Plan 生成 → Skill 构建
                                            ↑
                                    ToolCatalogProvider
                                    (自动推荐三方库)
```

**关键点**：
- ✅ **自动执行**：不需要用户手动触发或选择
- ✅ **基于上下文**：根据 `task_type` 和 `capability_tags` 自动匹配
- ✅ **安全降级**：如果没有匹配的库，不会影响 skill 生成

### 2. 推荐逻辑

**代码位置**：`src/skill_creator/providers/tool_catalog_provider.py`

```python
def recommend(self, ctx: SkillCreatorContext) -> Recommendation:
    # 1. 基于 capability_tags 搜索 tools
    query = SearchQuery(
        layer="tools",
        task_type=ctx.task_type,
        capability_tags=ctx.capability_tags,
        keywords=[],
        top_k=5  # 最多推荐 5 个库
    )
    
    # 2. 搜索匹配的工具库
    result = search_data_packs(self.data_root, query)
    
    # 3. 返回推荐结果
    return Recommendation(items=items, confidence=confidence)
```

**匹配规则**：
- 根据 `capability_tags` 匹配工具库的 `tags`
- 根据 `keywords` 匹配工具库的 `keywords`
- 计算匹配分数，返回 top-5

### 3. 推荐信息输出

推荐的库信息会在**多个地方**展示：

#### A. Plan 生成阶段（AI 可见）

**代码位置**：`src/skill_creator/core/orchestrator.py`

```python
def _generate_summary(self, ctx, output_pack, recipe_id):
    summary_parts = [...]
    
    # 添加推荐的三方库信息
    libraries = self._get_recommended_libraries(ctx)
    if libraries:
        summary_parts.append("**推荐的第三方库**:")
        for lib in libraries:
            summary_parts.append(f"- `{lib.name}`: {lib.purpose}")
            summary_parts.append(f"  - 推荐理由: {lib.reason}")
            summary_parts.append(f"  - PyPI: {lib.pypi_link}")
```

**输出示例**：
```markdown
**推荐的第三方库**:
- `feedparser`: 解析 RSS/Atom feed
  - 推荐理由: 成熟稳定，支持多种 feed 格式
  - PyPI: https://pypi.org/project/feedparser/
- `requests`: 发起 HTTP 请求
  - 推荐理由: Python 最流行的 HTTP 库
  - PyPI: https://pypi.org/project/requests/
```

#### B. Workflow Steps（嵌入到 skillspec.json）

**代码位置**：`src/skill_creator/core/builder.py`

```python
def _generate_workflow_steps(self, ctx, pack_template, recipe):
    steps = [...]
    
    # 添加三方库推荐信息到第一个步骤的 notes
    if steps and ctx.plan and ctx.plan.libraries:
        lib_notes = ["\n\n**推荐的第三方库**:"]
        for lib in ctx.plan.libraries:
            lib_notes.append(f"- `{lib.name}`: {lib.purpose}")
            lib_notes.append(f"  - 安装: `pip install {lib.name}`")
        
        steps[0]["notes"] += "\n".join(lib_notes)
```

#### C. Windsurf Workflow（最终输出）

**代码位置**：`src/skill_creator/targets/windsurf.py`

生成的 `.windsurf/workflows/{skill-name}.md` 会包含：

```markdown
## Prerequisites

**推荐的第三方库**:

- `feedparser`: 解析 RSS/Atom feed
  - 安装: `pip install feedparser`
  - PyPI: https://pypi.org/project/feedparser/
- `requests`: 发起 HTTP 请求
  - 安装: `pip install requests`
  - PyPI: https://pypi.org/project/requests/

```bash
# 安装所有依赖
pip install feedparser requests
```
```

## 数据文件位置

### 工具库索引

**文件**：`.shared/skill-creator/data_packs/tools/index.json`

```json
{
  "version": "1.0",
  "items": {
    "feedparser": {
      "file": "feedparser.json",
      "tags": ["rss", "xml_parse"],
      "keywords": ["rss", "atom", "feed", "parse"]
    },
    "requests": {
      "file": "requests.json",
      "tags": ["http_fetch"],
      "keywords": ["http", "request", "api", "fetch"]
    }
  }
}
```

### 工具库详情

**文件**：`.shared/skill-creator/data_packs/tools/{tool-name}.json`

```json
{
  "id": "feedparser",
  "name": "feedparser",
  "purpose": "解析 RSS/Atom feed",
  "reason": "成熟稳定，支持多种 feed 格式",
  "pypi_link": "https://pypi.org/project/feedparser/",
  "docs_link": "https://feedparser.readthedocs.io/",
  "github_link": "https://github.com/kurtmckee/feedparser",
  "minimal_usage_notes": "import feedparser\nfeed = feedparser.parse('http://example.com/feed.xml')",
  "fallback": "使用 requests + xml.etree.ElementTree",
  "tags": ["rss", "xml_parse"],
  "stability": "high",
  "last_updated": "2023"
}
```

## 如何添加新的工具库

### 1. 创建工具详情文件

创建 `.shared/skill-creator/data_packs/tools/your-tool.json`：

```json
{
  "id": "your-tool",
  "name": "your-tool",
  "purpose": "工具用途（一句话）",
  "reason": "推荐理由（为什么选这个库）",
  "pypi_link": "https://pypi.org/project/your-tool/",
  "docs_link": "https://docs.example.com/",
  "github_link": "https://github.com/...",
  "minimal_usage_notes": "import your_tool\n# 最小使用示例",
  "fallback": "替代方案（如果不用这个库）",
  "tags": ["tag1", "tag2"],
  "stability": "high",
  "last_updated": "2024"
}
```

### 2. 更新索引文件

在 `.shared/skill-creator/data_packs/tools/index.json` 中添加：

```json
{
  "items": {
    "your-tool": {
      "file": "your-tool.json",
      "tags": ["tag1", "tag2"],
      "keywords": ["keyword1", "keyword2", "keyword3"]
    }
  }
}
```

### 3. 选择合适的 tags

确保 tags 与系统的 `capability_tags` 设计一致：

**常用 tags**：
- `http_fetch` - HTTP 请求
- `html_parse` - HTML 解析
- `rss` - RSS/Atom feed
- `xml_parse` - XML 解析
- `json_parse` - JSON 处理
- `scheduler_local` - 本地任务调度
- `email_send` - 邮件发送
- `file_io` - 文件读写
- `database` - 数据库操作

## 优势

### 1. 自动化
- ✅ 无需用户手动选择库
- ✅ 基于任务类型自动匹配
- ✅ 减少用户交互负担

### 2. 可见性
- ✅ AI 在生成过程中能看到推荐的库
- ✅ 用户在最终 workflow 中能看到库信息
- ✅ 包含安装命令和文档链接

### 3. 可扩展性
- ✅ 添加新库只需创建 JSON 文件
- ✅ 不需要修改代码
- ✅ 支持多层索引和按需加载

### 4. 安全降级
- ✅ 如果没有匹配的库，不影响 skill 生成
- ✅ Provider 失败不会导致整个流程失败
- ✅ 提供 fallback 方案

## 示例场景

### 场景：创建 RSS 监控 skill

**用户请求**：
```
我想创建一个 skill，每天抓取 RSS feed 并发送邮件通知
```

**系统自动推荐**：
1. Router 识别：`task_type = "rss_monitoring"`, `capability_tags = ["rss", "http_fetch", "email_send"]`
2. ToolCatalogProvider 自动推荐：
   - `feedparser` (匹配 tag: `rss`)
   - `requests` (匹配 tag: `http_fetch`)
   - `smtplib` (匹配 tag: `email_send`)
3. 生成的 workflow 包含：
   ```markdown
   ## Prerequisites
   
   **推荐的第三方库**:
   - `feedparser`: 解析 RSS/Atom feed
   - `requests`: 发起 HTTP 请求
   
   ```bash
   pip install feedparser requests
   ```
   ```

**用户无需**：
- ❌ 手动搜索合适的库
- ❌ 手动指定要使用的库
- ❌ 手动编写安装命令

**AI 自动获得**：
- ✅ 推荐的库列表
- ✅ 每个库的用途和推荐理由
- ✅ 安装命令和文档链接

## 总结

三方库推荐机制是 skill-creator 的核心特性之一，它：
- **自动化**：无需用户手动选择
- **智能化**：基于任务类型和能力标签匹配
- **透明化**：推荐信息在多个阶段输出
- **可扩展**：通过 JSON 文件轻松添加新库
- **安全化**：失败不影响主流程

这确保了 skill-creator 能够在多领域、多任务场景下稳定工作，同时保持低交互负担和高质量输出。
