# Providers Module

Providers 层（可插拔增强能力，默认启用，安全降级）。

## Provider 列表

### base.py
Provider 基类：
- `Provider`: 抽象基类
- `recommend(ctx)`: 推荐资源（可选）
- 小接口设计，避免网状依赖

### recipe_provider.py
Recipe/Blueprint Provider：
- 推荐成熟方案骨架
- 基于 task_type + capability_tags 搜索 recipes
- 返回 top-1 recipe（如果有）
- 未命中则返回空推荐（安全降级）

### tool_catalog_provider.py
Tool Catalog Provider：
- 推荐第三方库
- 基于 capability_tags 搜索 tools
- 返回 top-5 tools
- 未命中则返回空推荐（安全降级）

### checklist_provider.py
Checklist Provider：
- 推荐反踩坑规则
- 必须加载 universal/minimal_checklists（不可关闭）
- 可选加载 checklists_ext（扩展 checklist）
- 基于 task_type + capability_tags 过滤

## 工作原理

1. **并行推荐**: 主引擎并行调用所有 providers
2. **聚合结果**: Plan Orchestrator 聚合推荐结果
3. **安全降级**: 任何 provider 失败不影响主流程
4. **可插拔**: 新增 provider 只需继承 `Provider` 基类

## 添加新 Provider

```python
from .base import Provider
from ..core.types import SkillCreatorContext, Recommendation

class MyProvider(Provider):
    def recommend(self, ctx: SkillCreatorContext) -> Recommendation:
        # 实现推荐逻辑
        return Recommendation(
            provider_name=self.get_name(),
            items=[...],
            confidence=0.8,
            trace={...}
        )
```

然后在 `engine.py` 中注册：
```python
self.providers = [
    RecipeProvider(data_root),
    ToolCatalogProvider(data_root),
    ChecklistProvider(data_root),
    MyProvider(data_root),  # 新增
]
```

## 设计原则

1. **可插拔**: 通过小接口接入，避免网状依赖
2. **安全降级**: Provider 失败不影响主流程
3. **默认启用**: 不对普通用户暴露开关
4. **可追溯**: 返回 trace 信息用于 debug
