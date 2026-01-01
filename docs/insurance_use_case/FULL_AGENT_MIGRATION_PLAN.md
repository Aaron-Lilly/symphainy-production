# Full Agent Migration Plan

**Date:** 2025-12-06  
**Status:** ⏳ **IN PROGRESS**

---

## 🎯 Objective

Migrate all remaining archived agents to the declarative pattern, using the 4 established patterns as templates.

---

## 📋 Migration Priority

### **High Priority (1 agent)**
1. ✅ **WavePlanningSpecialist** - Used by Wave Orchestrator

### **Medium Priority (3 agents)**
2. ⏳ **QualityRemediationSpecialist** - Used by Insurance Migration Orchestrator
3. ⏳ **RoutingDecisionSpecialist** - Used by Insurance Migration Orchestrator
4. ⏳ **ChangeImpactAssessmentSpecialist** - Used by Insurance Migration Orchestrator

### **Low Priority (7 agents)**
5. ⏳ **BusinessAnalysisSpecialist**
6. ⏳ **SOPGenerationSpecialist**
7. ⏳ **WorkflowGenerationSpecialist**
8. ⏳ **CoexistenceBlueprintSpecialist**
9. ⏳ **RoadmapProposalSpecialist**
10. ⏳ **CoexistenceStrategySpecialist**
11. ⏳ **SagaWALManagementSpecialist**

---

## 🔄 Migration Process

For each agent:

1. **Analyze archived agent:**
   - Identify main methods
   - Determine pattern (Stateless, Stateful, Iterative, Guide)
   - Identify required tools/MCP servers

2. **Create YAML config:**
   - Copy from similar agent template
   - Update agent_name, role, goal, backstory
   - Configure pattern (stateful, iterative_execution)
   - List allowed_tools and allowed_mcp_servers
   - Add instructions

3. **Create declarative Python implementation:**
   - Copy from similar agent template
   - Update class name and config path
   - Implement domain methods (call process_request)
   - Extract results from LLM response
   - Preserve Priority 2 metadata

4. **Update imports:**
   - Update `agents/__init__.py`
   - Update orchestrator imports
   - Remove TODO comments

5. **Test:**
   - Run pattern-specific test
   - Verify functionality
   - Check cost tracking

---

## 📊 Pattern Mapping

| Agent | Pattern | Template | Notes |
|-------|---------|----------|-------|
| WavePlanningSpecialist | Iterative | UniversalMapperSpecialist | Complex analysis with multiple steps |
| QualityRemediationSpecialist | Stateless | RecommendationSpecialist | Single-pass analysis |
| RoutingDecisionSpecialist | Stateless | RecommendationSpecialist | Single-pass decision |
| ChangeImpactAssessmentSpecialist | Iterative | UniversalMapperSpecialist | Complex impact analysis |
| BusinessAnalysisSpecialist | Stateless | RecommendationSpecialist | Single-pass analysis |
| SOPGenerationSpecialist | Iterative | UniversalMapperSpecialist | Multi-step generation |
| WorkflowGenerationSpecialist | Iterative | UniversalMapperSpecialist | Multi-step generation |
| CoexistenceBlueprintSpecialist | Iterative | UniversalMapperSpecialist | Complex blueprint generation |
| RoadmapProposalSpecialist | Iterative | UniversalMapperSpecialist | Complex roadmap generation |
| CoexistenceStrategySpecialist | Stateless | RecommendationSpecialist | Single-pass strategy |
| SagaWALManagementSpecialist | Stateless | RecommendationSpecialist | Single-pass management |

---

## 🚀 Migration Order

1. **WavePlanningSpecialist** (High Priority)
2. **QualityRemediationSpecialist** (Medium Priority)
3. **RoutingDecisionSpecialist** (Medium Priority)
4. **ChangeImpactAssessmentSpecialist** (Medium Priority)
5. **BusinessAnalysisSpecialist** (Low Priority)
6. **SOPGenerationSpecialist** (Low Priority)
7. **WorkflowGenerationSpecialist** (Low Priority)
8. **CoexistenceBlueprintSpecialist** (Low Priority)
9. **RoadmapProposalSpecialist** (Low Priority)
10. **CoexistenceStrategySpecialist** (Low Priority)
11. **SagaWALManagementSpecialist** (Low Priority)

---

## ✅ Success Criteria

For each migrated agent:
- ✅ YAML config created and valid
- ✅ Python implementation created
- ✅ Inherits from DeclarativeAgentBase
- ✅ Uses absolute imports
- ✅ Implements domain methods
- ✅ Preserves Priority 2 metadata
- ✅ Imports updated
- ✅ Orchestrator imports fixed
- ✅ Test passes (if test exists)

---

## 📝 Notes

- Use established patterns as templates
- All agents use absolute imports
- All agents preserve Priority 2 metadata
- All agents maintain interface compatibility
- Config paths: `Path(__file__).parent / "configs" / "{agent_name}.yaml"`







