# Utility Bootstrap Pattern for Service Providers

## Overview

Some Smart City services **provide** utilities that other services use. These services need special bootstrap patterns to avoid circular dependencies when they need to report on their own operations.

## Services Requiring Bootstrap Patterns

1. **Nurse Service** - Manages telemetry utilities
   - Cannot use `log_operation_with_telemetry()` for its own telemetry collection operations
   - Can use error handling, security, tenant utilities
   - Can use health metrics (for its own operations, not telemetry collection)

2. **Security Guard Service** - Manages security utilities
   - Cannot use `get_security().check_permissions()` for its own security operations
   - Can use telemetry, error handling, tenant utilities
   - Can use health metrics

## Bootstrap Pattern

### Pattern 1: Direct Infrastructure Access (Bootstrap)

For operations that **provide** the utility, use direct infrastructure access instead of utility methods:

```python
# ❌ WRONG: Circular dependency
await self.log_operation_with_telemetry("collect_telemetry_start", ...)  # Nurse can't use this!

# ✅ CORRECT: Direct infrastructure access
telemetry_abstraction = self.get_telemetry_abstraction()
if telemetry_abstraction:
    await telemetry_abstraction.record_metric(...)
```

### Pattern 2: Conditional Utility Usage

For operations that **use** the utility (not providing it), use utilities normally:

```python
# ✅ CORRECT: Nurse can use security utilities
security = self.get_security()
if security:
    if not await security.check_permissions(user_context, "telemetry", "read"):
        raise PermissionError("Access denied")
```

### Pattern 3: Self-Reporting Pattern

Services that provide utilities should report their own operations using:
- Direct infrastructure access (bypassing their own utility)
- Error handling utilities (if not providing error handling)
- Health metrics (if not providing health monitoring)

---

## Nurse Service Bootstrap Pattern

### Operations That PROVIDE Telemetry (Use Bootstrap)

```python
async def collect_telemetry(self, ...):
    """Collect telemetry - CANNOT use telemetry utilities."""
    # ❌ DON'T USE: await self.log_operation_with_telemetry(...)
    
    # ✅ USE: Direct telemetry abstraction access
    telemetry_abstraction = self.get_telemetry_abstraction()
    if telemetry_abstraction:
        await telemetry_abstraction.record_metric(
            metric_name="telemetry_collected",
            value=1.0,
            metadata={...}
        )
    
    # ✅ CAN USE: Error handling utilities
    try:
        # ... collection logic ...
    except Exception as e:
        await self.handle_error_with_audit(e, "collect_telemetry")
    
    # ✅ CAN USE: Health metrics (for own operations)
    await self.record_health_metric(
        "nurse_telemetry_collected",
        1.0,
        {...}
    )
```

### Operations That USE Telemetry (Use Utilities Normally)

```python
async def initialize(self):
    """Initialize Nurse - CAN use telemetry utilities."""
    # ✅ CAN USE: Telemetry utilities (not providing telemetry here)
    await self.log_operation_with_telemetry(
        "nurse_initialize_start",
        success=True
    )
    
    try:
        # ... initialization logic ...
        await self.log_operation_with_telemetry(
            "nurse_initialize_complete",
            success=True
        )
    except Exception as e:
        await self.handle_error_with_audit(e, "nurse_initialize")
        await self.log_operation_with_telemetry(
            "nurse_initialize_complete",
            success=False,
            details={"error": str(e)}
        )
```

---

## Security Guard Service Bootstrap Pattern

### Operations That PROVIDE Security (Use Bootstrap)

```python
async def check_permissions(self, user_context, resource, action):
    """Check permissions - CANNOT use security utilities."""
    # ❌ DON'T USE: security = self.get_security()
    
    # ✅ USE: Direct security abstraction access
    security_abstraction = self.get_security_abstraction()
    if security_abstraction:
        return await security_abstraction.check_permissions(
            user_context=user_context,
            resource=resource,
            action=action
        )
    
    # ✅ CAN USE: Error handling utilities
    try:
        # ... permission check logic ...
    except Exception as e:
        await self.handle_error_with_audit(e, "check_permissions")
    
    # ✅ CAN USE: Telemetry utilities (for own operations)
    await self.log_operation_with_telemetry(
        "security_permission_checked",
        success=True,
        details={"resource": resource, "action": action}
    )
```

### Operations That USE Security (Use Utilities Normally)

```python
async def initialize(self):
    """Initialize Security Guard - CAN use security utilities."""
    # ✅ CAN USE: All utilities (not providing security here)
    await self.log_operation_with_telemetry(
        "security_guard_initialize_start",
        success=True
    )
    
    try:
        # ... initialization logic ...
        await self.log_operation_with_telemetry(
            "security_guard_initialize_complete",
            success=True
        )
    except Exception as e:
        await self.handle_error_with_audit(e, "security_guard_initialize")
        await self.log_operation_with_telemetry(
            "security_guard_initialize_complete",
            success=False,
            details={"error": str(e)}
        )
```

---

## Decision Tree

For each operation in Nurse/Security Guard:

1. **Does this operation PROVIDE the utility?**
   - YES → Use bootstrap pattern (direct infrastructure access)
   - NO → Use utilities normally

2. **Does this operation USE the utility?**
   - YES → Use utilities normally
   - NO → Use bootstrap pattern (direct infrastructure access)

3. **Can this operation use OTHER utilities?**
   - YES → Use other utilities normally
   - NO → Only use direct infrastructure access

---

## Examples

### Nurse Service: collect_telemetry() - PROVIDES Telemetry

```python
async def collect_telemetry(self, ...):
    """Collect telemetry - PROVIDES telemetry utility."""
    # Bootstrap: Direct telemetry abstraction access
    telemetry_abstraction = self.get_telemetry_abstraction()
    
    try:
        # ... collection logic ...
        
        # Record using direct abstraction (not utility)
        if telemetry_abstraction:
            await telemetry_abstraction.record_metric(...)
        
        # Can use error handling utility
        # Can use health metrics utility
        await self.record_health_metric("telemetry_collected", 1.0, {...})
        
    except Exception as e:
        # Can use error handling utility
        await self.handle_error_with_audit(e, "collect_telemetry")
        raise
```

### Security Guard Service: check_permissions() - PROVIDES Security

```python
async def check_permissions(self, user_context, resource, action):
    """Check permissions - PROVIDES security utility."""
    # Bootstrap: Direct security abstraction access
    security_abstraction = self.get_security_abstraction()
    
    try:
        # ... permission check logic ...
        
        # Check using direct abstraction (not utility)
        if security_abstraction:
            result = await security_abstraction.check_permissions(
                user_context=user_context,
                resource=resource,
                action=action
            )
        
        # Can use telemetry utility
        await self.log_operation_with_telemetry(
            "permission_checked",
            success=True,
            details={"resource": resource, "action": action}
        )
        
        return result
        
    except Exception as e:
        # Can use error handling utility
        await self.handle_error_with_audit(e, "check_permissions")
        raise
```

---

## Summary

- **Bootstrap Pattern**: Use direct infrastructure access for operations that PROVIDE the utility
- **Normal Pattern**: Use utilities normally for operations that USE the utility
- **Mixed Pattern**: Can use other utilities even when providing one utility
- **Error Handling**: Always use error handling utilities (unless providing error handling)
- **Health Metrics**: Always use health metrics utilities (unless providing health monitoring)







