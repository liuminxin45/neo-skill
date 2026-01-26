"""
Interview Engine: Two-Level Interview Framework (不可禁用)
Level 1: 固定 5-7 问
Level 2: 缺口驱动，最多两轮，每轮≤3问
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from .types import (
    QuestionSpec, QuestionOption, AnswerType, InterviewState,
    GapScore, GapLevel, SlotGap
)
from .search import IndexManager


class InterviewEngine:
    """
    提问引擎（不变量）。
    必须执行 Level1 → Gap Scoring → (可选) Level2。
    """
    
    def __init__(self, data_root: Path):
        self.data_root = data_root
        self.index_manager = IndexManager(data_root)
    
    def get_level1_questions(self, task_type: str, capability_tags: list[str]) -> list[QuestionSpec]:
        """
        获取 Level 1 问题（固定 5-7 问）。
        从 universal/questions.level1.json 加载。
        """
        questions_data = self.index_manager.load_required_pack("questions.level1", "universal")
        
        if not questions_data:
            # 安全降级：使用硬编码的最小问题集
            return self._get_fallback_level1_questions()
        
        questions = []
        for q_data in questions_data.get("questions", []):
            options = [
                QuestionOption(
                    value=opt["value"],
                    label=opt["label"],
                    recommended=opt.get("recommended", False),
                    reason=opt.get("reason")
                )
                for opt in q_data.get("options", [])
            ]
            
            questions.append(QuestionSpec(
                slot=q_data["slot"],
                required=q_data["required"],
                prompt=q_data["prompt"],
                answer_type=AnswerType(q_data["answer_type"]),
                options=options,
                default=q_data.get("default"),
                stop_condition=q_data.get("stop_condition"),
                level=1
            ))
        
        return questions
    
    def _get_fallback_level1_questions(self) -> list[QuestionSpec]:
        """硬编码的最小 Level 1 问题集（安全降级）"""
        return [
            QuestionSpec(
                slot="goal",
                required=True,
                prompt="这个 skill 的一句话目标是什么（动词开头，面向可重复任务）？",
                answer_type=AnswerType.TEXT,
                level=1
            ),
            QuestionSpec(
                slot="input",
                required=True,
                prompt="需要哪些输入（URL/文件/配置等），从哪里来？请至少给 1 个示例。",
                answer_type=AnswerType.EXAMPLES,
                level=1
            ),
            QuestionSpec(
                slot="output",
                required=True,
                prompt="期望输出是什么形态？",
                answer_type=AnswerType.ENUM,
                options=[
                    QuestionOption("A", "纯文本消息（邮件/IM）", recommended=True, reason="最简单"),
                    QuestionOption("B", "Markdown 报告"),
                    QuestionOption("C", "JSON 结果"),
                    QuestionOption("D", "代码片段/脚本"),
                    QuestionOption("E", "其他（请说明）"),
                ],
                level=1
            ),
            QuestionSpec(
                slot="environment",
                required=False,
                prompt="运行环境有哪些约束（本地/CI/联网/权限/代理等）？",
                answer_type=AnswerType.TEXT,
                default="本地环境，可联网",
                level=1
            ),
            QuestionSpec(
                slot="constraints",
                required=False,
                prompt="硬约束有哪些（频率/合规/不可做的事）？",
                answer_type=AnswerType.TEXT,
                default="无特殊约束",
                level=1
            ),
            QuestionSpec(
                slot="acceptance",
                required=True,
                prompt="请提供至少 2 条验收用例（必须包含'无数据'或'失败'场景之一）",
                answer_type=AnswerType.EXAMPLES,
                level=1
            ),
        ]
    
    def score_gaps(self, state: InterviewState) -> GapScore:
        """
        缺口评分（不变量）。
        
        生成阈值（满足即可停止提问）：
        - output 槽位可模板化（可选择/推断 Output Pack）
        - acceptance ≥ 2（含失败/无数据场景之一）
        - environment/constraints 不矛盾且不阻塞执行
        """
        gaps = []
        
        # 检查 goal
        if not state.goal or len(state.goal.strip()) < 10:
            gaps.append(SlotGap(
                slot="goal",
                level=GapLevel.MAJOR,
                reason="missing" if not state.goal else "vague",
                priority=10
            ))
        
        # 检查 input
        if not state.input_source:
            gaps.append(SlotGap(
                slot="input",
                level=GapLevel.MAJOR,
                reason="missing",
                priority=9
            ))
        
        # 检查 output
        if not state.output_format:
            gaps.append(SlotGap(
                slot="output",
                level=GapLevel.MAJOR,
                reason="missing",
                priority=8
            ))
        
        # 检查 acceptance
        if len(state.acceptance) < 2:
            gaps.append(SlotGap(
                slot="acceptance",
                level=GapLevel.MAJOR,
                reason="missing",
                priority=7
            ))
        else:
            # 检查是否包含失败/无数据场景
            has_failure_case = any(
                "失败" in a or "错误" in a or "无数据" in a or "empty" in a.lower() or "fail" in a.lower()
                for a in state.acceptance
            )
            if not has_failure_case:
                gaps.append(SlotGap(
                    slot="acceptance",
                    level=GapLevel.MINOR,
                    reason="missing failure case",
                    priority=5
                ))
        
        # 检查 environment/constraints 是否矛盾
        if state.environment and state.constraints:
            if "不可联网" in state.environment and "需要联网" in state.constraints:
                gaps.append(SlotGap(
                    slot="environment",
                    level=GapLevel.MAJOR,
                    reason="conflicting",
                    priority=6
                ))
        
        # 判断是否满足生成阈值
        major_gaps = [g for g in gaps if g.level == GapLevel.MAJOR]
        should_continue = len(major_gaps) > 0
        
        stop_reason = None
        if not should_continue:
            stop_reason = "满足生成阈值：output 可模板化，acceptance ≥ 2，无矛盾约束"
        
        return GapScore(
            gaps=gaps,
            should_continue_level2=should_continue,
            stop_reason=stop_reason
        )
    
    def generate_level2_questions(
        self, 
        state: InterviewState, 
        gap_score: GapScore
    ) -> list[QuestionSpec]:
        """
        生成 Level 2 问题（缺口驱动）。
        最多两轮，每轮≤3问。
        """
        if state.level2_rounds >= state.max_level2_rounds:
            return []
        
        top_gaps = gap_score.get_top_gaps(max_count=state.max_questions_per_round)
        
        questions = []
        for gap in top_gaps:
            question = self._create_level2_question_for_gap(gap, state)
            if question:
                questions.append(question)
        
        return questions
    
    def _create_level2_question_for_gap(
        self, 
        gap: SlotGap, 
        state: InterviewState
    ) -> Optional[QuestionSpec]:
        """为特定缺口创建 Level 2 问题"""
        
        if gap.slot == "goal":
            return QuestionSpec(
                slot="goal",
                required=True,
                prompt="请更具体地描述目标：这个 skill 要解决什么问题？成功的标准是什么？",
                answer_type=AnswerType.TEXT,
                level=2
            )
        
        elif gap.slot == "input":
            return QuestionSpec(
                slot="input",
                required=True,
                prompt="请提供输入的具体示例（URL/文件路径/配置内容等）",
                answer_type=AnswerType.EXAMPLES,
                level=2
            )
        
        elif gap.slot == "output":
            return QuestionSpec(
                slot="output",
                required=True,
                prompt="输出应该是什么形态？",
                answer_type=AnswerType.ENUM,
                options=[
                    QuestionOption("A", "纯文本消息", recommended=True),
                    QuestionOption("B", "Markdown 报告"),
                    QuestionOption("C", "JSON 结果"),
                    QuestionOption("D", "代码片段"),
                ],
                level=2
            )
        
        elif gap.slot == "acceptance":
            if gap.reason == "missing":
                return QuestionSpec(
                    slot="acceptance",
                    required=True,
                    prompt="请提供至少 2 条验收用例（包含正常情况和失败/无数据情况）",
                    answer_type=AnswerType.EXAMPLES,
                    level=2
                )
            elif gap.reason == "missing failure case":
                return QuestionSpec(
                    slot="acceptance",
                    required=False,
                    prompt="请补充一条失败或无数据场景的验收用例",
                    answer_type=AnswerType.EXAMPLES,
                    level=2
                )
        
        elif gap.slot == "environment":
            if gap.reason == "conflicting":
                return QuestionSpec(
                    slot="environment",
                    required=True,
                    prompt="环境约束与需求矛盾，请明确：是否可以联网？是否有代理？",
                    answer_type=AnswerType.TEXT,
                    level=2
                )
        
        return None
