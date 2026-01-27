"""Router: signals -> domains/checks using reasoning + overrides."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class Signal:
    """A signal from analyzers."""
    type: str
    value: Any
    confidence: float
    source: str


@dataclass
class Check:
    """A check to perform."""
    id: str
    domain: str
    title: str
    severity: str
    description: str
    evidence_requirements: str
    automatable: str


@dataclass
class RoutingResult:
    """Result of routing signals to checks."""
    selected_checks: List[Check]
    triggered_domains: Set[str]
    reasoning_applied: List[str]


class Router:
    """Routes signals to appropriate checks using reasoning rules."""
    
    def __init__(self, data_dir: Path, review_system_dir: Path):
        self.data_dir = data_dir
        self.review_system_dir = review_system_dir
        self.reasoning_rules = self._load_reasoning_rules()
        self.domain_checks = self._load_domain_checks()
        self.overrides = {}
    
    def load_overrides(self, stack: Optional[str] = None, packages: Optional[List[str]] = None, paths: Optional[List[str]] = None):
        """Load layered overrides."""
        self.overrides = {}
        
        master = self.review_system_dir / "MASTER.md"
        if master.exists():
            self.overrides.update(self._parse_override_file(master))
        
        if stack:
            stack_file = self.review_system_dir / "stacks" / f"{stack}.md"
            if stack_file.exists():
                self.overrides.update(self._parse_override_file(stack_file))
        
        if packages:
            for pkg in packages:
                pkg_file = self.review_system_dir / "packages" / f"{pkg}.md"
                if pkg_file.exists():
                    self.overrides.update(self._parse_override_file(pkg_file))
        
        if paths:
            for path in paths:
                path_file = self.review_system_dir / "paths" / f"{path.replace('/', '_')}.md"
                if path_file.exists():
                    self.overrides.update(self._parse_override_file(path_file))
    
    def route(self, signals: List[Signal]) -> RoutingResult:
        """Route signals to checks."""
        triggered_domains = set()
        reasoning_applied = []
        selected_checks = []
        
        for signal in signals:
            for rule in self.reasoning_rules:
                if self._matches_condition(signal, rule):
                    domains = rule.get("domains", "").split(",")
                    for domain in domains:
                        domain = domain.strip()
                        if domain:
                            triggered_domains.add(domain)
                    reasoning_applied.append(rule.get("condition", ""))
        
        for domain in triggered_domains:
            checks = self.domain_checks.get(domain, [])
            for check in checks:
                check_with_override = self._apply_overrides(check)
                selected_checks.append(check_with_override)
        
        return RoutingResult(
            selected_checks=selected_checks,
            triggered_domains=triggered_domains,
            reasoning_applied=reasoning_applied,
        )
    
    def _load_reasoning_rules(self) -> List[Dict[str, str]]:
        """Load review-reasoning.csv."""
        reasoning_file = self.data_dir / "reasoning" / "review-reasoning.csv"
        if not reasoning_file.exists():
            return []
        
        with reasoning_file.open(encoding="utf-8") as f:
            return list(csv.DictReader(f))
    
    def _load_domain_checks(self) -> Dict[str, List[Check]]:
        """Load checks from all domains."""
        domains = {}
        domains_dir = self.data_dir / "domains"
        
        if not domains_dir.exists():
            return domains
        
        for domain_dir in domains_dir.iterdir():
            if not domain_dir.is_dir():
                continue
            
            checks_file = domain_dir / "checks.csv"
            if not checks_file.exists():
                continue
            
            with checks_file.open(encoding="utf-8") as f:
                reader = csv.DictReader(f)
                checks = []
                for row in reader:
                    checks.append(Check(
                        id=row.get("id", ""),
                        domain=domain_dir.name,
                        title=row.get("title", ""),
                        severity=row.get("severity", "RECOMMENDATION"),
                        description=row.get("description", ""),
                        evidence_requirements=row.get("evidence_requirements", ""),
                        automatable=row.get("automatable", "NO"),
                    ))
                domains[domain_dir.name] = checks
        
        return domains
    
    def _matches_condition(self, signal: Signal, rule: Dict[str, str]) -> bool:
        """Check if signal matches rule condition."""
        condition = rule.get("condition", "").lower()
        signal_type = signal.type.lower()
        
        return signal_type in condition or condition in str(signal.value).lower()
    
    def _parse_override_file(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """Parse override markdown file."""
        overrides = {}
        
        try:
            content = file_path.read_text(encoding="utf-8")
            current_check = None
            
            for line in content.split("\n"):
                if line.startswith("## ") and line.count("-") >= 2:
                    current_check = line.strip("# ").strip()
                    overrides[current_check] = {}
                elif current_check and ":" in line:
                    key, value = line.split(":", 1)
                    overrides[current_check][key.strip().lower()] = value.strip()
        except Exception:
            pass
        
        return overrides
    
    def _apply_overrides(self, check: Check) -> Check:
        """Apply overrides to a check."""
        override = self.overrides.get(check.id, {})
        
        if "severity" in override:
            check.severity = override["severity"]
        
        return check
