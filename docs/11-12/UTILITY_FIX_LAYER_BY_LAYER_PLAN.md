# Utility Fix - Layer by Layer Plan

**Date:** December 20, 2024  
**Approach:** Manual, systematic, layer by layer with audit at each step

---

## 🎯 Strategy

**Manual, one-pass-per-file approach:**
- Add ALL utilities (error handling, telemetry, security, multi-tenancy) in one pass
- Work layer by layer, bottom-up
- Audit after each layer to ensure 100% coverage
- Use FileParserService as the reference pattern

---

## 📋 Layer Order

### **Layer 1: DI Container** ✅ START HERE
- `foundations/di_container/di_container_service.py`
- **Audit:** Verify all utility access methods work correctly

### **Layer 2: Foundations** (5 foundations)
1. **Public Works Foundation**
   - `foundations/public_works_foundation/public_works_foundation_service.py`
   - All infrastructure abstractions
   - All composition services
   - **Audit:** Run validator on Public Works Foundation

2. **Curator Foundation**
   - `foundations/curator_foundation/curator_foundation_service.py`
   - All curator services
   - **Audit:** Run validator on Curator Foundation

3. **Communication Foundation**
   - `foundations/communication_foundation/communication_foundation_service.py`
   - All communication services (websocket, messaging, event_bus)
   - **Audit:** Run validator on Communication Foundation

4. **Agentic Foundation**
   - `foundations/agentic_foundation/agentic_foundation_service.py`
   - All agentic services
   - **Audit:** Run validator on Agentic Foundation

5. **Experience Foundation**
   - `foundations/experience_foundation/experience_foundation_service.py`
   - All experience services
   - **Audit:** Run validator on Experience Foundation

### **Layer 3: Realms** (4 realms)
1. **Smart City Realm**
   - All Smart City services (City Manager, Librarian, Content Steward, etc.)
   - **Audit:** Run validator on Smart City Realm

2. **Business Enablement Realm**
   - All enabling services (25 services)
   - All orchestrators (4 orchestrators)
   - Delivery Manager
   - **Audit:** Run validator on Business Enablement Realm

3. **Journey Realm**
   - All Journey services
   - **Audit:** Run validator on Journey Realm

4. **Solution Realm**
   - All Solution services
   - **Audit:** Run validator on Solution Realm

---

## 🔧 Fix Checklist Per File

For each service file, add:

### **1. Error Handling**
- [ ] Add `await self.handle_error_with_audit(e, "method_name")` to all except blocks
- [ ] Add `"error_code": type(e).__name__` to all error responses

### **2. Telemetry** (for operation methods)
- [ ] Add `import time` and `start_time = time.time()` at method start
- [ ] Add `await self.track_performance("method_name", duration, metadata)` after operations
- [ ] Add `await self.record_telemetry_event("event_name", data)` for significant events
- [ ] Add `await self.record_health_metric("metric_name", value, metadata)` for health tracking

### **3. Security** (for data access operations)
- [ ] Add `self.set_security_context(context)` where user_context is available
- [ ] Add `if not self.validate_access(resource, action): return access_denied` before data operations

### **4. Multi-Tenancy** (for data operations)
- [ ] Add `tenant_id = self.get_tenant_id()` check
- [ ] Add `if not self.validate_tenant_access(tenant_id): return tenant_denied` before data operations
- [ ] Ensure tenant isolation in metadata

---

## 📊 Progress Tracking

### **Layer 1: DI Container**
- [ ] DI Container Service
- [ ] Audit: Validator run

### **Layer 2: Foundations**
- [ ] Public Works Foundation
- [ ] Curator Foundation
- [ ] Communication Foundation
- [ ] Agentic Foundation
- [ ] Experience Foundation
- [ ] Audit: Validator run on all foundations

### **Layer 3: Realms**
- [ ] Smart City Realm
- [ ] Business Enablement Realm
- [ ] Journey Realm
- [ ] Solution Realm
- [ ] Audit: Validator run on all realms

---

## 🎯 Success Criteria

After each layer:
1. ✅ All try/except blocks have `handle_error_with_audit`
2. ✅ All error responses have `error_code`
3. ✅ All operation methods have telemetry tracking
4. ✅ All data access operations have security validation
5. ✅ All data operations have tenant validation
6. ✅ Validator shows 0 violations for that layer

---

**Status:** Starting with Layer 1 - DI Container













