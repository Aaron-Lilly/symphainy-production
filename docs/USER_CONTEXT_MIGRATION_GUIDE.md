# User Context Migration Guide

## Problem

Previously, we were threading `user_context` through every function call:
```python
async def process_file(file_id, user_id, user_context=None):
    # ... 
    await store_parsed_file(file_id, data, user_context=user_context)
    # ...
```

This was error-prone and led to:
- `user_context` being lost at various points in the call chain
- Functions needing `user_context` parameter even when they didn't directly use it
- Difficult debugging when permissions/tenant_id were missing

## Solution: Request-Scoped Context

We now use Python's `contextvars` to store user context at the request level. It's set once at the entry point and accessible throughout the request lifecycle.

## Migration Steps

### 1. Entry Point (Already Done)

`FrontendGatewayService.route_frontend_request()` now sets the request context:
```python
from utilities.security_authorization.request_context import set_request_user_context

user_context = {...}  # Built from headers/token
set_request_user_context(user_context)
```

### 2. Update Service Methods

**Before:**
```python
async def process_file(
    self,
    file_id: str,
    user_id: str,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    # Use user_context parameter
    tenant_id = user_context.get("tenant_id") if user_context else None
    permissions = user_context.get("permissions", []) if user_context else []
```

**After:**
```python
from utilities.security_authorization.request_context import get_request_user_context

async def process_file(
    self,
    file_id: str,
    user_id: str
    # No user_context parameter needed!
) -> Dict[str, Any]:
    # Get from request context
    user_context = get_request_user_context()
    tenant_id = user_context.get("tenant_id") if user_context else None
    permissions = user_context.get("permissions", []) if user_context else []
```

### 3. Convenience Methods

For common operations, use convenience methods:
```python
from utilities.security_authorization.request_context import (
    get_user_id,
    get_tenant_id,
    get_permissions
)

# Instead of:
user_context = get_request_user_context()
user_id = user_context.get("user_id") if user_context else None

# Use:
user_id = get_user_id()
tenant_id = get_tenant_id()
permissions = get_permissions()
```

### 4. Update Function Calls

**Before:**
```python
result = await content_orchestrator.process_file(
    file_id=file_id,
    user_id=user_id,
    user_context=user_context  # Passing through
)
```

**After:**
```python
result = await content_orchestrator.process_file(
    file_id=file_id,
    user_id=user_id
    # No user_context parameter!
)
```

## Benefits

1. **Cleaner Function Signatures**: No need to add `user_context` parameter to every function
2. **No Lost Context**: Context is automatically available throughout the request
3. **Easier Debugging**: Single source of truth for user context
4. **Better Performance**: No need to pass context through every call
5. **Type Safety**: Can add type hints for context structure

## Testing

For tests, you can set the context manually:
```python
from utilities.security_authorization.request_context import set_request_user_context

async def test_process_file():
    # Set test context
    set_request_user_context({
        "user_id": "test-user",
        "tenant_id": "test-tenant",
        "permissions": ["read", "write"]
    })
    
    # Run test - context is automatically available
    result = await orchestrator.process_file(file_id="test")
    
    # Clear context after test
    from utilities.security_authorization.request_context import clear_request_user_context
    clear_request_user_context()
```

## Migration Checklist

- [x] Create `request_context.py` utility
- [x] Set context in `FrontendGatewayService.route_frontend_request()`
- [ ] Update `ContentOrchestrator.process_file()` to use request context
- [ ] Update `ContentSteward.store_parsed_file()` to use request context
- [ ] Update `EmbeddingService` methods to use request context
- [ ] Update adapter handlers in `FrontendGatewayService` to remove `user_context` parameter
- [ ] Update all service methods that currently accept `user_context` parameter
- [ ] Update tests to use `set_request_user_context()` instead of passing context

## Backward Compatibility

During migration, we can support both patterns:
```python
async def process_file(
    self,
    file_id: str,
    user_id: str,
    user_context: Optional[Dict[str, Any]] = None  # Keep for backward compatibility
) -> Dict[str, Any]:
    # Use provided context or get from request context
    ctx = user_context or get_request_user_context()
    # ...
```

This allows gradual migration without breaking existing code.


