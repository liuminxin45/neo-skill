# Layer Violation Recipes

## Recipe: Fix Domain → Presentation Import

**Problem**: Domain layer imports from presentation layer

**Steps**:
1. Identify the shared concern (usually types or interfaces)
2. Extract to `types/` or `shared/` directory
3. Update imports in both domain and presentation
4. Verify no circular dependency created

**Example**:
```typescript
// Before: domain/user/service.ts
import { UserCard } from '@/presentation/components/UserCard'

// After: Extract interface
// types/user.ts
export interface UserDisplay { id: string; name: string; }

// domain/user/service.ts
import { UserDisplay } from '@/types/user'

// presentation/components/UserCard.tsx
import { UserDisplay } from '@/types/user'
```

## Recipe: Fix Application → Presentation Import

**Problem**: Application layer imports UI components

**Steps**:
1. Identify what application needs from presentation
2. Usually this is a callback or event handler pattern
3. Use dependency injection or observer pattern
4. Pass UI concerns from presentation down to application

**Example**:
```typescript
// Before: application/auth/login.ts
import { showToast } from '@/presentation/toast'

// After: Use callback
// application/auth/login.ts
export async function login(credentials: Creds, onSuccess: () => void) {
  // ... login logic
  onSuccess()
}

// presentation/pages/LoginPage.tsx
import { login } from '@/application/auth/login'
import { showToast } from './toast'

await login(creds, () => showToast('Success'))
```

## Recipe: Refactor Mixed-Layer File

**Problem**: Single file contains logic from multiple layers

**Steps**:
1. Identify distinct responsibilities
2. Create separate files for each layer
3. Move code to appropriate layer
4. Wire together with clean interfaces

**Example**:
```typescript
// Before: features/user/UserManager.ts (mixed)
class UserManager {
  fetchUser() { /* API call */ }
  validateUser() { /* business logic */ }
  renderUser() { /* UI logic */ }
}

// After: Split into layers
// infra/api/userApi.ts
export async function fetchUser(id: string) { /* API */ }

// domain/user/validator.ts
export function validateUser(user: User) { /* logic */ }

// presentation/components/UserView.tsx
export function UserView({ user }: Props) { /* UI */ }
```
