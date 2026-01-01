# Journey & Solution Realms Strategic Refactoring Plan

**Date:** December 15, 2024  
**Status:** 🎯 **STRATEGIC REFACTORING**  
**Goal:** Fully realize strategic architectural vision for Journey and Solution realms with Operations and Business Outcomes capabilities

---

## 🎯 Executive Summary

**Current State:**
- Journey realm has foundation services (journey orchestration, analytics, milestone tracking)
- Solution realm has foundation services (solution composition, analytics, deployment)
- **Missing:** Operations capabilities (workflow/SOP conversion, coexistence analysis)
- **Missing:** Business Outcomes capabilities (roadmap generation, POC proposals)
- **Missing:** MVP showcase integration (frontend UI, agent interactions, pillar workflows)

**Target State:**
- **Journey Realm** = Operations capabilities (workflow/SOP management, coexistence analysis)
- **Solution Realm** = Business Outcomes capabilities (roadmap generation, POC proposals)
- **Clear Realm Boundaries:** Each realm owns its domain services
- **MVP Showcase:** Full end-to-end user journey with all 4 pillars working together

---

## 🏗️ Strategic Architecture Vision

### **Realm Ownership Model (Like Smart City)**

```
Content Realm (✅ Complete)
├── Services: file_parser, embedding, content_metadata, semantic_enrichment
└── Orchestrator: ContentOrchestrator

Insights Realm (✅ Complete)
├── Services: data_analyzer, visualization_engine
└── Orchestrator: InsightsOrchestrator

Journey Realm (🔄 Needs Operations)
├── Services: workflow_conversion, sop_builder, coexistence_analysis
└── Orchestrator: OperationsOrchestrator (NEW)

Solution Realm (🔄 Needs Business Outcomes)
├── Services: roadmap_generation, poc_generation
└── Orchestrator: BusinessOutcomesOrchestrator (NEW)
```

**Key Principle:** Each realm owns its domain services (no cross-realm service dependencies)

---

## 📋 Phase 1: Journey Realm - Operations Capabilities

### **1.1 Move Operations Services to Journey Realm**

**Services to Move/Create:**
- `workflow_conversion_service` → `backend/journey/services/workflow_conversion_service/`
- `sop_builder_service` → `backend/journey/services/sop_builder_service/`
- `coexistence_analysis_service` → `backend/journey/services/coexistence_analysis_service/`

**Decision:** Build from scratch (old services have hardcoded cheats per BUSINESS_LOGIC_EVALUATION.md)

**Why Build New:**
- Old services have hardcoded returns, placeholder logic, mock data
- Better to build correctly using current patterns (RealmServiceBase, micro-modules, proper abstractions)
- Cleaner architecture without legacy debt

### **1.2 Create OperationsOrchestrator**

**Location:** `backend/journey/orchestrators/operations_orchestrator/`

**Purpose:** Orchestrates Operations pillar workflows:
- File selection/upload (redirects to Content pillar)
- Workflow/SOP generation from files
- Coexistence blueprint generation
- Operations Liaison Agent integration

**Key Capabilities:**
- Convert files → Workflows/SOPs (bidirectional conversion)
- Generate coexistence blueprints (with AI optimization analysis)
- Integrate with Operations Liaison Agent (chat-triggered wizard)
- Store all artifacts as Journey artifacts (workflows, SOPs, blueprints)

**SOA APIs:**
```python
async def generate_workflow_from_file(file_id, options)
async def generate_sop_from_file(file_id, options)
async def generate_coexistence_blueprint(current_state, target_state)
async def create_workflow_from_description(description)  # Via Operations Liaison
async def create_coexistence_from_description(description)  # Via Operations Liaison
```

### **1.3 Operations Services Implementation**

#### **WorkflowConversionService**
- **Location:** `backend/journey/services/workflow_conversion_service/`
- **Pattern:** RealmServiceBase with micro-modules
- **Key Methods:**
  - `convert_file_to_workflow(file_id)` - Parse file, extract process, generate workflow (stored as Journey artifact)
  - `convert_file_to_sop(file_id)` - Parse file, extract procedures, generate SOP (stored as Journey artifact)
  - `convert_workflow_to_sop(workflow_id)` - **Bidirectional conversion** - Convert workflow to SOP format
  - `convert_sop_to_workflow(sop_id)` - **Bidirectional conversion** - Convert SOP to executable workflow

#### **SOPBuilderService**
- **Location:** `backend/journey/services/sop_builder_service/`
- **Pattern:** RealmServiceBase with wizard pattern
- **Key Methods:**
  - `start_sop_wizard()` - Initialize wizard session (can be triggered by Operations Liaison Agent)
  - `process_wizard_step(session_token, step_data)` - Process wizard step (agent can call on behalf of user)
  - `generate_sop_from_wizard(session_token)` - Generate SOP from wizard (stored as Journey artifact)
  - `validate_sop(sop_definition)` - Validate SOP structure

#### **CoexistenceAnalysisService**
- **Location:** `backend/journey/services/coexistence_analysis_service/`
- **Pattern:** RealmServiceBase with analysis modules
- **Key Methods:**
  - `analyze_coexistence(current_state, target_state)` - **Evaluate AI optimization opportunities** in workflow/SOP process
  - `generate_coexistence_blueprint(analysis_result)` - Generate blueprint with analysis, recommendations, future state artifacts (stored as Journey artifact)
  - `optimize_coexistence(blueprint)` - Optimize blueprint
  - `generate_future_state_artifacts(blueprint)` - Generate AI-enabled SOP/workflow artifacts

### **1.4 Operations Liaison Agent**

**Location:** `backend/journey/agents/operations_liaison_agent/`

**Purpose:** Guide users through Operations pillar workflows

**Capabilities:**
- **Chat-triggered SOP wizard** - Users describe process via chat, agent guides through wizard
- Help design target state coexistence (→ Coexistence analyzer)
- Navigate Operations pillar features
- Answer questions about workflows, SOPs, coexistence
- **MCP Tools:** operations_start_sop_wizard, operations_process_wizard_step, operations_complete_sop_wizard

---

## 📋 Phase 2: Solution Realm - Business Outcomes Capabilities

### **2.1 Move Business Outcomes Services to Solution Realm**

**Services to Move/Create:**
- `roadmap_generation_service` → `backend/solution/services/roadmap_generation_service/`
- `poc_generation_service` → `backend/solution/services/poc_generation_service/`

**Decision:** Build from scratch (old services have hardcoded cheats)

### **2.2 Create BusinessOutcomesOrchestrator**

**Location:** `backend/solution/orchestrators/business_outcomes_orchestrator/`

**Purpose:** Orchestrates Business Outcomes pillar workflows:
- Display pillar summaries (Content, Insights, Operations)
- Generate roadmap from pillar outputs
- Generate POC proposal from pillar outputs
- Solution Liaison Agent integration

**Key Capabilities:**
- Compose pillar outputs into strategic roadmap (flexible - works with partial inputs)
- Generate comprehensive POC proposals (with financials: ROI, NPV, IRR)
- Integrate with Solution Liaison Agent
- Store all artifacts as Solution artifacts (roadmaps, POC proposals)

**SOA APIs:**
```python
async def generate_roadmap(pillar_outputs, business_context)
async def generate_poc_proposal(pillar_outputs, poc_type)
async def get_pillar_summaries(user_id)  # Content, Insights, Operations summaries
async def update_roadmap(roadmap_id, updates)
async def get_poc_status(poc_id)
```

### **2.3 Business Outcomes Services Implementation**

#### **RoadmapGenerationService**
- **Location:** `backend/solution/services/roadmap_generation_service/`
- **Pattern:** RealmServiceBase with strategic planning modules
- **Key Methods:**
  - `generate_roadmap(pillar_outputs, business_context)` - Generate strategic roadmap from **flexible pillar inputs** (doesn't require all pillars) - stored as Solution artifact
  - `update_roadmap(roadmap_id, updates)` - Update roadmap
  - `visualize_roadmap(roadmap_id)` - Generate roadmap visualization
  - `track_progress(roadmap_id)` - Track roadmap progress

#### **POCGenerationService**
- **Location:** `backend/solution/services/poc_generation_service/`
- **Pattern:** RealmServiceBase with proposal composition modules
- **Key Methods:**
  - `generate_poc_proposal(pillar_outputs, poc_type)` - Generate POC proposal from **flexible pillar inputs** (doesn't require all pillars) - stored as Solution artifact
  - `calculate_financials(poc_proposal)` - Calculate ROI, NPV, IRR, payback period
  - `generate_executive_summary(poc_proposal)` - Generate executive summary
  - `validate_poc_proposal(poc_proposal)` - Validate proposal completeness

### **2.4 Solution Liaison Agent**

**Location:** `backend/solution/agents/solution_liaison_agent/`

**Purpose:** Guide users through Business Outcomes pillar workflows

**Capabilities:**
- Help users understand pillar summaries
- Prompt for additional context/files
- Guide roadmap and POC generation
- Answer questions about business outcomes

---

## 📋 Phase 3: MVP Showcase Integration

### **3.1 Frontend Integration**

**Requirements from MVP Description:**
- Landing page with GuideAgent introduction
- 4 pillar navigation (Content, Insights, Operations, Business Outcomes)
- Persistent chat panel (GuideAgent + Pillar Liaison)
- File upload/selection workflows
- Data preview capabilities
- Visualization/analysis displays
- Workflow/SOP visual elements
- Coexistence blueprint display
- Roadmap visualization
- POC proposal display

**Implementation:**
- Update `symphainy-frontend` to use new realm orchestrators
- Create pillar-specific UI components
- Integrate agent chat interfaces
- Add visualization components (charts, graphs, workflows)

### **3.2 Agent Integration**

**Agents Needed:**
- ✅ GuideAgent (already exists)
- ✅ ContentLiaisonAgent (already exists)
- ✅ InsightsLiaisonAgent (already exists)
- 🔄 OperationsLiaisonAgent (needs creation)
- 🔄 SolutionLiaisonAgent (needs creation)

**Agent Capabilities:**
- GuideAgent: Overall journey guidance, pillar navigation
- ContentLiaisonAgent: Content pillar navigation, file interaction
- InsightsLiaisonAgent: Insights navigation, data analysis guidance
- OperationsLiaisonAgent: Operations navigation, workflow/SOP guidance
- SolutionLiaisonAgent: Business Outcomes navigation, roadmap/POC guidance

### **3.3 API Endpoint Integration**

**New Endpoints Needed:**

**Operations Pillar:**
- `POST /api/v1/operations-pillar/generate-workflow` - Generate workflow from file
- `POST /api/v1/operations-pillar/generate-sop` - Generate SOP from file
- `POST /api/v1/operations-pillar/generate-coexistence` - Generate coexistence blueprint
- `GET /api/v1/operations-pillar/workflow/{workflow_id}` - Get workflow
- `GET /api/v1/operations-pillar/sop/{sop_id}` - Get SOP

**Business Outcomes Pillar:**
- `POST /api/v1/business-outcomes-pillar/generate-roadmap` - Generate roadmap
- `POST /api/v1/business-outcomes-pillar/generate-poc` - Generate POC proposal
- `GET /api/v1/business-outcomes-pillar/pillar-summaries` - Get pillar summaries
- `GET /api/v1/business-outcomes-pillar/roadmap/{roadmap_id}` - Get roadmap
- `GET /api/v1/business-outcomes-pillar/poc/{poc_id}` - Get POC proposal

---

## 🎯 Implementation Phases

### **Phase 1: Journey Realm Operations (Week 1-2)**
1. Create `backend/journey/services/` structure
2. Build `WorkflowConversionService` (from scratch)
3. Build `SOPBuilderService` (from scratch)
4. Build `CoexistenceAnalysisService` (from scratch)
5. Create `OperationsOrchestrator`
6. Create `OperationsLiaisonAgent`
7. Test Operations pillar workflows

### **Phase 2: Solution Realm Business Outcomes (Week 2-3)**
1. Create `backend/solution/services/` structure
2. Build `RoadmapGenerationService` (from scratch)
3. Build `POCGenerationService` (from scratch)
4. Create `BusinessOutcomesOrchestrator`
5. Create `SolutionLiaisonAgent`
6. Test Business Outcomes pillar workflows

### **Phase 3: MVP Showcase Integration (Week 3-4)**
1. Update frontend to use new orchestrators
2. Create pillar-specific UI components
3. Integrate agent chat interfaces
4. Add visualization components
5. End-to-end testing of full user journey

---

## ✅ Success Criteria

1. **Journey Realm:** Owns all Operations services (workflow, SOP, coexistence)
2. **Solution Realm:** Owns all Business Outcomes services (roadmap, POC)
3. **Clear Boundaries:** No cross-realm service dependencies
4. **MVP Functionality Delivered:**
   - ✅ Display workflow and SOP (visual elements)
   - ✅ Bidirectional conversion (workflow ↔ SOP)
   - ✅ Wizard agent via chat (Operations Liaison triggers SOP wizard)
   - ✅ Coexistence optimizer (evaluates AI optimization, generates blueprint)
   - ✅ Flexible pillar inputs (roadmap/POC work with partial outputs)
5. **Architectural Vision Realized:**
   - ✅ Artifacts stored as Journey artifacts (workflows, SOPs, blueprints)
   - ✅ Artifacts stored as Solution artifacts (roadmaps, POC proposals)
   - ✅ Artifacts discoverable via Curator, trackable via Conductor/Solution Analytics
6. **MVP Showcase:** Full end-to-end user journey works (all 4 pillars)
7. **Agent Integration:** All 5 agents working (Guide + 4 Liaisons)
8. **Frontend Integration:** All pillar UIs functional with visualizations

---

## 📚 References

- MVP Description: `docs/MVP_Description_For_Business_and_Technical_Readiness.md`
- Enabling Services Refactoring Plan: `docs/ENABLING_SERVICES_REFACTORING_PLAN.md`
- Business Logic Evaluation: `backend/business_enablement_old/enabling_services/BUSINESS_LOGIC_EVALUATION.md`

