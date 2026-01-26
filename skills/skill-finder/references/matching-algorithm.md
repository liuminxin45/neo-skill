# skill-finder 匹配算法

## 一、两阶段匹配流程

### 阶段 1: 粗筛（Coarse Filtering）
**目标**: 快速缩小候选范围

**输入**: SearchQuery (goal, tags, keywords, ide, env, constraints)

**方法**: 倒排索引命中
1. **Tag 倒排**: 从 `indexes/units.by_tag.json` 查找匹配 `query.tags` 的 unit_id
2. **Keyword 倒排**: 从 `indexes/units.by_keyword.json` 查找匹配 `query.keywords` 的 unit_id
3. **IDE 倒排**: 从 `indexes/units.by_ide.json` 查找匹配 `query.ide` 的 unit_id
4. **合并**: 取并集（tag OR keyword）与 IDE 交集

**输出**: 候选 unit_id 列表

**拒绝条件**: 若候选为空，返回 `no_candidates_by_tag`

---

### 阶段 2: 精排（Fine Ranking）
**目标**: 计算置信度分数，过滤低质量匹配

**评分公式**:
```
score = tag_coverage * 0.6 + keyword_match * 0.3 + ide_bonus * 0.1
```

**评分细节**:

1. **Tag 覆盖率** (权重 0.6)
   ```
   tag_coverage = len(matched_tags) / len(query.tags)
   matched_tags = set(query.tags) ∩ set(unit.capability_tags)
   ```

2. **Keyword 匹配** (权重 0.3)
   ```
   keyword_match = len(matched_keywords) / len(query.keywords)
   matched_keywords = set(query.keywords) ∩ set(unit.keywords)
   ```

3. **IDE 支持** (权重 0.1)
   - 支持: +0.1
   - 不支持: score *= 0.2 (显著降权)

4. **约束过滤** (降权因子)
   - **env 冲突**: 若 `unit.conflicts` 提及 `query.env` → score *= 0.3
   - **constraints 违反**: 若 unit 描述与约束冲突 → score *= 0.5
     - 示例: `no-network` 约束 + unit 描述含 "network" → 降权

**输出**: 按 score 降序排列的 MatchResult 列表

---

## 二、置信门槛与拒绝策略

### 置信门槛
```python
MIN_SCORE = 0.6  # 60%
```

**规则**:
- `score >= 0.6`: 返回 Top 1-3
- `score < 0.6`: **必须拒绝**，不得返回低质量结果

---

### 拒绝原因分类

#### 1. `no_candidates_by_tag`
**条件**: 粗筛阶段无候选
**原因**: 未找到匹配的能力标签或关键词
**建议**: 补充更多标签/关键词，或使用 skill-creator 创建自研 skill

#### 2. `candidates_but_no_ide_support`
**条件**: 有候选但所有 unit 均不支持目标 IDE
**原因**: 找到候选能力，但均不支持 {query.ide}
**建议**: 更换 IDE 或使用 generic 模式

#### 3. `candidates_but_incompatible_env`
**条件**: 有候选但所有 unit 均因 env/constraints 被降权至 < 0.6
**原因**: 找到候选能力，但均不满足环境或约束条件
**建议**: 放宽约束或调整环境

#### 4. `insufficient_info`
**条件**: 有候选但最高分 < 0.6，且无明确冲突
**原因**: 候选能力置信度不足（< 60%），建议补充更多需求信息
**建议**: 回答 Level 2 问题，提供更多细节

---

## 三、匹配示例

### 示例 1: 高置信匹配
```
Query:
  goal: "AI 辅助多文件代码重构"
  tags: ["code-refactoring", "multi-file-editing"]
  ide: "windsurf"

候选: gh:aider-chat/aider#code-edit
  capability_tags: ["code-generation", "code-refactoring", "multi-file-editing"]
  ide_support: ["windsurf", "cursor"]

评分:
  tag_coverage = 2/2 = 1.0 → 0.6
  keyword_match = 0 (未提供) → 0
  ide_bonus = 0.1
  score = 0.7 ✓ (通过)

结果: 返回 Top 1
```

### 示例 2: IDE 不支持拒绝
```
Query:
  goal: "生成 commit message"
  tags: ["git-commit"]
  ide: "vscode"

候选: gh:aider-chat/aider#git-commit
  capability_tags: ["git-commit"]
  ide_support: ["windsurf", "cursor", "generic"]

评分:
  tag_coverage = 1/1 = 1.0 → 0.6
  ide_bonus = 0 (不支持 vscode)
  降权: score *= 0.2 → 0.12 ✗

拒绝原因: candidates_but_no_ide_support
```

### 示例 3: 约束冲突拒绝
```
Query:
  goal: "自动化代码编辑"
  tags: ["code-generation"]
  constraints: ["no-network"]
  ide: "windsurf"

候选: gh:aider-chat/aider#code-edit
  description: "AI-powered ... (需要 LLM API)"
  conflicts: "需要网络访问 LLM provider"

评分:
  tag_coverage = 1/1 = 1.0 → 0.6
  ide_bonus = 0.1
  约束冲突: score *= 0.5 → 0.35 ✗

拒绝原因: candidates_but_incompatible_env
```

---

## 四、实现要点

### 宁缺毋滥原则
- **禁止强行匹配**: 低于阈值必须拒绝
- **禁止虚构结果**: 不得返回不存在的 unit
- **诚实反馈**: 明确告知拒绝原因与缺口信息

### 性能优化
- **按需加载**: 粗筛仅加载索引，精排才加载完整 unit/package 数据
- **Top-K 限制**: 最多返回 Top 3，避免信息过载
- **索引预构建**: 使用 `build_third_party_indexes.py` 预生成倒排索引

### 可扩展性
- **插件化评分**: 可新增评分因子（如 popularity, last_updated）
- **动态阈值**: 可根据 query 复杂度调整 MIN_SCORE
- **多语言支持**: 索引构建时归一化大小写，支持中英文关键词
