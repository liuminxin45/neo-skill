"""
Provider 基类（小接口，避免网状依赖）
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path

from ..core.types import SkillCreatorContext, Recommendation


class Provider(ABC):
    """
    Provider 基类。
    每个 provider 仅通过小接口接入，避免网状依赖。
    """
    
    def __init__(self, data_root: Path):
        self.data_root = data_root
    
    @abstractmethod
    def recommend(self, ctx: SkillCreatorContext) -> Recommendation:
        """
        推荐资源（可选）。
        
        Args:
            ctx: 全局上下文
            
        Returns:
            Recommendation: 推荐结果（items + confidence + trace）
        """
        pass
    
    def get_name(self) -> str:
        """获取 provider 名称"""
        return self.__class__.__name__.replace("Provider", "").lower()
