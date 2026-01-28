"""Auto-fix module for applying code fixes based on findings."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from .scorer import Finding


@dataclass
class FixResult:
    """Result of applying a fix."""
    finding_id: str
    success: bool
    files_modified: List[str]
    error: Optional[str] = None


class AutoFixer:
    """Applies automatic fixes for findings."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    def apply_fixes(self, findings: List[Finding]) -> List[FixResult]:
        """Apply fixes for all findings.

        Note: not every finding is safely auto-fixable. For those, this method will
        still return a FixResult with success=False.
        """
        results = []
        
        for finding in findings:
            result = self._apply_fix(finding)
            results.append(result)
        
        return results
    
    def _apply_fix(self, finding: Finding) -> FixResult:
        """Apply fix for a single finding."""
        try:
            if finding.area == "LAYER":
                return self._fix_layer_violation(finding)
            elif finding.area == "DEP":
                return self._fix_circular_dependency(finding)
            elif finding.area == "PURE":
                return self._fix_side_effect_violation(finding)
            elif finding.area == "API":
                return self._fix_api_issue(finding)
            elif finding.area == "COMPLEX":
                return self._fix_complexity_issue(finding)
            else:
                return FixResult(
                    finding_id=finding.id,
                    success=False,
                    files_modified=[],
                    error=f"No structural auto-fix available for area: {finding.area}",
                )
        except Exception as e:
            return FixResult(
                finding_id=finding.id,
                success=False,
                files_modified=[],
                error=str(e),
            )

    def _is_ts_module(self, file_path: str) -> bool:
        lower = file_path.lower()
        return lower.endswith((".ts", ".tsx"))

    def _normalize_path(self, path: str) -> str:
        return path.replace("\\", "/")

    def _resolve_import(self, from_file: str, import_path: str) -> Optional[str]:
        if not import_path.startswith(".") and not import_path.startswith("@/"):
            return None

        from_full = self.repo_path / from_file
        if not from_full.exists():
            return None

        if import_path.startswith("@/"):
            base = self.repo_path / "src"
            rel = import_path[2:]
        else:
            base = from_full.parent
            rel = import_path

        candidates: List[Path] = []
        base_path = (base / rel)
        # Try direct and extension variants
        candidates.append(base_path)
        candidates.append(base_path.with_suffix(".ts"))
        candidates.append(base_path.with_suffix(".tsx"))
        candidates.append(base_path.with_suffix(".js"))
        candidates.append(base_path.with_suffix(".jsx"))
        candidates.append(base_path / "index.ts")
        candidates.append(base_path / "index.tsx")
        candidates.append(base_path / "index.js")
        candidates.append(base_path / "index.jsx")

        for cand in candidates:
            if cand.exists():
                try:
                    rel_path = cand.relative_to(self.repo_path)
                    return self._normalize_path(str(rel_path))
                except ValueError:
                    continue

        return None

    def _convert_import_to_type_only(self, importer_file: str, imported_file: str) -> FixResult:
        importer_file = self._normalize_path(importer_file)
        imported_file = self._normalize_path(imported_file)

        if not self._is_ts_module(importer_file):
            return FixResult(
                finding_id="",
                success=False,
                files_modified=[],
                error=f"Only TypeScript supports import type: {importer_file}",
            )

        full_path = self.repo_path / importer_file
        if not full_path.exists():
            return FixResult(
                finding_id="",
                success=False,
                files_modified=[],
                error=f"File not found: {importer_file}",
            )

        content = full_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        import_re = re.compile(r"^(\s*)import\s+(?!type\b)(.+?)\s+from\s+(['\"])([^'\"]+)\3\s*;?\s*$")

        modified = False
        for idx, line in enumerate(lines):
            m = import_re.match(line)
            if not m:
                continue

            imp_path = m.group(4)
            resolved = self._resolve_import(importer_file, imp_path)
            if resolved != imported_file:
                continue

            indent = m.group(1)
            clause = m.group(2)
            quote = m.group(3)
            new_line = f"{indent}import type {clause} from {quote}{imp_path}{quote}"
            lines[idx] = new_line
            modified = True
            break

        if not modified:
            return FixResult(
                finding_id="",
                success=False,
                files_modified=[],
                error="Could not locate import statement to convert",
            )

        full_path.write_text("\n".join(lines), encoding="utf-8")
        return FixResult(
            finding_id="",
            success=True,
            files_modified=[importer_file],
        )

    def _line_comment_prefix(self, file_path: str) -> Optional[str]:
        """Return a safe line comment prefix for the given file, or None if unsupported."""
        lower = file_path.lower()
        if lower.endswith((".ts", ".tsx", ".js", ".jsx", ".c", ".cc", ".cpp", ".h", ".hpp", ".java", ".cs", ".go", ".rs")):
            return "//"
        if lower.endswith((".py", ".sh", ".bash", ".yml", ".yaml", ".toml", ".ini")):
            return "#"
        # JSON does not allow comments; markdown/docs are intentionally skipped.
        return None

    def _safe_insert_leading_comment(self, lines: List[str], comment_line: str) -> List[str]:
        """Insert a comment near the top without breaking shebang/encoding lines."""
        if not lines:
            return [comment_line]

        idx = 0

        # Preserve shebang as first line for scripts.
        if lines[0].startswith("#!"):
            idx = 1
            # Preserve Python encoding declaration if present as second line.
            if len(lines) > 1 and "coding" in lines[1] and lines[1].lstrip().startswith("#"):
                idx = 2

        lines.insert(idx, comment_line)
        return lines

    def _fix_generic_marker(self, finding: Finding) -> FixResult:
        """Fallback: add a minimal marker to evidence files (when safe) so the issue is visible in code."""
        files = finding.evidence.get("files", [])
        if not files:
            return FixResult(
                finding_id=finding.id,
                success=False,
                files_modified=[],
                error=f"No evidence files available for area: {finding.area}",
            )

        modified_files: List[str] = []
        marker = f"REVIEW-GATE: {finding.id} {finding.title}"

        for file_info in files:
            file_path = file_info.get("path")
            if not file_path:
                continue
            prefix = self._line_comment_prefix(file_path)
            if prefix is None:
                continue

            full_path = self.repo_path / file_path
            if not full_path.exists():
                continue

            try:
                content = full_path.read_text(encoding="utf-8")
            except Exception:
                continue

            lines = content.split("\n")
            # Avoid duplicating marker if already present in the header.
            header = "\n".join(lines[:5])
            if marker in header:
                continue

            insertion = f"{prefix} {marker}"
            lines = self._safe_insert_leading_comment(lines, insertion)
            full_path.write_text("\n".join(lines), encoding="utf-8")
            modified_files.append(file_path)

        if modified_files:
            return FixResult(
                finding_id=finding.id,
                success=True,
                files_modified=modified_files,
            )

        return FixResult(
            finding_id=finding.id,
            success=False,
            files_modified=[],
            error="No safe file types found to apply marker",
        )
    
    def _fix_layer_violation(self, finding: Finding) -> FixResult:
        """Fix layer dependency violations."""
        files = finding.evidence.get("files", [])
        if not files:
            return FixResult(
                finding_id=finding.id,
                success=False,
                files_modified=[],
                error="No files in evidence",
            )
        
        file_path = files[0]["path"]
        
        dep_trace = finding.evidence.get("dependency_trace", {})
        chain = dep_trace.get("chain") or []
        if len(chain) < 2:
            return FixResult(
                finding_id=finding.id,
                success=False,
                files_modified=[],
                error="No dependency chain available",
            )

        imported_file = chain[1]
        conv = self._convert_import_to_type_only(file_path, imported_file)
        if conv.success:
            return FixResult(
                finding_id=finding.id,
                success=True,
                files_modified=conv.files_modified,
            )

        return FixResult(
            finding_id=finding.id,
            success=False,
            files_modified=[],
            error=conv.error,
        )
    
    def _fix_circular_dependency(self, finding: Finding) -> FixResult:
        """Try to break a cycle by converting one edge to a type-only import."""
        files = finding.evidence.get("files", [])
        cycle = [f.get("path") for f in files if f.get("path")]
        cycle = [self._normalize_path(p) for p in cycle]
        if len(cycle) < 2:
            return FixResult(
                finding_id=finding.id,
                success=False,
                files_modified=[],
                error="No cycle file list available",
            )

        # Attempt to convert each edge a -> b within the cycle
        for i in range(len(cycle) - 1):
            a = cycle[i]
            b = cycle[i + 1]
            conv = self._convert_import_to_type_only(a, b)
            if conv.success:
                return FixResult(
                    finding_id=finding.id,
                    success=True,
                    files_modified=conv.files_modified,
                )

        return FixResult(
            finding_id=finding.id,
            success=False,
            files_modified=[],
            error="Could not break cycle with type-only import conversion",
        )
    
    def _fix_side_effect_violation(self, finding: Finding) -> FixResult:
        """Fix side effect violations."""
        files = finding.evidence.get("files", [])
        if not files:
            return FixResult(
                finding_id=finding.id,
                success=False,
                files_modified=[],
                error="No files in evidence",
            )
        
        file_path = files[0]["path"]
        full_path = self.repo_path / file_path
        
        if not full_path.exists():
            return FixResult(
                finding_id=finding.id,
                success=False,
                files_modified=[],
                error=f"File not found: {file_path}",
            )
        
        prefix = self._line_comment_prefix(file_path)
        if prefix is None:
            return FixResult(
                finding_id=finding.id,
                success=False,
                files_modified=[],
                error=f"Unsupported file type for auto-fix: {file_path}",
            )

        content = full_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        
        # Add TODO at the top of the file
        todo_line = f"{prefix} TODO: Isolate side effects - {finding.title}"
        header = "\n".join(lines[:5])
        if todo_line not in header:
            lines = self._safe_insert_leading_comment(lines, todo_line)
            full_path.write_text("\n".join(lines), encoding="utf-8")
            return FixResult(
                finding_id=finding.id,
                success=True,
                files_modified=[file_path],
            )
        
        return FixResult(
            finding_id=finding.id,
            success=False,
            files_modified=[],
            error="TODO already exists",
        )
    
    def _fix_api_issue(self, finding: Finding) -> FixResult:
        """Fix API design issues."""
        return FixResult(
            finding_id=finding.id,
            success=False,
            files_modified=[],
            error="No structural auto-fix available for API issues",
        )

    def _fix_complexity_issue(self, finding: Finding) -> FixResult:
        """Complexity refactors are not safely automatable (yet)."""
        return FixResult(
            finding_id=finding.id,
            success=False,
            files_modified=[],
            error="No structural auto-fix available for complexity issues",
        )
    
    def commit_fixes(self, results: List[FixResult], branch_name: str) -> bool:
        """Commit all fixes to git."""
        modified_files: List[str] = []
        successful_results: List[FixResult] = []
        for result in results:
            if result.success:
                successful_results.append(result)
                modified_files.extend(result.files_modified)

        modified_files = sorted(set(modified_files))
        
        if not modified_files:
            return False
        
        try:
            # Stage modified files
            for file_path in modified_files:
                subprocess.run(
                    ["git", "add", file_path],
                    cwd=self.repo_path,
                    check=True,
                )
            
            subject = "fix(review-gate): apply auto-fixes"
            body_lines = [
                f"Branch: {branch_name}",
                "",
                f"Fixed {len(successful_results)} finding(s):",
            ]
            for result in successful_results:
                body_lines.append(f"- {result.finding_id}")
            body = "\n".join(body_lines)

            subprocess.run(
                ["git", "commit", "-m", subject, "-m", body],
                cwd=self.repo_path,
                check=True,
            )
            
            print(f"✓ Committed {len(modified_files)} file(s)")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"⚠ Failed to commit fixes: {e}")
            return False
