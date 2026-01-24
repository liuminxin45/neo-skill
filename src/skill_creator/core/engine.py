"""
Main Engine: 主流程编排器（整合所有 Core + Providers）
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from .types import SkillCreatorContext, InterviewState
from .router import Router
from .interview import InterviewEngine
from .orchestrator import PlanOrchestrator
from .builder import SkillBuilder
from .validator import Validator
from ..providers import RecipeProvider, ToolCatalogProvider, ChecklistProvider


class SkillCreatorEngine:
    """
    Skill Creator 主引擎。
    整合 Core (不变量) + Providers (可插拔)。
    """
    
    def __init__(self, data_root: Path):
        self.data_root = data_root
        
        # Core 组件（不可禁用）
        self.router = Router()
        self.interview_engine = InterviewEngine(data_root)
        self.plan_orchestrator = PlanOrchestrator(data_root)
        self.skill_builder = SkillBuilder(data_root)
        self.validator = Validator(data_root)
        
        # Providers（可插拔，默认启用）
        self.providers = [
            RecipeProvider(data_root),
            ToolCatalogProvider(data_root),
            ChecklistProvider(data_root),
        ]
    
    def create_skill(self, user_request: str) -> SkillCreatorContext:
        """
        创建 skill 的完整流程。
        
        流程:
        1. Router/Tagger → task_type + capability_tags
        2. Interview Engine → Level1 → Gap → Level2 (可选)
        3. Providers 并行推荐
        4. Plan Orchestrator → 生成 Plan
        5. Skill Builder → 生成 SkillDraft
        6. Validator → schema + dry-run
        7. 返回 Context（包含所有中间结果）
        """
        # 1. Router/Tagger
        task_type, capability_tags = self.router.route(user_request)
        
        # 初始化 Context
        ctx = SkillCreatorContext(
            user_request=user_request,
            task_type=task_type,
            capability_tags=capability_tags,
            interview_state=InterviewState(
                task_type=task_type,
                capability_tags=capability_tags
            )
        )
        
        ctx.add_trace("routing", {
            "task_type": task_type,
            "capability_tags": capability_tags
        })
        
        # 2. Interview Engine - Level 1
        level1_questions = self.interview_engine.get_level1_questions(task_type, capability_tags)
        ctx.add_trace("level1_questions", {
            "count": len(level1_questions),
            "questions": [q.prompt for q in level1_questions]
        })
        
        # 注意：实际使用时，这里需要与用户交互收集答案
        # 这里仅作为框架演示，假设已收集答案
        # 在实际实现中，应该返回 questions 给调用者，等待用户回答
        
        return ctx
    
    def continue_with_answers(
        self, 
        ctx: SkillCreatorContext, 
        answers: dict[str, any]
    ) -> SkillCreatorContext:
        """
        继续流程（在收集到用户答案后）。
        
        Args:
            ctx: 当前上下文
            answers: 用户答案 {slot: value}
        """
        # 更新 interview state
        for slot, value in answers.items():
            ctx.interview_state.add_answer(slot, value, "user")
        
        ctx.interview_state.level1_completed = True
        
        # Gap Scoring
        gap_score = self.interview_engine.score_gaps(ctx.interview_state)
        ctx.gap_score = gap_score
        
        ctx.add_trace("gap_scoring", {
            "should_continue_level2": gap_score.should_continue_level2,
            "gaps_count": len(gap_score.gaps),
            "major_gaps": len([g for g in gap_score.gaps if g.level.value == "major"])
        })
        
        # 如果需要 Level 2，生成问题并返回
        if gap_score.should_continue_level2 and \
           ctx.interview_state.level2_rounds < ctx.interview_state.max_level2_rounds:
            level2_questions = self.interview_engine.generate_level2_questions(
                ctx.interview_state, 
                gap_score
            )
            ctx.add_trace("level2_questions", {
                "round": ctx.interview_state.level2_rounds + 1,
                "count": len(level2_questions),
                "questions": [q.prompt for q in level2_questions]
            })
            # 返回 ctx，调用者需要继续收集答案
            return ctx
        
        # 否则，继续生成流程
        return self._continue_generation(ctx)
    
    def _continue_generation(self, ctx: SkillCreatorContext) -> SkillCreatorContext:
        """继续生成流程（在提问完成后）"""
        
        # 3. Providers 并行推荐
        for provider in self.providers:
            try:
                recommendation = provider.recommend(ctx)
                ctx.recommendations[provider.get_name()] = recommendation
                ctx.add_trace(f"provider_{provider.get_name()}", {
                    "items_count": len(recommendation.items),
                    "confidence": recommendation.confidence
                })
            except Exception as e:
                # 安全降级：provider 失败不影响主流程
                ctx.add_trace(f"provider_{provider.get_name()}_error", str(e))
        
        # 4. Plan Orchestrator
        plan = self.plan_orchestrator.generate_plan(ctx)
        ctx.plan = plan
        
        # 5. Skill Builder
        skill_draft = self.skill_builder.build_skill(ctx, plan)
        ctx.skill_draft = skill_draft
        
        # 6. Validator
        validation_result = self.validator.validate(ctx, skill_draft)
        ctx.validation_result = validation_result
        
        # 如果有缺口，可以触发最小追问（这里简化处理）
        if validation_result.missing_gaps:
            ctx.add_trace("validation_gaps", {
                "gaps_count": len(validation_result.missing_gaps),
                "gaps": [g.slot for g in validation_result.missing_gaps]
            })
        
        return ctx
    
    def get_doctor_report(self, ctx: SkillCreatorContext) -> str:
        """
        生成 doctor/debug 报告。
        展示本次命中哪些索引/加载哪些文件/为何命中/最终选用的资源。
        """
        lines = [
            "# Skill Creator Doctor Report",
            "",
            "## 1. Routing",
            f"- **User Request**: {ctx.user_request[:100]}...",
            f"- **Task Type**: {ctx.task_type}",
            f"- **Capability Tags**: {', '.join(ctx.capability_tags)}",
            "",
            "## 2. Interview",
        ]
        
        if "level1_questions" in ctx.trace:
            level1 = ctx.trace["level1_questions"]
            lines.append(f"- **Level 1 Questions**: {level1['count']} 个")
        
        if "gap_scoring" in ctx.trace:
            gap = ctx.trace["gap_scoring"]
            lines.append(f"- **Gap Scoring**: {gap['gaps_count']} 个缺口 ({gap['major_gaps']} 个主要)")
            lines.append(f"- **Continue Level 2**: {gap['should_continue_level2']}")
        
        if "level2_questions" in ctx.trace:
            level2 = ctx.trace["level2_questions"]
            lines.append(f"- **Level 2 Questions**: Round {level2['round']}, {level2['count']} 个")
        
        lines.extend([
            "",
            "## 3. Providers Recommendations",
        ])
        
        for provider_name, rec in ctx.recommendations.items():
            lines.append(f"### {provider_name.title()}")
            lines.append(f"- **Items**: {len(rec.items)}")
            lines.append(f"- **Confidence**: {rec.confidence:.2f}")
            if rec.trace:
                lines.append(f"- **Trace**: {rec.trace}")
        
        lines.extend([
            "",
            "## 4. Plan",
        ])
        
        if ctx.plan:
            lines.append(f"- **Output Pack**: {ctx.plan.output_pack}")
            lines.append(f"- **Recipe**: {ctx.plan.recipe_id or 'None'}")
            lines.append(f"- **Libraries**: {len(ctx.plan.libraries)}")
            for lib in ctx.plan.libraries:
                lines.append(f"  - {lib.name}: {lib.purpose}")
            lines.append(f"- **Checklists**: {', '.join(ctx.plan.checklists) or 'None'}")
        
        lines.extend([
            "",
            "## 5. Skill Draft",
        ])
        
        if ctx.skill_draft:
            lines.append(f"- **Name**: {ctx.skill_draft.name}")
            lines.append(f"- **Triggers**: {len(ctx.skill_draft.triggers)}")
            lines.append(f"- **Workflow Steps**: {len(ctx.skill_draft.workflow_steps)}")
        
        lines.extend([
            "",
            "## 6. Validation",
        ])
        
        if ctx.validation_result:
            lines.append(f"- **Passed**: {ctx.validation_result.passed}")
            lines.append(f"- **Issues**: {len(ctx.validation_result.issues)}")
            for issue in ctx.validation_result.issues:
                lines.append(f"  - [{issue.severity.upper()}] {issue.message}")
        
        lines.extend([
            "",
            "## 7. Full Trace",
            "```json"
        ])
        
        import json
        lines.append(json.dumps(ctx.trace, indent=2, ensure_ascii=False))
        lines.append("```")
        
        return "\n".join(lines)
