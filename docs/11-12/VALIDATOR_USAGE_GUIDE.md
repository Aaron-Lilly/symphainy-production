# Foundation Utility Validator Usage Guide

**Date:** December 20, 2024  
**Purpose:** Track compliance with utility usage patterns across foundation layers

---

## 🚀 Quick Start

### **Run Validator**

```bash
# Validate all foundations
cd /home/founders/demoversion
python3 symphainy_source/symphainy-platform/scripts/validate_foundation_utilities.py all

# Validate specific foundation
python3 symphainy_source/symphainy-platform/scripts/validate_foundation_utilities.py curator
python3 symphainy_source/symphainy-platform/scripts/validate_foundation_utilities.py communication
python3 symphainy_source/symphainy-platform/scripts/validate_foundation_utilities.py agentic
python3 symphainy_source/symphainy-platform/scripts/validate_foundation_utilities.py experience
```

### **Output**

The validator generates:
1. **Console Report** - Human-readable summary with violations
2. **JSON Report** - Detailed machine-readable report per foundation
3. **Combined Summary** - All foundations in one JSON file (when using `all`)

**Report Locations:**
- Individual: `symphainy_source/docs/11-12/{foundation}_utility_compliance_report.json`
- Summary: `symphainy_source/docs/11-12/foundation_utility_compliance_summary.json`

---

## 📊 What the Validator Checks

### **1. Error Handling** ✅ Required
- ✅ Uses `handle_error_with_audit()` or `get_error_handler()`
- ❌ No bare `except Exception as e:` blocks
- ❌ No exception blocks without proper error handling

### **2. Telemetry** ✅ Required
- ✅ Uses `log_operation_with_telemetry()` for operation tracking
- ✅ Uses `record_health_metric()` for success paths

### **3. Security** ✅ Required (Service Layer Only)
- ✅ Uses `get_security()` and `check_permissions()` for data access operations
- ⚠️ Abstractions don't need security validation (already done at service layer)

### **4. Multi-Tenancy** ✅ Required (Service Layer Only)
- ✅ Uses `get_tenant()` and `validate_tenant_access()` for data access operations
- ⚠️ Abstractions don't need tenant validation (already done at service layer)

---

## 📋 Validation Rules

### **Service Layer (User-Facing)**
- ✅ **Full utilities required**: Error handling, telemetry, security, tenant
- ✅ **All async methods** must use utilities
- ✅ **Data access operations** must validate security and tenant

### **Abstraction Layer (Internal)**
- ✅ **Error handling and telemetry required**
- ❌ **No security/tenant validation** (already validated at service layer)

---

## 🔍 Understanding the Report

### **Summary Statistics**
```
Total Files Scanned: 15
Total Methods: 120
Async Methods: 85
Compliant Methods: 45
```

### **Violations by Category**
```
error_handling: 25
telemetry: 18
security: 12
tenant: 8
```

### **Violations by File**
```
📄 curator_foundation_service.py
  ERROR_HANDLING:
    - register_service: Bare except block without handle_error_with_audit
    - discover_service: Exception block without proper error handling
  TELEMETRY:
    - register_service: Missing log_operation_with_telemetry
    - discover_service: Missing record_health_metric
```

---

## 🎯 Using Reports for Fixes

### **Step 1: Review Violations**
1. Open the JSON report for detailed information
2. Identify files with most violations
3. Prioritize by impact (user-facing methods first)

### **Step 2: Fix Pattern**
For each violation:
1. **Error Handling**: Replace bare except with `await self.handle_error_with_audit(e, "method_name")`
2. **Telemetry**: Add `log_operation_with_telemetry()` at start/end
3. **Health Metrics**: Add `record_health_metric()` for success paths
4. **Security**: Add security validation before data operations (service layer only)
5. **Tenant**: Add tenant validation before data operations (service layer only)

### **Step 3: Re-validate**
```bash
python3 symphainy_source/symphainy-platform/scripts/validate_foundation_utilities.py curator
```

---

## 📝 Example Fix

### **Before (Violations)**
```python
async def get_service(self, service_name: str):
    try:
        return await self._discover_service(service_name)
    except Exception as e:
        self.logger.error(f"Error: {e}")
        return None
```

### **After (Compliant)**
```python
async def get_service(self, service_name: str):
    try:
        await self.log_operation_with_telemetry("get_service_start", success=True)
        
        result = await self._discover_service(service_name)
        
        await self.record_health_metric("get_service_success", 1.0, {"service_name": service_name})
        await self.log_operation_with_telemetry("get_service_complete", success=True)
        
        return result
    except Exception as e:
        await self.handle_error_with_audit(e, "get_service")
        return {"success": False, "error": str(e), "error_code": type(e).__name__}
```

---

## 🔄 Continuous Validation

### **Before Each Commit**
```bash
# Quick check
python3 symphainy_source/symphainy-platform/scripts/validate_foundation_utilities.py all
```

### **After Fixing a Foundation**
```bash
# Validate specific foundation
python3 symphainy_source/symphainy-platform/scripts/validate_foundation_utilities.py curator
```

### **Track Progress**
- Compare JSON reports over time
- Monitor violation counts decreasing
- Track compliant method count increasing

---

## ⚠️ Common Issues

### **Issue: "Missing log_operation_with_telemetry"**
**Fix:** Add telemetry calls at method start and end
```python
await self.log_operation_with_telemetry("method_name_start", success=True)
# ... business logic ...
await self.log_operation_with_telemetry("method_name_complete", success=True)
```

### **Issue: "Bare except block without handle_error_with_audit"**
**Fix:** Replace with proper error handling
```python
except Exception as e:
    await self.handle_error_with_audit(e, "method_name")
```

### **Issue: "Missing security validation for data access operation"**
**Fix:** Add security check before data operations (service layer only)
```python
security = self.get_security()
if security and not await security.check_permissions(user_context, resource_id, "read"):
    return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
```

---

## 📚 Reference

- **Pattern Documentation:** `FOUNDATION_UTILITY_COMPLIANCE_APPROACH.md`
- **Public Works Reference:** `PUBLIC_WORKS_FOUNDATION_UTILITY_FIX_PROGRESS.md`
- **Validator Script:** `symphainy-platform/scripts/validate_foundation_utilities.py`




