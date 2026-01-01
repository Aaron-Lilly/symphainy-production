# Agentic Overhaul Roadmap

**Date:** December 2024  
**Status:** 📋 **COMPREHENSIVE ROADMAP CREATED**  
**Scope:** All Agents (Insurance Use Case + MVP Pre-Existing)

---

## 🎯 Executive Summary

**Problem:** Agents receive LLM infrastructure but use placeholders, fallbacks, and mock implementations instead of actual LLM calls.

**Solution:** Overhaul all agents to use `self.llm_abstraction` directly (no fallbacks) and implement real agentic functionality via MCP tools.

**Impact:** 
- **Insurance Use Case Agents:** 8 specialist agents + 1 liaison agent
- **MVP Pre-Existing Agents:** 6 specialist agents + 4 liaison agents + 1 guide agent + 3 orchestrator agents
- **Total:** 23 agents requiring fixes

---

## 📊 Agent Inventory & Anti-Pattern Analysis

### **Insurance Use Case Agents (9 agents)**

| Agent | Base Class | Anti-Patterns | Priority |
|-------|-----------|---------------|----------|
| `UniversalMapperSpecialist` | `SpecialistCapabilityAgent` | Semantic similarity placeholder | High |
| `QualityRemediationSpecialist` | `SpecialistCapabilityAgent` | None (uses heuristics correctly) | Medium |
| `RoutingDecisionSpecialist` | `SpecialistCapabilityAgent` | Reasoning generation placeholder | High |
| `WavePlanningSpecialist` | `SpecialistCapabilityAgent` | Planning logic placeholder | High |
| `ChangeImpactAssessmentSpecialist` | `SpecialistCapabilityAgent` | Impact analysis placeholder | Medium |
| `CoexistenceStrategySpecialist` | `SpecialistCapabilityAgent` | Strategy analysis placeholder | Medium |
| `SagaWALManagementSpecialist` | `SpecialistCapabilityAgent` | Time calculation placeholder | Low |
| `SpecialistCapabilityAgent` (base) | `DimensionSpecialistAgent` | `_enhance_with_ai()` placeholder, `_call_enabling_service()` placeholder, `_gather_requirements()` placeholder | **CRITICAL** |
| `InsuranceLiaisonAgent` | `LiaisonDomainAgent` | MCP tool execution placeholder | High |
| `LiaisonDomainAgent` (base) | `DimensionLiaisonAgent` | `_handle_with_mcp_tools()` placeholder | **CRITICAL** |

### **MVP Pre-Existing Agents (14 agents)**

| Agent | Base Class | Anti-Patterns | Priority |
|-------|-----------|---------------|----------|
| `BusinessAnalysisSpecialist` | `SpecialistCapabilityAgent` | 6 placeholders (insights, patterns, risks, opportunities) | High |
| `RecommendationSpecialist` | `SpecialistCapabilityAgent` | 4 placeholders (strategic thinking, priority, impact, implementation) | High |
| `SOPGenerationSpecialist` | `SpecialistCapabilityAgent` | Content enhancement placeholder | Medium |
| `WorkflowGenerationSpecialist` | `SpecialistCapabilityAgent` | Workflow generation placeholder | Medium |
| `CoexistenceBlueprintSpecialist` | `SpecialistCapabilityAgent` | Blueprint generation placeholder | Medium |
| `RoadmapProposalSpecialist` | `SpecialistCapabilityAgent` | Roadmap generation placeholder | Medium |
| `InsightsAnalysisAgent` | `AgentBase` | 4 "Mock LLM" fallbacks (insights, recommendations, trends, anomalies) | **CRITICAL** |
| `OperationsSpecialistAgent` | `BusinessSpecialistAgentBase` | 2 fallback patterns (blueprint generation) | High |
| `ContentProcessingAgent` | `BusinessSpecialistAgentBase` | MCP tool fallback patterns | Medium |
| `InsightsSpecialistAgent` | `BusinessSpecialistAgentBase` | ✅ **GOOD PATTERN** - Uses MCP tools correctly | Reference |
| `BusinessOutcomesSpecialistAgent` | `BusinessSpecialistAgentBase` | MCP tool usage patterns | Medium |
| `GuideCrossDomainAgent` | `GlobalGuideAgent` | LLM abstraction placeholder | Medium |
| MVP Liaison Agents (4) | `LiaisonDomainAgent` | Inherit from base (placeholder in `_handle_with_mcp_tools()`) | High |

---

## 🔍 Anti-Pattern Categories

### **Category 1: LLM Placeholders (Most Common)**

**Pattern:**
```python
# Placeholder - would use LLM for strategic thinking
recommendations = self._simple_heuristic_ranking(service_result)
```

**Affected Agents:**
- `BusinessAnalysisSpecialist` (6 methods)
- `RecommendationSpecialist` (4 methods)
- `SOPGenerationSpecialist` (1 method)
- `UniversalMapperSpecialist` (1 method)
- `SpecialistCapabilityAgent._enhance_with_ai()` (1 method)

**Fix:** Replace with `self.llm_abstraction.generate_content()` or appropriate LLM method.

---

### **Category 2: Mock LLM Fallbacks (Critical)**

**Pattern:**
```python
if hasattr(self, 'llm_composition_service') and self.llm_composition_service:
    insights = await self.llm_composition_service.generate_insights(...)
else:
    # Mock LLM insights generation  # ❌ ANTI-PATTERN
    insights = [{"type": "trend_insight", ...}]
```

**Affected Agents:**
- `InsightsAnalysisAgent` (4 methods)
- `OperationsSpecialistAgent` (2 methods)

**Fix:** Remove fallbacks, use `self.llm_abstraction` directly, fail fast if unavailable.

---

### **Category 3: MCP Tool Placeholders (Critical)**

**Pattern:**
```python
# Execute MCP tool (placeholder - would use SDK's tool composition)
# Placeholder response
return {"success": True, "response": "placeholder"}
```

**Affected Agents:**
- `SpecialistCapabilityAgent._call_enabling_service()` (1 method)
- `LiaisonDomainAgent._handle_with_mcp_tools()` (1 method)

**Fix:** Use MCP tools exposed by orchestrator MCP servers:
- `self.orchestrator.mcp_server.execute_tool()` (preferred - if orchestrator available)
- OR `self.mcp_client_manager.execute_tool()` (if orchestrator not available)
- OR `self.tool_composition.execute_tool_chain()` (for multi-step workflows)
- **DO NOT** try to discover or access enabling services directly
- MCP servers already expose enabling services as tools - agents just call the tools

---

### **Category 4: Heuristic Fallbacks (Acceptable for Some)**

**Pattern:**
```python
if not hasattr(self, 'llm_abstraction') or not self.llm_abstraction:
    # Fallback to heuristic classification
    return "simple"
```

**Affected Agents:**
- `SpecialistCapabilityAgent._classify_task()` (has fallback)
- `SpecialistCapabilityAgent._assess_complexity()` (has fallback)

**Fix:** Remove fallbacks per user requirement - fail fast if LLM unavailable.

---

## 🛠️ Required Services & MCP Tools

### **Missing/Incomplete Services**

#### **1. LLM Composition Service**
**Status:** Referenced but not fully implemented  
**Needed By:** `InsightsAnalysisAgent`, `OperationsSpecialistAgent`  
**What's Needed:**
- `generate_insights()` method
- `generate_recommendations()` method
- `analyze_trends()` method
- `detect_anomalies()` method
- `generate_blueprint()` method

**Implementation:** Should wrap `llm_abstraction` with domain-specific prompts and structured outputs.

---

#### **2. Enhanced MCP Tool Integration**
**Status:** Partially implemented  
**Needed By:** All agents via `SpecialistCapabilityAgent._call_enabling_service()`  
**What's Needed:**
- ✅ **CRITICAL:** Agents must use MCP tools (never access enabling services directly)
- ✅ Standardized pattern for accessing orchestrator's MCP server
- ✅ Tool composition for multi-step workflows
- ✅ Error handling and retry logic
- ✅ Tool result aggregation

**Architectural Principle:**
- MCP servers expose enabling services as MCP tools
- Agents call MCP tools (not services directly)
- This is the entire point of MCP - abstraction layer

**Implementation:** 
- Fix `_call_enabling_service()` to use orchestrator's MCP server
- Use `self.orchestrator.mcp_server.execute_tool()` pattern
- Remove any code that tries to discover or access enabling services directly

---

#### **3. Conversational AI Service**
**Status:** Not implemented  
**Needed By:** `SpecialistCapabilityAgent._gather_requirements()`  
**What's Needed:**
- Multi-turn conversation management
- Context-aware question generation
- Requirements extraction from dialogue
- User intent clarification

**Implementation:** Create `ConversationalAIService` that uses `llm_abstraction` for dialogue.

---

### **Missing MCP Tools**

#### **For Insurance Use Case Agents:**

1. **Universal Mapper Specialist:**
   - `semantic_similarity_tool` - Calculate semantic similarity using LLM embeddings
   - `pattern_learning_tool` - Learn mapping patterns from corrections

2. **Quality Remediation Specialist:**
   - `anomaly_interpretation_tool` - Interpret quality anomalies with business context
   - `remediation_strategy_tool` - Generate remediation strategies

3. **Routing Decision Specialist:**
   - `routing_reasoning_tool` - Generate routing decisions with reasoning

4. **Wave Planning Specialist:**
   - `wave_planning_tool` - Generate wave plans with risk assessment

---

#### **For MVP Agents:**

1. **Insights Analysis Agent:**
   - `generate_insights_tool` - Generate insights from data
   - `generate_recommendations_tool` - Generate recommendations
   - `analyze_trends_tool` - Analyze trends
   - `detect_anomalies_tool` - Detect anomalies

2. **Operations Specialist Agent:**
   - `generate_blueprint_tool` - Generate coexistence blueprints
   - `enhance_sop_tool` - Enhance SOPs with LLM

3. **Business Analysis Specialist:**
   - `generate_business_insights_tool` - Generate business insights
   - `extract_key_findings_tool` - Extract key findings
   - `detect_business_patterns_tool` - Detect business patterns
   - `identify_risks_tool` - Identify risks
   - `identify_opportunities_tool` - Identify opportunities

---

## 📋 Implementation Phases

### **Phase 1: Foundation Layer (Week 1-2)**

**Goal:** Fix base classes and critical infrastructure

#### **1.1 Fix `SpecialistCapabilityAgent` Base Class**
- ✅ **CRITICAL:** Remove enabling service discovery from `initialize()` method
  - Currently tries to discover enabling service via Curator (lines 154-166)
  - **This is the anti-pattern** - agents should NOT discover services
  - Remove `self.enabling_service` storage
  - Agents only need to know MCP tool names (from config), not service instances
- ✅ Remove fallbacks from `_classify_task()` and `_assess_complexity()`
- ✅ Replace `_enhance_with_ai()` placeholder with `self.llm_abstraction.generate_content()`
- ✅ **CRITICAL:** Replace `_call_enabling_service()` placeholder with MCP tool execution:
  - Use `self.orchestrator.mcp_server.execute_tool()` if orchestrator available
  - OR use `self.mcp_client_manager.execute_tool()` for tool execution
  - OR use `self.tool_composition.execute_tool_chain()` for multi-step workflows
  - **DO NOT** try to discover or access enabling services directly
  - **DO NOT** store `self.enabling_service` - use MCP tools only
  - MCP tools are already exposed by orchestrator's MCP server
- ✅ Replace `_gather_requirements()` placeholder with conversational AI

**Files:**
- `backend/business_enablement/agents/specialist_capability_agent.py`

**Critical Changes:**
1. **Remove Service Discovery (Lines 154-166):**
   ```python
   # ❌ REMOVE THIS ANTI-PATTERN:
   # Discover enabling service via Curator
   if self.enabling_service_name and self.curator_foundation:
       self.enabling_service = await self.curator_foundation.get_service(self.enabling_service_name)
   ```
   
   **Replace with:**
   ```python
   # ✅ CORRECT PATTERN:
   # Agents don't discover services - they use MCP tools
   # MCP tools are exposed by orchestrator's MCP server
   # Tool names come from capability_config['mcp_tools']
   ```

2. **Remove `self.enabling_service` Storage (Line 119):**
   ```python
   # ❌ REMOVE:
   self.enabling_service = None
   
   # ✅ KEEP (for reference only - used in tool naming):
   self.enabling_service_name = capability_config.get('enabling_service')
   ```

**Dependencies:**
- `ConversationalAIService` (new service)

---

#### **1.2 Fix `LiaisonDomainAgent` Base Class**
- ✅ **CRITICAL:** Replace `_handle_with_mcp_tools()` placeholder with MCP tool execution:
  - Use `self.orchestrator.mcp_server.execute_tool()` if orchestrator available
  - OR use `self.mcp_client_manager.execute_tool()` for tool execution
  - OR use `self.tool_composition.execute_tool_chain()` for multi-step workflows
  - **DO NOT** try to discover or access enabling services directly
  - MCP tools are already exposed by orchestrator's MCP server

**Files:**
- `backend/business_enablement/agents/liaison_domain_agent.py`

---

#### **1.3 Create `ConversationalAIService`**
- ✅ Multi-turn conversation management
- ✅ Context-aware question generation
- ✅ Requirements extraction
- ✅ Uses `llm_abstraction` for dialogue

**Files:**
- `backend/business_enablement/enabling_services/conversational_ai_service/conversational_ai_service.py`

---

#### **1.4 Fix MCP Tool Integration Pattern**
- ✅ **CRITICAL:** Agents should ONLY use MCP tools (never access enabling services directly)
- ✅ Use orchestrator's MCP server: `self.orchestrator.mcp_server.execute_tool()`
- ✅ OR use `self.mcp_client_manager.execute_tool()` for tool execution
- ✅ OR use `self.tool_composition.execute_tool_chain()` for multi-step workflows
- ✅ MCP servers already expose enabling services as tools - agents just call the tools
- ✅ Remove any code that tries to discover or access enabling services directly

**Architectural Principle:**
- **MCP servers expose enabling services as MCP tools**
- **Agents call MCP tools (not services directly)**
- **This is the entire point of MCP - abstraction layer**

**How Agents Access MCP Tools:**
1. **Via Orchestrator (Preferred):** If agent has orchestrator reference, use `self.orchestrator.mcp_server.execute_tool()`
   - Orchestrators set themselves on agents via `agent.set_orchestrator(self)` during initialization
   - Example: `ContentAnalysisOrchestrator` sets orchestrator on `ContentProcessingAgent` (line 206-207)
2. **Via MCP Client Manager:** Use `self.mcp_client_manager.execute_tool()` for role-based tool execution
3. **Via Tool Composition:** Use `self.tool_composition.execute_tool_chain()` for multi-step workflows

**Note:** Agents should NOT try to:
- ❌ Discover enabling services via Curator (current anti-pattern in `SpecialistCapabilityAgent.initialize()`)
- ❌ Store `self.enabling_service` (agents don't need service instances)
- ❌ Access enabling services directly
- ❌ Create service instances
- ✅ ONLY call MCP tools that are already exposed by orchestrator MCP servers
- ✅ MCP tool names come from agent config (`capability_config['mcp_tools']`), not service discovery

**Files:**
- `backend/business_enablement/agents/specialist_capability_agent.py` (fix `_call_enabling_service()`)
- `backend/business_enablement/agents/liaison_domain_agent.py` (fix `_handle_with_mcp_tools()`)

---

### **Phase 2: Insurance Use Case Agents (Week 2-3)**

**Goal:** Fix all Insurance Use Case specialist agents

#### **2.1 Universal Mapper Specialist**
- ✅ Replace `_calculate_semantic_similarity()` placeholder with LLM embeddings
- ✅ Create `semantic_similarity_tool` MCP tool

**Files:**
- `backend/business_enablement/agents/specialists/universal_mapper_specialist.py`
- `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/insurance_migration_orchestrator/mcp_server/insurance_migration_mcp_server.py` (add tool)

---

#### **2.2 Routing Decision Specialist**
- ✅ Replace `_generate_reasoning()` placeholder with LLM reasoning
- ✅ Create `routing_reasoning_tool` MCP tool

**Files:**
- `backend/business_enablement/agents/specialists/routing_decision_specialist.py`
- `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/insurance_migration_orchestrator/mcp_server/insurance_migration_mcp_server.py` (add tool)

---

#### **2.3 Wave Planning Specialist**
- ✅ Replace planning logic placeholder with LLM planning
- ✅ Create `wave_planning_tool` MCP tool

**Files:**
- `backend/business_enablement/agents/specialists/wave_planning_specialist.py`
- `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/wave_orchestrator/mcp_server/wave_mcp_server.py` (add tool)

---

#### **2.4 Quality Remediation Specialist**
- ✅ Enhance anomaly interpretation with LLM
- ✅ Create `anomaly_interpretation_tool` and `remediation_strategy_tool` MCP tools

**Files:**
- `backend/business_enablement/agents/specialists/quality_remediation_specialist.py`
- `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/insurance_migration_orchestrator/mcp_server/insurance_migration_mcp_server.py` (add tools)

---

#### **2.5 Change Impact Assessment Specialist**
- ✅ Replace impact analysis placeholder with LLM analysis
- ✅ Create `impact_analysis_tool` MCP tool

**Files:**
- `backend/business_enablement/agents/specialists/change_impact_assessment_specialist.py`
- `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/insurance_migration_orchestrator/mcp_server/insurance_migration_mcp_server.py` (add tool)

---

#### **2.6 Coexistence Strategy Specialist**
- ✅ Replace strategy analysis placeholder with LLM analysis
- ✅ Create `strategy_analysis_tool` MCP tool

**Files:**
- `backend/business_enablement/agents/specialists/coexistence_strategy_specialist.py`
- `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/insurance_migration_orchestrator/mcp_server/insurance_migration_mcp_server.py` (add tool)

---

#### **2.7 Saga WAL Management Specialist**
- ✅ Replace time calculation placeholder (low priority - can use simple calculation)

**Files:**
- `backend/business_enablement/agents/specialists/saga_wal_management_specialist.py`

---

#### **2.8 Insurance Liaison Agent**
- ✅ Inherits fix from `LiaisonDomainAgent` base class

**Files:**
- `backend/business_enablement/agents/insurance_liaison_agent.py` (verify inheritance)

---

### **Phase 3: MVP Pre-Existing Agents (Week 3-4)**

**Goal:** Fix all MVP pre-existing agents

#### **3.1 Insights Analysis Agent (CRITICAL)**
- ✅ Remove all 4 "Mock LLM" fallbacks
- ✅ Use `self.llm_abstraction` directly
- ✅ Create `LLMCompositionService` wrapper

**Files:**
- `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/agents/insights_analysis_agent.py`
- `backend/business_enablement/enabling_services/llm_composition_service/llm_composition_service.py` (new service)

---

#### **3.2 Business Analysis Specialist**
- ✅ Replace 6 placeholders with LLM calls
- ✅ Create MCP tools for each capability

**Files:**
- `backend/business_enablement/agents/specialists/business_analysis_specialist.py`
- `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/mcp_server/insights_mcp_server.py` (add tools)

---

#### **3.3 Recommendation Specialist**
- ✅ Replace 4 placeholders with LLM calls
- ✅ Create MCP tools for strategic thinking, priority, impact, implementation

**Files:**
- `backend/business_enablement/agents/specialists/recommendation_specialist.py`
- `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/mcp_server/insights_mcp_server.py` (add tools)

---

#### **3.4 Operations Specialist Agent**
- ✅ Remove 2 fallback patterns
- ✅ Use `self.llm_abstraction` directly for blueprint generation

**Files:**
- `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/operations_orchestrator/agents/operations_specialist_agent.py`

---

#### **3.5 SOP Generation Specialist**
- ✅ Replace content enhancement placeholder with LLM

**Files:**
- `backend/business_enablement/agents/specialists/sop_generation_specialist.py`
- `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/operations_orchestrator/mcp_server/operations_mcp_server.py` (add tool)

---

#### **3.6 Workflow Generation Specialist**
- ✅ Replace workflow generation placeholder with LLM

**Files:**
- `backend/business_enablement/agents/specialists/workflow_generation_specialist.py`
- `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/operations_orchestrator/mcp_server/operations_mcp_server.py` (add tool)

---

#### **3.7 Coexistence Blueprint Specialist**
- ✅ Replace blueprint generation placeholder with LLM

**Files:**
- `backend/business_enablement/agents/specialists/coexistence_blueprint_specialist.py`
- `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/operations_orchestrator/mcp_server/operations_mcp_server.py` (add tool)

---

#### **3.8 Roadmap Proposal Specialist**
- ✅ Replace roadmap generation placeholder with LLM

**Files:**
- `backend/business_enablement/agents/specialists/roadmap_proposal_specialist.py`
- `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/business_outcomes_orchestrator/mcp_server/business_outcomes_mcp_server.py` (add tool)

---

#### **3.9 Content Processing Agent**
- ✅ Review MCP tool fallback patterns
- ✅ Ensure proper error handling

**Files:**
- `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/agents/content_processing_agent.py`

---

#### **3.10 Business Outcomes Specialist Agent**
- ✅ Review MCP tool usage patterns
- ✅ Ensure proper LLM integration

**Files:**
- `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/business_outcomes_orchestrator/agents/business_outcomes_specialist_agent.py`

---

#### **3.11 Guide Cross Domain Agent**
- ✅ Replace LLM abstraction placeholder

**Files:**
- `backend/business_enablement/agents/guide_cross_domain_agent.py`

---

#### **3.12 MVP Liaison Agents (4 agents)**
- ✅ Inherit fix from `LiaisonDomainAgent` base class

**Files:**
- `backend/business_enablement/agents/mvp_liaison_agents.py` (verify inheritance)

---

### **Phase 4: New Services & MCP Tools (Week 4-5)**

**Goal:** Create missing services and MCP tools

#### **4.1 LLM Composition Service**
- ✅ Wrap `llm_abstraction` with domain-specific methods
- ✅ `generate_insights()`, `generate_recommendations()`, `analyze_trends()`, `detect_anomalies()`
- ✅ Structured output formatting
- ✅ Error handling and retry logic

**Files:**
- `backend/business_enablement/enabling_services/llm_composition_service/llm_composition_service.py`
- `backend/business_enablement/enabling_services/llm_composition_service/__init__.py`

---

#### **4.2 Conversational AI Service**
- ✅ Multi-turn conversation management
- ✅ Context-aware question generation
- ✅ Requirements extraction from dialogue
- ✅ Uses `llm_abstraction` for dialogue

**Files:**
- `backend/business_enablement/enabling_services/conversational_ai_service/conversational_ai_service.py`
- `backend/business_enablement/enabling_services/conversational_ai_service/__init__.py`

---

#### **4.3 Enhanced MCP Tool Integration**
- ✅ Standardized tool discovery for enabling services
- ✅ Tool composition for multi-step workflows
- ✅ Error handling and retry logic

**Files:**
- `foundations/agentic_foundation/agent_sdk/tool_composition.py` (enhance)
- OR `backend/business_enablement/enabling_services/enabling_service_mcp_bridge/enabling_service_mcp_bridge.py` (new)

---

#### **4.4 Add MCP Tools to Orchestrators**
- ✅ Add semantic similarity tool to Insurance Migration MCP Server
- ✅ Add routing reasoning tool to Insurance Migration MCP Server
- ✅ Add wave planning tool to Wave Orchestrator MCP Server
- ✅ Add quality remediation tools to Insurance Migration MCP Server
- ✅ Add insights tools to Insights Orchestrator MCP Server
- ✅ Add operations tools to Operations Orchestrator MCP Server
- ✅ Add business outcomes tools to Business Outcomes Orchestrator MCP Server

**Files:**
- All MCP server files in orchestrator directories

---

### **Phase 5: Testing & Validation (Week 5-6)**

**Goal:** Comprehensive testing of all agent fixes

#### **5.1 Unit Tests**
- ✅ Test each agent method with real LLM calls
- ✅ Test error handling (LLM unavailable scenarios)
- ✅ Test MCP tool execution
- ✅ Test tool composition

**Files:**
- `scripts/insurance_use_case/test_agent_llm_integration.py` (new)
- `scripts/mvp/test_mvp_agent_llm_integration.py` (new)

---

#### **5.2 Integration Tests**
- ✅ Test agent-orchestrator integration
- ✅ Test agent-service integration via MCP tools
- ✅ Test end-to-end workflows

**Files:**
- `scripts/insurance_use_case/test_agent_integration.py` (new)
- `scripts/mvp/test_mvp_agent_integration.py` (new)

---

#### **5.3 Performance Tests**
- ✅ Test LLM call latency
- ✅ Test tool composition performance
- ✅ Test concurrent agent execution

**Files:**
- `scripts/test_agent_performance.py` (new)

---

#### **5.4 Cost Monitoring**
- ✅ Track LLM token usage per agent
- ✅ Track LLM costs per operation
- ✅ Set up alerts for cost thresholds

**Files:**
- `scripts/monitor_llm_costs.py` (new)

---

## 🎯 Success Criteria

### **Phase 1 Success:**
- ✅ All base class placeholders removed
- ✅ `SpecialistCapabilityAgent` uses `llm_abstraction` directly
- ✅ `LiaisonDomainAgent` uses `tool_composition` directly
- ✅ `ConversationalAIService` created and working

### **Phase 2 Success:**
- ✅ All Insurance Use Case agents use LLM directly (no placeholders)
- ✅ All Insurance Use Case MCP tools created
- ✅ All agents fail fast if LLM unavailable (no fallbacks)

### **Phase 3 Success:**
- ✅ All MVP agents use LLM directly (no placeholders, no mock fallbacks)
- ✅ All MVP MCP tools created
- ✅ `LLMCompositionService` created and working

### **Phase 4 Success:**
- ✅ All new services created and registered
- ✅ All MCP tools added to orchestrators
- ✅ Tool composition working end-to-end

### **Phase 5 Success:**
- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ Performance acceptable (< 2s latency for LLM calls)
- ✅ Cost monitoring in place

---

## 📊 Risk Mitigation

### **Risk 1: LLM API Failures**
**Mitigation:**
- Implement retry logic with exponential backoff
- Set timeout limits (30s default)
- Log all failures for monitoring
- **NO FALLBACKS** - Fail fast to surface issues

### **Risk 2: LLM Latency**
**Mitigation:**
- Use async/await throughout
- Implement request batching where possible
- Cache common prompts/responses
- Set SLA targets (< 2s for most operations)

### **Risk 3: LLM Costs**
**Mitigation:**
- Implement cost tracking per agent/operation
- Set cost alerts and thresholds
- Use appropriate LLM models (not always GPT-4)
- Implement prompt optimization

### **Risk 4: LLM Quality/Consistency**
**Mitigation:**
- Implement response validation
- Use structured output formats (AGUI)
- Test with diverse inputs
- Monitor quality metrics

---

## 📅 Timeline

| Phase | Duration | Start | End |
|-------|----------|-------|-----|
| Phase 1: Foundation Layer | 2 weeks | Week 1 | Week 2 |
| Phase 2: Insurance Use Case Agents | 2 weeks | Week 2 | Week 3 |
| Phase 3: MVP Pre-Existing Agents | 2 weeks | Week 3 | Week 4 |
| Phase 4: New Services & MCP Tools | 2 weeks | Week 4 | Week 5 |
| Phase 5: Testing & Validation | 2 weeks | Week 5 | Week 6 |
| **Total** | **6 weeks** | **Week 1** | **Week 6** |

---

## 🔧 Implementation Guidelines

### **Pattern for LLM Integration:**

```python
async def _enhance_with_ai(self, service_result: Dict[str, Any], ...):
    """Enhance service results with AI reasoning."""
    if not self.llm_abstraction:
        raise RuntimeError("LLM abstraction not available - agent requires LLM")
    
    # Build prompt from service result
    prompt = f"""
    Analyze this service result and provide AI-powered insights:
    {json.dumps(service_result, indent=2)}
    
    Provide:
    1. Key insights
    2. Patterns detected
    3. Recommendations
    4. Risk factors
    """
    
    # Use LLM directly (NO FALLBACK)
    enhanced = await self.llm_abstraction.generate_content(
        prompt=prompt,
        content_type="enhancement",
        output_format="structured_json"
    )
    
    return enhanced
```

### **Pattern for MCP Tool Integration (CORRECT ARCHITECTURE):**

**Key Principle:** Agents use MCP tools exposed by orchestrator MCP servers - they NEVER access enabling services directly.

```python
async def _call_enabling_service(self, request: Dict[str, Any], ...):
    """Call enabling service via MCP tools (NOT direct service access)."""
    
    # Pattern 1: Use orchestrator's MCP server (if available)
    if hasattr(self, 'orchestrator') and self.orchestrator and hasattr(self.orchestrator, 'mcp_server'):
        mcp_server = self.orchestrator.mcp_server
        
        # MCP tools are already registered by orchestrator's MCP server
        # Tool names follow pattern: {service_name}_{operation}
        tool_name = f"{self.enabling_service_name}_{request.get('operation')}"
        
        result = await mcp_server.execute_tool(
            tool_name=tool_name,
            parameters=request.get('parameters', {}),
            user_context=request.get('user_context', {})
        )
        return result
    
    # Pattern 2: Use MCP client manager (if orchestrator not available)
    elif self.mcp_client_manager:
        # Use role-based tool execution
        role_name = self.enabling_service_name  # e.g., "SchemaMapperService"
        tool_name = request.get('operation')    # e.g., "map_to_canonical"
        
        result = await self.mcp_client_manager.execute_tool(
            role_name=role_name,
            tool_name=tool_name,
            parameters=request.get('parameters', {}),
            tenant_context=request.get('user_context', {})
        )
        return result
    
    # Pattern 3: Use tool composition for multi-step workflows
    elif self.tool_composition:
        tool_chain = [
            {
                "tool": f"{self.enabling_service_name}_{request.get('operation')}",
                "parameters": request.get('parameters', {}),
                "context": request
            }
        ]
        
        result = await self.tool_composition.execute_tool_chain(
            tool_chain=tool_chain,
            context=request.get('user_context', {})
        )
        return result
    
    # NO FALLBACK - Fail fast if no MCP access
    raise RuntimeError(
        f"MCP tool execution not available for {self.enabling_service_name}. "
        "Agent requires orchestrator MCP server, MCP client manager, or tool composition."
    )
```

**Important Notes:**
- ✅ MCP servers expose enabling services as tools (this is the abstraction)
- ✅ Agents call MCP tools (never services directly)
- ✅ Tool names are registered by orchestrator's MCP server
- ✅ Agents discover tools via orchestrator, not by discovering services

### **Pattern for Conversational AI:**

```python
async def _gather_requirements(self, request: Dict[str, Any], ...):
    """Gather requirements via conversational AI."""
    if not self.conversational_ai_service:
        raise RuntimeError("Conversational AI service not available")
    
    # Use conversational AI service
    conversation = await self.conversational_ai_service.start_conversation(
        initial_request=request,
        context=context_analysis
    )
    
    # Multi-turn dialogue
    requirements = await self.conversational_ai_service.extract_requirements(
        conversation=conversation
    )
    
    return requirements
```

---

## 📝 Next Steps

1. **Review and Approve Roadmap** - Get stakeholder approval
2. **Set Up LLM Infrastructure** - Ensure LLM abstraction is properly configured
3. **Create Project Board** - Track tasks and progress
4. **Start Phase 1** - Begin with base class fixes

---

**Last Updated:** December 2024  
**Status:** Ready for Implementation  
**Owner:** Development Team

