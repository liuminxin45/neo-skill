"""
Recipe Provider: 推荐蓝图（可选增强）
"""
from __future__ import annotations
from pathlib import Path

from .base import Provider
from ..core.types import SkillCreatorContext, Recommendation, SearchQuery
from ..core.search import search_data_packs


class RecipeProvider(Provider):
    """
    Recipe/Blueprint Provider。
    推荐成熟方案骨架（步骤序列 + 推荐库栈 + 配置键 + 验收模板）。
    """
    
    def recommend(self, ctx: SkillCreatorContext) -> Recommendation:
        """
        推荐 recipe。
        
        策略:
        1. 基于 task_type + capability_tags 搜索 recipes
        2. 返回 top-1 recipe（如果有）
        3. 未命中则返回空推荐（安全降级）
        """
        # 检查 recipes 目录是否存在
        recipes_dir = self.data_root / "recipes"
        if not recipes_dir.exists():
            # 安全降级：recipes 目录不存在
            return Recommendation(
                provider_name=self.get_name(),
                items=[],
                confidence=0.0,
                trace={"status": "recipes_dir_not_found"}
            )
        
        # 搜索 recipes
        query = SearchQuery(
            layer="recipes",
            task_type=ctx.task_type,
            capability_tags=ctx.capability_tags,
            keywords=[],
            top_k=1  # 只取 top-1
        )
        
        result = search_data_packs(self.data_root, query)
        
        items = []
        confidence = 0.0
        
        if result.candidates:
            top_recipe = result.candidates[0]
            if top_recipe.content:
                items.append(top_recipe.content)
                # 根据匹配分数计算 confidence
                confidence = min(top_recipe.score / 20.0, 1.0)  # 归一化到 0-1
        
        return Recommendation(
            provider_name=self.get_name(),
            items=items,
            confidence=confidence,
            trace={
                "search_result": {
                    "candidates_count": len(result.candidates),
                    "top_score": result.candidates[0].score if result.candidates else 0,
                    "loaded_files": result.trace.loaded_item_files
                }
            }
        )
