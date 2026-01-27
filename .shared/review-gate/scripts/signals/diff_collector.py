"""Extract changeset from git diff."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DiffHunk:
    """Represents a diff hunk."""
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: List[str]
    context: str


@dataclass
class FileDiff:
    """Represents changes to a single file."""
    path: str
    status: str  # A=added, M=modified, D=deleted, R=renamed
    old_path: Optional[str]
    hunks: List[DiffHunk]
    additions: int
    deletions: int


@dataclass
class Changeset:
    """Complete changeset from a PR/branch."""
    base_branch: str
    files: List[FileDiff]
    total_additions: int
    total_deletions: int
    total_files: int


class DiffCollector:
    """Collects diff information from git."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    def collect(self, base_branch: str = "main") -> Changeset:
        """Collect changeset between current branch and base."""
        files = self._get_changed_files(base_branch)
        file_diffs = []
        total_additions = 0
        total_deletions = 0
        
        for file_info in files:
            diff = self._parse_file_diff(file_info, base_branch)
            if diff:
                file_diffs.append(diff)
                total_additions += diff.additions
                total_deletions += diff.deletions
        
        return Changeset(
            base_branch=base_branch,
            files=file_diffs,
            total_additions=total_additions,
            total_deletions=total_deletions,
            total_files=len(file_diffs),
        )
    
    def _get_changed_files(self, base_branch: str) -> List[Dict[str, str]]:
        """Get list of changed files."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-status", f"{base_branch}...HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            
            files = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("\t")
                status = parts[0]
                
                if status.startswith("R"):  # Renamed
                    files.append({
                        "status": "R",
                        "old_path": parts[1],
                        "path": parts[2],
                    })
                else:
                    files.append({
                        "status": status,
                        "path": parts[1],
                    })
            
            return files
        except subprocess.CalledProcessError:
            return []
    
    def _parse_file_diff(self, file_info: Dict[str, str], base_branch: str) -> Optional[FileDiff]:
        """Parse diff for a single file."""
        path = file_info["path"]
        status = file_info["status"]
        old_path = file_info.get("old_path")
        
        try:
            result = subprocess.run(
                ["git", "diff", "-U3", f"{base_branch}...HEAD", "--", path],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            
            hunks = self._parse_hunks(result.stdout)
            additions = sum(1 for h in hunks for l in h.lines if l.startswith("+") and not l.startswith("+++"))
            deletions = sum(1 for h in hunks for l in h.lines if l.startswith("-") and not l.startswith("---"))
            
            return FileDiff(
                path=path,
                status=status,
                old_path=old_path,
                hunks=hunks,
                additions=additions,
                deletions=deletions,
            )
        except subprocess.CalledProcessError:
            return None
    
    def _parse_hunks(self, diff_text: str) -> List[DiffHunk]:
        """Parse hunks from unified diff."""
        hunks = []
        current_hunk = None
        
        for line in diff_text.split("\n"):
            if line.startswith("@@"):
                if current_hunk:
                    hunks.append(current_hunk)
                
                match = re.match(r"@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@(.*)", line)
                if match:
                    old_start = int(match.group(1))
                    old_count = int(match.group(2) or 1)
                    new_start = int(match.group(3))
                    new_count = int(match.group(4) or 1)
                    context = match.group(5).strip()
                    
                    current_hunk = DiffHunk(
                        old_start=old_start,
                        old_count=old_count,
                        new_start=new_start,
                        new_count=new_count,
                        lines=[],
                        context=context,
                    )
            elif current_hunk is not None:
                current_hunk.lines.append(line)
        
        if current_hunk:
            hunks.append(current_hunk)
        
        return hunks
    
    def get_file_content(self, path: str, ref: str = "HEAD") -> Optional[str]:
        """Get file content at a specific ref."""
        try:
            result = subprocess.run(
                ["git", "show", f"{ref}:{path}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return None
