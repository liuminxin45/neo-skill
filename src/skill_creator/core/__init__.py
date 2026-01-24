"""
Core module: invariant capabilities that cannot be disabled.
"""
from .types import (
    QuestionSpec,
    QuestionOption,
    AnswerType,
    InterviewState,
    Answer,
    GapScore,
    GapLevel,
    SlotGap,
    Plan,
    LibraryRecommendation,
    Recommendation,
    SkillDraft,
    ValidationResult,
    ValidationIssue,
    SearchQuery,
    SearchResult,
    SearchCandidate,
    SearchTrace,
    SkillCreatorContext,
)

from .search import IndexManager, search_data_packs

__all__ = [
    "QuestionSpec",
    "QuestionOption",
    "AnswerType",
    "InterviewState",
    "Answer",
    "GapScore",
    "GapLevel",
    "SlotGap",
    "Plan",
    "LibraryRecommendation",
    "Recommendation",
    "SkillDraft",
    "ValidationResult",
    "ValidationIssue",
    "SearchQuery",
    "SearchResult",
    "SearchCandidate",
    "SearchTrace",
    "SkillCreatorContext",
    "IndexManager",
    "search_data_packs",
]
