"""两级提问逻辑"""

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
            "id": "input",
            "text": "输入是什么？（文件/代码/数据/命令等）",
            "required": False,
            "default": "任意"
        },
        {
            "id": "env",
            "text": "运行环境？（OS/Shell/Runtime，如 Windows/Linux/Python/Node）",
            "required": False,
            "default": "通用"
        },
        {
            "id": "ide",
            "text": "使用哪个 IDE/编辑器？（windsurf/cursor/vscode/generic）",
            "required": True
        }
    ]
    
    def collect(self) -> SearchQuery:
        """收集需求"""
        answers = {}
        
        print("=== 需求收集（Level 1）===\n")
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
        
        if self._needs_clarification(answers):
            print("\n=== 补充信息（Level 2）===\n")
            
            if len(answers["goal"].split()) < 3:
                detail = input("能否详细描述一下具体要做什么？: ").strip()
                if detail:
                    answers["goal"] += f" - {detail}"
            
            constraints = input("有什么硬约束吗？（如不可联网/必须离线/不可修改文件等，无则回车）: ").strip()
            if constraints:
                answers["constraints"] = [c.strip() for c in constraints.split(",")]
        
        return SearchQuery(
            goal=answers["goal"],
            input_type=answers.get("input"),
            env=answers.get("env"),
            ide=answers["ide"],
            constraints=answers.get("constraints"),
            tags=self._extract_tags(answers["goal"]),
            keywords=self._extract_keywords(answers["goal"])
        )
    
    def _needs_clarification(self, answers: Dict) -> bool:
        """判断是否需要 Level 2"""
        return len(answers["goal"].split()) < 5
    
    def _extract_tags(self, goal: str) -> List[str]:
        """从 goal 提取 tags（简单关键词映射）"""
        tag_map = {
            "代码": "code-generation",
            "生成": "code-generation",
            "重构": "code-refactoring",
            "git": "git-integration",
            "commit": "git-commit",
            "多文件": "multi-file-editing",
            "测试": "testing",
            "文档": "documentation",
            "编辑": "code-generation",
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
        words = goal.split()
        return [w.strip() for w in words if len(w.strip()) > 2]
