# Performance Recipes

## Recipe: Fix Resource Leak

**Steps**:
1. Identify unclosed resources
2. Add cleanup in useEffect return
3. Clear timers/intervals
