"""被动推荐接口 - 供 skill-creator 调用"""

from typing import Optional
from .models import SearchQuery, SearchResult
from .registry import Registry
from .matcher import Matcher


class Recommender:
    """推荐器 - 被动推荐接口"""
    
    def __init__(self, registry: Optional[Registry] = None, min_score: float = 0.7):
        """
        初始化推荐器
        
        Args:
            registry: Registry 实例（可选）
            min_score: 最小置信度（推荐模式使用更高阈值 0.7）
        """
        if registry is None:
            registry = Registry()
        
        self.registry = registry
        self.matcher = Matcher(registry, min_score=min_score)
    
    def recommend(self, query: SearchQuery) -> SearchResult:
        """
        推荐第三方 unit（高置信度）
        
        Args:
            query: 搜索查询
            
        Returns:
            SearchResult: 仅返回高置信度结果（>= 0.7），否则返回空
        """
        result = self.matcher.match(query)
        
        if result.matches and result.matches[0].score >= 0.7:
            return SearchResult(
                query=query,
                matches=result.matches[:1],
                rejection_reason=None,
                rejection_category=None
            )
        
        return SearchResult(
            query=query,
            matches=[],
            rejection_reason="未找到高置信度推荐（< 70%）",
            rejection_category="insufficient_info"
        )
