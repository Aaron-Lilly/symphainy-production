# Startup Refactoring Quick Reference

**Date:** 2025-11-09  
**Status:** Ready to implement

---

## 🎯 The Core Insight

**OrchestratorBase completes the Platform Execution Triangle:**

```
Managers → Orchestrators → Services
```

- **Managers** (ManagerServiceBase): Lifecycle control, realm orchestration
- **Orchestrators** (OrchestratorBase): Compose tasks across services
- **Services** (RealmServiceBase): Atomic business capabilities

---

## 🚀 Startup Flow (Simplified)

### **Boot Time (EAGER):**
1. Foundations (DI Container, Public Works, Curator, Communication, Agentic)
2. Smart City Gateway (City Manager)

**That's it!** Everything else is lazy.

### **On-Demand (LAZY):**
- User Action → GuideAgent → Smart City Gateway
- → Manager (lazy-loaded by PlatformOrchestrator)
- → Orchestrator (lazy-loaded by Manager via OrchestratorBase)
- → Service (lazy-loaded by Orchestrator)

---

## ✅ What This Fixes

1. **Traffic Cop:** Lazy-initialized via City Manager's `orchestrate_realm_startup()` on first use
2. **Fast Startup:** Only 2 phases at boot (vs. 6 phases before)
3. **OrchestratorBase:** Enables Managers to lazy-load orchestrators consistently
4. **Clean Separation:** Clear hierarchy, no mixing of concerns

---

## 📋 Implementation Checklist

- [ ] Phase 1: Add StartupPolicy infrastructure
- [ ] Phase 2: Remove Phase 5 (eager realm services) from PlatformOrchestrator
- [ ] Phase 3: Implement lazy Smart City role initialization
- [ ] Phase 4: Implement lazy Manager loading
- [ ] Phase 5: Implement lazy Orchestrator loading (OrchestratorBase shines here!)
- [ ] Phase 6: Fix Traffic Cop (via lazy Smart City roles)
- [ ] Phase 7: Unify agent initialization
- [ ] Phase 8: Add dependency validation

---

## 🎯 Key Files to Update

1. `bases/startup_policy.py` (NEW)
2. `main.py` (remove Phase 5, add lazy loading)
3. `backend/smart_city/services/city_manager/city_manager_service.py` (lazy Smart City roles)
4. Managers (add `get_orchestrator()` method)
5. `backend/platform_infrastructure/service_registry.py` (NEW)

---

**Status:** Ready to start! 🚀






