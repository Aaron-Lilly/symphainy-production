# Standard Error Handling Pattern

**Date:** January 2025  
**Status:** ✅ Standard Pattern Defined  
**Phase:** 2.1 - Document Standard Error Handling Pattern

---

## Executive Summary

This document defines the standard error handling pattern for the Symphainy Platform. All services and abstractions must follow these patterns to ensure consistent error handling, audit trails, telemetry logging, and health monitoring across the platform.

---

## Core Principles

### 1. Separation of Concerns

- **Services (Business Layer):** Handle business errors with audit, telemetry, and health metrics
- **Abstractions (Infrastructure Layer):** Log infrastructure errors only, re-raise for service layer

### 2. Error Handling Hierarchy

```
Service Method
  ├─ Try: Business Logic
  ├─ Success: Log telemetry, record health metrics, return result
  └─ Exception: Handle with audit, log telemetry, record health metrics, return structured error
      └─ Abstraction Method
          ├─ Try: Infrastructure Operation
          ├─ Success: Return result
          └─ Exception: Log infrastructure error, re-raise for service layer
```

### 3. Required Components

All service error handling must include:
1. **Audit Trail** - `handle_error_with_audit()`
2. **Telemetry Logging** - `log_operation_with_telemetry()`
3. **Health Metrics** - `record_health_metric()`
4. **Structured Error Response** - Consistent error format

---

## Service Layer Pattern (✅ Correct)

### Standard Service Method Pattern

```python
async def my_service_method(self, param1: str, param2: int, **kwargs) -> Dict[str, Any]:
    """
    Service method with proper error handling.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Dict with success status and result or error details
    """
    try:
        # Log operation start
        await self.log_operation_with_telemetry(
            "my_service_method_start",
            success=True,
            details={
                "param1": param1,
                "param2": param2
            }
        )
        
        # Business logic
        result = await self.some_operation(param1, param2)
        
        # Additional operations
        processed_result = await self.process_result(result)
        
        # Log success
        await self.log_operation_with_telemetry(
            "my_service_method_complete",
            success=True,
            details={
                "result_id": processed_result.get("id"),
                "status": "success"
            }
        )
        
        # Record health metric
        await self.record_health_metric(
            "my_service_method_success",
            1.0,
            metadata={"operation": "my_service_method"}
        )
        
        # Return structured success response
        return {
            "success": True,
            "result": processed_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationError as e:
        # Validation errors - handle with audit
        await self.handle_error_with_audit(
            e,
            "my_service_method",
            {
                "error_type": "validation_error",
                "param1": param1,
                "param2": param2,
                "validation_details": str(e)
            }
        )
        
        # Log failure
        await self.log_operation_with_telemetry(
            "my_service_method_failed",
            success=False,
            details={
                "error_type": "validation_error",
                "error_message": str(e)
            }
        )
        
        # Record health metric
        await self.record_health_metric(
            "my_service_method_success",
            0.0,
            metadata={"operation": "my_service_method", "error_type": "validation_error"}
        )
        
        # Return structured error response
        return {
            "success": False,
            "error": str(e),
            "error_code": "VALIDATION_ERROR",
            "error_type": "validation_error",
            "message": f"Validation failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ConnectionError as e:
        # Infrastructure errors - handle with audit
        await self.handle_error_with_audit(
            e,
            "my_service_method",
            {
                "error_type": "infrastructure_error",
                "param1": param1,
                "param2": param2,
                "connection_details": str(e)
            }
        )
        
        # Log failure
        await self.log_operation_with_telemetry(
            "my_service_method_failed",
            success=False,
            details={
                "error_type": "infrastructure_error",
                "error_message": str(e)
            }
        )
        
        # Record health metric
        await self.record_health_metric(
            "my_service_method_success",
            0.0,
            metadata={"operation": "my_service_method", "error_type": "infrastructure_error"}
        )
        
        # Return structured error response
        return {
            "success": False,
            "error": str(e),
            "error_code": "INFRASTRUCTURE_ERROR",
            "error_type": "infrastructure_error",
            "message": f"Infrastructure error: {str(e)}",
            "retryable": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Generic errors - handle with audit
        await self.handle_error_with_audit(
            e,
            "my_service_method",
            {
                "error_type": "unexpected_error",
                "param1": param1,
                "param2": param2,
                "error_class": type(e).__name__
            }
        )
        
        # Log failure
        await self.log_operation_with_telemetry(
            "my_service_method_failed",
            success=False,
            details={
                "error_type": "unexpected_error",
                "error_message": str(e),
                "error_class": type(e).__name__
            }
        )
        
        # Record health metric
        await self.record_health_metric(
            "my_service_method_success",
            0.0,
            metadata={"operation": "my_service_method", "error_type": "unexpected_error"}
        )
        
        # Return structured error response
        return {
            "success": False,
            "error": str(e),
            "error_code": type(e).__name__.upper(),
            "error_type": "unexpected_error",
            "message": f"Operation failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }
```

### Simplified Service Method Pattern (For Simple Operations)

For simple operations that don't require detailed error categorization:

```python
async def simple_service_method(self, param: str) -> Dict[str, Any]:
    """Simple service method with standard error handling."""
    try:
        # Log operation start
        await self.log_operation_with_telemetry("simple_service_method_start", success=True)
        
        # Business logic
        result = await self.simple_operation(param)
        
        # Log success
        await self.log_operation_with_telemetry("simple_service_method_complete", success=True)
        await self.record_health_metric("simple_service_method_success", 1.0)
        
        return {"success": True, "result": result}
        
    except Exception as e:
        # Error handling with audit
        await self.handle_error_with_audit(e, "simple_service_method", {"param": param})
        
        # Log failure
        await self.log_operation_with_telemetry("simple_service_method_failed", success=False)
        await self.record_health_metric("simple_service_method_success", 0.0)
        
        # Return structured error response
        return {
            "success": False,
            "error": str(e),
            "error_code": type(e).__name__,
            "message": f"Operation failed: {str(e)}"
        }
```

---

## Abstraction Layer Pattern (✅ Correct)

### Standard Abstraction Method Pattern

```python
async def my_abstraction_method(self, param1: str, param2: int) -> Any:
    """
    Abstraction method with infrastructure error logging.
    
    Abstractions should:
    1. Log infrastructure errors only (no business logic)
    2. Re-raise all exceptions for service layer
    3. Never use error handler utilities (that's for services)
    """
    try:
        # Infrastructure operation
        result = await self.adapter.some_operation(param1, param2)
        return result
        
    except ConnectionError as e:
        # Infrastructure error logging (no business logic)
        self.logger.error(f"❌ Connection error in {self.__class__.__name__}: {e}")
        raise  # Re-raise for service layer
        
    except TimeoutError as e:
        # Infrastructure error logging
        self.logger.error(f"❌ Timeout error in {self.__class__.__name__}: {e}")
        raise  # Re-raise for service layer
        
    except ValueError as e:
        # Parameter validation errors (infrastructure level)
        self.logger.error(f"❌ Invalid parameter in {self.__class__.__name__}: {e}")
        raise  # Re-raise for service layer
        
    except Exception as e:
        # Generic infrastructure error logging
        self.logger.error(f"❌ Unexpected error in {self.__class__.__name__}: {e}")
        raise  # Re-raise for service layer
```

### Simplified Abstraction Method Pattern

For simple abstractions:

```python
async def simple_abstraction_method(self, param: str) -> Any:
    """Simple abstraction method with infrastructure error logging."""
    try:
        return await self.adapter.simple_operation(param)
        
    except Exception as e:
        # Infrastructure error logging (no business logic)
        self.logger.error(f"❌ Error in {self.__class__.__name__}: {e}")
        raise  # Re-raise for service layer
```

---

## Anti-Patterns (❌ Wrong)

### ❌ Anti-Pattern 1: Abstractions Using Error Handler Utilities

```python
# ❌ WRONG: Abstractions should NOT use error handler utilities
async def my_abstraction_method(self, param: str):
    try:
        return await self.adapter.operation(param)
    except Exception as e:
        await self.error_handler.handle_error(e)  # ❌ Remove - this is for services
        raise
```

**Why it's wrong:**
- Abstractions are infrastructure layer - they shouldn't have business error handling
- Error handler utilities are for services (business layer)
- Mixing concerns creates spaghetti code

**✅ Correct:**
```python
async def my_abstraction_method(self, param: str):
    try:
        return await self.adapter.operation(param)
    except Exception as e:
        self.logger.error(f"❌ Infrastructure error: {e}")  # ✅ Infrastructure logging only
        raise  # Re-raise for service layer
```

### ❌ Anti-Pattern 2: Services Not Using Standard Methods

```python
# ❌ WRONG: Services should use standard error handling methods
async def my_service_method(self, param: str):
    try:
        result = await self.operation(param)
        return result
    except Exception as e:
        self.logger.error(f"Error: {e}")  # ❌ Missing audit, telemetry, health metrics
        return {"error": str(e)}  # ❌ Inconsistent error format
```

**Why it's wrong:**
- Missing audit trail (no `handle_error_with_audit()`)
- Missing telemetry logging (no `log_operation_with_telemetry()`)
- Missing health metrics (no `record_health_metric()`)
- Inconsistent error format

**✅ Correct:**
```python
async def my_service_method(self, param: str):
    try:
        await self.log_operation_with_telemetry("my_service_method_start", success=True)
        result = await self.operation(param)
        await self.log_operation_with_telemetry("my_service_method_complete", success=True)
        await self.record_health_metric("my_service_method_success", 1.0)
        return {"success": True, "result": result}
    except Exception as e:
        await self.handle_error_with_audit(e, "my_service_method", {"param": param})
        await self.log_operation_with_telemetry("my_service_method_failed", success=False)
        await self.record_health_metric("my_service_method_success", 0.0)
        return {
            "success": False,
            "error": str(e),
            "error_code": type(e).__name__,
            "message": f"Operation failed: {str(e)}"
        }
```

### ❌ Anti-Pattern 3: Generic Exception Handling Without Categorization

```python
# ❌ WRONG: All errors treated the same
async def my_service_method(self, param: str):
    try:
        result = await self.operation(param)
        return {"success": True, "result": result}
    except Exception as e:  # ❌ Too generic - should categorize errors
        await self.handle_error_with_audit(e, "my_service_method")
        return {"success": False, "error": str(e)}
```

**Why it's wrong:**
- Can't distinguish between validation errors, infrastructure errors, business logic errors
- Can't provide appropriate retry logic
- Can't provide user-friendly error messages

**✅ Correct:**
```python
async def my_service_method(self, param: str):
    try:
        result = await self.operation(param)
        return {"success": True, "result": result}
    except ValidationError as e:
        # Handle validation errors specifically
        await self.handle_error_with_audit(e, "my_service_method", {"error_type": "validation"})
        return {"success": False, "error": str(e), "error_code": "VALIDATION_ERROR", "retryable": False}
    except ConnectionError as e:
        # Handle infrastructure errors specifically
        await self.handle_error_with_audit(e, "my_service_method", {"error_type": "infrastructure"})
        return {"success": False, "error": str(e), "error_code": "INFRASTRUCTURE_ERROR", "retryable": True}
    except Exception as e:
        # Handle unexpected errors
        await self.handle_error_with_audit(e, "my_service_method", {"error_type": "unexpected"})
        return {"success": False, "error": str(e), "error_code": "UNEXPECTED_ERROR"}
```

---

## Error Response Format

All service methods must return a consistent error response format:

```python
{
    "success": False,
    "error": str(e),  # Error message
    "error_code": "ERROR_CODE",  # Machine-readable error code
    "error_type": "validation_error" | "infrastructure_error" | "business_logic_error" | "unexpected_error",
    "message": "User-friendly error message",
    "retryable": True | False,  # Whether the operation can be retried
    "timestamp": "2025-01-XX...",  # ISO timestamp
    "details": {  # Optional additional context
        "param1": value1,
        "param2": value2
    }
}
```

---

## Available Methods

All services inheriting from `RealmServiceBase` or `OrchestratorBase` have access to:

### `handle_error_with_audit(error: Exception, operation: str, details: Optional[Dict[str, Any]] = None)`
- Handles error with audit logging
- Records error in audit trail
- Logs error with context

### `log_operation_with_telemetry(operation: str, success: bool = True, details: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None)`
- Logs operation with telemetry
- Records operation in telemetry system
- Tracks operation success/failure

### `record_health_metric(metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None)`
- Records health metric
- Tracks service health
- Used for health monitoring

---

## Migration Checklist

When updating a service to use the standard error handling pattern:

- [ ] Replace generic `except Exception as e:` with specific exception types where appropriate
- [ ] Add `handle_error_with_audit()` call in exception handlers
- [ ] Add `log_operation_with_telemetry()` calls for operation start, success, and failure
- [ ] Add `record_health_metric()` calls for success/failure tracking
- [ ] Ensure error responses follow standard format
- [ ] Remove any error handler utility calls from abstractions
- [ ] Ensure abstractions only log infrastructure errors and re-raise

---

## Examples

### Example 1: Content Service Method

```python
async def parse_file(self, file_path: str, format: str) -> Dict[str, Any]:
    """Parse file into structured format."""
    try:
        await self.log_operation_with_telemetry(
            "parse_file_start",
            success=True,
            details={"file_path": file_path, "format": format}
        )
        
        # Get abstraction
        parser = self.get_abstraction("parser")
        
        # Parse file
        parsed_document = await parser.parse_file(file_path, format)
        
        # Store parsed document
        stored_doc = await self.store_document(parsed_document)
        
        await self.log_operation_with_telemetry(
            "parse_file_complete",
            success=True,
            details={"document_id": stored_doc.get("id")}
        )
        await self.record_health_metric("parse_file_success", 1.0)
        
        return {
            "success": True,
            "result": stored_doc,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except FileNotFoundError as e:
        await self.handle_error_with_audit(
            e,
            "parse_file",
            {"error_type": "file_not_found", "file_path": file_path}
        )
        await self.log_operation_with_telemetry("parse_file_failed", success=False)
        await self.record_health_metric("parse_file_success", 0.0)
        
        return {
            "success": False,
            "error": str(e),
            "error_code": "FILE_NOT_FOUND",
            "error_type": "validation_error",
            "message": f"File not found: {file_path}",
            "retryable": False
        }
        
    except Exception as e:
        await self.handle_error_with_audit(
            e,
            "parse_file",
            {"error_type": "unexpected_error", "file_path": file_path, "format": format}
        )
        await self.log_operation_with_telemetry("parse_file_failed", success=False)
        await self.record_health_metric("parse_file_success", 0.0)
        
        return {
            "success": False,
            "error": str(e),
            "error_code": type(e).__name__.upper(),
            "error_type": "unexpected_error",
            "message": f"Failed to parse file: {str(e)}"
        }
```

### Example 2: Abstraction Method

```python
async def parse_file(self, file_path: str, format: str) -> ParsedDocument:
    """Parse file using adapter."""
    try:
        return await self.adapter.parse_file(file_path, format)
        
    except FileNotFoundError as e:
        self.logger.error(f"❌ File not found in {self.__class__.__name__}: {e}")
        raise
        
    except ValueError as e:
        self.logger.error(f"❌ Invalid format in {self.__class__.__name__}: {e}")
        raise
        
    except Exception as e:
        self.logger.error(f"❌ Unexpected error in {self.__class__.__name__}: {e}")
        raise
```

---

## Testing Error Handling

When testing error handling:

1. **Test Success Path:**
   - Verify `log_operation_with_telemetry()` called with `success=True`
   - Verify `record_health_metric()` called with value `1.0`
   - Verify success response format

2. **Test Error Paths:**
   - Verify `handle_error_with_audit()` called with correct error and context
   - Verify `log_operation_with_telemetry()` called with `success=False`
   - Verify `record_health_metric()` called with value `0.0`
   - Verify error response format matches standard

3. **Test Abstraction Errors:**
   - Verify abstractions log errors and re-raise
   - Verify services handle re-raised errors correctly

---

**Last Updated:** January 2025  
**Status:** ✅ Standard Pattern Defined - Ready for Implementation

