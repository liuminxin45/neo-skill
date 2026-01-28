#!/usr/bin/env python3
"""
Review Gate - Architecture/Code Anti-Corruption Review

Main CLI entry point for review-gate skill.
Follows skill-creator conventions for consistency.

Usage:
    python3 .shared/review-gate/scripts/review.py --base-branch main
    python3 .shared/review-gate/scripts/review.py --ensure-tests-pass --stack nextjs
    python3 .shared/review-gate/scripts/review.py --domain layer --max-results 10
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

SCRIPT_DIR = Path(__file__).parent
REVIEW_GATE_DIR = SCRIPT_DIR.parent
DATA_DIR = REVIEW_GATE_DIR / "data"
REVIEW_SYSTEM_DIR = REVIEW_GATE_DIR / "review-system"

sys.path.insert(0, str(SCRIPT_DIR))

from signals import (
    DiffCollector,
    GraphBuilder,
    LayerClassifier,
    ApiSurfaceAnalyzer,
    SideEffectScanner,
    ComplexityScanner,
    TestRunner,
)
from engine import Router, Scorer, Composer, PersistManager
from engine.scorer import Finding
from engine.router import Signal
from engine.auto_fixer import AutoFixer


def create_review_branch(base_branch: str, repo_path: Path) -> str:
    """Create review-gate branch."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        ref = result.stdout.strip()
    except subprocess.CalledProcessError:
        ref = "unknown"
    
    branch_name = f"review-gate/{timestamp}-{ref}"
    
    try:
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        print(f"✓ Created branch: {branch_name}")
        return branch_name
    except subprocess.CalledProcessError as e:
        print(f"⚠ Could not create branch: {e}", file=sys.stderr)
        print("⚠ Continuing on current branch", file=sys.stderr)
        # Get current branch name
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"


def collect_signals(
    repo_path: Path,
    base_branch: str,
    ensure_tests_pass: bool,
) -> tuple:
    """Collect all signals from analyzers."""
    print("\n📊 Collecting signals...")
    
    diff_collector = DiffCollector(repo_path)
    changeset = diff_collector.collect(base_branch)
    
    print(f"  ✓ Changeset: {changeset.total_files} files, +{changeset.total_additions}/-{changeset.total_deletions}")
    
    changed_files = [f.path for f in changeset.files]
    
    graph_builder = GraphBuilder(repo_path)
    dep_graph = graph_builder.build_impacted_subgraph(changed_files)
    
    print(f"  ✓ Dependency graph: {len(dep_graph.impacted_nodes)} impacted nodes, {len(dep_graph.cycles)} cycles")
    
    layer_classifier = LayerClassifier(repo_path)
    layer_info = layer_classifier.classify_batch(changed_files)
    
    api_analyzer = ApiSurfaceAnalyzer(repo_path)
    api_surface = api_analyzer.analyze(changed_files)
    
    side_effect_scanner = SideEffectScanner(repo_path)
    complexity_scanner = ComplexityScanner(repo_path)
    
    signals = []
    
    for file_path in changed_files:
        layer = layer_info.get(file_path)
        if layer:
            signals.append(Signal(
                type="layer_classification",
                value={"file": file_path, "layer": layer.layer, "confidence": layer.confidence},
                confidence=0.9 if layer.confidence == "HIGH" else 0.6,
                source="layer_classifier",
            ))
            
            side_effects = side_effect_scanner.scan(file_path, layer.layer)
            if side_effects:
                signals.append(Signal(
                    type="side_effect_violation",
                    value={"file": file_path, "violations": len(side_effects)},
                    confidence=0.95,
                    source="side_effect_scanner",
                ))
        
        complexity_issues = complexity_scanner.scan(file_path)
        if complexity_issues:
            signals.append(Signal(
                type="complexity_issue",
                value={"file": file_path, "issues": len(complexity_issues)},
                confidence=0.8,
                source="complexity_scanner",
            ))
    
    if dep_graph.cycles:
        signals.append(Signal(
            type="circular_dependency",
            value={"cycles": len(dep_graph.cycles)},
            confidence=1.0,
            source="graph_builder",
        ))
    
    if api_surface.breaking_changes:
        signals.append(Signal(
            type="api_breaking_change",
            value={"changes": len(api_surface.breaking_changes)},
            confidence=0.9,
            source="api_surface_analyzer",
        ))
    
    deep_indexes = api_analyzer.has_deep_index_files(changed_files)
    if deep_indexes:
        signals.append(Signal(
            type="deep_index_files",
            value={"files": deep_indexes},
            confidence=0.85,
            source="api_surface_analyzer",
        ))
    
    test_result = None
    if ensure_tests_pass:
        test_runner = TestRunner(repo_path)
        test_result = test_runner.run_tests()
        
        if not test_result.passed:
            signals.append(Signal(
                type="test_failure",
                value={"failed": test_result.failed_tests},
                confidence=1.0,
                source="test_runner",
            ))
    
    print(f"  ✓ Generated {len(signals)} signals")
    
    return signals, changeset, dep_graph, layer_info, api_surface, test_result


def generate_findings(
    signals: List[Signal],
    changeset,
    dep_graph,
    layer_info,
    api_surface,
) -> List[Finding]:
    """Generate findings from signals and analysis."""
    print("\n🔍 Generating findings...")
    
    findings = []
    finding_counter = {"LAYER": 0, "DEP": 0, "API": 0, "PURE": 0, "COMPLEX": 0}
    
    for signal in signals:
        if signal.type == "layer_classification":
            file_path = signal.value["file"]
            layer = signal.value["layer"]
            
            node = dep_graph.nodes.get(file_path)
            if node:
                for imp in node.imports:
                    imp_layer_info = layer_info.get(imp)
                    if imp_layer_info:
                        if not LayerClassifier(Path.cwd()).is_valid_dependency(layer, imp_layer_info.layer):
                            finding_counter["LAYER"] += 1
                            findings.append(Finding(
                                id=f"RG-LAYER-{finding_counter['LAYER']:03d}",
                                severity="BLOCKER",
                                area="LAYER",
                                checklist_ref="C-LAYER-01",
                                title=f"{layer} layer imports from {imp_layer_info.layer}",
                                status="OPEN",
                                confidence="HIGH",
                                evidence={
                                    "files": [{"path": file_path, "diff_hunks": []}],
                                    "dependency_trace": {
                                        "chain": [file_path, imp],
                                        "direction_violation": True,
                                    },
                                },
                                impact=["ARCH", "MAINTAINABILITY"],
                                blast_radius="MODULE",
                                risk_if_merge=f"Violates dependency inversion: {layer} should not depend on {imp_layer_info.layer}",
                                proposed_fix=[
                                    "Extract shared types to types/ or shared/",
                                    "Use dependency injection for cross-layer concerns",
                                    "Refactor to respect layer boundaries",
                                ],
                                acceptance_criteria=f"{layer} layer has no imports from {imp_layer_info.layer}",
                                automatable="PARTIAL",
                                hard_gate_candidate={
                                    "rule_idea": f"Detect imports from {layer}/* to {imp_layer_info.layer}/*",
                                    "implementation_hint": "AST analysis + import path checking",
                                    "false_positive_risk": "LOW",
                                    "scope": "TypeScript/JavaScript imports",
                                },
                            ))
        
        elif signal.type == "circular_dependency":
            finding_counter["DEP"] += 1
            cycle_files = []
            if getattr(dep_graph, "cycles", None):
                try:
                    first_cycle = dep_graph.cycles[0]
                    if isinstance(first_cycle, list):
                        cycle_files = [{"path": p, "diff_hunks": []} for p in first_cycle]
                except Exception:
                    cycle_files = []
            findings.append(Finding(
                id=f"RG-DEP-{finding_counter['DEP']:03d}",
                severity="BLOCKER",
                area="DEP",
                checklist_ref="C-DEP-01",
                title="Circular dependencies detected",
                status="OPEN",
                confidence="HIGH",
                evidence={
                    "files": cycle_files,
                    "dependency_trace": {
                        "cycles": signal.value["cycles"],
                    },
                },
                impact=["ARCH", "MAINTAINABILITY", "TESTABILITY"],
                blast_radius="PACKAGE",
                risk_if_merge="Circular dependencies make code hard to test and refactor",
                proposed_fix=[
                    "Identify the cycle using dependency graph",
                    "Extract shared abstractions to break the cycle",
                    "Use dependency injection or event-driven patterns",
                ],
                acceptance_criteria="Zero circular dependencies in the module",
                automatable="YES",
                hard_gate_candidate={
                    "rule_idea": "Detect circular imports using static analysis",
                    "implementation_hint": "Build import graph and detect cycles with DFS",
                    "false_positive_risk": "LOW",
                    "scope": "All TypeScript/JavaScript files",
                },
            ))
        
        elif signal.type == "side_effect_violation":
            finding_counter["PURE"] += 1
            findings.append(Finding(
                id=f"RG-PURE-{finding_counter['PURE']:03d}",
                severity="RECOMMENDATION",
                area="PURE",
                checklist_ref="C-PURE-01",
                title=f"Side effects in pure layer: {signal.value['file']}",
                status="OPEN",
                confidence="HIGH",
                evidence={
                    "files": [{"path": signal.value["file"], "diff_hunks": []}],
                },
                impact=["TESTABILITY", "MAINTAINABILITY"],
                blast_radius="MODULE",
                risk_if_merge="Makes business logic hard to test and reason about",
                proposed_fix=[
                    "Move I/O operations to infrastructure layer",
                    "Use dependency injection for external dependencies",
                    "Keep domain/application layers pure",
                ],
                acceptance_criteria="Domain/application layers have no direct side effects",
                automatable="PARTIAL",
                hard_gate_candidate={
                    "rule_idea": "Detect fetch/axios/fs/Date.now in domain/application",
                    "implementation_hint": "Regex or AST analysis for side-effect patterns",
                    "false_positive_risk": "MEDIUM",
                    "scope": "domain/* and application/* files",
                },
            ))
        
        elif signal.type == "complexity_issue":
            finding_counter["COMPLEX"] += 1
            findings.append(Finding(
                id=f"RG-COMPLEX-{finding_counter['COMPLEX']:03d}",
                severity="RECOMMENDATION",
                area="COMPLEX",
                checklist_ref="C-COMPLEX-01",
                title=f"Complexity issues in {signal.value['file']}",
                status="OPEN",
                confidence="MEDIUM",
                evidence={
                    "files": [{"path": signal.value["file"], "diff_hunks": []}],
                },
                impact=["MAINTAINABILITY"],
                blast_radius="LOCAL",
                risk_if_merge="Complex code is harder to understand and maintain",
                proposed_fix=[
                    "Extract complex logic into smaller functions",
                    "Reduce nesting with early returns",
                    "Split god functions into focused units",
                ],
                acceptance_criteria="Functions are focused and easy to understand",
                automatable="NO",
            ))
        
        elif signal.type == "deep_index_files":
            finding_counter["API"] += 1
            findings.append(Finding(
                id=f"RG-API-{finding_counter['API']:03d}",
                severity="RECOMMENDATION",
                area="API",
                checklist_ref="C-API-01",
                title="Deep index.ts files may cause coupling",
                status="OPEN",
                confidence="MEDIUM",
                evidence={
                    "files": [{"path": f} for f in signal.value["files"]],
                },
                impact=["ARCH", "MAINTAINABILITY"],
                blast_radius="MODULE",
                risk_if_merge="Deep index files can lead to circular dependencies and tight coupling",
                proposed_fix=[
                    "Use package.json exports instead of deep index files",
                    "Export from root index.ts only",
                    "Remove intermediate index.ts files",
                ],
                acceptance_criteria="No index.ts files deeper than 2 levels",
                automatable="PARTIAL",
                hard_gate_candidate={
                    "rule_idea": "Detect index.ts files deeper than src/module/index.ts",
                    "implementation_hint": "File path depth analysis",
                    "false_positive_risk": "LOW",
                    "scope": "All index.ts files",
                },
            ))
    
    print(f"  ✓ Generated {len(findings)} findings")
    
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Review Gate - Architecture/Code Anti-Corruption Review"
    )
    parser.add_argument("--base-branch", default="main", help="Base branch for comparison")
    parser.add_argument("--ensure-tests-pass", action="store_true", help="Ensure tests pass")
    parser.add_argument("--stack", help="Stack-specific configuration (react/nextjs/node)")
    parser.add_argument("--format", choices=["ascii", "markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--persist", choices=["path", "package", "stack"], help="Persist override rules")
    parser.add_argument("--domain", help="Focus on specific domain")
    parser.add_argument("--max-results", type=int, default=50, help="Maximum results to show")
    parser.add_argument("--repo-path", type=Path, help="Repository path (default: current directory)")
    
    args = parser.parse_args()
    
    repo_path = args.repo_path or Path.cwd()
    
    if not (repo_path / ".git").exists():
        print("❌ Not a git repository", file=sys.stderr)
        sys.exit(1)
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║              REVIEW GATE - Architecture Review                ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    print(f"\n📋 Base branch: {args.base_branch}")
    print("\n🌿 Creating review branch...")
    branch_name = create_review_branch(args.base_branch, repo_path)
    
    signals, changeset, dep_graph, layer_info, api_surface, test_result = collect_signals(
        repo_path,
        args.base_branch,
        args.ensure_tests_pass,
    )
    
    router = Router(DATA_DIR, REVIEW_SYSTEM_DIR)
    router.load_overrides(stack=args.stack)
    
    routing_result = router.route(signals)
    print(f"\n🎯 Router selected {len(routing_result.selected_checks)} checks from {len(routing_result.triggered_domains)} domains")
    
    findings = generate_findings(signals, changeset, dep_graph, layer_info, api_surface)
    
    scorer = Scorer()
    all_findings = scorer.prioritize(findings)

    findings_for_fix = all_findings
    if args.domain:
        findings_for_fix = [f for f in findings_for_fix if f.area.lower() == args.domain.lower()]

    findings_for_report = findings_for_fix[:args.max_results]
    
    composer = Composer(DATA_DIR / "templates")
    
    changeset_summary = {
        "total_files": changeset.total_files,
        "total_additions": changeset.total_additions,
        "total_deletions": changeset.total_deletions,
    }
    
    report = composer.compose_report(
        findings_for_report,
        changeset_summary,
        branch_name,
        args.base_branch,
        format=args.format,
    )
    
    print("\n" + "="*70)
    print(report)
    print("="*70)
    
    output_dir = repo_path / ".review-gate"
    output_dir.mkdir(exist_ok=True)
    
    report_file = composer.save_report(report, output_dir, format=args.format)
    print(f"\n✓ Report saved to: {report_file}")
    
    json_report = composer.compose_report(findings_for_report, changeset_summary, branch_name, args.base_branch, format="json")
    json_file = composer.save_report(json_report, output_dir, format="json")
    print(f"✓ JSON report saved to: {json_file}")
    
    if args.persist:
        persist_mgr = PersistManager(REVIEW_SYSTEM_DIR)
        print(f"\n📝 Persisting {args.persist} overrides...")
    
    blockers = [f for f in findings_for_fix if f.severity == "BLOCKER"]

    print(f"\n🔧 Applying auto-fixes for {len(findings_for_fix)} finding(s)...")
    auto_fixer = AutoFixer(repo_path)
    fix_results = auto_fixer.apply_fixes(findings_for_fix)

    successful_fixes = [r for r in fix_results if r.success]
    failed_fixes = [r for r in fix_results if not r.success]

    if successful_fixes:
        print(f"  ✓ Applied {len(successful_fixes)} fix(es)")
        for result in successful_fixes[:20]:
            files_str = ", ".join(result.files_modified)
            print(f"    - {result.finding_id}: {files_str}")
        if len(successful_fixes) > 20:
            print(f"    ... and {len(successful_fixes) - 20} more")

        print("\n💾 Committing fixes...")
        if auto_fixer.commit_fixes(fix_results, branch_name):
            print(f"  ✓ Fixes committed to branch: {branch_name}")
        else:
            print("  ⚠ No changes to commit")
    else:
        print("  ℹ No auto-fixable issues found")

    if failed_fixes:
        print(f"\n  ⚠ {len(failed_fixes)} issue(s) were not auto-fixable")
        for result in failed_fixes[:10]:
            print(f"    - {result.finding_id}: {result.error}")
        if len(failed_fixes) > 10:
            print(f"    ... and {len(failed_fixes) - 10} more")

    print(f"\n📌 Review branch: {branch_name}")
    print("   Run 'git diff' to see applied fixes")
    print(f"   Merge with: git checkout {args.base_branch} && git merge {branch_name}")

    if blockers:
        print(f"\n⚠️  {len(blockers)} BLOCKER(S) found - review required before merge")
        sys.exit(1)
    else:
        print(f"\n✅ No blockers found")
        sys.exit(0)


if __name__ == "__main__":
    main()
