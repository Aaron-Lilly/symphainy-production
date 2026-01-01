# Agent Migration Cleanup Plan

**Date:** 2025-12-06  
**Status:** 📋 **PLAN CREATED**

---

## 🎯 Goals

1. **Archive old agent implementations** and properly name new declarative versions
2. **Recommend folder structure** for better organization

---

## 📊 Current State Analysis

### **Parallel Implementations Found:**

1. **Insurance Liaison Agent:**
   - `insurance_liaison_agent.py` (old)
   - `insurance_liaison_agent_declarative.py` (new)

2. **Guide Cross-Domain Agent:**
   - `guide_cross_domain_agent.py` (old)
   - `guide_cross_domain_agent_declarative.py` (new)

3. **Recommendation Specialist:**
   - `specialists/recommendation_specialist.py` (old)
   - `specialists/recommendation_specialist_declarative.py` (new)

4. **Universal Mapper Specialist:**
   - `specialists/universal_mapper_specialist.py` (old)
   - `specialists/universal_mapper_specialist_declarative.py` (new)

### **Import Dependencies:**
- `insurance_migration_orchestrator.py` imports `InsuranceLiaisonAgent`
- `test_stateful_conversational_pattern.py` imports from `_declarative`
- `agents/__init__.py` has try/except fallback pattern
- `specialists/__init__.py` has try/except fallback pattern

---

## 🔧 Migration Process

### **Step 1: Archive Old Agents**

Move old implementations to `archive/` folder:

```bash
# Insurance Liaison Agent
mv agents/insurance_liaison_agent.py agents/archive/insurance_liaison_agent_legacy.py

# Guide Cross-Domain Agent
mv agents/guide_cross_domain_agent.py agents/archive/guide_cross_domain_agent_legacy.py

# Recommendation Specialist
mv agents/specialists/recommendation_specialist.py agents/archive/recommendation_specialist_legacy.py

# Universal Mapper Specialist
mv agents/specialists/universal_mapper_specialist.py agents/archive/universal_mapper_specialist_legacy.py
```

### **Step 2: Rename Declarative Agents**

Remove `_declarative` suffix from new implementations:

```bash
# Insurance Liaison Agent
mv agents/insurance_liaison_agent_declarative.py agents/insurance_liaison_agent.py

# Guide Cross-Domain Agent
mv agents/guide_cross_domain_agent_declarative.py agents/guide_cross_domain_agent.py

# Recommendation Specialist
mv agents/specialists/recommendation_specialist_declarative.py agents/specialists/recommendation_specialist.py

# Universal Mapper Specialist
mv agents/specialists/universal_mapper_specialist_declarative.py agents/specialists/universal_mapper_specialist.py
```

### **Step 3: Update Imports**

Update all import statements to remove `_declarative` references:

1. **`agents/__init__.py`:**
   - Remove try/except fallback
   - Direct import: `from .insurance_liaison_agent import InsuranceLiaisonAgent`

2. **`specialists/__init__.py`:**
   - Remove try/except fallback
   - Direct import: `from .recommendation_specialist import RecommendationSpecialist`
   - Direct import: `from .universal_mapper_specialist import UniversalMapperSpecialist`

3. **Test scripts:**
   - Update imports to remove `_declarative` suffix

4. **Orchestrator imports:**
   - Already using direct import (no change needed)

---

## 📁 Folder Structure Recommendation

### **Option 1: Flat Structure (Recommended)**

**Structure:**
```
agents/
├── __init__.py
├── declarative_agent_base.py
├── guide_cross_domain_agent.py
├── liaison_domain_agent.py
├── specialist_capability_agent.py
├── mvp_guide_agent.py
├── mvp_liaison_agents.py
├── mvp_specialist_agents.py
├── insurance_liaison_agent.py
├── configs/
│   ├── insurance_liaison_agent.yaml
│   ├── mvp_guide_agent.yaml
│   ├── recommendation_specialist.yaml
│   └── universal_mapper_specialist.yaml
└── archive/
    ├── insurance_liaison_agent_legacy.py
    ├── guide_cross_domain_agent_legacy.py
    └── ...
```

**Pros:**
- ✅ Simple imports (no nested paths)
- ✅ Easy to find agents
- ✅ Matches enabling services pattern
- ✅ No path confusion
- ✅ Works well with declarative pattern (YAML configs separate)

**Cons:**
- ❌ All agents in one folder (could get large)
- ❌ No visual grouping by pattern

---

### **Option 2: Pattern-Based Folders**

**Structure:**
```
agents/
├── __init__.py
├── declarative_agent_base.py
├── base/
│   ├── guide_cross_domain_agent.py
│   ├── liaison_domain_agent.py
│   └── specialist_capability_agent.py
├── stateless/
│   ├── recommendation_specialist.py
│   └── ...
├── stateful/
│   ├── insurance_liaison_agent.py
│   ├── mvp_guide_agent.py
│   └── ...
├── iterative/
│   ├── universal_mapper_specialist.py
│   └── ...
├── configs/
│   └── ...
└── archive/
    └── ...
```

**Pros:**
- ✅ Clear pattern organization
- ✅ Easy to find agents by behavior
- ✅ Developer-friendly (knows where to look)

**Cons:**
- ❌ More complex imports (`from agents.stateful.insurance_liaison_agent import ...`)
- ❌ Path confusion (agents can be in multiple categories)
- ❌ Agents might need to move folders if pattern changes
- ❌ Doesn't match enabling services pattern

---

### **Option 3: Type-Based Folders (Hybrid)**

**Structure:**
```
agents/
├── __init__.py
├── declarative_agent_base.py
├── guides/
│   ├── guide_cross_domain_agent.py
│   └── mvp_guide_agent.py
├── liaisons/
│   ├── liaison_domain_agent.py
│   ├── insurance_liaison_agent.py
│   └── mvp_liaison_agents.py
├── specialists/
│   ├── specialist_capability_agent.py
│   ├── recommendation_specialist.py
│   ├── universal_mapper_specialist.py
│   └── ...
├── configs/
│   └── ...
└── archive/
    └── ...
```

**Pros:**
- ✅ Clear agent type organization
- ✅ Matches current structure (specialists folder exists)
- ✅ Logical grouping (Guide, Liaison, Specialist)

**Cons:**
- ❌ Still has nested imports
- ❌ "Specialist" isn't really a type (it's a capability pattern)
- ❌ Doesn't align with declarative pattern (patterns are behavioral, not structural)

---

## 🎯 **Recommendation: Option 1 (Flat Structure)**

### **Rationale:**

1. **Declarative Pattern Alignment:**
   - With declarative agents, the pattern (stateless/stateful/iterative) is in the YAML config, not the folder structure
   - The folder structure should reflect **what** the agent is (Guide, Liaison, Specialist), not **how** it behaves (stateless, stateful, iterative)

2. **Import Simplicity:**
   - Flat structure = simple imports
   - No nested path confusion
   - Matches enabling services pattern (which we've established as a good pattern)

3. **Scalability:**
   - Even with 20-30 agents, a flat structure is manageable
   - Configs are in separate `configs/` folder
   - Easy to find agents by name

4. **Consistency:**
   - Matches enabling services pattern
   - Consistent with platform architecture
   - No special cases

### **Implementation:**

1. **Keep flat structure** in `agents/` folder
2. **Remove `specialists/` folder** and move all agents to `agents/`
3. **Update imports** to reflect flat structure
4. **Use YAML configs** to document patterns (stateless/stateful/iterative)

### **Naming Convention:**

- **Base agents:** `guide_cross_domain_agent.py`, `liaison_domain_agent.py`, `specialist_capability_agent.py`
- **Solution factories:** `mvp_guide_agent.py`, `mvp_liaison_agents.py`, `mvp_specialist_agents.py`
- **Specific agents:** `insurance_liaison_agent.py`, `recommendation_specialist.py`, `universal_mapper_specialist.py`

---

## 📋 Migration Checklist

### **Phase 1: Archive and Rename**
- [ ] Archive `insurance_liaison_agent.py` → `archive/insurance_liaison_agent_legacy.py`
- [ ] Rename `insurance_liaison_agent_declarative.py` → `insurance_liaison_agent.py`
- [ ] Archive `guide_cross_domain_agent.py` → `archive/guide_cross_domain_agent_legacy.py`
- [ ] Rename `guide_cross_domain_agent_declarative.py` → `guide_cross_domain_agent.py`
- [ ] Archive `specialists/recommendation_specialist.py` → `archive/recommendation_specialist_legacy.py`
- [ ] Rename `specialists/recommendation_specialist_declarative.py` → `specialists/recommendation_specialist.py`
- [ ] Archive `specialists/universal_mapper_specialist.py` → `archive/universal_mapper_specialist_legacy.py`
- [ ] Rename `specialists/universal_mapper_specialist_declarative.py` → `specialists/universal_mapper_specialist.py`

### **Phase 2: Update Imports**
- [ ] Update `agents/__init__.py` (remove try/except fallback)
- [ ] Update `specialists/__init__.py` (remove try/except fallback)
- [ ] Update test scripts
- [ ] Verify orchestrator imports (should already work)

### **Phase 3: Folder Structure (Optional)**
- [ ] If adopting flat structure: Move all agents from `specialists/` to `agents/`
- [ ] Update all imports
- [ ] Remove `specialists/` folder
- [ ] Update documentation

---

## ⚠️ **Important Notes**

1. **Test Before Migration:**
   - Run all tests to ensure nothing breaks
   - Verify imports work correctly
   - Check orchestrator integration

2. **Gradual Migration:**
   - Can do archive/rename first
   - Folder structure change can be separate step
   - Allows for testing at each stage

3. **Documentation:**
   - Update any documentation referencing `_declarative` files
   - Update migration guides
   - Update test scripts

---

## 🚀 Next Steps

1. **Review and approve** folder structure recommendation
2. **Execute Phase 1** (archive and rename)
3. **Execute Phase 2** (update imports)
4. **Test thoroughly**
5. **Execute Phase 3** (folder structure) if approved







