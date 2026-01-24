"""
Tool Catalog Provider: 推荐库栈（可选增强）
"""
from __future__ import annotations
from pathlib import Path

from .base import Provider
from ..core.types import SkillCreatorContext, Recommendation, SearchQuery
from ..core.search import search_data_packs


class ToolCatalogProvider(Provider):
    """
    Tool Catalog Provider。
    推荐第三方库（含 links + minimal_usage_notes）。
    """
    
    def recommend(self, ctx: SkillCreatorContext) -> Recommendation:
        """
        推荐工具库。
        
        策略:
        1. 基于 capability_tags 搜索 tools
        2. 返回 top-5 tools
        3. 未命中则返回空推荐（安全降级）
        """
        # 检查 tools 目录是否存在
        tools_dir = self.data_root / "tools"
        if not tools_dir.exists():
            # 安全降级：tools 目录不存在
            return Recommendation(
                provider_name=self.get_name(),
                items=[],
                confidence=0.0,
                trace={"status": "tools_dir_not_found"}
            )
        
        # 搜索 tools
        query = SearchQuery(
            layer="tools",
            task_type=ctx.task_type,
            capability_tags=ctx.capability_tags,
            keywords=[],
            top_k=5  # 最多 5 个库
        )
        
        result = search_data_packs(self.data_root, query)
        
        items = []
        confidence = 0.0
        
        if result.candidates:
            for candidate in result.candidates:
                if candidate.content:
                    items.append(candidate.content)
            
            # 根据匹配分数计算 confidence
            if items:
                avg_score = sum(c.score for c in result.candidates) / len(result.candidates)
                confidence = min(avg_score / 15.0, 1.0)  # 归一化到 0-1
        
        return Recommendation(
            provider_name=self.get_name(),
            items=items,
            confidence=confidence,
            trace={
                "search_result": {
                    "candidates_count": len(result.candidates),
                    "loaded_files": result.trace.loaded_item_files
                }
            }
        )
