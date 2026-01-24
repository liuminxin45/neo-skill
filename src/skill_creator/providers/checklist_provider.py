"""
Checklist Provider: 推荐反踩坑规则（可选增强）
"""
from __future__ import annotations
from pathlib import Path

from .base import Provider
from ..core.types import SkillCreatorContext, Recommendation, SearchQuery
from ..core.search import search_data_packs


class ChecklistProvider(Provider):
    """
    Checklist Provider。
    推荐反踩坑规则（最小 checklist 必须内置不可关闭）。
    """
    
    def recommend(self, ctx: SkillCreatorContext) -> Recommendation:
        """
        推荐 checklists。
        
        策略:
        1. 必须加载 universal/minimal_checklists（不可关闭）
        2. 可选加载 checklists_ext（扩展 checklist）
        3. 基于 task_type + capability_tags 过滤
        """
        items = []
        trace = {}
        
        # 1. 加载最小 checklists（必需）
        minimal_checklists = self._load_minimal_checklists(ctx)
        items.extend(minimal_checklists)
        trace["minimal_checklists_count"] = len(minimal_checklists)
        
        # 2. 尝试加载扩展 checklists（可选）
        ext_checklists_dir = self.data_root / "checklists_ext"
        if ext_checklists_dir.exists():
            ext_checklists = self._load_extended_checklists(ctx)
            items.extend(ext_checklists)
            trace["extended_checklists_count"] = len(ext_checklists)
        else:
            trace["extended_checklists_count"] = 0
            trace["extended_status"] = "dir_not_found"
        
        # 计算 confidence（最小 checklist 总是有的）
        confidence = 1.0 if minimal_checklists else 0.5
        
        return Recommendation(
            provider_name=self.get_name(),
            items=items,
            confidence=confidence,
            trace=trace
        )
    
    def _load_minimal_checklists(self, ctx: SkillCreatorContext) -> list[dict]:
        """加载最小 checklists（必需）"""
        query = SearchQuery(
            layer="universal/minimal_checklists",
            task_type=ctx.task_type,
            capability_tags=ctx.capability_tags,
            keywords=[],
            top_k=3  # 最多 3 个 checklist
        )
        
        # 修正 layer 路径
        minimal_dir = self.data_root / "universal" / "minimal_checklists"
        if not minimal_dir.exists():
            return []
        
        # 手动搜索（因为 layer 路径特殊）
        from ..core.search import IndexManager
        manager = IndexManager(self.data_root)
        
        index_file = minimal_dir / "index.json"
        if not index_file.exists():
            return []
        
        index_data = manager._load_json(index_file)
        
        items = []
        for item_id, item_meta in index_data.get("items", {}).items():
            # 简单匹配：task_type 或 tags
            if ctx.task_type in item_meta.get("task_types", []) or \
               any(tag in ctx.capability_tags for tag in item_meta.get("tags", [])):
                item_file = minimal_dir / item_meta["file"]
                if item_file.exists():
                    content = manager._load_json(item_file)
                    items.append(content)
        
        return items
    
    def _load_extended_checklists(self, ctx: SkillCreatorContext) -> list[dict]:
        """加载扩展 checklists（可选）"""
        query = SearchQuery(
            layer="checklists_ext",
            task_type=ctx.task_type,
            capability_tags=ctx.capability_tags,
            keywords=[],
            top_k=2
        )
        
        result = search_data_packs(self.data_root, query)
        
        items = []
        for candidate in result.candidates:
            if candidate.content:
                items.append(candidate.content)
        
        return items
