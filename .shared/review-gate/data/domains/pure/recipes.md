# Purity Violation Recipes

## Recipe: Extract Side Effects to Infrastructure

**Problem**: Domain layer makes HTTP calls or file I/O

**Steps**:
1. Define repository interface in domain
2. Implement repository in infrastructure
3. Inject repository into domain service
4. Replace direct I/O with repository calls

## Recipe: Make Time-Dependent Code Testable

**Problem**: Code uses Date.now() or new Date() directly

**Steps**:
1. Create Clock interface in domain
2. Implement SystemClock in infrastructure
3. Inject clock into services
4. Use MockClock in tests

**Example**:
```typescript
// Before
export function isExpired(timestamp: number) {
  return Date.now() > timestamp
}

// After
export interface Clock {
  now(): number
}

export function isExpired(timestamp: number, clock: Clock) {
  return clock.now() > timestamp
}
```

## Recipe: Isolate Random Number Generation

**Problem**: Code uses Math.random() directly

**Steps**:
1. Create RandomGenerator interface
2. Inject generator into functions
3. Use deterministic generator in tests
