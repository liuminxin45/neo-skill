"""Scorer: prioritize findings by severity/confidence/blast radius."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Finding:
    """A review finding."""
    id: str
    severity: str
    area: str
    checklist_ref: str
    title: str
    status: str
    confidence: str
    evidence: dict
    impact: List[str]
    blast_radius: str
    risk_if_merge: str
    proposed_fix: List[str]
    acceptance_criteria: str
    automatable: str = "NO"
    hard_gate_candidate: dict = None
    fixed_by_commits: List[str] = None
    
    def __post_init__(self):
        if self.hard_gate_candidate is None:
            self.hard_gate_candidate = {}
        if self.fixed_by_commits is None:
            self.fixed_by_commits = []


class Scorer:
    """Scores and prioritizes findings."""
    
    SEVERITY_WEIGHTS = {
        "BLOCKER": 100,
        "RECOMMENDATION": 50,
        "INFO": 10,
    }
    
    CONFIDENCE_WEIGHTS = {
        "HIGH": 1.0,
        "MEDIUM": 0.7,
        "LOW": 0.4,
    }
    
    BLAST_RADIUS_WEIGHTS = {
        "APP": 4,
        "PACKAGE": 3,
        "MODULE": 2,
        "LOCAL": 1,
    }
    
    def score(self, finding: Finding) -> float:
        """Calculate priority score for a finding."""
        severity_score = self.SEVERITY_WEIGHTS.get(finding.severity, 10)
        confidence_mult = self.CONFIDENCE_WEIGHTS.get(finding.confidence, 0.5)
        blast_mult = self.BLAST_RADIUS_WEIGHTS.get(finding.blast_radius, 1)
        
        return severity_score * confidence_mult * blast_mult
    
    def prioritize(self, findings: List[Finding]) -> List[Finding]:
        """Sort findings by priority score."""
        scored = [(self.score(f), f) for f in findings]
        scored.sort(key=lambda x: -x[0])
        return [f for _, f in scored]
    
    def group_by_severity(self, findings: List[Finding]) -> dict:
        """Group findings by severity."""
        groups = {
            "BLOCKER": [],
            "RECOMMENDATION": [],
            "INFO": [],
        }
        
        for finding in findings:
            severity = finding.severity
            if severity in groups:
                groups[severity].append(finding)
        
        return groups
    
    def filter_by_confidence(self, findings: List[Finding], min_confidence: str = "MEDIUM") -> List[Finding]:
        """Filter findings by minimum confidence."""
        confidence_order = ["LOW", "MEDIUM", "HIGH"]
        min_idx = confidence_order.index(min_confidence)
        
        return [f for f in findings if confidence_order.index(f.confidence) >= min_idx]
