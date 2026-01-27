# Purity Anti-Patterns

## Anti-Pattern: Hidden Side Effects

**Description**: Functions that look pure but have side effects

**Detection Signals**:
- Function modifies global state
- Function makes network calls
- Function writes to console/logs

**Why It's Bad**:
- Hard to test
- Unpredictable behavior
- Difficult to reason about

**Fix**:
- Make side effects explicit in function signature
- Use dependency injection
- Separate pure and impure code

## Anti-Pattern: God Service

**Description**: Service that does everything including I/O

**Detection Signals**:
- Service has >10 methods
- Service mixes business logic with I/O
- Service is hard to test

**Why It's Bad**:
- Violates single responsibility
- Hard to test in isolation
- Tight coupling to infrastructure

**Fix**:
- Split into focused services
- Extract I/O to repositories
- Use dependency injection
