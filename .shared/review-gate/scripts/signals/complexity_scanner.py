"""Scan for complexity issues."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class ComplexityIssue:
    """A complexity issue found in code."""
    file_path: str
    line_number: int
    issue_type: str
    severity: str
    details: str


class ComplexityScanner:
    """Scans for complexity anti-patterns."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    def scan(self, file_path: str) -> List[ComplexityIssue]:
        """Scan a file for complexity issues."""
        full_path = self.repo_path / file_path
        if not full_path.exists():
            return []
        
        try:
            content = full_path.read_text(encoding="utf-8")
        except Exception:
            return []
        
        issues = []
        issues.extend(self._check_nesting(file_path, content))
        issues.extend(self._check_function_length(file_path, content))
        issues.extend(self._check_god_functions(file_path, content))
        
        return issues
    
    def _check_nesting(self, file_path: str, content: str) -> List[ComplexityIssue]:
        """Check for excessive nesting."""
        issues = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines, 1):
            indent = len(line) - len(line.lstrip())
            if indent > 16:
                issues.append(ComplexityIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type="deep_nesting",
                    severity="MEDIUM",
                    details=f"Nesting depth: {indent // 2} levels",
                ))
        
        return issues
    
    def _check_function_length(self, file_path: str, content: str) -> List[ComplexityIssue]:
        """Check for long functions."""
        issues = []
        lines = content.split("\n")
        
        func_pattern = r"^\s*(function|const|let|var)\s+(\w+)\s*[=\(]"
        current_func = None
        func_start = 0
        
        for i, line in enumerate(lines, 1):
            if re.match(func_pattern, line):
                if current_func and (i - func_start) > 60:
                    issues.append(ComplexityIssue(
                        file_path=file_path,
                        line_number=func_start,
                        issue_type="long_function",
                        severity="MEDIUM",
                        details=f"Function '{current_func}' is {i - func_start} lines",
                    ))
                current_func = re.match(func_pattern, line).group(2)
                func_start = i
        
        return issues
    
    def _check_god_functions(self, file_path: str, content: str) -> List[ComplexityIssue]:
        """Check for god functions (too many responsibilities)."""
        issues = []
        
        if_count = len(re.findall(r"\bif\s*\(", content))
        for_count = len(re.findall(r"\b(for|while)\s*\(", content))
        
        if if_count > 10 or for_count > 5:
            issues.append(ComplexityIssue(
                file_path=file_path,
                line_number=1,
                issue_type="god_function",
                severity="HIGH",
                details=f"High branching: {if_count} ifs, {for_count} loops",
            ))
        
        return issues
