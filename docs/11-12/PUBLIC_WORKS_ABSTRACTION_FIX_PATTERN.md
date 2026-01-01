# Public Works Abstraction Fix Pattern

**Date:** December 2024  
**Status:** ✅ Pattern Established  
**Goal:** Restore architecturally compliant abstractions

---

## ✅ Correct Pattern (from messaging_abstraction.py)

### Abstraction Methods Should:

1. **NO utility getters** - Remove all `get_utility()` calls
2. **NO telemetry calls** - Remove all telemetry recording
3. **Basic logging only** - Use `self.logger.info()` and `self.logger.error()`
4. **Re-raise exceptions** - Don't handle errors, let service layer handle them
5. **Simple, clean code** - Pure infrastructure logic

### Example (Correct Pattern):

```python
async def method_name(self, ...):
    """Method description."""
    try:
        # Infrastructure logic only
        result = await self.adapter.method_name(...)
        
        if result:
            self.logger.info(f"✅ Operation completed: {result}")
        
        return result
    except Exception as e:
        self.logger.error(f"❌ Error in method_name: {e}")
        raise  # Re-raise for service layer to handle
```

---

## ❌ Broken Patterns to Fix

### Pattern 1: Broken Utility Getter Blocks
```python
# ❌ WRONG - Remove this entire block
# Get utilities from DI container
error_handler = None
telemetry = None
if self.di_container and hasattr(self.di_container, 'get_utility'):
    try:
    except Exception:
        pass
```

**Fix:** Remove entire block, start with `try:` directly

### Pattern 2: Broken Exception Handling
```python
# ❌ WRONG
except Exception as e:
    if error_handler and hasattr(error_handler, 'handle_error'):
        self.logger.error(f"Error: {e}")
    return None  # or return False, return []
```

**Fix:**
```python
# ✅ CORRECT
except Exception as e:
    self.logger.error(f"❌ Error: {e}")
    raise  # Re-raise for service layer to handle
```

### Pattern 3: Orphaned Telemetry Code
```python
# ❌ WRONG - Remove these lines
# Record telemetry on success (abstractions use local performance logging)
# Note: Full telemetry handled at service layer
service_name=self.service_name,
operation="method_name",
status="success",
metadata={...}
)
```

**Fix:** Remove all orphaned telemetry fragments

### Pattern 4: Duplicate Raise Statements
```python
# ❌ WRONG
except Exception as e:
    ...
    raise  # Re-raise for service layer to handle

raise  # Re-raise for service layer to handle
raise  # Re-raise for service layer to handle
```

**Fix:** Keep only one `raise` statement inside the except block

### Pattern 5: Broken Code Structure
```python
# ❌ WRONG
try:
except Exception:
    self.logger.error(...)
    pass

raise  # Re-raise for service layer to handle
try:
    # actual code here
```

**Fix:** Remove empty try/except, remove orphaned raise, keep only the actual try block

---

## 📋 Files Fixed

- ✅ `task_management_abstraction.py` - Fully fixed and verified
- ✅ `llm_abstraction.py` - Fully fixed and verified
- ✅ `auth_abstraction.py` - Fully fixed and verified
- ✅ `event_management_abstraction.py` - Fully fixed and verified
- ✅ `messaging_abstraction.py` - Fully fixed and verified
- ⚠️ `state_management_abstraction.py` - In progress (extensive damage, needs more fixes)

## 📋 Files Remaining (44 files)

All files in `infrastructure_abstractions/` directory need the same pattern applied.

---

## 🔧 Fix Process

For each file:
1. Remove all "Get utilities from DI container" blocks
2. Remove all `error_handler` and `telemetry` variable declarations
3. Fix exception handling to use simple `self.logger.error()` + `raise`
4. Remove orphaned telemetry code fragments
5. Fix broken code structure (empty try/except, duplicate raises)
6. Verify syntax with `python3 -m py_compile`

---

## ✅ Verification

After fixing, verify:
- ✅ File compiles without syntax errors
- ✅ No utility getter blocks
- ✅ No telemetry calls
- ✅ Simple exception handling (log + raise)
- ✅ Clean, readable code

