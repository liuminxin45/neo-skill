# Review Gate Configuration: Node.js Stack

Stack-specific overrides for Node.js backend applications.

## Stack Settings

**Runtime**: Node.js  
**Focus Areas**: API design, error handling, async patterns

## Check Overrides

### C-ERROR-01

**Severity**: BLOCKER  
**Notes**: Empty catch blocks in backend can hide critical errors

### C-ASYNC-01

**Severity**: BLOCKER  
**Notes**: Unhandled promise rejections crash Node.js

### C-SEC-02

**Severity**: BLOCKER  
**Notes**: Input validation is critical for APIs

## Allowlist

None - backend code should follow strict patterns

## Additional Checks

- Proper error handling in async routes
- Input validation on all endpoints
- Rate limiting considerations
- Database connection management

## Domain Weight Adjustments

- **error**: 1.0 (error handling is critical)
- **async**: 1.0 (async patterns must be correct)
- **sec**: 1.0 (security is paramount)
- **obs**: 0.8 (logging is important)
