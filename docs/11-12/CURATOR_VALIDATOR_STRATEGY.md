# Curator Foundation Validator Strategy

**Date:** December 19, 2024  
**Purpose:** Determine what Curator Foundation validator should enforce and on which layers

---

## 🎯 CURATOR FOUNDATION'S ROLE

Curator Foundation provides:
1. **Service Registration** - Services register capabilities with Curator
2. **Service Discovery** - Services discover other services via Curator
3. **Capability Registry** - Central registry of service capabilities
4. **Pattern Validation** - Architectural pattern enforcement
5. **Anti-Pattern Detection** - Code scanning and violation tracking

---

## 📊 CURRENT USAGE PATTERNS

### **Realm Services (Business Enablement, Journey, Solution)**
- ✅ **MUST** register with Curator via `register_with_curator()`
- ✅ **MUST** use Curator for service discovery
- ✅ **MUST** register capabilities with Curator
- **Pattern**: `RealmServiceBase` provides `register_with_curator()` helper

**Examples**:
- `FileParserService` - Registers with Curator
- `ContentAnalysisOrchestrator` - Registers with Curator
- `OperationsOrchestrator` - Registers with Curator

### **Foundation Services (Communication, Agentic, Experience)**
- ⚠️ **CAN** use Curator (optional)
- ⚠️ **MAY** register with Curator
- **Pattern**: Foundation services are peers - they can use Curator but don't have to

**Examples**:
- `AgenticFoundationService` - Registers agents with Curator (optional)
- `ToolRegistryService` - Registers tools with Curator (optional)

### **Smart City Services**
- ❓ **SHOULD** register with Curator (for service discovery)
- ❓ **SHOULD** use Curator for capability registry
- **Pattern**: Smart City services are first-class citizens - they might use Curator differently

---

## 💡 RECOMMENDATION

### **Curator Validator Should Focus on Realm Services**

**Why:**
1. **Realm Services** are the primary consumers of Curator
2. **Realm Services** have a standardized pattern (`register_with_curator()`)
3. **Realm Services** MUST use Curator for service discovery
4. **Foundation Services** are peers - optional usage is acceptable

### **What Curator Validator Should Check**

#### **For Realm Services (REQUIRED)**
1. ✅ **Service Registration** - Must call `register_with_curator()` during initialization
2. ✅ **Service Discovery** - Must use Curator for service discovery (not direct access)
3. ✅ **Capability Registration** - Must register capabilities with Curator
4. ❌ **No Bypassing** - Must not bypass Curator for service discovery

#### **For Foundation Services (OPTIONAL)**
1. ⚠️ **Can Use Curator** - Foundation services can use Curator (not required)
2. ⚠️ **No Violations** - Foundation services don't violate if they don't use Curator

#### **For Smart City Services (SHOULD)**
1. ⚠️ **Should Register** - Smart City services should register with Curator
2. ⚠️ **Should Use Discovery** - Smart City services should use Curator for discovery
3. ⚠️ **May Have Direct Access** - Smart City services can access Public Works directly (they're first-class)

---

## 🎯 PROPOSED VALIDATOR SCOPE

### **Option A: Realm Services Only (RECOMMENDED)**
**Focus**: Validate that realm services use Curator properly

**Checks**:
- Realm services call `register_with_curator()` during initialization
- Realm services use Curator for service discovery
- Realm services don't bypass Curator

**Pros**:
- Clear scope
- Enforces critical pattern
- Focused on where it matters most

**Cons**:
- Doesn't validate foundation services (but they're optional)

### **Option B: All Services (COMPREHENSIVE)**
**Focus**: Validate all services use Curator (with different rules per layer)

**Checks**:
- Realm services: MUST use Curator
- Foundation services: CAN use Curator (no violations if they don't)
- Smart City services: SHOULD use Curator (warnings, not errors)

**Pros**:
- Comprehensive coverage
- Catches all usage patterns

**Cons**:
- More complex
- Foundation services are peers - less critical

---

## ✅ RECOMMENDED APPROACH

### **Create Curator Validator for Realm Services**

**Scope**: Validate realm services (Business Enablement, Journey, Solution)

**What to Check**:
1. ✅ Realm services call `register_with_curator()` during initialization
2. ✅ Realm services use Curator for service discovery (not direct service access)
3. ✅ Realm services register capabilities with Curator
4. ❌ Realm services don't bypass Curator

**When to Run**:
- On realm services (Business Enablement, Journey, Solution)
- After Curator Foundation tests
- Before moving to higher layers

**Foundation Services**:
- Don't require Curator validator (they're peers)
- Can use Curator optionally
- No violations if they don't use Curator

---

## 📋 IMPLEMENTATION PLAN

### **Step 1: Create Curator Validator**
- Focus on realm services
- Check for `register_with_curator()` calls
- Check for Curator usage patterns
- Check for bypassing Curator

### **Step 2: Test on Existing Realm Services**
- Run on Business Enablement services
- Identify violations
- Fix violations

### **Step 3: Integrate into Test Suite**
- Add validator compliance tests
- Run as part of realm service tests

---

## 🎯 DECISION POINT

**Question**: Should Curator validator apply to:
- **A) Realm Services Only** (Recommended)
- **B) All Services** (Comprehensive)

**My Recommendation**: **Option A - Realm Services Only**

**Reasoning**:
1. Realm services are the primary consumers
2. Foundation services are peers - optional usage is fine
3. Clearer scope and easier to maintain
4. Focuses on where it matters most

---

## 📝 NOTES

### **Foundation Services as Peers**
Foundation services (Communication, Agentic, Experience) are peers to Curator Foundation. They:
- Can use Curator (like Agentic does)
- Don't have to use Curator
- Are at the same architectural layer

### **Realm Services as Consumers**
Realm services (Business Enablement, Journey, Solution) are consumers of Curator Foundation. They:
- MUST use Curator for service discovery
- MUST register with Curator
- Are at a higher architectural layer

### **Smart City Services**
Smart City services are first-class citizens. They:
- Can access Public Works directly
- Should register with Curator (for discovery)
- May have different patterns

---

## 🎉 SUMMARY

**Recommended Approach**: Create Curator validator that focuses on **Realm Services Only**

**Rationale**:
- Realm services are the primary consumers
- Foundation services are peers (optional usage)
- Clearer scope and easier to maintain

**Next Step**: Create Curator validator for realm services, then proceed to Communication Foundation tests.


