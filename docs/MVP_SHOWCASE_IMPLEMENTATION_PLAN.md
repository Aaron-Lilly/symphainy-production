# MVP Showcase Implementation Plan

**Date:** December 15, 2024  
**Status:** 🎯 **IMPLEMENTATION PLAN**  
**Goal:** Implement remaining MVP showcase elements for full end-to-end user journey

---

## 🎯 Executive Summary

**Current State:**
- ✅ Content pillar: File upload, parsing, metadata extraction, embeddings
- ✅ Insights pillar: Data analysis, visualization, insights generation
- 🔄 Operations pillar: Needs workflow/SOP generation, coexistence analysis
- 🔄 Business Outcomes pillar: Needs roadmap generation, POC proposals
- 🔄 Frontend: Needs full integration with all 4 pillars
- 🔄 Agents: Needs Operations and Solution Liaison agents

**Target State:**
- Complete 4-pillar user journey from landing page to POC proposal
- All agents functional (GuideAgent + 4 Liaison agents)
- Full frontend integration with all pillar capabilities
- End-to-end workflow: Content → Insights → Operations → Business Outcomes

---

## 📋 MVP Requirements Analysis

### **Landing Page Requirements**
- Welcome message introducing GuideAgent and 4 pillars
- GuideAgent prompts user about goals
- Suggests data to share based on goals
- Directs user to Content pillar

**Implementation:**
- Create landing page component in `symphainy-frontend`
- Integrate GuideAgent chat interface
- Add goal collection form
- Add data suggestion logic based on goals

### **Content Pillar Requirements**
- ✅ Dashboard view of available files
- ✅ File uploader (multiple file types, mainframe binary/copybook support)
- ✅ Parsing function (parquet, JSON Structured, JSON Chunks)
- ✅ Data preview
- ✅ Metadata extraction section
- ✅ Metadata preview
- ✅ ContentLiaisonAgent chatbot
- ✅ Ready to move to Insights pillar

**Status:** ✅ Mostly complete, may need UI polish

### **Insights Pillar Requirements**
- ✅ File selection prompt (parsed files)
- ✅ Business analysis text element
- ✅ Visual/tabular representation (side-by-side)
- ✅ Insights Liaison chatbot
- ✅ "Double click" analysis capability
- ✅ Insights summary section (recap, visual, recommendations)
- ✅ Ready to move to Operations pillar

**Status:** ✅ Mostly complete, may need UI polish

### **Operations Pillar Requirements**
- 🔄 3 cards at top: Select existing file(s), Upload new file, Generate from scratch
- 🔄 Section 2: File(s) → Workflow/SOP visual elements
- 🔄 AI prompt to create missing element (workflow or SOP)
- 🔄 Section 3: Coexistence blueprint (analysis, recommendations, future state artifacts)
- 🔄 Operations Liaison Agent (describe current process, design target state)
- 🔄 Ready to move to Business Outcomes pillar

**Status:** 🔄 Needs implementation

### **Business Outcomes Pillar Requirements**
- 🔄 Display pillar summaries (Content, Insights, Operations)
- 🔄 Solution Liaison Agent (prompt for additional context/files)
- 🔄 Final analysis (roadmap + POC proposal)
- 🔄 Ready for user to proceed

**Status:** 🔄 Needs implementation

---

## 🏗️ Implementation Plan

### **Phase 1: Operations Pillar Backend (Week 1)**

#### **1.1 OperationsOrchestrator**
**Location:** `backend/journey/orchestrators/operations_orchestrator/operations_orchestrator.py`

**Key Methods:**
```python
async def generate_workflow_from_file(file_id, options)
async def generate_sop_from_file(file_id, options)
async def generate_coexistence_blueprint(current_state, target_state)
async def get_workflow(workflow_id)
async def get_sop(sop_id)
async def get_coexistence_blueprint(blueprint_id)
```

**Integration:**
- Uses `WorkflowConversionService` (Journey realm service)
- Uses `SOPBuilderService` (Journey realm service)
- Uses `CoexistenceAnalysisService` (Journey realm service)
- Uses Content realm services for file retrieval

#### **1.2 Operations Services**
**Services to Build:**
- `WorkflowConversionService` - Convert files to workflows/SOPs
- `SOPBuilderService` - Build SOPs via wizard
- `CoexistenceAnalysisService` - Analyze and generate coexistence blueprints

**Pattern:** RealmServiceBase with micro-modules (build from scratch, don't reuse old)

#### **1.3 OperationsLiaisonAgent**
**Location:** `backend/journey/agents/operations_liaison_agent/`

**Capabilities:**
- Help users describe current processes (→ SOP builder wizard)
- Help design target state coexistence (→ Coexistence analyzer)
- Navigate Operations pillar features
- Answer questions about workflows, SOPs, coexistence

**MCP Tools:**
- `operations_generate_workflow` - Generate workflow from file
- `operations_generate_sop` - Generate SOP from file
- `operations_generate_coexistence` - Generate coexistence blueprint
- `operations_describe_process` - Start SOP wizard from description
- `operations_design_coexistence` - Design coexistence from description

### **Phase 2: Business Outcomes Pillar Backend (Week 1-2)**

#### **2.1 BusinessOutcomesOrchestrator**
**Location:** `backend/solution/orchestrators/business_outcomes_orchestrator/business_outcomes_orchestrator.py`

**Key Methods:**
```python
async def get_pillar_summaries(user_id)
async def generate_roadmap(pillar_outputs, business_context)
async def generate_poc_proposal(pillar_outputs, poc_type)
async def get_roadmap(roadmap_id)
async def get_poc_proposal(poc_id)
```

**Integration:**
- Uses `RoadmapGenerationService` (Solution realm service)
- Uses `POCGenerationService` (Solution realm service)
- Retrieves pillar outputs from Content, Insights, Operations realms

#### **2.2 Business Outcomes Services**
**Services to Build:**
- `RoadmapGenerationService` - Generate strategic roadmaps
- `POCGenerationService` - Generate POC proposals with financials

**Pattern:** RealmServiceBase with micro-modules (build from scratch, don't reuse old)

#### **2.3 SolutionLiaisonAgent**
**Location:** `backend/solution/agents/solution_liaison_agent/`

**Capabilities:**
- Help users understand pillar summaries
- Prompt for additional context/files
- Guide roadmap and POC generation
- Answer questions about business outcomes

**MCP Tools:**
- `solution_get_pillar_summaries` - Get summaries from all pillars
- `solution_generate_roadmap` - Generate roadmap from pillar outputs
- `solution_generate_poc` - Generate POC proposal from pillar outputs
- `solution_add_context` - Add additional context/files

### **Phase 3: Frontend Integration (Week 2-3)**

#### **3.1 Landing Page**
**Component:** `symphainy-frontend/src/pages/LandingPage.tsx`

**Features:**
- Welcome message
- GuideAgent chat interface
- Goal collection form
- Data suggestion based on goals
- Navigation to Content pillar

#### **3.2 Operations Pillar UI**
**Component:** `symphainy-frontend/src/pages/OperationsPillar.tsx`

**Sections:**
1. **Top Cards:**
   - Select existing file(s) card
   - Upload new file card (redirects to Content)
   - Generate from scratch card (triggers Operations Liaison)

2. **Section 2: Workflow/SOP Generation**
   - File selection/display
   - Workflow visualization component
   - SOP visualization component
   - AI prompt to create missing element

3. **Section 3: Coexistence Blueprint**
   - Coexistence analysis display
   - Recommendations display
   - Future state artifacts (SOP/workflow)

4. **Side Panel:**
   - Operations Liaison Agent chat

#### **3.3 Business Outcomes Pillar UI**
**Component:** `symphainy-frontend/src/pages/BusinessOutcomesPillar.tsx`

**Sections:**
1. **Pillar Summaries Display:**
   - Content pillar summary (files uploaded, parsed)
   - Insights pillar summary (insights gained, recommendations)
   - Operations pillar summary (coexistence blueprint)

2. **Solution Liaison Agent:**
   - Chat interface for additional context/files

3. **Final Analysis:**
   - Roadmap visualization
   - POC proposal display (with financials)

#### **3.4 Shared Components**
**Components to Create/Update:**
- `FileUploader.tsx` - Enhanced with mainframe binary/copybook support
- `DataPreview.tsx` - Preview parsed data (parquet, JSON)
- `MetadataPreview.tsx` - Preview content metadata
- `WorkflowVisualization.tsx` - Visual workflow display
- `SOPVisualization.tsx` - Visual SOP display
- `CoexistenceBlueprint.tsx` - Coexistence blueprint display
- `RoadmapVisualization.tsx` - Roadmap visualization
- `POCProposal.tsx` - POC proposal display
- `AgentChat.tsx` - Reusable agent chat component

### **Phase 4: API Integration (Week 3)**

#### **4.1 Operations Pillar Endpoints**
**Frontend Gateway Routes:**
- `POST /api/v1/operations-pillar/generate-workflow`
- `POST /api/v1/operations-pillar/generate-sop`
- `POST /api/v1/operations-pillar/generate-coexistence`
- `GET /api/v1/operations-pillar/workflow/{workflow_id}`
- `GET /api/v1/operations-pillar/sop/{sop_id}`
- `GET /api/v1/operations-pillar/coexistence/{blueprint_id}`

#### **4.2 Business Outcomes Pillar Endpoints**
**Frontend Gateway Routes:**
- `GET /api/v1/business-outcomes-pillar/pillar-summaries`
- `POST /api/v1/business-outcomes-pillar/generate-roadmap`
- `POST /api/v1/business-outcomes-pillar/generate-poc`
- `GET /api/v1/business-outcomes-pillar/roadmap/{roadmap_id}`
- `GET /api/v1/business-outcomes-pillar/poc/{poc_id}`

### **Phase 5: Agent Integration (Week 3-4)**

#### **5.1 OperationsLiaisonAgent**
- Create agent service
- Register MCP tools
- Integrate with OperationsOrchestrator
- Connect to frontend chat interface

#### **5.2 SolutionLiaisonAgent**
- Create agent service
- Register MCP tools
- Integrate with BusinessOutcomesOrchestrator
- Connect to frontend chat interface

#### **5.3 GuideAgent Enhancement**
- Add pillar navigation guidance
- Add goal-based data suggestions
- Add journey progression guidance

---

## 🎯 Implementation Checklist

### **Backend (Operations)**
- [ ] Create `WorkflowConversionService` (Journey realm)
- [ ] Create `SOPBuilderService` (Journey realm)
- [ ] Create `CoexistenceAnalysisService` (Journey realm)
- [ ] Create `OperationsOrchestrator`
- [ ] Create `OperationsLiaisonAgent`
- [ ] Add Operations pillar API endpoints
- [ ] Test Operations pillar workflows

### **Backend (Business Outcomes)**
- [ ] Create `RoadmapGenerationService` (Solution realm)
- [ ] Create `POCGenerationService` (Solution realm)
- [ ] Create `BusinessOutcomesOrchestrator`
- [ ] Create `SolutionLiaisonAgent`
- [ ] Add Business Outcomes pillar API endpoints
- [ ] Test Business Outcomes pillar workflows

### **Frontend**
- [ ] Create/update Landing page
- [ ] Create Operations pillar page
- [ ] Create Business Outcomes pillar page
- [ ] Create shared visualization components
- [ ] Integrate agent chat interfaces
- [ ] Add navigation between pillars
- [ ] Test end-to-end user journey

### **Integration**
- [ ] Connect frontend to backend APIs
- [ ] Integrate all agents with frontend
- [ ] Test full user journey (Content → Insights → Operations → Business Outcomes)
- [ ] Validate all MVP requirements

---

## 📚 References

- MVP Description: `docs/MVP_Description_For_Business_and_Technical_Readiness.md`
- Journey/Solution Refactoring Plan: `docs/JOURNEY_SOLUTION_REALMS_REFACTORING_PLAN.md`
- Enabling Services Refactoring Plan: `docs/ENABLING_SERVICES_REFACTORING_PLAN.md`









