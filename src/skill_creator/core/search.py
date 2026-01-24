"""
Multi-layer index and on-demand loading (no SQL/database).
Implements the search contract defined in types.py.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
from dataclasses import asdict

from .types import SearchQuery, SearchResult, SearchCandidate, SearchTrace


class IndexManager:
    """
    多层索引管理器。
    按需加载 top_k 文件，严控注入 prompt 的内容规模。
    """
    
    def __init__(self, data_root: Path):
        self.data_root = data_root
        self.index_cache: dict[str, dict] = {}
    
    def search(self, query: SearchQuery) -> SearchResult:
        """
        执行多层索引检索。
        
        流程:
        1. 加载该 layer 的索引文件 (index.json)
        2. 根据 task_type + capability_tags + keywords 计算匹配分数
        3. 按需加载 top_k 条目文件
        4. 返回结果 + trace
        """
        trace = SearchTrace(
            loaded_index_files=[],
            loaded_item_files=[],
            scoring_notes={}
        )
        
        # 1. 加载索引
        layer_path = self.data_root / query.layer
        if not layer_path.exists():
            # 安全降级：layer 不存在
            return SearchResult(candidates=[], trace=trace)
        
        index_file = layer_path / "index.json"
        if not index_file.exists():
            # 安全降级：无索引文件
            return SearchResult(candidates=[], trace=trace)
        
        index_data = self._load_json(index_file)
        trace.loaded_index_files.append(str(index_file))
        
        # 2. 计算匹配分数
        candidates = []
        for item_id, item_meta in index_data.get("items", {}).items():
            score, matched_tags, matched_keywords = self._calculate_score(
                query, item_meta
            )
            
            if score > 0:
                candidates.append({
                    "id": item_id,
                    "score": score,
                    "matched_tags": matched_tags,
                    "matched_keywords": matched_keywords,
                    "file_path": str(layer_path / item_meta["file"])
                })
        
        # 排序
        candidates.sort(key=lambda x: x["score"], reverse=True)
        trace.scoring_notes["total_candidates"] = len(candidates)
        trace.scoring_notes["top_k"] = query.top_k
        
        # 3. 按需加载 top_k 条目
        top_candidates = candidates[:query.top_k]
        result_candidates = []
        
        for cand in top_candidates:
            file_path = Path(cand["file_path"])
            content = None
            
            if file_path.exists():
                content = self._load_json(file_path)
                trace.loaded_item_files.append(str(file_path))
            
            result_candidates.append(SearchCandidate(
                id=cand["id"],
                score=cand["score"],
                matched_tags=cand["matched_tags"],
                matched_keywords=cand["matched_keywords"],
                file_path=str(file_path),
                content=content
            ))
        
        return SearchResult(candidates=result_candidates, trace=trace)
    
    def _calculate_score(
        self, 
        query: SearchQuery, 
        item_meta: dict
    ) -> tuple[float, list[str], list[str]]:
        """
        计算匹配分数。
        
        评分策略:
        - task_type 完全匹配: +10
        - task_type 部分匹配: +5
        - 每个 capability_tag 匹配: +3
        - 每个 keyword 匹配: +1
        """
        score = 0.0
        matched_tags = []
        matched_keywords = []
        
        # task_type 匹配
        item_task_types = item_meta.get("task_types", [])
        if query.task_type in item_task_types:
            score += 10
        elif any(query.task_type in tt or tt in query.task_type for tt in item_task_types):
            score += 5
        
        # capability_tags 匹配
        item_tags = item_meta.get("tags", [])
        for tag in query.capability_tags:
            if tag in item_tags:
                score += 3
                matched_tags.append(tag)
        
        # keywords 匹配
        item_keywords = item_meta.get("keywords", [])
        for kw in query.keywords:
            if kw.lower() in [k.lower() for k in item_keywords]:
                score += 1
                matched_keywords.append(kw)
        
        return score, matched_tags, matched_keywords
    
    def _load_json(self, path: Path) -> dict:
        """加载 JSON 文件（带缓存）"""
        path_str = str(path)
        if path_str not in self.index_cache:
            with open(path, "r", encoding="utf-8") as f:
                self.index_cache[path_str] = json.load(f)
        return self.index_cache[path_str]
    
    def load_required_pack(self, pack_name: str, layer: str) -> Optional[dict]:
        """
        加载必需的 pack（不通过 search，直接加载）。
        用于加载 universal 层的必需资源。
        """
        pack_file = self.data_root / layer / f"{pack_name}.json"
        if pack_file.exists():
            return self._load_json(pack_file)
        return None


def search_data_packs(
    data_root: Path,
    query: SearchQuery
) -> SearchResult:
    """
    便捷函数：执行搜索。
    """
    manager = IndexManager(data_root)
    return manager.search(query)
