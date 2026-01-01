# Business Enablement Holistic Refactoring Roadmap

**Date:** December 11, 2025  
**Status:** 🚀 Planning Phase  
**Strategy:** Parallel Complete Rebuilds (Avoid Incremental Refactoring)

---

## 🎯 **Executive Summary**

This roadmap addresses the complete refactoring of Business Enablement realm with a **parallel rebuild strategy** to avoid the complexity and risk of incremental refactoring across 4 major categories:

1. **Orchestrators** - Complete rebuild with DIL SDK integration, separation of concerns
2. **Enabling Services** - Complete rebuild with agentic forward patterns, fix all hard-coded cheats
3. **Agents** - Complete rebuild to best versions + agentic forward approach
4. **MCP Servers** - Complete rebuild to support agentic forward design

**Key Principle:** Rebuild each category completely in parallel, then integrate. This avoids touching files 3-5 times with complex integrations that subsequent phases might wipe out.

---

## 📊 **Current State Assessment**

### **Orchestrators (4 MVP Pillar Orchestrators)**
- **ContentAnalysisOrchestrator**: Mixed concerns (content + insights), needs complete rebuild
- **InsightsOrchestrator**: Uses enabling services with hard-coded cheats
- **OperationsOrchestrator**: Uses enabling services with hard-coded cheats
- **BusinessOutcomesOrchestrator**: Uses enabling services with hard-coded cheats

**Issues:**
- No DIL SDK integration
- Mixed concerns (content orchestrator doing insights work)
- Direct Smart City service access (should use DIL SDK)
- No workflow_id propagation

### **Enabling Services (24 Services)**
**Critical Issues:**
- 1 Critical: SchemaMapperService (hard-coded schema discovery)
- 15 High Priority: ValidationEngine, TransformationEngine, MetricsCalculator, InsightsGenerator, APGProcessor, RoadmapGeneration, ReportGenerator, VisualizationEngine, ExportFormatter, DataCompositor, DataAnalyzer
- 8 Medium Priority: Various services
- 6 Low Priority: Various services

**Architecture Issues:**
- Hard-coded return values (same output regardless of input)
- Placeholder logic (`# TODO`, `pass`, empty implementations)
- Stub methods (return success without doing work)
- Missing validation and error handling
- Mock data instead of real implementations

### **Agents (15+ Specialist Agents + Liaison Agents)**
**Current Structure:**
- Declarative agent pattern (YAML configs)
- Specialist agents: RecommendationSpecialist, UniversalMapperSpecialist, WavePlanningSpecialist, QualityRemediationSpecialist, RoutingDecisionSpecialist, ChangeImpactAssessmentSpecialist, BusinessAnalysisSpecialist, SOPGenerationSpecialist, WorkflowGenerationSpecialist, CoexistenceBlueprintSpecialist, RoadmapProposalSpecialist, CoexistenceStrategySpecialist, SagaWALManagementSpecialist
- Liaison agents: ContentLiaisonAgent, OperationsLiaisonAgent, InsightsLiaisonAgent, BusinessOutcomesLiaisonAgent
- StatelessHFInferenceAgent (embeddings)

**Issues:**
- Not optimized for agentic forward patterns
- Limited integration with enabling services
- Not leveraging agents to fix enabling service hard-coded cheats
- Need to be "best versions of themselves"

### **MCP Servers (4 MVP Orchestrator MCP Servers)**
**Current Structure:**
- ContentAnalysisMCPServer
- InsightsMCPServer
- OperationsMCPServer
- BusinessOutcomesMCPServer

**Issues:**
- Not designed for agentic forward patterns
- Tools don't leverage agents for complex business logic
- Need refactoring to support agent-enhanced enabling services

---

## 🏗️ **Refactoring Strategy: Parallel Complete Rebuilds**

### **Why Parallel Rebuilds?**

**Problem with Incremental Refactoring:**
- Touch each file 3-5 times
- Complex integrations that next phase might wipe out
- Hard to track dependencies
- High risk of breaking working code
- Difficult to test incrementally

**Solution: Parallel Complete Rebuilds**
- Rebuild each category completely
- Capture ALL changes needed in each file
- Change each file ONCE
- Clean integration points
- Easier to test and validate
- Lower risk of breaking working code

### **Rebuild Approach**

For each category:
1. **Design Phase**: Design complete new architecture
2. **Build Phase**: Build complete new implementation
3. **Test Phase**: Test in isolation
4. **Integration Phase**: Integrate with other rebuilt categories
5. **Cutover Phase**: Switch from old to new (with rollback plan)

---

## 📅 **Roadmap: Parallel Rebuild Phases**

### **Phase 0: Vertical Slice (Template Creation)** (Weeks 1-3)

**Goal:** Build complete vertical slice to validate approach and create templates

**Status:** ✅ **Implementation Plan Created** - `BUSINESS_ENABLEMENT_VERTICAL_SLICE_IMPLEMENTATION_PLAN.md`

**Scope:**
- Complete ContentAnalysisOrchestrator workflow (upload → parse → metadata → embeddings)
- All 4 categories in one slice (Orchestrator, Enabling Services, Agents, MCP Server)
- End-to-end testing and validation
- Template creation for parallel teams

**Output:** 
- Working vertical slice ✅
- Templates for all 4 categories ✅
- Patterns documented ✅
- Lessons learned captured ✅

---

### **Phase 1: Parallel Rebuilds** (Weeks 4-7)

**Note:** Teams can start using templates from Phase 0 vertical slice (Week 3)

**Goal:** Rebuild all 4 categories in parallel

#### **1.1 Orchestrators Rebuild** (Weeks 2-5)

**Team:** Orchestrator Team (can work in parallel with other teams)

**Scope:**
- **ContentAnalysisOrchestrator**: Complete rebuild
  - Focus: Content pillar only (parsing, metadata extraction, embeddings)
  - Remove: Insights capabilities (move to Insights Orchestrator)
  - Add: DIL SDK integration, workflow_id propagation
  - Add: ContentMetadataExtractionService integration
  - Add: EmbeddingService integration
  - Add: Workflow/SOP parsing support (basic text extraction)

- **InsightsOrchestrator**: Complete rebuild
  - Focus: Semantic data usage (query semantic data, generate insights)
  - Add: DIL SDK integration for semantic data queries
  - Add: Integration with refactored enabling services
  - Remove: Direct Smart City service access

- **OperationsOrchestrator**: Complete rebuild
  - Focus: Process optimization, SOP building, workflow visualization
  - Add: DIL SDK integration
  - Add: Integration with refactored enabling services
  - Add: Use parsed content from ContentAnalysisOrchestrator

- **BusinessOutcomesOrchestrator**: Complete rebuild
  - Focus: Business outcomes tracking, roadmap generation
  - Add: DIL SDK integration
  - Add: Integration with refactored enabling services

**Key Changes:**
- All orchestrators use DIL SDK (no direct Smart City access)
- All orchestrators propagate workflow_id
- Clear separation of concerns (content vs insights vs operations vs outcomes)
- Integration with rebuilt enabling services
- Integration with rebuilt agents
- Integration with rebuilt MCP servers

**Deliverables:**
- Complete orchestrator implementations
- Unit tests
- Integration tests with DIL SDK
- Documentation

---

#### **1.2 Enabling Services Rebuild** (Weeks 2-5)

**Team:** Enabling Services Team (can work in parallel with other teams)

**Scope:**
- **24 Enabling Services**: Complete rebuild of all micro-modules

**Critical Services (Must Fix):**
1. **SchemaMapperService** (CRITICAL)
   - Rebuild `_discover_schema_from_data()` - Actual schema discovery
   - Remove hard-coded schema returns

2. **ValidationEngineService** (HIGH - 4 issues)
   - Rebuild `validate_custom_rules()` - Actual custom rule validation
   - Rebuild `check_compliance_standard()` - Actual compliance checking
   - Rebuild `enforce_single_rule()` - Actual rule enforcement
   - Rebuild `validate_against_schema()` - Actual schema validation

3. **TransformationEngineService** (HIGH - 2 issues)
   - Rebuild `convert_data_format()` - Actual format conversion
   - Rebuild `map_to_schema()` - Actual schema mapping

4. **MetricsCalculatorService** (HIGH)
   - Rebuild `get_metric_definition()` - Metric registry lookup

5. **InsightsGeneratorService** (HIGH)
   - Rebuild `get_historical_context()` - Query actual historical data

6. **APGProcessingService** (HIGH - 5 issues)
   - Rebuild all 5 workflow methods - Actual pattern generation, insights discovery, automation

7. **RoadmapGenerationService** (HIGH)
   - Rebuild `generate_fallback_trend_analysis()` - Actual trend analysis

8. **ReportGeneratorService** (HIGH - 2 issues)
   - Rebuild `render_report()` - Actual template rendering
   - Rebuild `export_report()` - Actual format conversion

9. **VisualizationEngineService** (HIGH)
   - Rebuild `generate_visualization()` - Actual chart/graph generation

10. **ExportFormatterService** (HIGH)
    - Rebuild `format_for_export()` - Actual format conversion

11. **DataCompositorService** (HIGH - 2 issues)
    - Rebuild `execute_federated_query()` - Actual federated query execution
    - Rebuild `materialize_composition()` - Actual materialization

12. **DataAnalyzerService** (HIGH)
    - Rebuild `extract_entities()` - Actual entity extraction
    - Refactor to focus on semantic data usage only
    - Split: ContentMetadataExtractionService (NEW), EmbeddingService (NEW)

**New Services:**
- **ContentMetadataExtractionService** (NEW)
  - Extract structural metadata from parsed files
  - Store via DIL SDK → Librarian

- **EmbeddingService** (NEW)
  - Create embeddings from parsed content
  - Wrap StatelessHFInferenceAgent
  - Store via DIL SDK → Librarian

**FileParserService Simplification:**
- Add parsing type determination (structured/unstructured/hybrid/workflow/sop)
- Create three parsing modules (structured_parsing, unstructured_parsing, hybrid_parsing)
- Refactor decision tree (parsing type → file type → abstraction)
- Update to return files for backend saving (JSON format)

**Key Changes:**
- Remove ALL hard-coded cheats
- Implement actual business logic
- Integrate with agents for complex logic (agentic forward)
- DIL SDK integration where applicable
- Clean micro-module architecture

**Deliverables:**
- Complete enabling service implementations
- Unit tests
- Integration tests
- Documentation

---

#### **1.3 Agents Rebuild** (Weeks 2-5)

**Team:** Agents Team (can work in parallel with other teams)

**Scope:**
- **15+ Specialist Agents**: Complete rebuild to best versions
- **4+ Liaison Agents**: Complete rebuild to best versions
- **StatelessHFInferenceAgent**: Enhance for embedding service

**Agentic Forward Pattern:**
- Agents enhance enabling services with AI reasoning
- Agents handle complex business logic that enabling services can't
- Agents provide fallback when enabling services have limitations
- Agents learn and improve over time

**Specialist Agents Rebuild:**
1. **RecommendationSpecialist** - Best version + agentic forward
2. **UniversalMapperSpecialist** - Best version + agentic forward
3. **WavePlanningSpecialist** - Best version + agentic forward
4. **QualityRemediationSpecialist** - Best version + agentic forward
5. **RoutingDecisionSpecialist** - Best version + agentic forward
6. **ChangeImpactAssessmentSpecialist** - Best version + agentic forward
7. **BusinessAnalysisSpecialist** - Best version + agentic forward
8. **SOPGenerationSpecialist** - Best version + agentic forward
9. **WorkflowGenerationSpecialist** - Best version + agentic forward
10. **CoexistenceBlueprintSpecialist** - Best version + agentic forward
11. **RoadmapProposalSpecialist** - Best version + agentic forward
12. **CoexistenceStrategySpecialist** - Best version + agentic forward
13. **SagaWALManagementSpecialist** - Best version + agentic forward

**Liaison Agents Rebuild:**
1. **ContentLiaisonAgent** - Best version + agentic forward
2. **OperationsLiaisonAgent** - Best version + agentic forward
3. **InsightsLiaisonAgent** - Best version + agentic forward
4. **BusinessOutcomesLiaisonAgent** - Best version + agentic forward

**Key Changes:**
- Optimize each agent to be the "best version of itself"
- Integrate with enabling services via agentic forward pattern
- Agents handle complex logic that enabling services can't
- Agents provide AI reasoning and learning
- Clean declarative pattern (YAML configs)
- Enhanced MCP tool integration

**Deliverables:**
- Complete agent implementations
- Agent configs (YAML)
- Unit tests
- Integration tests with enabling services
- Documentation

---

#### **1.4 MCP Servers Rebuild** (Weeks 2-5)

**Team:** MCP Servers Team (can work in parallel with other teams)

**Scope:**
- **4 MVP Orchestrator MCP Servers**: Complete rebuild

**MCP Servers:**
1. **ContentAnalysisMCPServer** - Rebuild for agentic forward
2. **InsightsMCPServer** - Rebuild for agentic forward
3. **OperationsMCPServer** - Rebuild for agentic forward
4. **BusinessOutcomesMCPServer** - Rebuild for agentic forward

**Agentic Forward Design:**
- Tools leverage agents for complex business logic
- Tools orchestrate enabling services + agents
- Tools provide high-level use case capabilities
- Tools handle agent-enhanced enabling service calls

**Key Changes:**
- Redesign tools to support agentic forward pattern
- Tools call enabling services, then agents enhance results
- Tools provide use case-level capabilities (not low-level)
- Clean tool definitions and handlers
- Enhanced error handling and validation

**Deliverables:**
- Complete MCP server implementations
- Tool definitions
- Unit tests
- Integration tests with orchestrators and agents
- Documentation

---

### **Phase 2: Integration & Testing** (Week 8)

**Goal:** Integrate all rebuilt categories and test end-to-end

#### **2.1 Category Integration**
- [ ] Integrate Orchestrators with Enabling Services
- [ ] Integrate Orchestrators with Agents
- [ ] Integrate Orchestrators with MCP Servers
- [ ] Integrate Agents with Enabling Services (agentic forward)
- [ ] Integrate MCP Servers with Orchestrators and Agents

#### **2.2 Integration Testing**
- [ ] Test orchestrator → enabling service integration
- [ ] Test orchestrator → agent integration
- [ ] Test orchestrator → MCP server integration
- [ ] Test agent → enabling service integration (agentic forward)
- [ ] Test complete workflows end-to-end

#### **2.3 End-to-End Testing**
- [ ] Test content pillar workflow (upload → parse → metadata → embeddings)
- [ ] Test insights pillar workflow (query semantic data → generate insights)
- [ ] Test operations pillar workflow (parse SOP → convert to workflow)
- [ ] Test business outcomes pillar workflow (track outcomes → generate roadmap)

**Output:** Fully integrated and tested system

---

### **Phase 3: Cutover & Validation** (Week 9)

**Goal:** Cutover from old to new implementations

#### **3.1 Cutover Planning**
- [ ] Create cutover plan with rollback strategy
- [ ] Prepare feature flags for gradual rollout
- [ ] Prepare monitoring and alerting
- [ ] Prepare rollback procedures

#### **3.2 Gradual Cutover**
- [ ] Cutover ContentAnalysisOrchestrator (with rollback plan)
- [ ] Cutover InsightsOrchestrator (with rollback plan)
- [ ] Cutover OperationsOrchestrator (with rollback plan)
- [ ] Cutover BusinessOutcomesOrchestrator (with rollback plan)
- [ ] Cutover Enabling Services (gradual, service by service)
- [ ] Cutover Agents (gradual, agent by agent)
- [ ] Cutover MCP Servers (gradual, server by server)

#### **3.3 Validation**
- [ ] Validate all workflows end-to-end
- [ ] Validate performance
- [ ] Validate error handling
- [ ] Validate rollback procedures

**Output:** Fully cutover to new implementations

---

### **Phase 4: Documentation & Handoff** (Week 10)

**Goal:** Complete documentation and handoff

#### **4.1 Documentation**
- [ ] Update architecture documentation
- [ ] Create service-specific guides
- [ ] Document agentic forward patterns
- [ ] Document DIL SDK integration patterns
- [ ] Create migration guides
- [ ] Create troubleshooting guides

#### **4.2 Handoff**
- [ ] Review all changes
- [ ] Create handoff documentation
- [ ] Conduct knowledge transfer sessions
- [ ] Create training materials

**Output:** Complete documentation and handoff

---

## 🔄 **Parallel Work Strategy**

### **Team Structure**

**Team 1: Orchestrators Team**
- Focus: Rebuild all 4 orchestrators
- Can work completely in parallel with other teams
- Integration points: DIL SDK, Enabling Services, Agents, MCP Servers

**Team 2: Enabling Services Team**
- Focus: Rebuild all 24 enabling services
- Can work completely in parallel with other teams
- Integration points: DIL SDK, Agents (agentic forward), Orchestrators

**Team 3: Agents Team**
- Focus: Rebuild all agents to best versions + agentic forward
- Can work completely in parallel with other teams
- Integration points: Enabling Services (agentic forward), MCP Servers, Orchestrators

**Team 4: MCP Servers Team**
- Focus: Rebuild all 4 MCP servers for agentic forward
- Can work completely in parallel with other teams
- Integration points: Orchestrators, Agents, Enabling Services

### **Coordination**

**Weekly Sync:**
- All teams sync weekly on integration points
- Review architecture decisions
- Resolve conflicts
- Validate integration points

**Integration Points:**
- DIL SDK (shared by all teams)
- Agentic forward patterns (shared by Agents and Enabling Services teams)
- MCP tool definitions (shared by MCP Servers and Orchestrators teams)

---

## 📋 **Detailed Implementation Plans**

### **Phase 0: Vertical Slice (Template Creation)**
1. ✅ **ContentAnalysisOrchestrator Vertical Slice Plan** - `BUSINESS_ENABLEMENT_VERTICAL_SLICE_IMPLEMENTATION_PLAN.md`
   - Complete vertical slice to validate approach
   - Creates templates for all 4 categories
   - **Status:** Ready to Start

### **Orchestrators**
1. **ContentAnalysisOrchestrator Rebuild Plan** (Template from vertical slice)
2. **InsightsOrchestrator Rebuild Plan**
3. **OperationsOrchestrator Rebuild Plan**
4. **BusinessOutcomesOrchestrator Rebuild Plan**

### **Enabling Services**
1. **Critical Services Remediation Plan** (SchemaMapper, ValidationEngine, etc.)
2. **High-Priority Services Remediation Plan** (MetricsCalculator, InsightsGenerator, etc.)
3. **FileParserService Simplification Plan**
4. **New Services Implementation Plan** (ContentMetadataExtraction, EmbeddingService)
5. **Remaining Services Remediation Plan**

### **Agents**
1. **Specialist Agents Rebuild Plan** (15+ agents)
2. **Liaison Agents Rebuild Plan** (4+ agents)
3. **Agentic Forward Pattern Implementation Plan**

### **MCP Servers**
1. **ContentAnalysisMCPServer Rebuild Plan**
2. **InsightsMCPServer Rebuild Plan**
3. **OperationsMCPServer Rebuild Plan**
4. **BusinessOutcomesMCPServer Rebuild Plan**
5. **Agentic Forward Tool Design Plan**

---

## 🎯 **Success Criteria**

### **Orchestrators**
- ✅ All orchestrators use DIL SDK (no direct Smart City access)
- ✅ All orchestrators propagate workflow_id
- ✅ Clear separation of concerns (content vs insights vs operations vs outcomes)
- ✅ All orchestrators integrate with rebuilt enabling services
- ✅ All orchestrators integrate with rebuilt agents
- ✅ All orchestrators integrate with rebuilt MCP servers

### **Enabling Services**
- ✅ All hard-coded cheats removed
- ✅ All business logic actually implemented
- ✅ All services integrate with agents (agentic forward)
- ✅ All services use DIL SDK where applicable
- ✅ Clean micro-module architecture

### **Agents**
- ✅ All agents are "best versions of themselves"
- ✅ All agents support agentic forward patterns
- ✅ All agents integrate with enabling services
- ✅ All agents enhance enabling service capabilities
- ✅ Clean declarative pattern (YAML configs)

### **MCP Servers**
- ✅ All MCP servers support agentic forward design
- ✅ All tools leverage agents for complex logic
- ✅ All tools provide use case-level capabilities
- ✅ Clean tool definitions and handlers

### **Integration**
- ✅ All categories integrate seamlessly
- ✅ Complete end-to-end workflows work
- ✅ Performance meets requirements
- ✅ Error handling is robust
- ✅ Rollback procedures tested

---

## 📊 **Risk Management**

### **Risks**

1. **Integration Complexity**
   - **Risk:** Categories might not integrate cleanly
   - **Mitigation:** Weekly syncs, clear integration points, early integration testing

2. **Scope Creep**
   - **Risk:** Rebuilds might expand beyond scope
   - **Mitigation:** Clear scope definition, regular reviews, change control

3. **Timeline**
   - **Risk:** Parallel rebuilds might take longer than expected
   - **Mitigation:** Realistic estimates, buffer time, phased cutover

4. **Quality**
   - **Risk:** Rebuilds might introduce new bugs
   - **Mitigation:** Comprehensive testing, code reviews, gradual cutover

### **Rollback Plan**

- Feature flags for gradual rollout
- Keep old implementations until new ones are validated
- Rollback procedures for each category
- Monitoring and alerting for early detection

---

## 📚 **Documentation Structure**

### **Planning Documents**
- This roadmap
- Architecture designs (per category)
- Detailed implementation plans (per category)

### **Implementation Documents**
- Code documentation
- API documentation
- Integration guides
- Testing guides

### **Handoff Documents**
- Architecture overview
- Service-specific guides
- Agentic forward patterns guide
- DIL SDK integration guide
- Troubleshooting guides
- Migration guides

---

## 🚀 **Next Steps**

1. **Review this roadmap** with stakeholders
2. **Create detailed implementation plans** for each category
3. **Form teams** for parallel work
4. **Begin Phase 0** (Foundation & Design)
5. **Start Phase 1** (Parallel Rebuilds)

---

**Last Updated:** December 11, 2025  
**Status:** Ready for Review

