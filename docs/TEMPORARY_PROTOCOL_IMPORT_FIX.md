# Temporary Protocol Import Fix

**Date:** December 14, 2025  
**Status:** ⚠️ TEMPORARY FIX - To be resolved in Section 1.3

---

## Issue

The `business_specialist_agent_protocol` module is missing, causing orchestrator initialization to fail:

```
ModuleNotFoundError: No module named 'backend.business_enablement.protocols.business_specialist_agent_protocol'
```

This blocks ContentOrchestrator and InsightsOrchestrator from initializing.

---

## Temporary Solution

Made the `SpecialistCapability` import optional in:
1. **ContentOrchestrator** (`content_orchestrator.py` line 217)
2. **InsightsOrchestrator** (`insights_orchestrator.py` line 22)

### Changes Made

1. **InsightsOrchestrator**: Moved module-level import to conditional import with fallback enum
2. **ContentOrchestrator**: Made import conditional within the method, with `specialist_capability=None` fallback

### Code Pattern

```python
# ⚠️ TEMPORARY: Optional import for SpecialistCapability
# TODO (Section 1.3): Properly implement business_specialist_agent_protocol when overhauling agents
try:
    from backend.business_enablement.protocols.business_specialist_agent_protocol import SpecialistCapability
    specialist_capability = SpecialistCapability.CONTENT_PROCESSING
except ImportError:
    self.logger.warning("⚠️ business_specialist_agent_protocol not available - skipping specialist_capability")
    specialist_capability = None
```

---

## Resolution Plan (Section 1.3)

When overhauling agents for the Content Pillar in Section 1.3:

1. **Create/Implement Protocol Module**: 
   - Create `backend/business_enablement/protocols/business_specialist_agent_protocol.py`
   - Define `SpecialistCapability` enum properly
   - Define `BusinessSpecialistAgentBase` class

2. **Update Agent Implementations**:
   - Update ContentProcessingAgent to properly use the protocol
   - Update InsightsSpecialistAgent to properly use the protocol
   - Ensure all agents follow the protocol pattern

3. **Remove Temporary Fixes**:
   - Remove try/except blocks
   - Restore direct imports
   - Remove fallback enum definitions

4. **Test**:
   - Verify agents initialize correctly with protocol
   - Verify specialist capabilities are properly assigned
   - Verify agent functionality works as expected

---

## Files Modified

1. `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_orchestrator/content_orchestrator.py`
2. `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/insights_orchestrator.py`

---

## Impact

- ✅ Orchestrators can now initialize without the protocol module
- ✅ Agents will still be created, but without specialist_capability if protocol unavailable
- ⚠️ Agent functionality may be limited until protocol is properly implemented
- ⚠️ This is a temporary workaround - proper fix required in Section 1.3

---

## Related Documentation

- `BUSINESS_ENABLEMENT_VERTICAL_SLICE_IMPLEMENTATION_PLAN.md` - Section 1.3 (Agent Refactoring)
- `BUSINESS_ENABLEMENT_VERTICAL_SLICE_ARCHITECTURE_DESIGN.md` - Agent Architecture



