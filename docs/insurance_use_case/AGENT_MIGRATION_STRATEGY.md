# Agent Migration Strategy - Declarative Pattern

**Date:** 2025-12-05  
**Status:** 📋 **STRATEGY DEFINED**

---

## 🎯 Migration Goal

Migrate all agents from the old pattern to the new **declarative pattern** with:
- ✅ YAML-based configuration
- ✅ LLM-powered reasoning
- ✅ Production-ready features (retry, timeout, rate limiting, JSON parsing)
- ✅ Optional features (stateful, iterative, cost tracking)

---

## 📊 Agent Landscape Analysis

### **Agent Types:**

1. **Guide Agents** (Cross-Domain Navigation)
   - `GuideCrossDomainAgent` - Platform-level guide
   - `MVPGuideAgent` - MVP solution factory
   - **Pattern:** Stateless, routing-focused
   - **Complexity:** Medium

2. **Liaison Agents** (Domain-Specific Conversation)
   - `LiaisonDomainAgent` - Platform-level liaison
   - `InsuranceLiaisonAgent` - Insurance domain (already exists)
   - `MVPLiaisonAgents` - MVP solution factory
   - **Pattern:** Stateful/conversational, orchestrator coordination
   - **Complexity:** High

3. **Specialist Agents** (Capability Execution)
   - `SpecialistCapabilityAgent` - Platform-level specialist
   - 13 specialist implementations
   - **Pattern:** Stateless, task-focused
   - **Complexity:** Low to Medium

### **Specialist Agents (13 total):**

**Already Migrated:**
- ✅ `UniversalMapperSpecialist` (declarative version exists)

**To Migrate (12):**
1. `BusinessAnalysisSpecialist` - Business analysis
2. `RecommendationSpecialist` - Recommendations
3. `SOPGenerationSpecialist` - SOP generation
4. `WorkflowGenerationSpecialist` - Workflow generation
5. `CoexistenceBlueprintSpecialist` - Coexistence planning
6. `RoadmapProposalSpecialist` - Roadmap planning
7. `WavePlanningSpecialist` - Wave planning
8. `ChangeImpactAssessmentSpecialist` - Impact assessment
9. `RoutingDecisionSpecialist` - Routing decisions
10. `QualityRemediationSpecialist` - Quality remediation
11. `CoexistenceStrategySpecialist` - Coexistence strategy
12. `SagaWALManagementSpecialist` - Saga WAL management

---

## 🚀 Recommended Migration Strategy

### **Phase 1: Pattern Establishment (Week 1)**

**Goal:** Create migration patterns by migrating one of each type.

#### **1.1 Stateless Specialist (Simple)**
**Target:** `RecommendationSpecialist` or `RoutingDecisionSpecialist`
- **Why:** Simple, focused capability
- **Pattern:** Stateless, single-purpose
- **YAML Config:** Minimal (role, goal, tools)
- **Expected Time:** 2-3 hours

#### **1.2 Conversational/Liaison (Complex)**
**Target:** `InsuranceLiaisonAgent` (already exists, but migrate to declarative)
- **Why:** Already exists, good test case
- **Pattern:** Stateful, conversational, orchestrator coordination
- **YAML Config:** Full (stateful, conversation history, tools)
- **Expected Time:** 4-6 hours

#### **1.3 Guide Agent (Medium)**
**Target:** `MVPGuideAgent` or create declarative version
- **Why:** Cross-domain routing pattern
- **Pattern:** Stateless, routing-focused
- **YAML Config:** Medium (routing rules, liaison discovery)
- **Expected Time:** 3-4 hours

**Deliverables:**
- ✅ 3 migration patterns documented
- ✅ Migration templates/checklists
- ✅ Test patterns established
- ✅ Common issues identified and resolved

---

### **Phase 2: Specialist Migration (Week 2-3)**

**Goal:** Migrate remaining 11 specialist agents from least to most complex.

#### **Complexity Ranking (Low → High):**

**Low Complexity (2-3 hours each):**
1. `RoutingDecisionSpecialist` - Simple routing logic
2. `RecommendationSpecialist` - Recommendation generation
3. `QualityRemediationSpecialist` - Quality checks

**Medium Complexity (3-4 hours each):**
4. `BusinessAnalysisSpecialist` - Analysis with multiple tools
5. `SOPGenerationSpecialist` - Document generation
6. `WorkflowGenerationSpecialist` - Workflow creation
7. `ChangeImpactAssessmentSpecialist` - Impact analysis

**High Complexity (4-6 hours each):**
8. `WavePlanningSpecialist` - Complex planning logic
9. `CoexistenceBlueprintSpecialist` - Blueprint generation
10. `RoadmapProposalSpecialist` - Roadmap planning
11. `CoexistenceStrategySpecialist` - Strategy development
12. `SagaWALManagementSpecialist` - Saga management

**Migration Order:**
1. Start with low complexity (build confidence)
2. Move to medium complexity (refine patterns)
3. Finish with high complexity (apply all learnings)

**Deliverables:**
- ✅ All 12 specialist agents migrated
- ✅ YAML configs for all agents
- ✅ Tests for all agents
- ✅ Documentation updated

---

### **Phase 3: Guide & Liaison Migration (Week 4)**

**Goal:** Migrate guide and liaison agents.

#### **Guide Agents:**
- `GuideCrossDomainAgent` → Declarative version
- `MVPGuideAgent` → Declarative version

#### **Liaison Agents:**
- `LiaisonDomainAgent` → Declarative version
- `MVPLiaisonAgents` → Declarative version
- `InsuranceLiaisonAgent` → Already migrated in Phase 1

**Deliverables:**
- ✅ All guide agents migrated
- ✅ All liaison agents migrated
- ✅ Full test coverage

---

## 📋 Migration Checklist Template

For each agent migration:

### **Pre-Migration:**
- [ ] Analyze current agent implementation
- [ ] Identify domain methods (interface)
- [ ] List required tools/MCP servers
- [ ] Document current behavior/edge cases
- [ ] Review test coverage

### **Migration:**
- [ ] Create YAML config file
- [ ] Create declarative agent class (thin wrapper)
- [ ] Implement domain methods (call `process_request`)
- [ ] Preserve Priority 2 metadata in responses
- [ ] Update imports/exports

### **Post-Migration:**
- [ ] Run comprehensive tests
- [ ] Verify cost controls work
- [ ] Check production readiness features
- [ ] Update documentation
- [ ] Update orchestrator integration (if needed)

---

## 🎯 Migration Patterns

### **Pattern 1: Stateless Specialist**

**Template:**
```python
class MySpecialist(DeclarativeAgentBase):
    """My Specialist - Declarative Implementation."""
    
    async def my_domain_method(self, param1, param2, user_context=None):
        """Domain method implementation."""
        request = {
            "message": f"Do something with {param1} and {param2}",
            "task": "my_task",
            "data": {"param1": param1, "param2": param2},
            "user_context": user_context or {}
        }
        result = await self.process_request(request)
        
        # Extract and format response
        # Preserve Priority 2 metadata
        return formatted_response
```

**YAML Config:**
```yaml
agent_name: MySpecialist
role: Specialist Role
goal: Specialist Goal
backstory: Specialist backstory
stateful: false
iterative_execution: false
cost_tracking: true
```

---

### **Pattern 2: Stateful/Conversational Agent**

**Template:**
```python
class MyLiaisonAgent(DeclarativeAgentBase):
    """My Liaison Agent - Declarative Implementation."""
    
    async def handle_conversation(self, message, user_context=None):
        """Handle conversational request."""
        request = {
            "message": message,
            "task": "conversation",
            "user_context": user_context or {},
            "session_id": user_context.get("session_id") if user_context else None
        }
        result = await self.process_request(request)
        
        # Preserve conversation history metadata
        return result
```

**YAML Config:**
```yaml
agent_name: MyLiaisonAgent
role: Conversational Agent
goal: Provide conversational guidance
backstory: Conversational backstory
stateful: true
max_conversation_history: 20
iterative_execution: false
cost_tracking: true
```

---

### **Pattern 3: Iterative/Complex Agent**

**Template:**
```python
class MyComplexSpecialist(DeclarativeAgentBase):
    """My Complex Specialist - Declarative Implementation."""
    
    async def complex_task(self, input_data, user_context=None):
        """Complex task with multiple steps."""
        request = {
            "message": f"Perform complex task with {input_data}",
            "task": "complex_task",
            "data": {"input": input_data},
            "user_context": user_context or {}
        }
        result = await self.process_request(request)
        
        # Extract results from iterations
        return formatted_response
```

**YAML Config:**
```yaml
agent_name: MyComplexSpecialist
role: Complex Specialist
goal: Perform complex multi-step tasks
backstory: Complex specialist backstory
stateful: false
iterative_execution: true
max_iterations: 5
cost_tracking: true
```

---

## 📊 Migration Priority Matrix

| Agent | Type | Complexity | Priority | Estimated Time |
|-------|------|------------|----------|----------------|
| RecommendationSpecialist | Specialist | Low | High | 2-3h |
| RoutingDecisionSpecialist | Specialist | Low | High | 2-3h |
| InsuranceLiaisonAgent | Liaison | High | High | 4-6h |
| MVPGuideAgent | Guide | Medium | High | 3-4h |
| QualityRemediationSpecialist | Specialist | Low | Medium | 2-3h |
| BusinessAnalysisSpecialist | Specialist | Medium | Medium | 3-4h |
| SOPGenerationSpecialist | Specialist | Medium | Medium | 3-4h |
| WorkflowGenerationSpecialist | Specialist | Medium | Medium | 3-4h |
| ChangeImpactAssessmentSpecialist | Specialist | Medium | Medium | 3-4h |
| WavePlanningSpecialist | Specialist | High | Medium | 4-6h |
| CoexistenceBlueprintSpecialist | Specialist | High | Low | 4-6h |
| RoadmapProposalSpecialist | Specialist | High | Low | 4-6h |
| CoexistenceStrategySpecialist | Specialist | High | Low | 4-6h |
| SagaWALManagementSpecialist | Specialist | High | Low | 4-6h |
| GuideCrossDomainAgent | Guide | Medium | Medium | 3-4h |
| LiaisonDomainAgent | Liaison | High | Medium | 4-6h |

**Total Estimated Time:** ~60-80 hours

---

## 🎯 Recommended Approach

### **Option A: Your Suggested Approach (RECOMMENDED)**
1. **Phase 1:** Migrate one of each type (stateless specialist, conversational liaison, guide)
2. **Phase 2:** Migrate remaining specialists from least to most complex
3. **Phase 3:** Migrate remaining guide/liaison agents

**Pros:**
- ✅ Establishes patterns early
- ✅ Builds confidence incrementally
- ✅ Identifies issues early
- ✅ Creates reusable templates

**Cons:**
- ⚠️ Takes longer to get full coverage
- ⚠️ Some agents wait longer

---

### **Option B: All Specialists First**
1. **Phase 1:** Migrate all 12 specialists (low → high complexity)
2. **Phase 2:** Migrate guide/liaison agents

**Pros:**
- ✅ Faster specialist coverage
- ✅ Consistent pattern (all specialists similar)

**Cons:**
- ⚠️ May miss patterns for guide/liaison
- ⚠️ Less variety early on

---

### **Option C: By Business Priority**
1. **Phase 1:** Migrate high-business-value agents first
2. **Phase 2:** Migrate remaining agents

**Pros:**
- ✅ Business value delivered faster
- ✅ Production impact sooner

**Cons:**
- ⚠️ May start with complex agents
- ⚠️ Patterns emerge later

---

## ✅ Recommendation: **Option A (Your Approach)**

**Rationale:**
1. **Pattern Establishment:** Starting with one of each type creates comprehensive patterns
2. **Risk Mitigation:** Identifies issues across all patterns early
3. **Confidence Building:** Success with diverse agents builds confidence
4. **Template Creation:** Creates reusable templates for each type
5. **Incremental Progress:** Clear milestones and deliverables

---

## 📝 Next Steps

1. **Select Phase 1 Agents:**
   - Stateless Specialist: `RecommendationSpecialist` or `RoutingDecisionSpecialist`
   - Conversational/Liaison: `InsuranceLiaisonAgent` (migrate to declarative)
   - Guide: `MVPGuideAgent` or create declarative version

2. **Create Migration Templates:**
   - Stateless specialist template
   - Stateful/conversational template
   - Guide agent template

3. **Set Up Migration Tracking:**
   - Create migration status document
   - Track progress per agent
   - Document learnings/issues

4. **Begin Phase 1:**
   - Start with simplest (stateless specialist)
   - Then conversational
   - Finally guide

---

## 🎉 Success Criteria

**Phase 1 Complete When:**
- ✅ 3 agents migrated (one of each type)
- ✅ Patterns documented
- ✅ Templates created
- ✅ Tests passing (100%)
- ✅ Cost controls verified

**Full Migration Complete When:**
- ✅ All agents migrated
- ✅ All tests passing
- ✅ All YAML configs created
- ✅ Documentation updated
- ✅ Production deployment ready

---

## 💡 Tips for Success

1. **Start Simple:** Begin with lowest complexity agents
2. **Test Early:** Run tests after each migration
3. **Document Learnings:** Capture patterns and issues
4. **Reuse Templates:** Use established patterns
5. **Verify Cost Controls:** Ensure cost controls work for each agent
6. **Preserve Metadata:** Always preserve Priority 2 metadata in responses

---

## 🚀 Ready to Begin?

**Recommended First Agent:** `RecommendationSpecialist` or `RoutingDecisionSpecialist`

**Why:**
- Simple, focused capability
- Stateless pattern (easiest)
- Good test case for pattern establishment
- Quick win (2-3 hours)

**Would you like to:**
1. Start with `RecommendationSpecialist` migration?
2. Review the current implementation first?
3. Create the migration template together?







