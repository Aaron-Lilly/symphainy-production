# Agent Folder Structure Recommendation

**Date:** 2025-12-06  
**Status:** 📋 **RECOMMENDATION**

---

## 🎯 Decision: **Option 1 - Flat Structure (Recommended)**

### **Rationale:**

1. **Declarative Pattern Alignment:**
   - Patterns (stateless/stateful/iterative) are **behavioral**, defined in YAML configs
   - Folder structure should reflect **what** the agent is (Guide, Liaison, Specialist), not **how** it behaves
   - YAML configs in `configs/` folder already document patterns

2. **Import Simplicity:**
   - Flat structure = simple imports: `from agents.insurance_liaison_agent import InsuranceLiaisonAgent`
   - No nested path confusion
   - Matches enabling services pattern (proven good pattern)

3. **Scalability:**
   - Even with 20-30 agents, flat structure is manageable
   - Configs are in separate `configs/` folder
   - Easy to find agents by name (alphabetical)

4. **Consistency:**
   - Matches enabling services pattern
   - Consistent with platform architecture
   - No special cases or exceptions

5. **Developer Experience:**
   - Simple mental model: "agents are in the agents folder"
   - No need to remember which pattern folder
   - Pattern is visible in YAML config, not folder structure

---

## 📁 Recommended Structure

```
agents/
├── __init__.py                          # All agent exports
├── declarative_agent_base.py            # Base class for declarative agents
├── guide_cross_domain_agent.py         # Base guide agent (declarative)
├── liaison_domain_agent.py              # Base liaison agent
├── specialist_capability_agent.py       # Base specialist agent
├── mvp_guide_agent.py                   # MVP solution factory
├── mvp_liaison_agents.py                # MVP liaison factory
├── mvp_specialist_agents.py             # MVP specialist factory
├── insurance_liaison_agent.py           # Insurance liaison (declarative)
├── business_analysis_specialist.py      # Specialist agents (all in flat structure)
├── recommendation_specialist.py         # (declarative)
├── universal_mapper_specialist.py       # (declarative)
├── ... (other specialists)
├── configs/                            # YAML configs (pattern documentation)
│   ├── insurance_liaison_agent.yaml
│   ├── mvp_guide_agent.yaml
│   ├── recommendation_specialist.yaml
│   └── universal_mapper_specialist.yaml
└── archive/                             # Legacy implementations
    ├── insurance_liaison_agent_legacy.py
    ├── guide_cross_domain_agent_legacy.py
    └── ...
```

---

## ❌ Why NOT Pattern-Based Folders (Option 2)

### **Issues:**

1. **Patterns are Behavioral, Not Structural:**
   - An agent's pattern (stateless/stateful/iterative) can change via YAML config
   - Would require moving files if pattern changes
   - Pattern is already documented in YAML

2. **Import Complexity:**
   - `from agents.stateful.insurance_liaison_agent import InsuranceLiaisonAgent`
   - More verbose than flat structure
   - Path confusion (which folder is it in?)

3. **Multi-Pattern Agents:**
   - Some agents might be stateful AND iterative
   - Which folder do they go in?
   - Creates ambiguity

4. **Doesn't Match Platform Patterns:**
   - Enabling services are flat
   - Other platform components are flat
   - Creates inconsistency

---

## ✅ Benefits of Flat Structure

1. **Simple Imports:**
   ```python
   from backend.business_enablement.agents.insurance_liaison_agent import InsuranceLiaisonAgent
   ```

2. **Easy Discovery:**
   - All agents in one place
   - Alphabetical listing
   - No need to know pattern to find agent

3. **YAML Configs Document Patterns:**
   ```yaml
   # configs/insurance_liaison_agent.yaml
   stateful: true
   iterative_execution: false
   ```

4. **Consistent with Platform:**
   - Matches enabling services pattern
   - Matches other platform components
   - No special cases

---

## 🚀 Implementation Plan

1. **Phase 1:** Archive old agents, rename declarative versions
2. **Phase 2:** Move all agents from `specialists/` to `agents/` (flat structure)
3. **Phase 3:** Update all imports
4. **Phase 4:** Remove `specialists/` folder
5. **Phase 5:** Test and verify

---

## 📝 Migration Notes

- **Keep `specialists/` folder temporarily** during migration for safety
- **Update imports gradually** to avoid breaking changes
- **Test after each phase** to ensure nothing breaks
- **Document pattern in YAML** (already done)

---

## ✅ Conclusion

**Recommendation: Adopt flat structure (Option 1)**

- Simpler imports
- Better alignment with declarative pattern
- Consistent with platform architecture
- Patterns documented in YAML configs (not folder structure)
- Easier to maintain and discover







