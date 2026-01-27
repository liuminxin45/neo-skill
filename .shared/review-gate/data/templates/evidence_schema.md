# Evidence Schema

Every finding must follow this JSON schema:

```json
{
  "id": "RG-<AREA>-NNN",
  "severity": "BLOCKER|RECOMMENDATION|INFO",
  "area": "LAYER|DEP|API|PURE|COMPLEX|ERROR|OBS|TYPE|ASYNC|UI|PERF|SEC|DOC|TEST",
  "checklist_ref": "C-<AREA>-NN",
  "title": "Brief description of the issue",
  "status": "OPEN|FIXED|WONT_FIX|NEEDS_OWNER_DECISION",
  "confidence": "HIGH|MEDIUM|LOW",
  "evidence": {
    "files": [
      {
        "path": "src/domain/user.ts",
        "diff_hunks": ["@@ -12,3 +12,5 @@\n+import { UserCard } from '@/presentation'"]
      }
    ],
    "dependency_trace": {
      "chain": ["src/domain/user.ts", "src/presentation/UserCard.tsx"],
      "direction_violation": true,
      "cycle_risk": false
    },
    "reproduction": {
      "command": "npm test -- user.test.ts",
      "error_snippet": "TypeError: Cannot read property...",
      "scope": "unit"
    }
  },
  "impact": ["ARCH", "MAINTAINABILITY", "TESTABILITY", "RELIABILITY", "SECURITY", "PERF"],
  "blast_radius": "LOCAL|MODULE|PACKAGE|APP",
  "risk_if_merge": "Detailed explanation of what could go wrong",
  "proposed_fix": [
    "Step 1: Extract shared types to types/ directory",
    "Step 2: Update imports in both files",
    "Step 3: Verify no circular dependency"
  ],
  "acceptance_criteria": "Clear, testable criteria for resolution",
  "automatable": "YES|NO|PARTIAL",
  "hard_gate_candidate": {
    "rule_idea": "Detect imports from domain/* to presentation/*",
    "implementation_hint": "AST analysis + import path checking",
    "false_positive_risk": "LOW|MEDIUM|HIGH",
    "scope": "TypeScript/JavaScript imports",
    "example_pattern": "import { X } from '@/presentation/...' in domain/*"
  },
  "fixed_by_commits": ["abc123", "def456"]
}
```

## Required Fields

- **id**: Unique identifier (RG-AREA-NNN)
- **severity**: BLOCKER (must fix), RECOMMENDATION (should fix), INFO (nice to know)
- **area**: Domain category
- **checklist_ref**: Reference to check in domain checks.csv
- **title**: Clear, concise description
- **status**: Current state
- **confidence**: How certain we are about this finding
- **evidence**: Concrete proof (files, traces, reproduction)
- **impact**: What aspects are affected
- **blast_radius**: Scope of impact
- **risk_if_merge**: What happens if not fixed
- **proposed_fix**: Actionable steps
- **acceptance_criteria**: How to verify fix

## Optional Fields

- **automatable**: Can this be automated?
- **hard_gate_candidate**: If automatable, details for hard-gate rule
- **fixed_by_commits**: Commits that addressed this finding
