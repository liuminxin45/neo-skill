"""匹配算法实现 - 两阶段匹配"""

from typing import List, Dict, Set
from .models import SearchQuery, SearchResult, MatchResult
from .registry import Registry


class Matcher:
    """匹配器 - 两阶段匹配算法"""
    
    def __init__(self, registry: Registry, min_score: float = 0.6):
        self.registry = registry
        self.min_score = min_score
    
    def match(self, query: SearchQuery) -> SearchResult:
        """执行两阶段匹配"""
        candidates = self._coarse_filter(query)
        
        if not candidates:
            return SearchResult(
                query=query,
                matches=[],
                rejection_reason="未找到匹配的能力标签或关键词",
                rejection_category="no_candidates_by_tag"
            )
        
        scored = self._fine_rank(candidates, query)
        filtered = [m for m in scored if m.score >= self.min_score]
        
        if not filtered:
            rejection = self._analyze_rejection(candidates, query)
            return SearchResult(
                query=query,
                matches=[],
                rejection_reason=rejection["reason"],
                rejection_category=rejection["category"]
            )
        
        return SearchResult(
            query=query,
            matches=filtered[:3],
            rejection_reason=None,
            rejection_category=None
        )
    
    def _coarse_filter(self, query: SearchQuery) -> List[str]:
        """阶段 1: 粗筛 - 倒排索引命中"""
        unit_ids = set()
        
        if query.tags:
            for tag in query.tags:
                unit_ids.update(self.registry.search_by_tag(tag))
        
        if query.keywords:
            for kw in query.keywords:
                unit_ids.update(self.registry.search_by_keyword(kw))
        
        if query.ide:
            ide_units = set(self.registry.search_by_ide(query.ide))
            if unit_ids:
                unit_ids &= ide_units
            else:
                unit_ids = ide_units
        
        return list(unit_ids)
    
    def _fine_rank(self, unit_ids: List[str], query: SearchQuery) -> List[MatchResult]:
        """阶段 2: 精排 - 计算置信度分数"""
        results = []
        
        for uid in unit_ids:
            unit = self.registry.get_unit(uid)
            if not unit:
                continue
            
            package = self.registry.get_package(unit.package_id)
            if not package:
                continue
            
            score = 0.0
            reasons = []
            warnings = []
            
            if query.tags:
                matched_tags = set(t.lower() for t in query.tags) & set(t.lower() for t in unit.capability_tags)
                if matched_tags:
                    tag_coverage = len(matched_tags) / len(query.tags)
                    score += tag_coverage * 0.6
                    reasons.append(f"匹配标签: {', '.join(matched_tags)}")
            
            if query.keywords:
                matched_kw = set(kw.lower() for kw in query.keywords) & set(kw.lower() for kw in unit.keywords)
                if matched_kw:
                    kw_score = len(matched_kw) / len(query.keywords)
                    score += kw_score * 0.3
                    reasons.append(f"匹配关键词: {', '.join(matched_kw)}")
            
            if query.ide:
                if query.ide.lower() in [ide.lower() for ide in unit.ide_support]:
                    score += 0.1
                    reasons.append(f"支持 {query.ide}")
                else:
                    score *= 0.2
                    warnings.append(f"不支持 {query.ide}（仅支持 {', '.join(unit.ide_support)}）")
            
            if query.env and unit.conflicts:
                if query.env.lower() in unit.conflicts.lower():
                    score *= 0.3
                    warnings.append(f"可能与 {query.env} 环境冲突")
            
            if query.constraints:
                for constraint in query.constraints:
                    if "no-network" in constraint.lower() and "network" in unit.description.lower():
                        score *= 0.5
                        warnings.append("可能需要网络访问，与约束冲突")
            
            results.append(MatchResult(
                unit=unit,
                package=package,
                score=score,
                reasons=reasons,
                warnings=warnings if warnings else None
            ))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    def _analyze_rejection(self, candidates: List[str], query: SearchQuery) -> Dict:
        """分析拒绝原因"""
        if not candidates:
            return {
                "reason": "未找到匹配的能力标签或关键词",
                "category": "no_candidates_by_tag"
            }
        
        if query.ide:
            ide_supported = False
            for uid in candidates:
                unit = self.registry.get_unit(uid)
                if unit and query.ide.lower() in [ide.lower() for ide in unit.ide_support]:
                    ide_supported = True
                    break
            
            if not ide_supported:
                return {
                    "reason": f"找到候选能力，但均不支持 {query.ide}",
                    "category": "candidates_but_no_ide_support"
                }
        
        if query.env or query.constraints:
            return {
                "reason": "找到候选能力，但均不满足环境或约束条件",
                "category": "candidates_but_incompatible_env"
            }
        
        return {
            "reason": "候选能力置信度不足（< 60%），建议补充更多需求信息",
            "category": "insufficient_info"
        }
