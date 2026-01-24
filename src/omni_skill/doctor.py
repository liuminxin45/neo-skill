"""
Doctor module: 诊断 skill 安装状态和依赖完整性

遵循架构规则：
- 检测 source path 泄漏
- 验证索引路径指向 Install Space
- 检查依赖闭包完整性
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set


@dataclass
class DiagnosticIssue:
    """诊断问题"""
    severity: str  # error, warning, info
    category: str  # path_leakage, missing_file, invalid_index, etc.
    message: str
    file: Optional[str] = None
    line: Optional[int] = None


@dataclass
class DiagnosticReport:
    """诊断报告"""
    skill_id: str
    install_root: Optional[str] = None
    installed_at: Optional[str] = None
    total_files: int = 0
    files: List[str] = field(default_factory=list)
    dependencies: dict = field(default_factory=dict)
    issues: List[DiagnosticIssue] = field(default_factory=list)
    
    def has_errors(self) -> bool:
        """是否有错误"""
        return any(issue.severity == "error" for issue in self.issues)
    
    def has_warnings(self) -> bool:
        """是否有警告"""
        return any(issue.severity == "warning" for issue in self.issues)
    
    def format(self) -> str:
        """格式化输出"""
        lines = [
            "=== Skill Diagnostic Report ===",
            "",
            f"Skill ID: {self.skill_id}",
        ]
        
        if self.install_root:
            lines.append(f"Install Root: {self.install_root}")
        if self.installed_at:
            lines.append(f"Installed At: {self.installed_at}")
        
        lines.extend([
            "",
            "--- Dependency Closure ---"
        ])
        
        if self.files:
            for file in self.files[:10]:  # 只显示前 10 个
                lines.append(f"✓ {file}")
            if len(self.files) > 10:
                lines.append(f"... and {len(self.files) - 10} more files")
        
        lines.append(f"\nTotal files: {self.total_files}")
        
        if self.dependencies:
            lines.extend([
                "",
                "--- Dependencies ---"
            ])
            
            if "libraries" in self.dependencies and self.dependencies["libraries"]:
                lines.append("Libraries:")
                for lib in self.dependencies["libraries"]:
                    lines.append(f"  - {lib}")
            
            if "data_packs" in self.dependencies and self.dependencies["data_packs"]:
                lines.append("\nData Packs:")
                for pack in self.dependencies["data_packs"]:
                    lines.append(f"  - {pack}")
        
        lines.extend([
            "",
            "--- Issues ---"
        ])
        
        if not self.issues:
            lines.append("None")
        else:
            # 按严重程度分组
            errors = [i for i in self.issues if i.severity == "error"]
            warnings = [i for i in self.issues if i.severity == "warning"]
            infos = [i for i in self.issues if i.severity == "info"]
            
            if errors:
                lines.append("\nErrors:")
                for issue in errors:
                    lines.append(f"  ❌ [{issue.category}] {issue.message}")
                    if issue.file:
                        lines.append(f"     File: {issue.file}")
            
            if warnings:
                lines.append("\nWarnings:")
                for issue in warnings:
                    lines.append(f"  ⚠️  [{issue.category}] {issue.message}")
                    if issue.file:
                        lines.append(f"     File: {issue.file}")
            
            if infos:
                lines.append("\nInfo:")
                for issue in infos:
                    lines.append(f"  ℹ️  [{issue.category}] {issue.message}")
        
        lines.extend([
            "",
            "=== Diagnostic Complete ==="
        ])
        
        return "\n".join(lines)


class SkillDoctor:
    """Skill 诊断器"""
    
    def __init__(self, install_root: Path):
        self.install_root = install_root
    
    def diagnose(self, skill_id: str, target: str = "windsurf") -> DiagnosticReport:
        """
        诊断 skill 安装状态
        
        Args:
            skill_id: skill ID
            target: 目标 AI 助手
        
        Returns:
            DiagnosticReport
        """
        report = DiagnosticReport(skill_id=skill_id)
        
        # 1. 查找 install manifest
        manifest_path = self._find_manifest(skill_id, target)
        if not manifest_path:
            report.issues.append(DiagnosticIssue(
                severity="error",
                category="missing_manifest",
                message=f"Install manifest not found for skill '{skill_id}'. Please run 'omni-skill install' first."
            ))
            return report
        
        # 2. 读取 manifest
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            report.install_root = manifest.get("install_root")
            report.installed_at = manifest.get("installed_at")
            report.dependencies = manifest.get("dependencies", {})
            
            files = manifest.get("files", [])
            report.total_files = len(files)
            report.files = [f["target"] for f in files[:10]]
        
        except Exception as e:
            report.issues.append(DiagnosticIssue(
                severity="error",
                category="invalid_manifest",
                message=f"Failed to read manifest: {e}",
                file=str(manifest_path)
            ))
            return report
        
        # 3. 检查文件完整性
        self._check_file_integrity(manifest, report)
        
        # 4. 检查 source path 泄漏
        self._check_path_leakage(skill_id, target, report)
        
        # 5. 检查索引可解析性
        self._check_index_validity(skill_id, target, report)
        
        return report
    
    def _find_manifest(self, skill_id: str, target: str) -> Optional[Path]:
        """查找 install manifest"""
        if target == "windsurf":
            manifest_path = self.install_root / ".windsurf" / "workflows" / "data" / skill_id / ".install_manifest.json"
        elif target == "claude":
            manifest_path = self.install_root / ".claude" / "skills" / skill_id / "resources" / ".install_manifest.json"
        elif target == "cursor":
            manifest_path = self.install_root / ".cursor" / "commands" / "data" / skill_id / ".install_manifest.json"
        elif target == "github":
            manifest_path = self.install_root / ".github" / "skills" / skill_id / ".install_manifest.json"
        else:
            return None
        
        return manifest_path if manifest_path.exists() else None
    
    def _check_file_integrity(self, manifest: dict, report: DiagnosticReport) -> None:
        """检查文件完整性"""
        files = manifest.get("files", [])
        
        for file_info in files:
            target = file_info.get("target")
            if not target:
                continue
            
            target_path = self.install_root / target
            if not target_path.exists():
                report.issues.append(DiagnosticIssue(
                    severity="error",
                    category="missing_file",
                    message=f"Referenced file does not exist",
                    file=target
                ))
    
    def _check_path_leakage(self, skill_id: str, target: str, report: DiagnosticReport) -> None:
        """检查 source path 泄漏"""
        # 查找 skill 主文档
        if target == "windsurf":
            skill_doc = self.install_root / ".windsurf" / "workflows" / f"{skill_id}.md"
        elif target == "claude":
            skill_doc = self.install_root / ".claude" / "skills" / skill_id / "SKILL.md"
        elif target == "cursor":
            skill_doc = self.install_root / ".cursor" / "commands" / f"{skill_id}.md"
        elif target == "github":
            skill_doc = self.install_root / ".github" / "skills" / skill_id / "SKILL.md"
        else:
            return
        
        if not skill_doc.exists():
            report.issues.append(DiagnosticIssue(
                severity="warning",
                category="missing_skill_doc",
                message=f"Skill document not found",
                file=str(skill_doc)
            ))
            return
        
        # 检查文档内容
        try:
            content = skill_doc.read_text(encoding='utf-8')
            
            # 检测禁止的路径模式
            forbidden_patterns = [
                "skills/",
                ".shared/",
                "../",
                "../../",
                "/home/",
                "/Users/",
                "C:/",
                "D:/",
            ]
            
            for pattern in forbidden_patterns:
                if pattern in content:
                    report.issues.append(DiagnosticIssue(
                        severity="error",
                        category="path_leakage",
                        message=f"Source path leakage detected: '{pattern}' found in skill document",
                        file=str(skill_doc)
                    ))
        
        except Exception as e:
            report.issues.append(DiagnosticIssue(
                severity="warning",
                category="read_error",
                message=f"Failed to read skill document: {e}",
                file=str(skill_doc)
            ))
    
    def _check_index_validity(self, skill_id: str, target: str, report: DiagnosticReport) -> None:
        """检查索引可解析性"""
        # 查找索引文件
        if target == "windsurf":
            data_dir = self.install_root / ".windsurf" / "workflows" / "data" / skill_id
        elif target == "claude":
            data_dir = self.install_root / ".claude" / "skills" / skill_id / "resources"
        elif target == "cursor":
            data_dir = self.install_root / ".cursor" / "commands" / "data" / skill_id
        elif target == "github":
            data_dir = self.install_root / ".github" / "skills" / skill_id
        else:
            return
        
        if not data_dir.exists():
            return
        
        # 查找所有 index.json
        for index_file in data_dir.rglob("index.json"):
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                
                # 检查索引项是否存在
                items = index_data.get("items", {})
                for item_id, item_info in items.items():
                    if isinstance(item_info, dict):
                        item_file = item_info.get("file")
                        if item_file:
                            item_path = index_file.parent / item_file
                            if not item_path.exists():
                                report.issues.append(DiagnosticIssue(
                                    severity="error",
                                    category="missing_indexed_file",
                                    message=f"Indexed file not found: {item_file}",
                                    file=str(index_file)
                                ))
            
            except Exception as e:
                report.issues.append(DiagnosticIssue(
                    severity="warning",
                    category="invalid_index",
                    message=f"Failed to parse index: {e}",
                    file=str(index_file)
                ))
