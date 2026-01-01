# Utility Usage Pattern for Smart City Services

## Overview

This document defines the standard pattern for using platform utilities (logging, error handling, telemetry, security, multi-tenancy) in Smart City services and their modules.

## Pattern Summary

**Service-level methods** use utilities directly on `self` (like Public Works Foundation).  
**Module methods** use utilities through `self.service` (delegating to service).

---

## Architecture Principles

1. **Service owns utility access** - Services extend `SmartCityRoleBase` → `RealmServiceBase` which includes utility mixins
2. **Service methods use utilities directly** - Consistent with foundation service pattern
3. **Modules delegate to service** - Modules access utilities through `self.service` to maintain clear ownership
4. **No utility passing** - Modules don't receive utilities as parameters, they access through service

---

## Service-Level Pattern

### ✅ CORRECT: Service Methods Use Utilities Directly

```python
class DataStewardService(SmartCityRoleBase, DataStewardServiceProtocol):
    async def initialize(self) -> bool:
        """Initialize Data Steward Service."""
        # Start telemetry tracking (direct on self)
        await self.log_operation_with_telemetry(
            "data_steward_initialize_start",
            success=True
        )
        
        try:
            # ... initialization logic ...
            
            # Record health metric (direct on self)
            await self.record_health_metric(
                "data_steward_initialized",
                1.0,
                {"service": "DataStewardService"}
            )
            
            # End telemetry tracking (direct on self)
            await self.log_operation_with_telemetry(
                "data_steward_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            # Use enhanced error handling (direct on self)
            await self.handle_error_with_audit(e, "data_steward_initialize")
            
            # End telemetry tracking with failure (direct on self)
            await self.log_operation_with_telemetry(
                "data_steward_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            return False
```

### Available Utility Methods (Service-Level)

- `self.log_operation_with_telemetry(operation, success, details)` - Log operation with telemetry
- `self.handle_error_with_audit(error, operation)` - Handle error with audit logging
- `self.record_health_metric(metric_name, value, metadata)` - Record health metric
- `self.get_security()` - Get security utility
- `self.get_tenant()` - Get tenant management utility
- `self.get_error_handler()` - Get error handling utility
- `self.get_telemetry()` - Get telemetry utility
- `self.get_logger()` - Get logger utility

---

## Module-Level Pattern

### ✅ CORRECT: Module Methods Use Utilities Through Service

```python
class PolicyManagement:
    """Policy management module for Data Steward service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def create_content_policy(self, data_type: str, rules: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> str:
        """Create content policy using Knowledge Governance Abstraction."""
        # Start telemetry tracking (through self.service)
        await self.service.log_operation_with_telemetry(
            "create_content_policy_start",
            success=True,
            details={"data_type": data_type}
        )
        
        try:
            # Security validation (through self.service)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "data_governance", "write"):
                        await self.service.record_health_metric("create_content_policy_access_denied", 1.0, {"data_type": data_type})
                        await self.service.log_operation_with_telemetry("create_content_policy_complete", success=False)
                        raise PermissionError(f"Access denied: insufficient permissions to create content policy for {data_type}")
            
            # Tenant validation (through self.service)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("create_content_policy_tenant_denied", 1.0, {"data_type": data_type, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("create_content_policy_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            # ... business logic ...
            
            # Record health metric (through self.service)
            await self.service.record_health_metric(
                "content_policy_created",
                1.0,
                {"data_type": data_type, "policy_id": created_policy_id}
            )
            
            # End telemetry tracking (through self.service)
            await self.service.log_operation_with_telemetry(
                "create_content_policy_complete",
                success=True,
                details={"data_type": data_type, "policy_id": created_policy_id}
            )
            
            return created_policy_id
            
        except Exception as e:
            # Use enhanced error handling (through self.service)
            await self.service.handle_error_with_audit(e, "create_content_policy")
            
            # End telemetry tracking with failure (through self.service)
            await self.service.log_operation_with_telemetry(
                "create_content_policy_complete",
                success=False,
                details={"data_type": data_type, "error": str(e)}
            )
            raise
```

### Available Utility Methods (Module-Level)

- `self.service.log_operation_with_telemetry(operation, success, details)` - Log operation with telemetry
- `self.service.handle_error_with_audit(error, operation)` - Handle error with audit logging
- `self.service.record_health_metric(metric_name, value, metadata)` - Record health metric
- `self.service.get_security()` - Get security utility
- `self.service.get_tenant()` - Get tenant management utility
- `self.service.get_error_handler()` - Get error handling utility
- `self.service.get_telemetry()` - Get telemetry utility
- `self.service.get_logger()` - Get logger utility

---

## Standard Operation Pattern

### For All Operations (Service and Module Level)

1. **Start telemetry tracking**
   ```python
   await self.log_operation_with_telemetry("operation_name_start", success=True, details={...})
   ```

2. **Security validation** (if user_context provided)
   ```python
   if user_context:
       security = self.get_security()  # or self.service.get_security()
       if security:
           if not await security.check_permissions(user_context, "resource", "action"):
               await self.record_health_metric("operation_access_denied", 1.0, {...})
               await self.log_operation_with_telemetry("operation_complete", success=False)
               raise PermissionError("Access denied")
   ```

3. **Tenant validation** (if user_context provided)
   ```python
   if user_context:
       tenant = self.get_tenant()  # or self.service.get_tenant()
       if tenant:
           tenant_id = user_context.get("tenant_id")
           if tenant_id:
               if not await tenant.validate_tenant_access(tenant_id):
                   await self.record_health_metric("operation_tenant_denied", 1.0, {...})
                   await self.log_operation_with_telemetry("operation_complete", success=False)
                   raise PermissionError("Tenant access denied")
   ```

4. **Business logic**
   ```python
   # ... actual operation logic ...
   ```

5. **Record success metrics**
   ```python
   await self.record_health_metric("operation_success", 1.0, {...})
   ```

6. **End telemetry tracking (success)**
   ```python
   await self.log_operation_with_telemetry("operation_complete", success=True, details={...})
   ```

7. **Error handling**
   ```python
   except Exception as e:
       await self.handle_error_with_audit(e, "operation_name")
       await self.log_operation_with_telemetry("operation_complete", success=False, details={"error": str(e)})
       raise  # or return error response
   ```

---

## Anti-Patterns

### ❌ WRONG: Module Using Direct Logger Instead of Utilities

```python
# ❌ WRONG
async def create_content_policy(self, ...):
    try:
        if self.service.logger:
            self.service.logger.info("Creating policy...")
        # ... logic ...
        if self.service.logger:
            self.service.logger.error(f"Error: {e}")
    except Exception as e:
        if self.service.logger:
            self.service.logger.error(f"Failed: {e}")
        raise
```

### ✅ CORRECT: Module Using Utilities Through Service

```python
# ✅ CORRECT
async def create_content_policy(self, ...):
    await self.service.log_operation_with_telemetry("create_content_policy_start", success=True)
    try:
        # ... logic ...
        await self.service.record_health_metric("content_policy_created", 1.0, {...})
        await self.service.log_operation_with_telemetry("create_content_policy_complete", success=True)
    except Exception as e:
        await self.service.handle_error_with_audit(e, "create_content_policy")
        await self.service.log_operation_with_telemetry("create_content_policy_complete", success=False, details={"error": str(e)})
        raise
```

### ❌ WRONG: Service Method Not Using Utilities

```python
# ❌ WRONG
async def initialize(self) -> bool:
    try:
        if self.logger:
            self.logger.info("Initializing...")
        # ... logic ...
        if self.logger:
            self.logger.info("Initialized")
        return True
    except Exception as e:
        if self.logger:
            self.logger.error(f"Failed: {e}")
        return False
```

### ✅ CORRECT: Service Method Using Utilities Directly

```python
# ✅ CORRECT
async def initialize(self) -> bool:
    await self.log_operation_with_telemetry("initialize_start", success=True)
    try:
        # ... logic ...
        await self.record_health_metric("initialized", 1.0, {...})
        await self.log_operation_with_telemetry("initialize_complete", success=True)
        return True
    except Exception as e:
        await self.handle_error_with_audit(e, "initialize")
        await self.log_operation_with_telemetry("initialize_complete", success=False, details={"error": str(e)})
        return False
```

---

## Special Cases

### Nurse Service (Telemetry Manager)

Nurse Service manages telemetry itself, so it should **NOT** use telemetry utilities in its telemetry collection methods (to avoid circular dependencies). However, it should still use:
- Error handling utilities
- Security/tenant utilities
- Health metrics (for its own operations, not telemetry collection)

### Services Without User Context

If an operation doesn't have user context (e.g., internal service operations), skip security/tenant validation but still use:
- Telemetry tracking
- Error handling
- Health metrics

---

## Migration Checklist

When refactoring a service/module to use utilities:

- [ ] Replace direct logger calls with `log_operation_with_telemetry()`
- [ ] Replace try/except with `handle_error_with_audit()`
- [ ] Add `record_health_metric()` for success/failure tracking
- [ ] Add security validation (if user_context available)
- [ ] Add tenant validation (if user_context available)
- [ ] Wrap operations with start/complete telemetry tracking
- [ ] Service methods use utilities on `self`
- [ ] Module methods use utilities on `self.service`

---

## Examples

See:
- `backend/smart_city/services/data_steward/data_steward_service.py` - Service-level pattern
- `backend/smart_city/services/data_steward/modules/policy_management.py` - Module-level pattern
- `foundations/public_works_foundation/public_works_foundation_service.py` - Foundation service pattern







