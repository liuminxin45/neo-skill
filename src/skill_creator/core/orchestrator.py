"""
Plan Orchestrator: 聚合 providers 推荐，生成 Plan（不可禁用）
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from .types import (
    SkillCreatorContext, Plan, LibraryRecommendation,
    InterviewState, SearchQuery
)
from .search import IndexManager


class PlanOrchestrator:
    """
    Plan 编排器（不变量）。
    聚合 providers 推荐，生成 Implementation Plan。
    """
    
    def __init__(self, data_root: Path):
        self.data_root = data_root
        self.index_manager = IndexManager(data_root)
    
    def generate_plan(self, ctx: SkillCreatorContext) -> Plan:
        """
        生成 Implementation Plan（不可禁用）。
        
        流程:
        1. 选择 Output Pack（必需）
        2. 聚合 providers 推荐（recipe/tools/checklists）
        3. 生成方案概述
        4. 列出假设和风险
        5. 返回 Plan
        """
        # 1. 选择 Output Pack（必需）
        output_pack = self._select_output_pack(ctx)
        
        # 2. 聚合 providers 推荐
        recipe_id = self._get_recommended_recipe(ctx)
        libraries = self._get_recommended_libraries(ctx)
        checklists = self._get_recommended_checklists(ctx)
        
        # 3. 生成方案概述
        summary = self._generate_summary(ctx, output_pack, recipe_id)
        
        # 4. 列出假设和风险
        assumptions = self._generate_assumptions(ctx)
        risks = self._generate_risks(ctx)
        
        plan = Plan(
            summary=summary,
            output_pack=output_pack,
            libraries=libraries,
            recipe_id=recipe_id,
            assumptions=assumptions,
            risks=risks,
            checklists=checklists
        )
        
        ctx.add_trace("plan_generation", {
            "output_pack": output_pack,
            "recipe_id": recipe_id,
            "libraries_count": len(libraries),
            "checklists_count": len(checklists)
        })
        
        return plan
    
    def _select_output_pack(self, ctx: SkillCreatorContext) -> str:
        """
        选择 Output Pack（必需，不可禁用）。
        基于 task_type + capability_tags + 用户输出偏好。
        """
        # 从 interview state 获取用户的输出偏好
        output_format = ctx.interview_state.output_format
        
        # 映射用户选择到 pack
        pack_mapping = {
            "A": "plain_text_message",
            "纯文本": "plain_text_message",
            "邮件": "plain_text_message",
            "B": "markdown_report",
            "markdown": "markdown_report",
            "报告": "markdown_report",
            "C": "json_result",
            "json": "json_result",
            "D": "code_snippet",
            "代码": "code_snippet",
            "脚本": "code_snippet",
        }
        
        # 尝试从用户输入映射
        if output_format:
            for key, pack in pack_mapping.items():
                if key.lower() in output_format.lower():
                    return pack
        
        # 基于 task_type 推断
        if ctx.task_type in ["notification", "monitoring"]:
            return "plain_text_message"
        elif ctx.task_type in ["report_generation"]:
            return "markdown_report"
        elif ctx.task_type in ["data_transformation", "web_scraping"]:
            return "json_result"
        
        # 默认：generic
        return "generic"
    
    def _get_recommended_recipe(self, ctx: SkillCreatorContext) -> Optional[str]:
        """从 providers 推荐中获取 recipe"""
        recipe_rec = ctx.recommendations.get("recipe")
        if recipe_rec and recipe_rec.items:
            return recipe_rec.items[0].get("id")
        return None
    
    def _get_recommended_libraries(self, ctx: SkillCreatorContext) -> list[LibraryRecommendation]:
        """从 providers 推荐中获取库栈"""
        tools_rec = ctx.recommendations.get("tools")
        libraries = []
        
        if tools_rec and tools_rec.items:
            for tool in tools_rec.items[:5]:  # 最多 5 个库
                libraries.append(LibraryRecommendation(
                    name=tool.get("name", ""),
                    purpose=tool.get("purpose", ""),
                    reason=tool.get("reason", ""),
                    pypi_link=tool.get("pypi_link", ""),
                    docs_link=tool.get("docs_link", ""),
                    fallback=tool.get("fallback")
                ))
        
        return libraries
    
    def _get_recommended_checklists(self, ctx: SkillCreatorContext) -> list[str]:
        """从 providers 推荐中获取 checklists"""
        checklist_rec = ctx.recommendations.get("checklists")
        if checklist_rec and checklist_rec.items:
            return [item.get("id", "") for item in checklist_rec.items]
        return []
    
    def _generate_summary(
        self, 
        ctx: SkillCreatorContext, 
        output_pack: str,
        recipe_id: Optional[str]
    ) -> str:
        """生成方案概述"""
        goal = ctx.interview_state.goal or "执行自动化任务"
        
        summary_parts = [
            f"**目标**: {goal}",
            "",
            f"**方案**: "
        ]
        
        if recipe_id:
            summary_parts.append(f"采用成熟蓝图 `{recipe_id}`，包含经过验证的步骤序列和配置模板。")
        else:
            summary_parts.append(f"使用通用自动化骨架，基于 `{output_pack}` 输出格式。")
        
        summary_parts.append("")
        summary_parts.append(f"**输出形式**: {self._get_pack_description(output_pack)}")
        
        return "\n".join(summary_parts)
    
    def _get_pack_description(self, pack: str) -> str:
        """获取 pack 描述"""
        descriptions = {
            "plain_text_message": "纯文本消息（适合邮件/IM 通知）",
            "markdown_report": "Markdown 格式报告（可读性强）",
            "json_result": "JSON 结构化数据（机器可消费）",
            "code_snippet": "代码片段/脚本（可执行）",
            "generic": "通用格式（灵活）"
        }
        return descriptions.get(pack, "未知格式")
    
    def _generate_assumptions(self, ctx: SkillCreatorContext) -> list[str]:
        """生成假设清单"""
        assumptions = []
        
        # 基于环境约束
        env = ctx.interview_state.environment or ""
        if "联网" in env or not env:
            assumptions.append("假设可以联网访问外部资源")
        
        if "本地" in env or not env:
            assumptions.append("假设在本地环境运行，可以读写文件")
        
        # 基于 capability_tags
        if "email_smtp" in ctx.capability_tags:
            assumptions.append("假设有可用的 SMTP 服务器和凭证")
        
        if "scheduler_local" in ctx.capability_tags:
            assumptions.append("假设可以长期运行或由系统调度器触发")
        
        # 基于输入
        if ctx.interview_state.input_source:
            assumptions.append(f"假设输入源稳定可访问: {ctx.interview_state.input_source[:50]}...")
        
        return assumptions
    
    def _generate_risks(self, ctx: SkillCreatorContext) -> list[str]:
        """生成风险清单"""
        risks = []
        
        # 基于 capability_tags
        if "http_fetch" in ctx.capability_tags:
            risks.append("网络请求可能超时或失败")
        
        if "html_parse" in ctx.capability_tags or "rss" in ctx.capability_tags:
            risks.append("目标网站结构变化可能导致解析失败")
        
        if "email_smtp" in ctx.capability_tags:
            risks.append("SMTP 凭证可能过期或被封禁")
        
        if "scheduler_local" in ctx.capability_tags:
            risks.append("进程意外退出会导致调度停止")
        
        # 基于约束
        constraints = ctx.interview_state.constraints or ""
        if "频率" in constraints or "定时" in constraints:
            risks.append("高频执行可能触发速率限制")
        
        return risks
