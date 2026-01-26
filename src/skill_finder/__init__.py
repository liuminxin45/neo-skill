"""skill-finder - 发现/匹配/安装第三方 skill 库"""

__version__ = "1.0.0"

from .models import (
    SkillPackage,
    SkillUnit,
    SearchQuery,
    SearchResult,
    MatchResult,
    InstallRecord,
)

__all__ = [
    "SkillPackage",
    "SkillUnit",
    "SearchQuery",
    "SearchResult",
    "MatchResult",
    "InstallRecord",
]
