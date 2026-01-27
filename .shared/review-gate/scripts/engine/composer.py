"""Composer: generate findings + reports (JSON + Markdown)."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import List

from .scorer import Finding


class Composer:
    """Composes findings and reports."""
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
    
    def compose_report(
        self,
        findings: List[Finding],
        changeset_summary: dict,
        branch_name: str,
        base_branch: str,
        format: str = "markdown",
    ) -> str:
        """Compose final report."""
        if format == "json":
            return self._compose_json(findings, changeset_summary, branch_name, base_branch)
        else:
            return self._compose_markdown(findings, changeset_summary, branch_name, base_branch)
    
    def _compose_markdown(
        self,
        findings: List[Finding],
        changeset_summary: dict,
        branch_name: str,
        base_branch: str,
    ) -> str:
        """Compose Markdown report."""
        lines = [
            "# Review Gate Report",
            "",
            f"**Branch**: `{branch_name}`",
            f"**Base**: `{base_branch}`",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Changeset Summary",
            "",
            f"- **Files Changed**: {changeset_summary.get('total_files', 0)}",
            f"- **Additions**: +{changeset_summary.get('total_additions', 0)}",
            f"- **Deletions**: -{changeset_summary.get('total_deletions', 0)}",
            "",
        ]
        
        blockers = [f for f in findings if f.severity == "BLOCKER"]
        recommendations = [f for f in findings if f.severity == "RECOMMENDATION"]
        hardgate_candidates = [f for f in findings if f.automatable in ["YES", "PARTIAL"]]
        
        lines.extend([
            "## Summary",
            "",
            f"- **{len(blockers)}** Blockers",
            f"- **{len(recommendations)}** Recommendations",
            f"- **{len(hardgate_candidates)}** HardGate Candidates",
            "",
        ])
        
        if blockers:
            lines.extend(["## Blockers", ""])
            for finding in blockers:
                lines.extend(self._format_finding_markdown(finding))
        
        if recommendations:
            lines.extend(["## Recommendations", ""])
            for finding in recommendations[:10]:
                lines.extend(self._format_finding_markdown(finding))
        
        if hardgate_candidates:
            lines.extend(["## HardGate Candidates", ""])
            for finding in hardgate_candidates:
                lines.extend(self._format_hardgate_candidate(finding))
        
        return "\n".join(lines)
    
    def _format_finding_markdown(self, finding: Finding) -> List[str]:
        """Format a single finding as Markdown."""
        lines = [
            f"### [{finding.id}] {finding.title}",
            "",
            f"**Severity**: {finding.severity} | **Confidence**: {finding.confidence} | **Area**: {finding.area}",
            "",
        ]
        
        if finding.evidence.get("files"):
            lines.append("**Evidence**:")
            for file_info in finding.evidence["files"][:3]:
                path = file_info.get("path", "unknown")
                lines.append(f"- File: `{path}`")
                if file_info.get("diff_hunks"):
                    for hunk in file_info["diff_hunks"][:2]:
                        lines.append(f"  ```\n  {hunk}\n  ```")
            lines.append("")
        
        if finding.evidence.get("dependency_trace"):
            trace = finding.evidence["dependency_trace"]
            lines.append("**Dependency Trace**:")
            if trace.get("chain"):
                lines.append(f"- Chain: {' → '.join(trace['chain'][:5])}")
            if trace.get("direction_violation"):
                lines.append("- ⚠️ Direction violation detected")
            lines.append("")
        
        lines.extend([
            f"**Impact**: {', '.join(finding.impact)}",
            f"**Blast Radius**: {finding.blast_radius}",
            "",
            f"**Risk if Merged**: {finding.risk_if_merge}",
            "",
        ])
        
        if finding.proposed_fix:
            lines.append("**Proposed Fix**:")
            for i, step in enumerate(finding.proposed_fix, 1):
                lines.append(f"{i}. {step}")
            lines.append("")
        
        lines.extend([
            f"**Acceptance Criteria**: {finding.acceptance_criteria}",
            "",
            "---",
            "",
        ])
        
        return lines
    
    def _format_hardgate_candidate(self, finding: Finding) -> List[str]:
        """Format HardGate candidate."""
        hgc = finding.hard_gate_candidate or {}
        lines = [
            f"### {finding.checklist_ref}: {finding.title}",
            "",
            f"- **Rule Idea**: {hgc.get('rule_idea', 'N/A')}",
            f"- **Implementation**: {hgc.get('implementation_hint', 'N/A')}",
            f"- **False Positive Risk**: {hgc.get('false_positive_risk', 'UNKNOWN')}",
            f"- **Scope**: {hgc.get('scope', 'N/A')}",
            "",
        ]
        return lines
    
    def _compose_json(
        self,
        findings: List[Finding],
        changeset_summary: dict,
        branch_name: str,
        base_branch: str,
    ) -> str:
        """Compose JSON report."""
        report = {
            "metadata": {
                "branch": branch_name,
                "base_branch": base_branch,
                "generated_at": datetime.now().isoformat(),
            },
            "changeset": changeset_summary,
            "summary": {
                "total_findings": len(findings),
                "blockers": len([f for f in findings if f.severity == "BLOCKER"]),
                "recommendations": len([f for f in findings if f.severity == "RECOMMENDATION"]),
                "hardgate_candidates": len([f for f in findings if f.automatable in ["YES", "PARTIAL"]]),
            },
            "findings": [asdict(f) for f in findings],
        }
        
        return json.dumps(report, indent=2, ensure_ascii=False)
    
    def save_report(self, content: str, output_path: Path, format: str = "markdown"):
        """Save report to file."""
        ext = "json" if format == "json" else "md"
        output_file = output_path / f"review-gate-report.{ext}"
        output_file.write_text(content, encoding="utf-8")
        return output_file
