# Layer Anti-Patterns

## Anti-Pattern: God Layer

**Description**: One layer (usually `utils/` or `shared/`) becomes a dumping ground for everything

**Detection Signals**:
- `utils/` or `shared/` has >50% of codebase
- Files in shared have no clear common purpose
- Circular dependencies involving shared

**Why It's Bad**:
- Defeats purpose of layered architecture
- Everything depends on everything
- Hard to test and refactor

**Fix**:
- Audit shared directory
- Move domain logic to domain layer
- Move infrastructure to infra layer
- Keep only truly cross-cutting concerns in shared

## Anti-Pattern: Leaky Abstraction

**Description**: Domain layer exposes infrastructure details

**Detection Signals**:
- Domain types include HTTP status codes
- Domain functions return Prisma models directly
- Domain layer imports from `axios` or `fetch`

**Why It's Bad**:
- Couples business logic to implementation
- Hard to swap infrastructure
- Violates dependency inversion

**Fix**:
- Define domain interfaces/types
- Map infrastructure models to domain models
- Use repository pattern

## Anti-Pattern: Anemic Domain

**Description**: Domain layer is just data structures, all logic in application

**Detection Signals**:
- Domain files only have interfaces/types
- Application layer has all business rules
- Domain models have no methods

**Why It's Bad**:
- Loses benefits of domain-driven design
- Business rules scattered across application
- Hard to maintain invariants

**Fix**:
- Move business rules into domain models
- Add methods to domain entities
- Keep application layer for orchestration only

## Anti-Pattern: Smart UI

**Description**: Presentation layer contains business logic

**Detection Signals**:
- Complex calculations in React components
- Business rules in event handlers
- Validation logic in UI code

**Why It's Bad**:
- Business logic not reusable
- Hard to test without UI
- Violates separation of concerns

**Fix**:
- Extract business logic to domain
- Use application services for orchestration
- Keep UI focused on presentation

## Anti-Pattern: Bidirectional Dependencies

**Description**: Two layers depend on each other

**Detection Signals**:
- Circular imports between layers
- Layer A imports from Layer B and vice versa
- Dependency graph has cycles

**Why It's Bad**:
- Creates tight coupling
- Makes testing difficult
- Hard to reason about flow

**Fix**:
- Identify the abstraction
- Extract to lower layer or shared
- Use dependency inversion
