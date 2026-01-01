# Agent Migration Status

**Date:** 2025-12-06  
**Status:** 🔄 **IN PROGRESS**

---

## ⚠️ Issue Discovered

The declarative agent files (`*_declarative.py`) were accidentally deleted during the rename operation. They need to be recreated before completing the migration.

---

## ✅ Completed Steps

1. ✅ **Old agents archived** to `archive/` folder:
   - `insurance_liaison_agent_legacy.py`
   - `guide_cross_domain_agent_legacy.py`
   - `recommendation_specialist_legacy.py`
   - `universal_mapper_specialist_legacy.py`

---

## ⏳ Pending Steps

1. **Recreate declarative files** (they were deleted during rename):
   - `insurance_liaison_agent_declarative.py`
   - `guide_cross_domain_agent_declarative.py`
   - `specialists/recommendation_specialist_declarative.py`
   - `specialists/universal_mapper_specialist_declarative.py`

2. **Rename declarative files** (remove `_declarative` suffix):
   - `insurance_liaison_agent_declarative.py` → `insurance_liaison_agent.py`
   - `guide_cross_domain_agent_declarative.py` → `guide_cross_domain_agent.py`
   - `specialists/recommendation_specialist_declarative.py` → `specialists/recommendation_specialist.py`
   - `specialists/universal_mapper_specialist_declarative.py` → `specialists/universal_mapper_specialist.py`

3. **Move to flat structure**:
   - Move all agents from `specialists/` to `agents/`
   - Update all imports
   - Remove `specialists/` folder

4. **Update imports**:
   - Remove try/except fallbacks from `__init__.py` files
   - Update test scripts
   - Update orchestrator imports

---

## 📋 Next Actions

1. Recreate declarative files from pattern templates
2. Complete rename operation
3. Move to flat structure
4. Update all imports
5. Test thoroughly

---

## 🔍 Files to Recreate

Based on the pattern templates and documentation:

1. **`insurance_liaison_agent_declarative.py`** - Stateful Conversational Pattern
2. **`guide_cross_domain_agent_declarative.py`** - Guide Agent Pattern  
3. **`specialists/recommendation_specialist_declarative.py`** - Stateless Specialist Pattern
4. **`specialists/universal_mapper_specialist_declarative.py`** - Iterative Specialist Pattern

All files should:
- Inherit from `DeclarativeAgentBase`
- Use absolute imports (not relative)
- Load config from `configs/` folder
- Preserve Priority 2 metadata
- Maintain interface compatibility







