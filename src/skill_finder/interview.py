"""两级提问逻辑"""

import re
from typing import Dict, List, Optional
from .models import SearchQuery


class Interview:
    """最小两级提问收集需求"""
    
    LEVEL1_QUESTIONS = [
        {
            "id": "goal",
            "text": "你想实现什么目标？（一句话描述任务）",
            "required": True
        },
        {
            "id": "env",
            "text": "技术栈/环境？（如 React/Vue/Next.js/SwiftUI/Flutter/HTML+Tailwind；不确定可回车）",
            "required": False,
            "default": "通用"
        },
        {
            "id": "ide",
            "text": "使用哪个 IDE/编辑器？（windsurf/cursor/vscode/generic）",
            "required": True
        },
        {
            "id": "constraints",
            "text": "硬约束？（如不可联网/必须离线/不可修改文件等；无则回车）",
            "required": False
        }
    ]
    
    def collect(self) -> SearchQuery:
        """收集需求（最多 1 轮，最多 4 问）"""
        answers = {}
        
        print("=== 需求收集 ===\n")
        for q in self.LEVEL1_QUESTIONS:
            if q["required"]:
                answer = input(f"{q['text']}: ").strip()
                while not answer:
                    answer = input(f"{q['text']}（必填）: ").strip()
                answers[q["id"]] = answer
            else:
                default_hint = f" [默认: {q.get('default', '跳过')}]" if q.get('default') else ""
                answer = input(f"{q['text']}{default_hint}: ").strip()
                answers[q["id"]] = answer if answer else q.get("default")

        constraints_value = answers.get("constraints")
        constraints_list: Optional[List[str]] = None
        if isinstance(constraints_value, str) and constraints_value and constraints_value != "通用":
            constraints_list = [c.strip() for c in re.split(r"[,，]", constraints_value) if c.strip()]
        
        return SearchQuery(
            goal=answers["goal"],
            env=answers.get("env"),
            ide=answers["ide"],
            constraints=constraints_list,
            tags=self._extract_tags(answers["goal"]),
            keywords=self._extract_keywords(answers["goal"])
        )
    
    def _extract_tags(self, goal: str) -> List[str]:
        """从 goal 提取 tags（简单关键词映射）"""
        tag_map = {
            "ui": "ui-design",
            "ux": "ux-design",
            "ui/ux": "ui-design",
            "原型": "ui-design",
            "prototype": "ui-design",
            "landing": "web-design",
            "落地页": "web-design",
            "dashboard": "frontend",
            "仪表板": "frontend",
            "设计系统": "design-system",
            "design system": "design-system",
            "style guide": "style-guide",
            "组件库": "component-library",
            "component library": "component-library",
            "design token": "design-tokens",
            "无障碍": "design-guidelines",
            "accessibility": "design-guidelines",
        }
        tags = []
        goal_lower = goal.lower()
        for keyword, tag in tag_map.items():
            if keyword in goal_lower:
                if tag not in tags:
                    tags.append(tag)
        return tags
    
    def _extract_keywords(self, goal: str) -> List[str]:
        """提取关键词"""
        keywords: List[str] = []
        text = goal.strip()

        for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9\+\-\./#]*", text):
            for part in re.split(r"[/_]+", token):
                part = part.strip()
                if part and part.lower() not in [k.lower() for k in keywords]:
                    keywords.append(part)

        for token in re.split(r"\s+", text):
            token = token.strip()
            if token and len(token) > 2 and token.lower() not in [k.lower() for k in keywords]:
                keywords.append(token)

        synonyms = {
            "ui/ux": ["ui", "ux"],
            "用户体验": ["ux"],
            "设计系统": ["design system", "design tokens"],
            "原型": ["prototype"],
            "落地页": ["landing page"],
        }
        lowered = text.lower()
        for k, vals in synonyms.items():
            if k in lowered:
                for v in vals:
                    if v.lower() not in [x.lower() for x in keywords]:
                        keywords.append(v)

        return keywords
