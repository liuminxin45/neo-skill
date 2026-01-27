# Dependency Violation Recipes

## Recipe: Break Circular Dependency

**Problem**: Module A imports B, B imports A

**Steps**:
1. Identify the shared concern causing the cycle
2. Extract shared types/interfaces to separate module
3. Both A and B import from the new module
4. Verify cycle is broken

**Example**:
```typescript
// Before: Cycle between user.ts and order.ts
// user.ts
import { Order } from './order'
export interface User { orders: Order[] }

// order.ts
import { User } from './user'
export interface Order { user: User }

// After: Extract to types
// types.ts
export interface UserRef { id: string; name: string }
export interface OrderRef { id: string; total: number }

// user.ts
import { OrderRef } from './types'
export interface User { orders: OrderRef[] }

// order.ts
import { UserRef } from './types'
export interface Order { user: UserRef }
```

## Recipe: Reduce Module Coupling

**Problem**: Module imports from too many other modules

**Steps**:
1. Identify common dependencies
2. Group related functionality
3. Create facade or aggregate module
4. Reduce direct dependencies

## Recipe: Abstract External Dependency

**Problem**: External library used directly throughout code

**Steps**:
1. Create adapter interface in domain
2. Implement adapter in infrastructure
3. Inject adapter through dependency injection
4. Replace direct library usage with adapter

**Example**:
```typescript
// Before: Direct axios usage in domain
// domain/user/service.ts
import axios from 'axios'
export async function getUser(id: string) {
  return axios.get(`/api/users/${id}`)
}

// After: Abstract with adapter
// domain/user/repository.ts
export interface UserRepository {
  getUser(id: string): Promise<User>
}

// infra/api/userApiRepository.ts
import axios from 'axios'
export class UserApiRepository implements UserRepository {
  async getUser(id: string) {
    const response = await axios.get(`/api/users/${id}`)
    return mapToUser(response.data)
  }
}

// domain/user/service.ts
export class UserService {
  constructor(private repo: UserRepository) {}
  async getUser(id: string) {
    return this.repo.getUser(id)
  }
}
```
