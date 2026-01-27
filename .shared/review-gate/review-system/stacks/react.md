# Review Gate Configuration: React Stack

Stack-specific overrides for React applications.

## Stack Settings

**Framework**: React  
**Focus Areas**: UI patterns, component design, hooks usage

## Check Overrides

### C-UI-01

**Severity**: RECOMMENDATION  
**Notes**: React.memo is important for performance but not always required

### C-UI-02

**Severity**: RECOMMENDATION  
**Notes**: Inline functions in JSX can be acceptable in some cases

### C-API-02

**Severity**: INFO  
**Notes**: Default exports are required for React components in some frameworks

## Allowlist

- Default exports in `pages/**/*.tsx` (Next.js requirement)
- Default exports in `app/**/*.tsx` (Next.js App Router)

## Domain Weight Adjustments

- **ui**: 0.8 (increased for React)
- **perf**: 0.8 (React performance matters)
- **type**: 0.7 (TypeScript with React)
