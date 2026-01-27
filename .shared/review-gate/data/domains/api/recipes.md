# API Design Recipes

## Recipe: Remove Deep Index Files

**Problem**: Multiple nested index.ts files causing coupling

**Steps**:
1. Identify all index.ts files >2 levels deep
2. Move exports to root index.ts or package.json exports
3. Remove intermediate index.ts files
4. Update imports to use direct paths or root exports

## Recipe: Convert Default to Named Exports

**Problem**: Overuse of default exports

**Steps**:
1. Change `export default` to `export const/function`
2. Update all import statements
3. Verify no framework requirements for default export

## Recipe: Document Public API

**Problem**: Public exports lack documentation

**Steps**:
1. Add JSDoc/TSDoc comments to all public exports
2. Include @param, @returns, @throws
3. Add usage examples for complex APIs
4. Document breaking changes and deprecations
