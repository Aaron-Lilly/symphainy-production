# Store State Root Cause Analysis

**Date:** November 27, 2024  
**Issue:** `StateManagementAbstraction.store_state() got an unexpected keyword argument 'state_key'`  
**Service:** `data_analyzer_service` → `track_data_lineage()` → `data_steward.record_lineage()`

---

## 🔍 SYMPTOM

```
StateManagementAbstraction.store_state() got an unexpected keyword argument 'state_key'
```

**Location:** Called during `analyze_data()` when tracking data lineage

---

## 📊 CALL STACK ANALYSIS

### **1. Service Method Call**
```python
# data_analyzer_service.py:283-292
await self.track_data_lineage(
    lineage_data={
        "asset_id": storage_result.get("document_id", analysis_id),
        "parent_assets": [data_id],
        "transformation": {...}
    }
)
```

### **2. Base Class Method**
```python
# realm_service_base.py:695-716
async def track_data_lineage(self, lineage_data: Dict[str, Any]) -> str:
    data_steward = await self.get_data_steward_api()
    return await data_steward.record_lineage(lineage_data)
```

### **3. Data Steward Service**
```python
# data_steward_service.py:150-153
async def record_lineage(self, lineage_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> str:
    return await self.lineage_tracking_module.record_lineage(lineage_data, user_context)
```

### **4. Lineage Tracking Module**
```python
# lineage_tracking.py:70-74
await self.service.state_management_abstraction.store_state(
    state_key=f"lineage:{asset_id}",  # ❌ WRONG PARAMETER NAME
    state_data=lineage_record,
    metadata={"type": "lineage", "asset_id": asset_id}
)
```

### **5. State Management Abstraction**
```python
# state_management_abstraction.py:50-53
async def store_state(self, 
                     state_id: str,  # ✅ EXPECTS state_id
                     state_data: Dict[str, Any],
                     metadata: Dict[str, Any] = None) -> bool:
```

---

## 🎯 ROOT CAUSE

### **Parameter Name Mismatch**

**The Problem:**
- `lineage_tracking.py` calls `store_state()` with `state_key=...`
- `StateManagementAbstraction.store_state()` expects `state_id=...`
- Python doesn't allow keyword arguments that don't match the method signature

**Evidence:**
1. **Caller (lineage_tracking.py:70-74):**
   ```python
   await self.service.state_management_abstraction.store_state(
       state_key=f"lineage:{asset_id}",  # ❌ Wrong parameter name
       state_data=lineage_record,
       metadata={"type": "lineage", "asset_id": asset_id}
   )
   ```

2. **Method Signature (state_management_abstraction.py:50-53):**
   ```python
   async def store_state(self, 
                        state_id: str,  # ✅ Expects state_id
                        state_data: Dict[str, Any],
                        metadata: Dict[str, Any] = None) -> bool:
   ```

3. **Protocol Definition (state_management_protocol.py:23-27):**
   ```python
   async def store_state(self, 
                        state_id: str,  # ✅ Protocol also uses state_id
                        state_data: Dict[str, Any],
                        metadata: Dict[str, Any] = None,
                        ttl: int = None) -> bool:
   ```

---

## 🔬 DEEPER INVESTIGATION

### **Why This Happened:**

1. **Naming Inconsistency:**
   - The lineage tracking module uses `state_key` (internal naming)
   - The abstraction uses `state_id` (protocol-compliant naming)
   - This is a naming convention mismatch

2. **Multiple Call Sites:**
   - `lineage_tracking.py:70` - Uses `state_key`
   - `lineage_tracking.py:79` - Uses `state_key`
   - `lineage_tracking.py:92` - Uses `state_key`
   - All need to be fixed

3. **Protocol Compliance:**
   - The protocol defines `state_id` as the parameter name
   - The abstraction correctly implements `state_id`
   - The lineage tracking module incorrectly uses `state_key`

---

## ✅ SOLUTION

### **Fix: Update Lineage Tracking Module to Use `state_id`**

**File:** `symphainy-platform/backend/smart_city/services/data_steward/modules/lineage_tracking.py`

**Change all three call sites:**

1. **Line 70-74:**
   ```python
   # OLD:
   await self.service.state_management_abstraction.store_state(
       state_key=f"lineage:{asset_id}",
       state_data=lineage_record,
       metadata={"type": "lineage", "asset_id": asset_id}
   )
   
   # NEW:
   await self.service.state_management_abstraction.store_state(
       state_id=f"lineage:{asset_id}",  # ✅ Changed state_key to state_id
       state_data=lineage_record,
       metadata={"type": "lineage", "asset_id": asset_id}
   )
   ```

2. **Line 79-88:**
   ```python
   # OLD:
   await self.service.state_management_abstraction.store_state(
       state_key=f"lineage_relationship:{parent_id}:{asset_id}",
       ...
   )
   
   # NEW:
   await self.service.state_management_abstraction.store_state(
       state_id=f"lineage_relationship:{parent_id}:{asset_id}",  # ✅ Changed
       ...
   )
   ```

3. **Line 92-96:**
   ```python
   # OLD:
   await self.service.state_management_abstraction.store_state(
       state_key=f"lineage_relationship:{asset_id}:{child_id}",
       ...
   )
   
   # NEW:
   await self.service.state_management_abstraction.store_state(
       state_id=f"lineage_relationship:{asset_id}:{child_id}",  # ✅ Changed
       ...
   )
   ```

---

## 📋 VERIFICATION

After fix:
1. ✅ Run test - should pass
2. ✅ Verify lineage tracking works
3. ✅ Verify no parameter name errors
4. ✅ Verify state is stored correctly

---

## 🎯 ROOT CAUSE SUMMARY

**Root Cause:** Parameter name mismatch - `lineage_tracking.py` uses `state_key` but `store_state()` expects `state_id`

**Why:** Naming convention inconsistency between internal module naming and protocol-compliant naming

**Fix:** Update all `store_state()` calls in `lineage_tracking.py` to use `state_id` instead of `state_key`

**Impact:** Low - simple parameter name fix, no logic changes needed






