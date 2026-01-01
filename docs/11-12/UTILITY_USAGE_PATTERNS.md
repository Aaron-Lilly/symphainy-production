# Utility Usage Patterns - Reference Guide

**Date:** December 20, 2024  
**Purpose:** Standard patterns for using foundational utilities in services

---

## 🎯 Core Principles

1. **All utilities come from DI Container** - Use `self.get_utility()` or mixin methods
2. **Error handling is mandatory** - All try/except blocks should use error_handler
3. **Telemetry is mandatory** - All operations should be tracked
4. **Security is mandatory** - All data access should be validated
5. **Multi-tenancy is mandatory** - All data operations should validate tenant access

---

## 1. Error Handling Utility

### **Pattern: Structured Error Handling**

```python
async def parse_file(self, file_id: str) -> Dict[str, Any]:
    """Parse file with structured error handling."""
    error_handler = self.get_error_handler()
    
    try:
        # Operation logic
        result = await self._parse_file_internal(file_id)
        return result
        
    except Exception as e:
        # Use error handler for structured error handling
        handled = await error_handler.handle_error(
            error=e,
            context={
                "operation": "parse_file",
                "file_id": file_id,
                "service": self.service_name
            }
        )
        return handled
```

### **Pattern: Using Mixin Method (Preferred)**

```python
async def parse_file(self, file_id: str) -> Dict[str, Any]:
    """Parse file with error handling."""
    try:
        result = await self._parse_file_internal(file_id)
        return result
        
    except Exception as e:
        # Use mixin method (handles error + audit automatically)
        await self.handle_error_with_audit(e, "parse_file")
        return {
            "success": False,
            "error": str(e),
            "error_code": type(e).__name__,
            "file_id": file_id
        }
```

### **Pattern: Error Handling with User Context**

```python
async def parse_file(self, file_id: str, user_context: UserContext) -> Dict[str, Any]:
    """Parse file with error handling and user context."""
    try:
        result = await self._parse_file_internal(file_id)
        return result
        
    except Exception as e:
        await self.handle_error_with_audit(e, "parse_file")
        
        # Include user context in error response
        return {
            "success": False,
            "error": str(e),
            "error_code": type(e).__name__,
            "file_id": file_id,
            "user_id": user_context.user_id,
            "tenant_id": user_context.tenant_id
        }
```

---

## 2. Telemetry Utility

### **Pattern: Operation Tracking**

```python
async def parse_file(self, file_id: str) -> Dict[str, Any]:
    """Parse file with telemetry tracking."""
    import time
    start_time = time.time()
    
    try:
        result = await self._parse_file_internal(file_id)
        
        # Track performance
        duration = time.time() - start_time
        await self.track_performance("parse_file", duration, {
            "file_id": file_id,
            "file_type": result.get("file_type"),
            "success": True
        })
        
        # Record telemetry event
        await self.record_telemetry_event("file_parsed", {
            "file_id": file_id,
            "file_type": result.get("file_type"),
            "duration": duration,
            "chunks": len(result.get("chunks", []))
        })
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        await self.track_performance("parse_file", duration, {
            "file_id": file_id,
            "success": False,
            "error": str(e)
        })
        
        await self.record_telemetry_event("file_parse_error", {
            "file_id": file_id,
            "error": str(e),
            "duration": duration
        })
        
        raise
```

### **Pattern: Simple Operation Tracking**

```python
async def get_supported_formats(self) -> Dict[str, Any]:
    """Get supported formats with telemetry."""
    import time
    start_time = time.time()
    
    result = {
        "success": True,
        "supported_formats": self.supported_formats,
        "format_count": len(self.supported_formats)
    }
    
    # Track simple operation
    duration = time.time() - start_time
    await self.record_telemetry_metric("get_supported_formats.duration", duration)
    
    return result
```

---

## 3. Health Monitoring Utility

### **Pattern: Service Health Check**

```python
async def health_check(self) -> Dict[str, Any]:
    """Perform comprehensive health check."""
    # Use mixin method (includes telemetry, performance metrics)
    health_data = await super().health_check()
    
    # Add service-specific health information
    health_data.update({
        "service_specific": {
            "files_processed": getattr(self, 'files_processed_count', 0),
            "last_operation": getattr(self, 'last_operation_time', None),
            "document_intelligence_available": self.document_intelligence is not None,
            "content_steward_available": self.content_steward is not None
        }
    })
    
    return health_data
```

### **Pattern: Recording Health Metrics**

```python
async def parse_file(self, file_id: str) -> Dict[str, Any]:
    """Parse file with health metrics."""
    try:
        result = await self._parse_file_internal(file_id)
        
        # Record health metric (success)
        await self.record_health_metric("files_parsed", 1.0, {
            "file_type": result.get("file_type"),
            "success": True
        })
        
        return result
        
    except Exception as e:
        # Record health metric (failure)
        await self.record_health_metric("files_parsed", 0.0, {
            "success": False,
            "error": type(e).__name__
        })
        
        raise
```

---

## 4. Security/Authorization Utility

### **Pattern: Access Validation**

```python
async def parse_file(self, file_id: str, user_context: UserContext) -> Dict[str, Any]:
    """Parse file with security validation."""
    # Set security context
    self.set_security_context({
        "user_id": user_context.user_id,
        "tenant_id": user_context.tenant_id,
        "roles": user_context.roles,
        "permissions": user_context.permissions,
        "session_id": user_context.session_id
    })
    
    # Validate access to file resource
    if not self.validate_access(resource="file", action="read"):
        return {
            "success": False,
            "error": "Access denied",
            "error_code": "ACCESS_DENIED",
            "resource": "file",
            "action": "read"
        }
    
    # Proceed with operation
    result = await self._parse_file_internal(file_id)
    return result
```

### **Pattern: Security Context from User Context**

```python
async def parse_file(self, file_id: str, user_context: UserContext) -> Dict[str, Any]:
    """Parse file with security from UserContext."""
    # Set security context from UserContext
    security_context = {
        "user_id": user_context.user_id,
        "tenant_id": user_context.tenant_id,
        "roles": user_context.roles,
        "permissions": user_context.permissions,
        "session_id": user_context.session_id
    }
    
    if not self.set_security_context(security_context):
        return {
            "success": False,
            "error": "Failed to set security context",
            "error_code": "SECURITY_CONTEXT_FAILED"
        }
    
    # Validate access
    if not self.validate_access(resource="file", action="read"):
        return {
            "success": False,
            "error": "Access denied",
            "error_code": "ACCESS_DENIED"
        }
    
    # Proceed
    result = await self._parse_file_internal(file_id)
    return result
```

---

## 5. Multi-Tenancy Utility

### **Pattern: Tenant Validation**

```python
async def store_document(self, document_data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Store document with tenant isolation."""
    # Get tenant ID from security context
    tenant_id = self.get_tenant_id()
    if not tenant_id:
        return {
            "success": False,
            "error": "Tenant ID required",
            "error_code": "TENANT_REQUIRED"
        }
    
    # Ensure tenant isolation in metadata
    metadata["tenant_id"] = tenant_id
    
    # Store with tenant-aware service
    result = await self.librarian.store_document(document_data, metadata)
    
    # Validate tenant access to stored document
    if result.get("document_id"):
        stored_tenant = result.get("metadata", {}).get("tenant_id")
        if stored_tenant and stored_tenant != tenant_id:
            # This should never happen, but validate anyway
            if not self.validate_tenant_access(stored_tenant):
                return {
                    "success": False,
                    "error": "Tenant mismatch",
                    "error_code": "TENANT_MISMATCH"
                }
    
    return result
```

### **Pattern: Tenant-Aware Data Retrieval**

```python
async def retrieve_document(self, document_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve document with tenant validation."""
    # Get tenant ID from security context
    tenant_id = self.get_tenant_id()
    if not tenant_id:
        self.logger.warning("No tenant ID in security context")
        return None
    
    # Retrieve document
    document = await self.librarian.get_document(document_id)
    if not document:
        return None
    
    # Validate tenant access
    document_tenant = document.get("metadata", {}).get("tenant_id")
    if document_tenant and not self.validate_tenant_access(document_tenant):
        self.logger.warning(f"Tenant access denied: {tenant_id} cannot access {document_tenant}")
        return None
    
    return document
```

---

## 6. Configuration Utility

### **Pattern: Configuration Access**

```python
async def initialize(self) -> bool:
    """Initialize service with configuration."""
    await super().initialize()
    
    # Get configuration utility
    config = self.get_config()
    
    # Get configuration values
    max_file_size = config.get_int("max_file_size", default=100 * 1024 * 1024)  # 100MB
    supported_formats = config.get_list("supported_formats", default=self.supported_formats)
    enable_ocr = config.get_bool("enable_ocr", default=True)
    
    # Store configuration
    self.max_file_size = max_file_size
    self.supported_formats = supported_formats
    self.enable_ocr = enable_ocr
    
    return True
```

---

## 7. Complete Example: Service Method with All Utilities

```python
async def parse_file(
    self,
    file_id: str,
    user_context: UserContext,
    parse_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Parse file with full utility usage:
    - Security validation
    - Tenant validation
    - Error handling
    - Telemetry tracking
    - Health metrics
    """
    import time
    start_time = time.time()
    
    # 1. Set security context
    self.set_security_context({
        "user_id": user_context.user_id,
        "tenant_id": user_context.tenant_id,
        "roles": user_context.roles,
        "permissions": user_context.permissions,
        "session_id": user_context.session_id
    })
    
    # 2. Validate access
    if not self.validate_access(resource="file", action="read"):
        await self.record_telemetry_event("access_denied", {
            "file_id": file_id,
            "user_id": user_context.user_id,
            "resource": "file",
            "action": "read"
        })
        return {
            "success": False,
            "error": "Access denied",
            "error_code": "ACCESS_DENIED"
        }
    
    # 3. Validate tenant (if file has tenant)
    file_tenant = await self._get_file_tenant(file_id)
    if file_tenant and not self.validate_tenant_access(file_tenant):
        await self.record_telemetry_event("tenant_access_denied", {
            "file_id": file_id,
            "user_tenant": user_context.tenant_id,
            "file_tenant": file_tenant
        })
        return {
            "success": False,
            "error": "Tenant access denied",
            "error_code": "TENANT_ACCESS_DENIED"
        }
    
    # 4. Perform operation with error handling and telemetry
    try:
        result = await self._parse_file_internal(file_id, parse_options)
        
        # Track performance
        duration = time.time() - start_time
        await self.track_performance("parse_file", duration, {
            "file_id": file_id,
            "file_type": result.get("file_type"),
            "success": True
        })
        
        # Record telemetry event
        await self.record_telemetry_event("file_parsed", {
            "file_id": file_id,
            "file_type": result.get("file_type"),
            "duration": duration,
            "user_id": user_context.user_id,
            "tenant_id": user_context.tenant_id
        })
        
        # Record health metric
        await self.record_health_metric("files_parsed", 1.0, {
            "file_type": result.get("file_type"),
            "success": True
        })
        
        return result
        
    except Exception as e:
        # Error handling with audit
        duration = time.time() - start_time
        await self.handle_error_with_audit(e, "parse_file")
        
        # Track failed performance
        await self.track_performance("parse_file", duration, {
            "file_id": file_id,
            "success": False,
            "error": str(e)
        })
        
        # Record error telemetry
        await self.record_telemetry_event("file_parse_error", {
            "file_id": file_id,
            "error": str(e),
            "duration": duration,
            "user_id": user_context.user_id
        })
        
        # Record health metric (failure)
        await self.record_health_metric("files_parsed", 0.0, {
            "success": False,
            "error": type(e).__name__
        })
        
        return {
            "success": False,
            "error": str(e),
            "error_code": type(e).__name__,
            "file_id": file_id
        }
```

---

## 📋 Quick Reference

### **Error Handling**
- ✅ Use `self.get_error_handler()` or `self.handle_error_with_audit()`
- ❌ Don't just use `self.logger.error()` without error_handler

### **Telemetry**
- ✅ Use `self.track_performance()` for operations
- ✅ Use `self.record_telemetry_event()` for events
- ✅ Use `self.record_telemetry_metric()` for metrics
- ❌ Don't skip telemetry tracking

### **Health**
- ✅ Use `await self.health_check()` for health checks
- ✅ Use `await self.record_health_metric()` for health metrics
- ❌ Don't skip health reporting

### **Security**
- ✅ Use `self.set_security_context()` to set context
- ✅ Use `self.validate_access()` before operations
- ❌ Don't skip security validation

### **Multi-Tenancy**
- ✅ Use `self.get_tenant_id()` to get tenant
- ✅ Use `self.validate_tenant_access()` before data operations
- ❌ Don't skip tenant validation

---

**Next Step:** Apply these patterns systematically to all services













