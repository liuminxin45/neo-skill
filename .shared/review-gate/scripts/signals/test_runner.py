"""Optional test runner for signal generation."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class TestResult:
    """Test execution result."""
    passed: bool
    total_tests: int
    failed_tests: int
    error_message: Optional[str]
    failed_files: List[str]


class TestRunner:
    """Runs tests and generates signals from failures."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    def run_tests(self) -> TestResult:
        """Run test suite and collect results."""
        try:
            result = subprocess.run(
                ["npm", "test", "--", "--passWithNoTests"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300,
            )
            
            passed = result.returncode == 0
            output = result.stdout + result.stderr
            
            failed_files = self._extract_failed_files(output)
            
            return TestResult(
                passed=passed,
                total_tests=self._count_tests(output),
                failed_tests=len(failed_files),
                error_message=None if passed else output[-500:],
                failed_files=failed_files,
            )
        except subprocess.TimeoutExpired:
            return TestResult(
                passed=False,
                total_tests=0,
                failed_tests=0,
                error_message="Test execution timed out",
                failed_files=[],
            )
        except Exception as e:
            return TestResult(
                passed=False,
                total_tests=0,
                failed_tests=0,
                error_message=str(e),
                failed_files=[],
            )
    
    def _extract_failed_files(self, output: str) -> List[str]:
        """Extract failed test files from output."""
        failed = []
        for line in output.split("\n"):
            if "FAIL" in line and ".test." in line:
                parts = line.split()
                for part in parts:
                    if ".test." in part:
                        failed.append(part)
        return failed
    
    def _count_tests(self, output: str) -> int:
        """Count total tests from output."""
        import re
        match = re.search(r"(\d+) total", output)
        return int(match.group(1)) if match else 0
