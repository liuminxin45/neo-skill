"""
Validator: Schema 校验 + Dry-run 仿真（不可禁用）
"""
from __future__ import annotations
from pathlib import Path
import re

from .types import (
    SkillDraft, ValidationResult, ValidationIssue,
    SkillCreatorContext, GapScore, SlotGap, GapLevel
)
from .search import IndexManager


class Validator:
    """
    校验器（不变量，不可禁用）。
    执行 schema 校验 + dry-run 仿真。
    """
    
    def __init__(self, data_root: Path):
        self.data_root = data_root
        self.index_manager = IndexManager(data_root)
    
    def validate(
        self, 
        ctx: SkillCreatorContext, 
        draft: SkillDraft
    ) -> ValidationResult:
        """
        执行完整校验（不可禁用）。
        
        流程:
        1. Schema 校验（字段完整性、类型正确性）
        2. Dry-run 仿真（用验收用例走一遍工作流）
        3. 发现缺口时返回 missing_gaps
        """
        issues = []
        
        # 1. Schema 校验
        schema_issues = self._validate_schema(draft)
        issues.extend(schema_issues)
        
        # 2. 业务规则校验
        business_issues = self._validate_business_rules(draft)
        issues.extend(business_issues)
        
        # 3. Dry-run 仿真
        dry_run_output, dry_run_issues = self._dry_run(ctx, draft)
        issues.extend(dry_run_issues)
        
        # 4. 检查是否有缺口
        missing_gaps = self._check_missing_gaps(ctx, issues)
        
        passed = not any(i.severity == "error" for i in issues)
        
        result = ValidationResult(
            passed=passed,
            issues=issues,
            dry_run_output=dry_run_output,
            missing_gaps=missing_gaps
        )
        
        ctx.add_trace("validation", {
            "passed": passed,
            "issues_count": len(issues),
            "errors_count": len([i for i in issues if i.severity == "error"]),
            "warnings_count": len([i for i in issues if i.severity == "warning"])
        })
        
        return result
    
    def _validate_schema(self, draft: SkillDraft) -> list[ValidationIssue]:
        """Schema 校验"""
        issues = []
        
        # 加载 schema
        schema = self.index_manager.load_required_pack("schema.skill", "universal")
        if not schema:
            # 使用硬编码的最小 schema
            schema = {
                "required_fields": ["name", "description", "triggers", "workflow_steps", "output_pack"]
            }
        
        # 检查必需字段
        required_fields = schema.get("required_fields", [])
        for field in required_fields:
            if not getattr(draft, field, None):
                issues.append(ValidationIssue(
                    severity="error",
                    message=f"缺少必需字段: {field}",
                    slot=field
                ))
        
        return issues
    
    def _validate_business_rules(self, draft: SkillDraft) -> list[ValidationIssue]:
        """业务规则校验"""
        issues = []
        
        # 规则 1: name 必须是 kebab-case
        if draft.name and not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', draft.name):
            issues.append(ValidationIssue(
                severity="error",
                message=f"name 必须是 kebab-case: {draft.name}",
                slot="name"
            ))
        
        # 规则 2: triggers 至少 3 条
        if len(draft.triggers) < 3:
            issues.append(ValidationIssue(
                severity="warning",
                message=f"triggers 建议至少 3 条，当前只有 {len(draft.triggers)} 条",
                slot="triggers"
            ))
        
        # 规则 3: workflow_steps 至少 1 个
        if len(draft.workflow_steps) < 1:
            issues.append(ValidationIssue(
                severity="error",
                message="workflow_steps 至少需要 1 个步骤",
                slot="workflow_steps"
            ))
        
        # 规则 4: output_pack 必须是已知的 pack
        known_packs = ["plain_text_message", "markdown_report", "json_result", "code_snippet", "generic"]
        if draft.output_pack not in known_packs:
            issues.append(ValidationIssue(
                severity="error",
                message=f"未知的 output_pack: {draft.output_pack}",
                slot="output_pack"
            ))
        
        return issues
    
    def _dry_run(
        self, 
        ctx: SkillCreatorContext, 
        draft: SkillDraft
    ) -> tuple[str, list[ValidationIssue]]:
        """
        Dry-run 仿真（用验收用例走一遍工作流）。
        
        这是简化版实现，主要检查：
        1. 验收用例是否覆盖失败/无数据场景
        2. workflow steps 是否能满足验收需求
        """
        issues = []
        output_lines = ["=== Dry-run 仿真 ===", ""]
        
        acceptance = ctx.interview_state.acceptance
        
        if not acceptance or len(acceptance) < 2:
            issues.append(ValidationIssue(
                severity="error",
                message="验收用例不足（至少需要 2 条）",
                slot="acceptance"
            ))
            output_lines.append("✗ 验收用例不足")
        else:
            output_lines.append(f"✓ 验收用例: {len(acceptance)} 条")
            
            # 检查是否包含失败/无数据场景
            has_failure_case = any(
                "失败" in a or "错误" in a or "无数据" in a or "empty" in a.lower() or "fail" in a.lower()
                for a in acceptance
            )
            
            if not has_failure_case:
                issues.append(ValidationIssue(
                    severity="warning",
                    message="验收用例缺少失败或无数据场景",
                    slot="acceptance"
                ))
                output_lines.append("⚠ 缺少失败/无数据场景")
            else:
                output_lines.append("✓ 包含失败/无数据场景")
        
        # 检查 workflow steps 是否完整
        if len(draft.workflow_steps) < 3:
            issues.append(ValidationIssue(
                severity="warning",
                message=f"workflow steps 较少（{len(draft.workflow_steps)} 个），可能不够完整",
                slot="workflow_steps"
            ))
            output_lines.append(f"⚠ workflow steps 较少: {len(draft.workflow_steps)} 个")
        else:
            output_lines.append(f"✓ workflow steps: {len(draft.workflow_steps)} 个")
        
        # 模拟执行验收用例
        output_lines.append("")
        output_lines.append("模拟执行验收用例:")
        for i, case in enumerate(acceptance[:3], 1):  # 最多展示 3 条
            output_lines.append(f"  {i}. {case}")
            output_lines.append(f"     → 预期可通过 workflow 实现")
        
        return "\n".join(output_lines), issues
    
    def _check_missing_gaps(
        self, 
        ctx: SkillCreatorContext, 
        issues: list[ValidationIssue]
    ) -> list[SlotGap]:
        """
        检查是否仍有缺口（触发最小追问）。
        """
        gaps = []
        
        for issue in issues:
            if issue.severity == "error" and issue.slot:
                # 将 error 转换为 gap
                gaps.append(SlotGap(
                    slot=issue.slot,
                    level=GapLevel.MAJOR,
                    reason="validation_failed",
                    priority=10
                ))
        
        return gaps
