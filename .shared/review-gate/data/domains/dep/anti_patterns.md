# Dependency Anti-Patterns

## Anti-Pattern: Dependency Hell

**Description**: Complex web of circular and tangled dependencies

**Detection Signals**:
- Multiple circular dependency warnings
- Changes in one module break many others
- Dependency graph looks like spaghetti

**Why It's Bad**:
- Hard to understand code flow
- Difficult to test in isolation
- Refactoring becomes risky

**Fix**:
- Map dependency graph
- Break cycles systematically
- Establish clear dependency direction

## Anti-Pattern: God Object Dependency

**Description**: One module that everything depends on

**Detection Signals**:
- Single module imported by >80% of codebase
- Module has too many responsibilities
- Changes to module require extensive testing

**Why It's Bad**:
- Single point of failure
- Bottleneck for development
- Hard to maintain and evolve

**Fix**:
- Split into focused modules
- Use dependency inversion
- Create clear interfaces

## Anti-Pattern: Shotgun Surgery

**Description**: Single change requires modifications in many modules

**Detection Signals**:
- Feature changes touch >10 files
- Related logic scattered across codebase
- High coupling between modules

**Why It's Bad**:
- Increases risk of bugs
- Slows down development
- Hard to ensure consistency

**Fix**:
- Colocate related functionality
- Reduce coupling
- Use events/observers for cross-cutting concerns
