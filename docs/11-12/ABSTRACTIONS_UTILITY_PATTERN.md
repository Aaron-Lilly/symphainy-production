# Infrastructure Abstractions Utility Pattern

**Date:** December 20, 2024  
**Status:** 📋 **PATTERN ESTABLISHED**

---

## Pattern for Adding Utilities to Abstractions

### **1. Constructor Update**

**Before:**
```python
def __init__(self, supabase_adapter, config_adapter):
    self.supabase_adapter = supabase_adapter
    self.config_adapter = config_adapter
    self.logger = logging.getLogger(__name__)
```

**After:**
```python
def __init__(self, supabase_adapter, config_adapter, di_container=None):
    self.supabase_adapter = supabase_adapter
    self.config_adapter = config_adapter
    self.di_container = di_container
    self.service_name = "abstraction_name"
    
    # Get logger from DI Container if available
    if di_container and hasattr(di_container, 'get_logger'):
        self.logger = di_container.get_logger(self.service_name)
    else:
        self.logger = logging.getLogger(__name__)
```

---

### **2. Success Path - Add Telemetry**

**Before:**
```python
result = await self.adapter.create_file(enhanced_file_data)
self.logger.info(f"✅ File created: {result.get('uuid')}")
return result
```

**After:**
```python
result = await self.adapter.create_file(enhanced_file_data)
self.logger.info(f"✅ File created: {result.get('uuid')}")

# Record platform operation event
telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
if telemetry:
    await telemetry.record_platform_operation_event("create_file", {
        "file_uuid": result.get("uuid"),
        "file_name": result.get("ui_name"),
        "file_type": result.get("file_type"),
        "success": True
    })

return result
```

---

### **3. Error Path - Add Error Handler**

**Before:**
```python
except Exception as e:
    self.logger.error(f"❌ Failed to create file: {e}")
    raise
```

**After:**
```python
except Exception as e:
    # Use error handler with telemetry
    error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
    telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
    if error_handler:
        await error_handler.handle_error(e, {
            "operation": "create_file",
            "service": self.service_name
        }, telemetry=telemetry)
    else:
        self.logger.error(f"❌ Failed to create file: {e}")
    raise
```

---

### **4. Methods That Return None on Error**

**Before:**
```python
except Exception as e:
    self.logger.error(f"❌ Failed to get file {file_uuid}: {e}")
    return None
```

**After:**
```python
except Exception as e:
    # Use error handler with telemetry
    error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
    telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
    if error_handler:
        await error_handler.handle_error(e, {
            "operation": "get_file",
            "file_uuid": file_uuid,
            "service": self.service_name
        }, telemetry=telemetry)
    else:
        self.logger.error(f"❌ Failed to get file {file_uuid}: {e}")
    return None
```

---

## Key Points

1. ✅ **Add `di_container=None` to constructor**
2. ✅ **Add `self.service_name` for consistent naming**
3. ✅ **Get logger from DI container if available**
4. ✅ **Add telemetry to success paths** (before return)
5. ✅ **Add error handler to exception blocks** (with telemetry)
6. ✅ **Preserve existing behavior** (fallback to logger if utilities not available)
7. ❌ **Do NOT add security/tenant validation** (stays at composition service level)

---

## Progress Tracking

### **File Management Abstraction** (In Progress)
- ✅ Constructor updated
- ✅ `create_file` - Done
- ✅ `get_file` - Done
- ⏳ `update_file` - Next
- ⏳ `delete_file` - Pending
- ⏳ `list_files` - Pending
- ⏳ `create_file_link` - Pending
- ⏳ `get_file_links` - Pending
- ⏳ `delete_file_link` - Pending
- ⏳ `get_lineage_tree` - Pending
- ⏳ `get_file_descendants` - Pending
- ⏳ `create_child_file` - Pending
- ⏳ `search_files` - Pending
- ⏳ `get_file_statistics` - Pending
- ⏳ `health_check` - Pending

---

**Status:** 📋 **PATTERN ESTABLISHED - Ready for batch processing**












