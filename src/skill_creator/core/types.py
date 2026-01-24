"""
Core data structures for skill-creator (invariants).
All structures here are part of the non-negotiable contract.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Optional, Any
from enum import Enum


# ============================================================
# QuestionSpec (受约束问题规格 - 不可绕过)
# ============================================================

class AnswerType(str, Enum):
    ENUM = "enum"
    TEXT = "text"
    NUMBER = "number"
    EXAMPLES = "examples"
    FILES = "files"


@dataclass
class QuestionOption:
    """选项定义"""
    value: str
    label: str
    recommended: bool = False
    reason: Optional[str] = None


@dataclass
class QuestionSpec:
    """
    所有问用户的问题必须符合此结构。
    这是不变量：任何提问都必须实例化 QuestionSpec。
    """
    slot: str  # goal/input/output/environment/constraints/acceptance 或领域槽位
    required: bool  # 必答/选答
    prompt: str  # 问题文本
    answer_type: AnswerType
    options: list[QuestionOption] = field(default_factory=list)  # A/B/C 选项
    default: Optional[str] = None  # 用户跳过时采用的默认
    stop_condition: Optional[str] = None  # 该槽位何时视为"足够"
    level: Literal[1, 2] = 1  # Level 1 或 Level 2
    
    def format_display(self) -> str:
        """格式化展示（必须清晰）"""
        parts = [f"**{self.prompt}**"]
        if self.required:
            parts.append("(必答)")
        else:
            parts.append("(选答)")
        if self.default:
            parts.append(f"(默认: {self.default})")
        
        result = " ".join(parts) + "\n"
        
        if self.options:
            for opt in self.options:
                prefix = "  - "
                if opt.recommended:
                    prefix += "✓ "
                result += f"{prefix}{opt.value}. {opt.label}"
                if opt.reason:
                    result += f" (原因: {opt.reason})"
                result += "\n"
        
        return result


# ============================================================
# InterviewState (提问状态机)
# ============================================================

@dataclass
class Answer:
    """用户回答"""
    slot: str
    value: Any
    source: Literal["user", "default", "inferred"]


@dataclass
class InterviewState:
    """
    提问状态，记录所有槽位的填充情况。
    不变量：必须经过 Level1 → Gap Scoring → (可选) Level2
    """
    task_type: str
    capability_tags: list[str]
    
    # Level 1 槽位 (固定)
    goal: Optional[str] = None
    input_source: Optional[str] = None
    output_format: Optional[str] = None
    environment: Optional[str] = None
    constraints: Optional[str] = None
    acceptance: list[str] = field(default_factory=list)
    
    # Level 2 额外槽位 (动态)
    extra_slots: dict[str, Any] = field(default_factory=dict)
    
    # 元数据
    level1_completed: bool = False
    level2_rounds: int = 0
    max_level2_rounds: int = 2
    max_questions_per_round: int = 3
    
    answers_history: list[Answer] = field(default_factory=list)
    
    def add_answer(self, slot: str, value: Any, source: Literal["user", "default", "inferred"]):
        """记录答案"""
        self.answers_history.append(Answer(slot=slot, value=value, source=source))
        
        # 更新槽位
        if slot == "goal":
            self.goal = value
        elif slot == "input":
            self.input_source = value
        elif slot == "output":
            self.output_format = value
        elif slot == "environment":
            self.environment = value
        elif slot == "constraints":
            self.constraints = value
        elif slot == "acceptance":
            if isinstance(value, list):
                self.acceptance.extend(value)
            else:
                self.acceptance.append(value)
        else:
            self.extra_slots[slot] = value
    
    def get_slot_value(self, slot: str) -> Optional[Any]:
        """获取槽位值"""
        if slot == "goal":
            return self.goal
        elif slot == "input":
            return self.input_source
        elif slot == "output":
            return self.output_format
        elif slot == "environment":
            return self.environment
        elif slot == "constraints":
            return self.constraints
        elif slot == "acceptance":
            return self.acceptance
        else:
            return self.extra_slots.get(slot)


# ============================================================
# GapScore (缺口评分 - 触发 Level 2 的依据)
# ============================================================

class GapLevel(str, Enum):
    NONE = "none"  # 无缺口
    MINOR = "minor"  # 小缺口，可用默认值
    MAJOR = "major"  # 大缺口，必须追问


@dataclass
class SlotGap:
    """单个槽位的缺口"""
    slot: str
    level: GapLevel
    reason: str  # missing/vague/conflicting
    priority: int  # 优先级 (1-10)


@dataclass
class GapScore:
    """
    缺口评分结果。
    不变量：必须对 Level1 结果做评分，决定是否进入 Level2。
    """
    gaps: list[SlotGap]
    should_continue_level2: bool
    stop_reason: Optional[str] = None  # 满足生成阈值时的原因
    
    def get_top_gaps(self, max_count: int = 3) -> list[SlotGap]:
        """获取优先级最高的缺口（用于 Level2 提问）"""
        major_gaps = [g for g in self.gaps if g.level == GapLevel.MAJOR]
        major_gaps.sort(key=lambda x: x.priority, reverse=True)
        return major_gaps[:max_count]
    
    def is_ready_to_generate(self) -> bool:
        """是否满足生成阈值"""
        return not self.should_continue_level2


# ============================================================
# Plan (Implementation Plan - 生成前必须展示)
# ============================================================

@dataclass
class LibraryRecommendation:
    """库推荐"""
    name: str
    purpose: str  # 用来做什么
    reason: str  # 推荐理由（简短客观）
    pypi_link: str
    docs_link: str
    fallback: Optional[str] = None  # 零依赖/离线/企业代理等的替代方案


@dataclass
class Plan:
    """
    生成前 Plan（不可禁用）。
    交互规则：用户不反对则默认继续；用户仅在有异议时提出替换/禁用需求。
    """
    summary: str  # 方案概述 (1-2段)
    output_pack: str  # 选定的 Output Pack
    libraries: list[LibraryRecommendation]  # 计划采用的默认库栈
    recipe_id: Optional[str] = None  # 选定的蓝图 (若有)
    assumptions: list[str] = field(default_factory=list)  # 默认采用了哪些假设
    risks: list[str] = field(default_factory=list)  # 风险
    checklists: list[str] = field(default_factory=list)  # 应用的 checklist
    
    def format_display(self) -> str:
        """格式化展示给用户"""
        lines = [
            "# Implementation Plan",
            "",
            "## 方案概述",
            self.summary,
            "",
            f"## Output Pack: `{self.output_pack}`",
            ""
        ]
        
        if self.recipe_id:
            lines.append(f"## 蓝图: `{self.recipe_id}`")
            lines.append("")
        
        if self.libraries:
            lines.append("## 推荐库栈")
            for lib in self.libraries:
                lines.append(f"### {lib.name}")
                lines.append(f"- **用途**: {lib.purpose}")
                lines.append(f"- **理由**: {lib.reason}")
                lines.append(f"- **PyPI**: {lib.pypi_link}")
                lines.append(f"- **文档**: {lib.docs_link}")
                if lib.fallback:
                    lines.append(f"- **Fallback**: {lib.fallback}")
                lines.append("")
        
        if self.assumptions:
            lines.append("## 假设")
            for a in self.assumptions:
                lines.append(f"- {a}")
            lines.append("")
        
        if self.risks:
            lines.append("## 风险")
            for r in self.risks:
                lines.append(f"- {r}")
            lines.append("")
        
        if self.checklists:
            lines.append("## 应用的 Checklist")
            for c in self.checklists:
                lines.append(f"- {c}")
            lines.append("")
        
        lines.append("---")
        lines.append("**如无异议，将继续生成 skill。如需调整库栈或禁用某项，请告知。**")
        
        return "\n".join(lines)


# ============================================================
# Recommendation (Provider 推荐结果)
# ============================================================

@dataclass
class Recommendation:
    """
    Provider 的推荐结果（可选增强）。
    Providers 通过小接口接入，返回此结构。
    """
    provider_name: str
    items: list[dict[str, Any]]  # 推荐的条目（recipe/tool/checklist等）
    confidence: float  # 0.0-1.0
    trace: dict[str, Any] = field(default_factory=dict)  # 调试信息


# ============================================================
# SkillDraft (生成的 skill 草稿)
# ============================================================

@dataclass
class SkillDraft:
    """
    Skill Builder 产出的草稿。
    必须包含足够信息以通过 schema 校验和 dry-run。
    """
    name: str
    description: str
    triggers: list[str]
    workflow_steps: list[dict[str, Any]]
    output_pack: str
    
    # 可选字段
    references: list[str] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    assets: list[str] = field(default_factory=list)
    
    # 元数据
    applied_recipe: Optional[str] = None
    applied_checklists: list[str] = field(default_factory=list)
    libraries_used: list[str] = field(default_factory=list)


# ============================================================
# ValidationResult (校验结果)
# ============================================================

@dataclass
class ValidationIssue:
    """单个校验问题"""
    severity: Literal["error", "warning"]
    message: str
    slot: Optional[str] = None  # 关联的槽位（若有）


@dataclass
class ValidationResult:
    """
    Validator 的校验结果（不可禁用）。
    包含 schema 校验 + dry-run 仿真。
    """
    passed: bool
    issues: list[ValidationIssue]
    dry_run_output: Optional[str] = None  # dry-run 的输出
    missing_gaps: list[SlotGap] = field(default_factory=list)  # 仍缺失的槽位
    
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)
    
    def format_display(self) -> str:
        """格式化展示"""
        if self.passed:
            return "✓ 校验通过"
        
        lines = ["✗ 校验失败:"]
        for issue in self.issues:
            prefix = "ERROR" if issue.severity == "error" else "WARNING"
            lines.append(f"  [{prefix}] {issue.message}")
            if issue.slot:
                lines.append(f"    (槽位: {issue.slot})")
        
        return "\n".join(lines)


# ============================================================
# SearchQuery & SearchResult (多层索引检索)
# ============================================================

@dataclass
class SearchQuery:
    """
    search.py 的输入契约（必须实现）。
    """
    layer: Literal["domains", "tasks", "recipes", "tools", "output_packs", "checklists", "acceptance_templates", "profiles"]
    task_type: str
    capability_tags: list[str]
    keywords: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    top_k: int = 3


@dataclass
class SearchCandidate:
    """搜索结果候选"""
    id: str
    score: float
    matched_tags: list[str]
    matched_keywords: list[str]
    file_path: str
    content: Optional[dict[str, Any]] = None  # 按需加载的内容


@dataclass
class SearchTrace:
    """搜索追踪信息（用于 doctor）"""
    loaded_index_files: list[str]
    loaded_item_files: list[str]
    scoring_notes: dict[str, Any]


@dataclass
class SearchResult:
    """
    search.py 的输出契约（必须实现）。
    """
    candidates: list[SearchCandidate]
    trace: SearchTrace
    
    def get_top(self, k: int = 1) -> list[SearchCandidate]:
        """获取 top-k 结果"""
        return self.candidates[:k]


# ============================================================
# Context (全局上下文，贯穿整个流程)
# ============================================================

@dataclass
class SkillCreatorContext:
    """
    全局上下文，在整个 skill 创建流程中传递。
    """
    user_request: str  # 原始用户请求
    task_type: str
    capability_tags: list[str]
    
    interview_state: InterviewState
    gap_score: Optional[GapScore] = None
    plan: Optional[Plan] = None
    skill_draft: Optional[SkillDraft] = None
    validation_result: Optional[ValidationResult] = None
    
    # Provider 推荐结果
    recommendations: dict[str, Recommendation] = field(default_factory=dict)
    
    # 调试信息
    trace: dict[str, Any] = field(default_factory=dict)
    
    def add_trace(self, key: str, value: Any):
        """添加调试信息"""
        self.trace[key] = value
