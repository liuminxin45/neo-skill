# Review Gate MASTER Configuration

Base configuration for all review-gate checks. Can be overridden by stack/package/path specific configs.

## Global Settings

**Default Severity Levels**: As defined in domain checks.csv  
**Confidence Threshold**: MEDIUM (filter out LOW confidence findings)  
**Max Findings**: 50 per review

## Check Overrides

### C-LAYER-01

**Severity**: BLOCKER  
**Notes**: Layer violations are critical architecture issues

### C-DEP-01

**Severity**: BLOCKER  
**Notes**: Circular dependencies must be resolved

### C-PURE-01

**Severity**: RECOMMENDATION  
**Notes**: Side effects in domain are important but not always blocking

### C-API-01

**Severity**: RECOMMENDATION  
**Notes**: Deep index files are a code smell but not critical

### C-COMPLEX-01

**Severity**: RECOMMENDATION  
**Notes**: Complexity issues should be addressed but rarely block merge

## Allowlist

None by default. Add exceptions in stack/package/path overrides.

## Domain Weights

- **layer**: 1.0 (highest priority)
- **dep**: 1.0
- **api**: 0.8
- **pure**: 0.9
- **complex**: 0.6
- **error**: 0.7
- **obs**: 0.5
- **type**: 0.6
- **async**: 0.7
- **ui**: 0.5
- **perf**: 0.7
- **sec**: 1.0
- **doc**: 0.4
- **test**: 0.6
