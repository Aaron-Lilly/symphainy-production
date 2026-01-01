# 🗓️ Week 1: Complete Refactoring Plan

**Timeline:** 7 Days  
**Scope:** Base Classes, Mixins, Base Class Protocols, Service Protocols  
**Status:** Ready to Execute

---

## 📊 EXECUTIVE SUMMARY

**What We're Doing:**
- Refactoring 4 bloated base classes (2,326 lines → 1,030 lines via mixins)
- Creating NEW base class protocols (not migrating old ones)
- Converting 16 ABC service interfaces to Python Protocols
- Setting clean foundation for 12-week refactoring

**Why 7 Days (vs original 3):**
- Original plan didn't account for service-level interface conversion
- Need time to audit services (what's actually implemented vs defined)
- Setting proper foundation saves time in Weeks 2-12

---

## 🎯 THE TWO PROTOCOL ISSUES

### **Issue 1: Base Class Protocols** (In `bases/protocols/`)

**Problem:**
- Current protocols contain BOTH protocol definitions AND duplicate base classes
- Not aligned with new architecture (Platform Gateway, Curator, Communication)

**Solution:** Start fresh with new protocols (contracts only, no base classes)

---

### **Issue 2: Service-Level Interfaces** (In `realm/interfaces/`)

**Problem:**
- 16 ABC interface files (like `IJourneyManager`, `IContentPillar`)
- Some methods outdated (old architecture patterns)
- Not all services implement all interface methods
- Duplicate definitions (`health_check()` defined 16 times)

**Solution:** Start fresh with new Python Protocols + protocol hierarchy

---

## 📅 7-DAY BREAKDOWN

### **Day 1-2: Base Class Protocols**

**Goal:** Create clean base class protocols (NO base classes in protocol files)

**Files to Create:**
```
bases/protocols/
├── __init__.py
├── realm_service_protocol.py (60 lines - contract only)
├── smart_city_role_protocol.py (70 lines - contract only)
├── foundation_service_protocol.py (50 lines - contract only)
├── manager_service_protocol.py (80 lines - contract only)
└── platform_gateway_protocol.py (40 lines - contract only)
```

**Key Requirements:**
- ✅ NO base classes in protocol files (protocols are contracts ONLY)
- ✅ Aligned with new architecture (Platform Gateway, Curator, Communication patterns)
- ✅ Type hints for all methods
- ✅ Clear docstrings

---

### **Day 3: Mixins**

**Goal:** Extract valuable functionality into focused, testable mixins

**Files to Create:**
```
bases/mixins/
├── __init__.py
├── security_mixin.py (120 lines - zero-trust, multi-tenancy)
├── platform_capabilities_mixin.py (100 lines - SOA, service discovery)
├── performance_monitoring_mixin.py (80 lines - telemetry, health)
├── infrastructure_access_mixin.py (150 lines - abstraction getters)
├── utility_access_mixin.py (80 lines - utility getters)
├── micro_module_support_mixin.py (130 lines - module loading)
└── communication_mixin.py (90 lines - messaging, events)
```

**Key Requirements:**
- ✅ Each mixin under 350 lines
- ✅ One responsibility per mixin
- ✅ Explicit `_init_*` methods (no constructor chaining)
- ✅ Use REAL implementations (no placeholders, stubs, or hardcoded cheats)

---

### **Day 4-5: Base Classes (Aggregators)**

**Goal:** Create new base classes that compose mixins

**Files to Create:**
```
bases/
├── realm_service_base.py (80 lines - composes 6 mixins)
├── smart_city_role_base.py (90 lines - composes 7 mixins)
├── foundation_service_base.py (70 lines - composes 3 mixins)
└── manager_service_base.py (110 lines - extends RealmServiceBase)
```

**Key Requirements:**
- ✅ Each base under 110 lines (aggregators, not implementations)
- ✅ Implements corresponding protocol
- ✅ Explicit mixin initialization
- ✅ Manager-specific logic ONLY in ManagerServiceBase (not in a mixin)

---

### **Day 6: Service Protocol Audit & Base Service Protocol**

**Goal:** Audit services and create base service protocol

**Tasks:**
1. **Audit Services:** For each service, identify what methods are ACTUALLY implemented
   ```bash
   # Example audit
   grep -r "async def orchestrate_journey" journey_solution/services/journey_manager/
   grep -r "async def health_check" journey_solution/services/journey_manager/
   # etc.
   ```

2. **Create Base Service Protocol:** Standard methods ALL services need
   ```python
   # bases/protocols/service_protocol.py (60 lines)
   class ServiceProtocol(Protocol):
       """Base protocol for ALL services."""
       
       # Lifecycle
       async def initialize(self) -> bool: ...
       async def shutdown(self) -> bool: ...
       
       # Health
       async def health_check(self) -> Dict[str, Any]: ...
       async def get_service_capabilities(self) -> Dict[str, Any]: ...
       
       # Communication (NEW ARCHITECTURE)
       async def send_message(self, message: Dict) -> Dict: ...
       async def publish_event(self, event: Dict) -> bool: ...
       
       # Infrastructure (NEW ARCHITECTURE)
       def get_infrastructure_abstraction(self, name: str) -> Any: ...
   ```

**Deliverable:**
- `bases/protocols/service_protocol.py` (60 lines)
- Service audit document (what's implemented vs what's defined)

---

### **Day 7: Realm-Specific Service Protocols**

**Goal:** Create focused, realm-specific service protocols

**Files to Create (~16 files):**
```
journey_solution/protocols/
├── __init__.py
├── journey_manager_protocol.py (50 lines)
├── journey_orchestrator_protocol.py (50 lines)
├── business_outcome_analyzer_protocol.py (50 lines)
└── solution_architect_protocol.py (50 lines)

experience/protocols/
├── __init__.py
├── experience_manager_protocol.py (50 lines)
├── frontend_integration_protocol.py (50 lines)
└── experience_service_protocol.py (50 lines)

backend/business_enablement/protocols/
├── __init__.py
├── content_pillar_protocol.py (50 lines)
├── insights_pillar_protocol.py (50 lines)
├── operations_pillar_protocol.py (50 lines)
├── business_outcomes_pillar_protocol.py (50 lines)
├── delivery_manager_protocol.py (50 lines)
├── business_orchestrator_protocol.py (50 lines)
└── guide_agent_protocol.py (50 lines)

engines/protocols/
├── __init__.py
└── policy_engine_protocol.py (50 lines)
```

**Example:**
```python
# journey_solution/protocols/journey_manager_protocol.py
from typing import Protocol, Dict, Any
from bases.protocols.service_protocol import ServiceProtocol

class JourneyManagerProtocol(ServiceProtocol, Protocol):
    """
    Protocol for Journey Manager services.
    Inherits standard methods from ServiceProtocol.
    """
    
    # ONLY journey-specific methods (not duplicates from ServiceProtocol)
    async def orchestrate_journey(self, journey_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate user journey across 4 pillars."""
        ...
    
    async def orchestrate_mvp_journey(self, user_intent: str, business_outcome: str) -> Dict[str, Any]:
        """Orchestrate MVP journey."""
        ...
    
    async def coordinate_with_pillar(self, pillar_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate with specific pillar service."""
        ...
```

**Key Requirements:**
- ✅ Each protocol inherits from `ServiceProtocol` (gets standard methods)
- ✅ Each protocol defines ONLY service-specific methods (no duplication)
- ✅ Only methods services ACTUALLY implement (based on Day 6 audit)
- ✅ Aligned with new architecture
- ✅ Each protocol under 80 lines

---

## 📦 WEEK 1 DELIVERABLES

| Category | Files | Lines | Status |
|----------|-------|-------|--------|
| **Base Class Protocols** | 5 | ~300 | Day 1-2 |
| **Base Service Protocol** | 1 | ~60 | Day 6 |
| **Service Protocols** | ~16 | ~800 | Day 7 |
| **Mixins** | 7 | ~750 | Day 3 |
| **Base Classes** | 4 | ~350 | Day 4-5 |
| **TOTAL NEW** | **33** | **~2,260** | **Week 1** |

**Archived:**
- Old base class protocols → `bases/protocols_old/`
- Old service interfaces → `realm/interfaces_old/`
- Old base classes → `*_old.py`

---

## ✅ SUCCESS CRITERIA

### **By End of Week 1:**

- [ ] All 5 base class protocols created (contracts only, no base classes)
- [ ] All 7 mixins created (each under 350 lines)
- [ ] All 4 base classes created (each under 110 lines)
- [ ] Service audit completed (what's implemented vs defined)
- [ ] Base service protocol created (standard methods)
- [ ] All 16 realm-specific service protocols created
- [ ] All old files archived (not deleted)
- [ ] All new protocols use REAL implementations (no placeholders)
- [ ] All base classes implement corresponding protocols
- [ ] Tests pass for each mixin independently

---

## 🚀 READY TO START?

### **Pre-Flight Checklist:**

- [ ] Team reviewed all 4 analysis documents:
  - `Base_Classes_And_Protocols_Refactoring_Analysis.md`
  - `Base_Refactoring_Visual_Guide.md`
  - `Service_Interface_To_Protocol_Migration_Analysis.md`
  - `ANSWERS_TO_CTO_QUESTIONS.md`

- [ ] Team approved:
  - ✅ Mixin pattern for base classes
  - ✅ Start fresh with base class protocols
  - ✅ Start fresh with service protocols
  - ✅ 7-day Week 1 plan

- [ ] Team understands:
  - **NO placeholders, stubs, or hardcoded cheats** (absolute rule)
  - **NO backwards compatibility** (clean slate, archive old code)
  - **350-line limit** enforced for all mixins and protocols
  - **Protocol hierarchy** eliminates duplication

---

## 📖 REFERENCE DOCUMENTS

1. **Base_Classes_And_Protocols_Refactoring_Analysis.md** (7,400 words)
   - Detailed analysis of base classes and protocols
   - Three options evaluated for each decision
   - Architectural recommendations

2. **Base_Refactoring_Visual_Guide.md** (4,800 words)
   - Before/After visual comparisons
   - Size reduction analysis
   - Transformation examples

3. **Service_Interface_To_Protocol_Migration_Analysis.md** (6,200 words)
   - Service-level interface analysis
   - ABC vs Protocol comparison
   - Migration strategy

4. **ANSWERS_TO_CTO_QUESTIONS.md** (4,800 words)
   - Direct answers to both questions
   - Updated 7-day Week 1 plan
   - Implementation requirements

5. **WEEK_1_COMPLETE_REFACTORING_PLAN.md** (This document)
   - Day-by-day breakdown
   - Deliverables checklist
   - Success criteria

---

## 💡 KEY PRINCIPLES

1. **Protocols = Contracts** (No implementations)
2. **Mixins = Focused Implementations** (One responsibility, <350 lines)
3. **Bases = Aggregators** (Compose mixins, <110 lines)
4. **No Placeholders** (All code must be working, real implementations)
5. **Start Fresh** (New architecture = new protocols, no legacy debt)
6. **Protocol Hierarchy** (Base protocol + realm-specific, eliminates duplication)

---

## 🎯 AFTER WEEK 1

You'll have a **clean foundation** for the remaining 11 weeks:
- ✅ All base classes simplified and composable
- ✅ All protocols aligned with new architecture
- ✅ Zero duplication across protocols
- ✅ Clear contracts for all services
- ✅ Independently testable components
- ✅ 350-line limit enforced throughout

**This foundation makes Weeks 2-12 much easier.**


