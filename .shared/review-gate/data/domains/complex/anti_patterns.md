# Complexity Anti-Patterns

## Anti-Pattern: Arrow Code

**Description**: Deeply nested if statements forming arrow shape

**Detection Signals**:
- Indentation >4 levels
- Multiple nested if/for/while
- Hard to follow control flow

**Why It's Bad**:
- Hard to read and understand
- Difficult to test all paths
- Error-prone to modify

**Fix**:
- Use early returns
- Extract nested logic to functions
- Flatten structure

## Anti-Pattern: God Function

**Description**: Single function doing everything

**Detection Signals**:
- Function >100 lines
- Multiple responsibilities
- High cyclomatic complexity

**Why It's Bad**:
- Hard to understand
- Difficult to test
- Violates single responsibility

**Fix**:
- Extract smaller functions
- Each function does one thing
- Use descriptive names
