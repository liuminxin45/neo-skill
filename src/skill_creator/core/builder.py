"""
Skill Builder: 产出 skill（基于 Plan + Output Pack）
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from .types import SkillCreatorContext, SkillDraft, Plan
from .search import IndexManager


class SkillBuilder:
    """
    Skill 构建器。
    基于 Plan + Output Pack 生成 SkillDraft。
    """
    
    def __init__(self, data_root: Path):
        self.data_root = data_root
        self.index_manager = IndexManager(data_root)
    
    def build_skill(self, ctx: SkillCreatorContext, plan: Plan) -> SkillDraft:
        """
        构建 skill（基于 Plan）。
        
        流程:
        1. 加载 Output Pack 模板
        2. 加载 Recipe（若有）
        3. 生成 workflow steps
        4. 生成 triggers
        5. 组装 SkillDraft
        """
        # 1. 加载 Output Pack 模板
        pack_template = self._load_output_pack(plan.output_pack)
        
        # 2. 加载 Recipe（若有）
        recipe = None
        if plan.recipe_id:
            recipe = self._load_recipe(plan.recipe_id)
        
        # 3. 生成 workflow steps
        workflow_steps = self._generate_workflow_steps(ctx, pack_template, recipe)
        
        # 4. 生成 triggers
        triggers = self._generate_triggers(ctx)
        
        # 5. 生成 name 和 description
        name = self._generate_name(ctx)
        description = self._generate_description(ctx)
        
        draft = SkillDraft(
            name=name,
            description=description,
            triggers=triggers,
            workflow_steps=workflow_steps,
            output_pack=plan.output_pack,
            applied_recipe=plan.recipe_id,
            applied_checklists=plan.checklists,
            libraries_used=[lib.name for lib in plan.libraries]
        )
        
        ctx.add_trace("skill_building", {
            "name": name,
            "workflow_steps_count": len(workflow_steps),
            "triggers_count": len(triggers)
        })
        
        return draft
    
    def _load_output_pack(self, pack_id: str) -> Optional[dict]:
        """加载 Output Pack 模板"""
        pack_file = self.data_root / "universal" / "output_packs" / f"{pack_id}.json"
        if pack_file.exists():
            return self.index_manager._load_json(pack_file)
        return None
    
    def _load_recipe(self, recipe_id: str) -> Optional[dict]:
        """加载 Recipe"""
        recipe_file = self.data_root / "recipes" / f"{recipe_id}.json"
        if recipe_file.exists():
            return self.index_manager._load_json(recipe_file)
        return None
    
    def _generate_workflow_steps(
        self, 
        ctx: SkillCreatorContext,
        pack_template: Optional[dict],
        recipe: Optional[dict]
    ) -> list[dict]:
        """
        生成 workflow steps。
        优先使用 recipe，否则使用 pack 的 workflow_pattern。
        """
        steps = []
        
        # 优先使用 recipe 的 workflow_steps
        if recipe and "workflow_steps" in recipe:
            steps = recipe["workflow_steps"]
        # 否则使用 pack 的 workflow_pattern
        elif pack_template and "template" in pack_template:
            pattern = pack_template["template"].get("workflow_pattern", [])
            for i, step_pattern in enumerate(pattern):
                steps.append({
                    "id": step_pattern.get("step", f"step_{i+1}"),
                    "title": step_pattern.get("description", f"Step {i+1}"),
                    "kind": "action",
                    "commands": [],
                    "notes": step_pattern.get("description", "")
                })
        # 兜底：通用步骤
        else:
            steps = [
                {
                    "id": "collect",
                    "title": "收集数据",
                    "kind": "action",
                    "commands": [],
                    "notes": f"从 {ctx.interview_state.input_source or '输入源'} 收集数据"
                },
                {
                    "id": "process",
                    "title": "处理数据",
                    "kind": "action",
                    "commands": [],
                    "notes": "根据需求处理数据"
                },
                {
                    "id": "output",
                    "title": "输出结果",
                    "kind": "action",
                    "commands": [],
                    "notes": f"输出为 {ctx.interview_state.output_format or '指定格式'}"
                }
            ]
        
        # 添加三方库推荐信息到第一个步骤的 notes
        if steps and ctx.plan and ctx.plan.libraries:
            lib_notes = ["\n\n**推荐的第三方库**:"]
            for lib in ctx.plan.libraries:
                lib_notes.append(f"- `{lib.name}`: {lib.purpose}")
                if lib.pypi_link:
                    lib_notes.append(f"  - 安装: `pip install {lib.name}`")
                if lib.docs_link:
                    lib_notes.append(f"  - 文档: {lib.docs_link}")
            
            # 将库信息添加到第一个步骤的 notes
            if steps[0].get("notes"):
                steps[0]["notes"] += "\n".join(lib_notes)
            else:
                steps[0]["notes"] = "\n".join(lib_notes)
        
        return steps
    
    def _generate_triggers(self, ctx: SkillCreatorContext) -> list[str]:
        """生成 triggers（至少 3 条）"""
        goal = ctx.interview_state.goal or "执行任务"
        
        triggers = [
            goal,
            f"帮我{goal}",
            f"自动{goal}"
        ]
        
        # 基于 task_type 添加触发词
        task_triggers = {
            "rss_monitoring": ["抓取 RSS", "监控 feed", "RSS 订阅"],
            "web_scraping": ["抓取网页", "爬取数据", "scrape website"],
            "notification": ["发送通知", "邮件提醒", "send notification"],
            "scheduled_task": ["定时执行", "每天运行", "schedule task"],
            "report_generation": ["生成报告", "创建总结", "generate report"]
        }
        
        if ctx.task_type in task_triggers:
            triggers.extend(task_triggers[ctx.task_type][:2])
        
        return triggers[:5]  # 最多 5 条
    
    def _generate_name(self, ctx: SkillCreatorContext) -> str:
        """生成 skill name（kebab-case）"""
        goal = ctx.interview_state.goal or "automation-task"
        
        # 简化为 kebab-case
        name = goal.lower()
        name = name.replace(" ", "-")
        name = name.replace("_", "-")
        # 移除非字母数字字符
        import re
        name = re.sub(r'[^a-z0-9\-]', '', name)
        # 移除多余的连字符
        name = re.sub(r'-+', '-', name)
        name = name.strip('-')
        
        # 限制长度
        if len(name) > 50:
            name = name[:50].rstrip('-')
        
        return name or "auto-task"
    
    def _generate_description(self, ctx: SkillCreatorContext) -> str:
        """生成 description"""
        goal = ctx.interview_state.goal or "执行自动化任务"
        constraints = ctx.interview_state.constraints
        
        desc = f"{goal}。"
        
        if constraints and constraints != "无特殊约束":
            desc += f" 约束: {constraints}"
        
        return desc
