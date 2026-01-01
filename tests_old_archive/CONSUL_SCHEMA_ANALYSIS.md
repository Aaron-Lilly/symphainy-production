# Consul Schema Analysis - Registration Format Mismatch

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

---

## 🔍 **Current Registration Format**

### **What We're Sending to Consul:**

**From `consul_service_discovery_adapter.py` (line 167-172):**
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

**Tag Format (line 128-164):**
- We convert `meta` dict to tags because `python-consul` doesn't support `meta` parameter directly
- Format: `["key:value", "key:value", ...]`
- We skip complex objects (thread locks, service instances, etc.)

### **What Consul Actually Supports:**

**Consul API (v1.0+):**
- `name`: string (required)
- `service_id`: string (required)
- `address`: string (required)
- `port`: int (required)
- `tags`: list of strings (optional)
- `meta`: dict of string key-value pairs (optional) ✅ **SUPPORTED IN CONSUL API**
- `check`: dict with health check config (optional)

**python-consul Library:**
- May not expose `meta` parameter directly (depends on version)
- We're using workaround: convert `meta` to tags

---

## 🚨 **Potential Issues**

### **Issue 1: python-consul Version**

**Question:** Does our version of `python-consul` support the `meta` parameter?

**Impact:** If it does, we should use `meta` directly instead of converting to tags.

### **Issue 2: Tag Format Limitations**

**Current Approach:** Converting `meta` dict to tags like `["key:value", "key:value"]`

**Limitations:**
- Tags are flat strings - no nested structures
- Limited to simple key-value pairs
- Can't represent complex metadata structures
- Tag length limits (Consul has tag size limits)

### **Issue 3: Pickle Error Source**

**Hypothesis:** The pickle error might be happening when:
1. Converting `meta` dict to tags (trying to serialize complex objects)
2. Consul client trying to serialize the entire registration payload
3. Capability registry trying to register with Consul

**Need to check:** Where exactly is the pickle happening?

---

## 📋 **Investigation Steps**

1. ⏳ Check python-consul version
2. ⏳ Check if python-consul supports `meta` parameter
3. ⏳ Check what's actually registered in Consul
4. ⏳ Compare registration format with what Consul expects
5. ⏳ Identify where pickle error is occurring

---

## 💡 **Next Steps**

1. Check python-consul version and capabilities
2. Verify Consul API version
3. Test if `meta` parameter works directly
4. Fix pickle error by ensuring only serializable data is sent

---

**Status:** Investigating Consul schema and registration format compatibility.

