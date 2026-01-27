# Review Gate Configuration: Next.js Stack

Stack-specific overrides for Next.js applications.

## Stack Settings

**Framework**: Next.js  
**Focus Areas**: SSR/SSG patterns, API routes, routing

## Check Overrides

### C-API-02

**Severity**: INFO  
**Notes**: Default exports required for pages and API routes

### C-PURE-01

**Severity**: BLOCKER  
**Notes**: Server components must be pure

### C-LAYER-01

**Severity**: BLOCKER  
**Notes**: Clear separation between server and client components

## Allowlist

- Default exports in `pages/**/*`
- Default exports in `app/**/*`
- Default exports in `api/**/*`

## Additional Checks

- Server component purity (no client-side APIs)
- Client component boundaries (use client directive)
- API route security (input validation)

## Domain Weight Adjustments

- **sec**: 1.0 (API routes need security review)
- **pure**: 1.0 (Server components must be pure)
- **async**: 0.8 (SSR async patterns)
