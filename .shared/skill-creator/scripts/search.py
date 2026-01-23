#!/usr/bin/env python3
"""
Skill Creator Search Tool

Search skill patterns, templates, and reasoning rules.
Inspired by ui-ux-pro-max's multi-domain search architecture.

Usage:
    python3 .shared/skill-creator/scripts/search.py "<query>" --domain <domain>
    python3 .shared/skill-creator/scripts/search.py "<query>" --skill-system
    python3 .shared/skill-creator/scripts/search.py "<query>" --stack windsurf
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def search_csv(data: List[Dict[str, str]], query: str, fields: Optional[List[str]] = None) -> List[Dict[str, str]]:
    """Search CSV data for matching rows."""
    query_lower = query.lower()
    keywords = query_lower.split()
    results = []
    
    for row in data:
        score = 0
        search_fields = fields or list(row.keys())
        text = " ".join(str(row.get(f, "")) for f in search_fields).lower()
        
        for kw in keywords:
            if kw in text:
                score += 1
        
        if score > 0:
            results.append((score, row))
    
    results.sort(key=lambda x: -x[0])
    return [r[1] for r in results]


def search_domain(domain: str, query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search a specific domain."""
    domains_config = load_json(DATA_DIR / "domains.json")
    
    if domain not in domains_config["domains"]:
        print(f"Unknown domain: {domain}", file=sys.stderr)
        print(f"Available: {', '.join(domains_config['domains'].keys())}", file=sys.stderr)
        sys.exit(1)
    
    domain_info = domains_config["domains"][domain]
    data_file = DATA_DIR / domain_info["data_file"]
    
    if not data_file.exists():
        print(f"Data file not found: {data_file}", file=sys.stderr)
        sys.exit(1)
    
    data = load_csv(data_file)
    results = search_csv(data, query)
    return results[:max_results]


def search_skill_system(query: str, project_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a complete skill system recommendation.
    Searches all domains in parallel and applies reasoning rules.
    """
    domains_config = load_json(DATA_DIR / "domains.json")
    reasoning_rules = load_csv(DATA_DIR / domains_config["reasoning_file"])
    
    # Search all domains
    results = {}
    for domain in domains_config["domains"]:
        results[domain] = search_domain(domain, query, max_results=3)
    
    # Apply reasoning rules
    applicable_rules = search_csv(reasoning_rules, query, ["condition"])
    
    # Build recommendation
    recommendation = {
        "project": project_name or "Untitled Skill",
        "query": query,
        "workflow_pattern": results.get("workflow", [{}])[0] if results.get("workflow") else {},
        "output_pattern": results.get("output", [{}])[0] if results.get("output") else {},
        "resource_strategy": results.get("resource", [{}])[0] if results.get("resource") else {},
        "trigger_examples": [r.get("example_triggers", "") for r in results.get("trigger", [])[:3]],
        "applicable_rules": [
            {"condition": r["condition"], "recommendation": r["recommendation"], "rationale": r["rationale"]}
            for r in applicable_rules[:5]
        ],
    }
    
    return recommendation


def search_stack(stack: str, query: str) -> Dict[str, Any]:
    """Get stack-specific guidelines."""
    domains_config = load_json(DATA_DIR / "domains.json")
    
    if stack not in domains_config["stacks"]:
        print(f"Unknown stack: {stack}", file=sys.stderr)
        print(f"Available: {', '.join(domains_config['stacks'].keys())}", file=sys.stderr)
        sys.exit(1)
    
    stack_info = domains_config["stacks"][stack]
    return {
        "stack": stack,
        "query": query,
        "description": stack_info["description"],
        "format": stack_info["format"],
        "output_path": stack_info["output_path"],
        "priority": stack_info["priority"],
    }


def format_domain_results(domain: str, results: List[Dict[str, str]]) -> str:
    """Format domain search results."""
    if not results:
        return f"No results found for domain '{domain}'"
    
    lines = [f"## {domain.upper()} Domain Results", ""]
    for i, row in enumerate(results, 1):
        lines.append(f"### {i}. {row.get('name', row.get('id', 'Unknown'))}")
        for key, value in row.items():
            if key not in ("id", "name") and value:
                lines.append(f"- **{key}**: {value}")
        lines.append("")
    
    return "\n".join(lines)


def format_skill_system(rec: Dict[str, Any]) -> str:
    """Format skill system recommendation."""
    lines = [
        "╔════════════════════════════════════════════════════════════════╗",
        f"║  SKILL SYSTEM: {rec['project']:<47} ║",
        "╠════════════════════════════════════════════════════════════════╣",
        f"║  Query: {rec['query']:<54} ║",
        "╠════════════════════════════════════════════════════════════════╣",
    ]
    
    # Workflow pattern
    wp = rec.get("workflow_pattern", {})
    if wp:
        lines.append(f"║  WORKFLOW: {wp.get('name', 'N/A'):<51} ║")
        lines.append(f"║    {wp.get('description', '')[:58]:<58} ║")
    
    # Output pattern
    op = rec.get("output_pattern", {})
    if op:
        lines.append(f"║  OUTPUT: {op.get('name', 'N/A'):<53} ║")
        lines.append(f"║    {op.get('description', '')[:58]:<58} ║")
    
    # Resource strategy
    rs = rec.get("resource_strategy", {})
    if rs:
        lines.append(f"║  RESOURCES: {rs.get('name', 'N/A'):<50} ║")
    
    lines.append("╠════════════════════════════════════════════════════════════════╣")
    lines.append("║  APPLICABLE RULES:                                             ║")
    for rule in rec.get("applicable_rules", [])[:3]:
        cond = rule.get("condition", "")[:20]
        rec_text = rule.get("recommendation", "")[:35]
        lines.append(f"║    • {cond}: {rec_text:<38} ║")
    
    lines.append("╚════════════════════════════════════════════════════════════════╝")
    
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search skill patterns, templates, and reasoning rules"
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument("--domain", "-d", help="Search specific domain")
    parser.add_argument("--skill-system", "-s", action="store_true", help="Generate complete skill system")
    parser.add_argument("--stack", help="Get stack-specific guidelines")
    parser.add_argument("--project", "-p", help="Project name (for --skill-system)")
    parser.add_argument("--max-results", "-n", type=int, default=5, help="Max results per domain")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    if args.skill_system:
        result = search_skill_system(args.query, args.project)
        if args.format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_skill_system(result))
    elif args.stack:
        result = search_stack(args.stack, args.query)
        if args.format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Stack: {result['stack']}")
            print(f"Format: {result['format']}")
            print(f"Output: {result['output_path']}")
    elif args.domain:
        results = search_domain(args.domain, args.query, args.max_results)
        if args.format == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(format_domain_results(args.domain, results))
    else:
        # Default: search all domains briefly
        domains_config = load_json(DATA_DIR / "domains.json")
        for domain in domains_config["domains"]:
            results = search_domain(domain, args.query, max_results=2)
            if results:
                print(format_domain_results(domain, results))


if __name__ == "__main__":
    main()
