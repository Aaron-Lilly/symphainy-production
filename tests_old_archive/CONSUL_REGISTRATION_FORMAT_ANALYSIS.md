# Consul Registration Format Analysis

**Date:** 2025-12-04  
**Status:** 🔍 **INVESTIGATING**

---

## 🎯 **User's Concern**

> "can you also check that the underlying consul tables actually match what we're trying to register? I just realized I can't remember the last time we revisited our consul setup, but we've iterated our curator strategy at least a dozen times."

---

## ✅ **Consul Status**

**Consul is Running:**
- Container: `symphainy-consul` (hashicorp/consul:latest)
- Status: Up 15 hours (healthy)
- Ports: 8500 (HTTP API), 8600 (DNS), 8300 (RPC)
- Connection: ✅ Connected successfully

**Services Successfully Registered:**
- `agent_capability_reporting`
- `agent_specialization_management`
- `agui_schema_documentation`
- `agent_health_monitoring`
- `CityManager` (multiple registrations)

---

## 🔍 **Current Registration Format**

### **What We're Sending to Consul:**

**From `consul_service_discovery_adapter.py` (line 135-142):**
```python
self.consul_client.agent.service.register(
    name=service_name,
    service_id=service_id,
    address=address,
    port=port,
    tags=enriched_tags,  # List of strings: ["key:value", "key:value", ...]
    check=check  # Optional health check dict
)
```

**Tag Format (line 128-132):**
```python
# Convert meta to tags (python-consul doesn't support meta parameter directly)
enriched_tags = tags.copy() if tags else []
for k, v in meta.items():
    enriched_tags.append(f"{k}:{str(v)}")  # ⚠️ POTENTIAL ISSUE: str(v) on complex objects
```

### **What Consul Expects:**

According to python-consul library and Consul API:
- `name`: string (required)
- `service_id`: string (required)
- `address`: string (required)
- `port`: int (required)
- `tags`: list of strings (optional)
- `check`: dict with health check config (optional)

**Consul DOES support `meta` parameter in newer versions**, but python-consul library may not expose it directly.

---

## 🚨 **Issues Identified**

### **Issue 1: Meta to Tags Conversion**

**Problem:** We're converting all meta dict values to strings using `str(v)`. If `v` contains complex objects (dicts, lists with thread locks, etc.), this can cause issues.

**Example:**
```python
meta = {
    "capabilities": ["cap1", "cap2"],  # List - OK
    "endpoints": ["/api/v1/endpoint"],  # List - OK
    "service_instance": <ServiceObject with thread locks>  # ❌ PROBLEM
}
```

**Current Code:**
```python
for k, v in meta.items():
    enriched_tags.append(f"{k}:{str(v)}")  # str(v) on ServiceObject might try to pickle
```

### **Issue 2: Pickle Error in Capability Registration**

**Error:** `cannot pickle '_thread.lock' object`

**Location:** `CapabilityRegistryService.register_capability()` line 259:
```python
result = {
    "success": True,
    "service_name": service_name,
    "capability": asdict(capability_def),  # ⚠️ asdict() might try to pickle nested objects
    "registered_at": capability_def.registered_at
}
```

**Root Cause:** `asdict()` from dataclasses tries to recursively convert all fields. If `CapabilityDefinition` contains nested objects with thread locks, it will fail.

---

## 📋 **What Needs to Be Fixed**

### **Fix 1: Safe Meta to Tags Conversion**

**Current:**
```python
for k, v in meta.items():
    enriched_tags.append(f"{k}:{str(v)}")
```

**Should Be:**
```python
for k, v in meta.items():
    # Only serialize simple types, skip complex objects
    if isinstance(v, (str, int, float, bool, type(None))):
        enriched_tags.append(f"{k}:{v}")
    elif isinstance(v, (list, tuple)):
        # Convert lists/tuples to comma-separated strings
        enriched_tags.append(f"{k}:{','.join(str(item) for item in v)}")
    elif isinstance(v, dict):
        # Convert dicts to JSON strings (but skip if contains unpicklable objects)
        try:
            import json
            enriched_tags.append(f"{k}:{json.dumps(v, default=str)}")
        except (TypeError, ValueError):
            # Skip if can't serialize
            self.logger.warning(f"⚠️ Skipping meta key '{k}' - cannot serialize value")
    else:
        # Skip complex objects (service instances, etc.)
        self.logger.debug(f"⚠️ Skipping meta key '{k}' - complex object type: {type(v).__name__}")
```

### **Fix 2: Safe asdict() for CapabilityDefinition**

**Current:**
```python
"capability": asdict(capability_def)
```

**Should Be:**
```python
# Use custom serialization that handles unpicklable objects
def safe_asdict(obj):
    """Safely convert dataclass to dict, handling unpicklable objects."""
    result = {}
    for field_name, field_value in obj.__dict__.items():
        try:
            # Try to serialize
            if isinstance(field_value, (str, int, float, bool, type(None))):
                result[field_name] = field_value
            elif isinstance(field_value, (list, tuple)):
                result[field_name] = [safe_asdict(item) if hasattr(item, '__dict__') else item for item in field_value]
            elif isinstance(field_value, dict):
                result[field_name] = {k: safe_asdict(v) if hasattr(v, '__dict__') else v for k, v in field_value.items()}
            elif hasattr(field_value, '__dict__'):
                result[field_name] = safe_asdict(field_value)
            else:
                result[field_name] = str(field_value)  # Fallback to string representation
        except (TypeError, ValueError, AttributeError):
            result[field_name] = str(field_value)  # Fallback to string representation
    return result

"capability": safe_asdict(capability_def)
```

---

## 🎯 **Consul Format Verification**

**What Consul Actually Stores:**
- Services are stored in Consul's service catalog
- Tags are stored as simple string arrays
- Meta information (if supported) would be stored separately
- Health checks are stored in Consul's health check system

**What We're Currently Doing:**
- ✅ Correct format for basic service registration
- ⚠️ Converting meta to tags (works but loses structure)
- ❌ Trying to serialize complex objects in tags (causes pickle errors)

---

## 📝 **Next Steps**

1. ✅ Verify Consul is running and connected
2. ✅ Check what services are actually registered
3. ⏳ Fix meta to tags conversion to handle complex objects safely
4. ⏳ Fix asdict() serialization to handle unpicklable objects
5. ⏳ Test registration with fixed serialization

---

**Status:** Consul is running and connected. Registration format is mostly correct, but serialization of complex objects needs to be fixed.

