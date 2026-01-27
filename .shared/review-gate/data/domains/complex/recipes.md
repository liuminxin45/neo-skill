# Complexity Reduction Recipes

## Recipe: Reduce Nesting with Early Returns

**Problem**: Deep nesting makes code hard to read

**Steps**:
1. Identify nested if statements
2. Invert conditions and return early
3. Flatten the code structure

**Example**:
```typescript
// Before
function process(data: Data) {
  if (data) {
    if (data.isValid) {
      if (data.hasPermission) {
        return doWork(data)
      }
    }
  }
  return null
}

// After
function process(data: Data) {
  if (!data) return null
  if (!data.isValid) return null
  if (!data.hasPermission) return null
  return doWork(data)
}
```

## Recipe: Extract Method

**Problem**: Long function doing too much

**Steps**:
1. Identify logical sections
2. Extract each section to named function
3. Keep functions focused and small

## Recipe: Replace Complex Condition with Function

**Problem**: Complex boolean expressions

**Steps**:
1. Extract condition to named function
2. Use descriptive name explaining intent
3. Improve readability

**Example**:
```typescript
// Before
if (user.age >= 18 && user.hasLicense && !user.isSuspended) {
  allowDriving()
}

// After
function canDrive(user: User) {
  return user.age >= 18 && user.hasLicense && !user.isSuspended
}

if (canDrive(user)) {
  allowDriving()
}
```
