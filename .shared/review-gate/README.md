# .shared/review-gate

Production-grade architecture/code anti-corruption review skill with modular, data-driven, searchable system.

## Overview

review-gate is NOT hard-gate. It focuses on:
- Architecture decisions and module boundaries
- Dependency direction and layer violations
- Side-effect isolation and testability
- Long-term maintainability and "slow decay" prevention

**Evidence-first**: Every finding is backed by concrete evidence (files, diff hunks, dependency traces).

## Architecture

### 3-Layer Design (aligned with skill-creator conventions)

1. **Data Layer (Domains Index)**
   - Split knowledge into 14 domains: layer/dep/api/pure/complex/error/obs/type/async/ui/perf/sec/doc/test
   - Each domain contains: checks.csv, recipes.md, anti_patterns.md, hardgate_candidates.csv

2. **Reasoning Layer (Routing & Prioritization)**
   - review-reasoning.csv maps signals → domains/checks/recipes with weights
   - Supports layered overrides (paths > packages > stacks > MASTER)

3. **Runtime Layer (Analyzers + Router + Composer)**
   - Signal analyzers: diff, dependency graph, layer classification, API surface, side-effects, complexity
   - Router: loads overrides + reasoning rules, selects checks
   - Composer: generates findings (JSON + Markdown) + reports

## Prerequisites

- Python 3.8+
- Git (for diff analysis)
- Node.js/TypeScript project (for dependency graph analysis)

## Usage

### Basic Review

```bash
python3 .shared/review-gate/scripts/review.py --base-branch main
```

### With Test Enforcement

```bash
python3 .shared/review-gate/scripts/review.py --ensure-tests-pass --base-branch main
```

### Focused Domain Search

```bash
python3 .shared/review-gate/scripts/review.py --domain layer --max-results 10
```

### Stack-Specific Review

```bash
python3 .shared/review-gate/scripts/review.py --stack nextjs --base-branch main
```

### Persist Override Rules

```bash
python3 .shared/review-gate/scripts/review.py --persist path --path src/domain/user
```

## Workflow

1. Creates branch: `review-gate/<YYYYMMDD>-<topic>-<ref>`
2. (Optional) Runs existing tests baseline
3. Extracts PR diff changeset
4. Builds impacted dependency subgraph
5. Generates signals (layer/dep/api/pure/complex/etc.)
6. Router selects & prioritizes checks
7. Composer generates findings + report
8. (Optional) Applies minimal fixes for blockers
9. (Optional) Reruns tests to ensure green
10. Outputs final report (Markdown + JSON)

## Domain Reference

### MVP Domains (Fully Implemented)

- **layer**: Layer violations, directory organization, dependency direction
- **dep**: Circular dependencies, coupling, dependency direction violations
- **api**: Public API design, exports management, breaking changes
- **pure**: Side-effect isolation, testability, pure function violations
- **complex**: Cognitive complexity, nesting, god functions

### Additional Domains (Pluggable Stubs)

- **error**: Error handling, error boundaries, error propagation
- **obs**: Logging, observability, console usage
- **type**: Type safety, type definitions, type exports
- **async**: Async patterns, promise handling, race conditions
- **ui**: React patterns, component design, rendering optimization
- **perf**: Performance anti-patterns, resource leaks, blocking operations
- **sec**: Security risks, XSS, injection, validation
- **doc**: Documentation quality, API docs, comments
- **test**: Test coverage, test quality, test maintainability

## Output Formats

### Evidence Schema (JSON)

Every finding follows this schema:

```json
{
  "id": "RG-LAYER-001",
  "severity": "BLOCKER",
  "area": "LAYER",
  "checklist_ref": "C-LAYER-01",
  "title": "Domain layer imports from presentation",
  "status": "OPEN",
  "confidence": "HIGH",
  "evidence": {
    "files": [{"path": "src/domain/user.ts", "diff_hunks": ["..."]}],
    "dependency_trace": {"chain": ["..."], "direction_violation": true}
  },
  "impact": ["ARCH", "MAINTAINABILITY"],
  "blast_radius": "MODULE",
  "risk_if_merge": "Violates dependency inversion...",
  "proposed_fix": ["1. Extract shared types...", "2. Use dependency injection..."],
  "acceptance_criteria": "Domain layer has no imports from presentation",
  "automatable": "PARTIAL",
  "hard_gate_candidate": {
    "rule_idea": "Detect imports from domain/* to presentation/*",
    "implementation_hint": "AST analysis + import path checking"
  }
}
```

### Report Structure

- **Summary**: Overview, changeset stats, signal summary
- **Blockers**: Critical findings that should prevent merge
- **Recommendations**: Important but non-blocking improvements
- **HardGateCandidates**: Automatable rules to add to hard-gate
- **Fix Commits**: Map of findings → commit hashes (if fixes applied)

## Layered Override System

Hierarchical precedence (highest to lowest):

1. `review-system/paths/*.md` - Path-specific overrides
2. `review-system/packages/<pkg>.md` - Package-specific overrides
3. `review-system/stacks/<stack>.md` - Stack-specific overrides
4. `review-system/MASTER.md` - Base configuration

Override files can modify:
- Check severity levels
- Allowlist exceptions
- Custom notes/rationale
- Domain weights

## Consistency with skill-creator

This skill follows the same conventions as skill-creator:

- **Directory layout**: `.shared/<skill>/` with `scripts/`, `data/`, standard structure
- **CLI pattern**: Similar to `scripts/search.py` with consistent flags and output formatting
- **Data organization**: CSV/JSON indexes in `data/`, hierarchical domain structure
- **Output formats**: ASCII/Markdown/JSON with consistent formatting
- **Reasoning rules**: CSV-based routing similar to `skill-reasoning.csv`

## Examples

### Example Command

```bash
python3 .shared/review-gate/scripts/review.py \
  --base-branch main \
  --stack nextjs \
  --format markdown \
  --ensure-tests-pass
```

### Example Output (Markdown)

```markdown
# Review Gate Report

**Branch**: review-gate/20260127-refactor-abc123
**Base**: main
**Stack**: nextjs
**Changeset**: 15 files, 234 additions, 89 deletions

## Summary

- 3 Blockers
- 7 Recommendations
- 2 HardGate Candidates

## Blockers

### [RG-LAYER-001] Domain layer imports from presentation
**Severity**: BLOCKER | **Confidence**: HIGH | **Area**: LAYER

**Evidence**:
- File: `src/domain/user/service.ts:12`
- Imports: `import { UserCard } from '@/presentation/components/UserCard'`

**Impact**: ARCH, MAINTAINABILITY
**Blast Radius**: MODULE

**Proposed Fix**:
1. Extract shared types to `src/types/user.ts`
2. Remove presentation dependency from domain
3. Use dependency injection for UI concerns

**Acceptance Criteria**: Domain layer has zero imports from presentation layer

---

## Recommendations

[... additional findings ...]

## HardGate Candidates

1. **Detect domain→presentation imports** (C-LAYER-01)
   - Implementation: AST + import path analysis
   - False positive risk: LOW
   - Scope: TypeScript/JavaScript imports
```

## Notes

- **NOT a linter**: Focus is architecture, not style
- **Evidence-required**: All findings must have concrete proof
- **Minimal changes**: Code modifications are scoped and traceable
- **No new tests**: Only fixes to make existing tests pass
- **Deterministic**: Same input always produces same output
