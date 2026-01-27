# API Design Anti-Patterns

## Anti-Pattern: Index File Cascade

**Description**: Deeply nested index.ts files re-exporting everything

**Detection Signals**:
- index.ts files at 3+ levels
- Circular dependency warnings
- Import paths going through multiple index files

**Why It's Bad**:
- Creates tight coupling
- Causes circular dependencies
- Hard to track actual dependencies

**Fix**:
- Use package.json exports field
- Export from root index.ts only
- Remove intermediate index files

## Anti-Pattern: Kitchen Sink Module

**Description**: Single module exports everything

**Detection Signals**:
- Module with >20 exports
- Unrelated functionality in same file
- Module name is generic (utils, helpers, common)

**Why It's Bad**:
- Unclear module purpose
- Forces importing unused code
- Hard to maintain

**Fix**:
- Split into focused modules
- Group related functionality
- Use clear, specific names
