"""
Router/Tagger: 产出 task_type + capability_tags
采用中等粒度、可扩展但不复杂的 tag 设计。
"""
from __future__ import annotations
import re
from typing import Tuple


# Coarse tags (小而稳定，~20-40个以内)
COARSE_TAGS = {
    # 数据获取
    "http_fetch": ["http", "https", "fetch", "request", "api", "rest"],
    "rss": ["rss", "feed", "atom"],
    "html_parse": ["html", "parse", "scrape", "beautifulsoup", "xpath"],
    "json_parse": ["json", "parse"],
    "xml_parse": ["xml", "parse"],
    "file_read": ["read file", "load file", "file input"],
    
    # 数据处理
    "text_process": ["text", "string", "process", "clean"],
    "data_transform": ["transform", "convert", "map"],
    "filter": ["filter", "select", "query"],
    "aggregate": ["aggregate", "sum", "count", "group"],
    
    # 输出/通知
    "email_smtp": ["email", "smtp", "send mail", "notify"],
    "file_write": ["write file", "save", "export"],
    "report_gen": ["report", "generate", "summary"],
    "markdown": ["markdown", "md"],
    
    # 调度/自动化
    "scheduler_local": ["schedule", "cron", "periodic", "daily", "hourly"],
    "automation": ["automate", "workflow", "pipeline"],
    
    # 认证/网络
    "auth": ["auth", "authentication", "login", "credential"],
    "token": ["token", "bearer", "jwt"],
    "proxy": ["proxy", "socks", "http proxy"],
    "offline": ["offline", "no network", "local only"],
    
    # 错误处理/可靠性
    "retry": ["retry", "resilient", "fault tolerant"],
    "timeout": ["timeout", "deadline"],
    "error_handling": ["error", "exception", "handle failure"],
    "logging": ["log", "logging", "trace"],
    
    # 格式/编码
    "csv": ["csv", "comma separated"],
    "excel": ["excel", "xlsx", "xls"],
    "pdf": ["pdf"],
    "image": ["image", "png", "jpg", "jpeg"],
    
    # 环境
    "docker": ["docker", "container"],
    "ci_cd": ["ci", "cd", "github actions", "gitlab ci"],
    "cloud": ["cloud", "aws", "gcp", "azure"],
}


# Task type patterns (基于动词+对象的模式)
TASK_TYPE_PATTERNS = [
    (r"(fetch|get|download|scrape|crawl).*(web|url|page|site)", "web_scraping"),
    (r"(fetch|get|read).*(rss|feed|atom)", "rss_monitoring"),
    (r"(send|email|notify|alert)", "notification"),
    (r"(schedule|cron|periodic|daily|hourly)", "scheduled_task"),
    (r"(generate|create|build).*(report|summary|document)", "report_generation"),
    (r"(transform|convert|process).*(data|file)", "data_transformation"),
    (r"(monitor|watch|track|check)", "monitoring"),
    (r"(backup|archive|sync)", "backup_sync"),
    (r"(deploy|release|publish)", "deployment"),
    (r"(test|validate|verify)", "testing_validation"),
]


class Router:
    """
    Router/Tagger: 分析用户请求，产出 task_type + capability_tags。
    实现必须简单：规则 + 少量同义词表 + 少量模式匹配。
    """
    
    def __init__(self):
        self.coarse_tags = COARSE_TAGS
        self.task_type_patterns = TASK_TYPE_PATTERNS
    
    def route(self, user_request: str) -> Tuple[str, list[str]]:
        """
        分析用户请求，返回 (task_type, capability_tags)。
        
        Args:
            user_request: 用户的原始请求
            
        Returns:
            (task_type, capability_tags)
        """
        request_lower = user_request.lower()
        
        # 1. 识别 task_type
        task_type = self._identify_task_type(request_lower)
        
        # 2. 识别 capability_tags
        capability_tags = self._identify_tags(request_lower)
        
        return task_type, capability_tags
    
    def _identify_task_type(self, request_lower: str) -> str:
        """识别任务类型"""
        for pattern, task_type in self.task_type_patterns:
            if re.search(pattern, request_lower):
                return task_type
        
        # 默认：automation
        return "automation"
    
    def _identify_tags(self, request_lower: str) -> list[str]:
        """识别能力标签"""
        tags = []
        
        for tag, keywords in self.coarse_tags.items():
            for keyword in keywords:
                if keyword in request_lower:
                    tags.append(tag)
                    break  # 每个 tag 最多匹配一次
        
        # 去重并排序（保持稳定性）
        tags = sorted(set(tags))
        
        return tags
    
    def add_fine_tag(self, tags: list[str], fine_tag: str) -> list[str]:
        """
        可选：添加 fine tag（仅在需要时由规则补充）。
        例如：specific_format/cdn_image_extract 等。
        """
        if fine_tag not in tags:
            tags.append(fine_tag)
        return tags
