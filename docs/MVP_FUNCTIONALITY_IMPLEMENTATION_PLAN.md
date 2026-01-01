# MVP Functionality Implementation Plan - Complete & Detailed

**Date:** December 15, 2024  
**Status:** 🎯 **DETAILED IMPLEMENTATION PLAN**  
**Goal:** Ensure ALL MVP functionality is actually delivered with artifacts stored as solutions/journeys

---

## 🎯 Critical MVP Requirements

### **Operations Pillar - Must Deliver:**

1. ✅ **Display Workflow and SOP** - Visual elements showing workflow diagrams and SOP documents
2. ✅ **Bidirectional Conversion** - Generate workflow from SOP AND SOP from workflow
3. ✅ **Wizard Agent via Chat** - Operations Liaison Agent can trigger SOP wizard through chat conversation
4. ✅ **Coexistence Optimizer** - Evaluates how AI can optimize workflow/SOP process and generates coexistence blueprint

### **Business Outcomes Pillar - Must Deliver:**

1. ✅ **Combine Pillar Outputs** - Roadmap and POC proposal from Content, Insights, Operations outputs
2. ✅ **Flexible Input** - Doesn't require all pillars (works with partial outputs)
3. ✅ **Artifact Storage** - Roadmaps and POC proposals stored as Solution artifacts

### **Architectural Vision - Must Realize:**

1. ✅ **Artifacts = Solutions/Journeys** - Workflows, SOPs, coexistence blueprints stored as Journey artifacts
2. ✅ **Roadmaps/POCs = Solutions** - Roadmaps and POC proposals stored as Solution artifacts
3. ✅ **Platform Integration** - Artifacts discoverable via Curator, trackable via Conductor, stored via Librarian

---

## 📋 Phase 1: Operations Pillar - Complete Implementation

### **1.1 WorkflowConversionService - Bidirectional Conversion**

**Location:** `backend/journey/services/workflow_conversion_service/`

**Key Requirements:**
- ✅ Convert file → Workflow (BPMN format)
- ✅ Convert file → SOP (structured document format)
- ✅ Convert Workflow → SOP (bidirectional)
- ✅ Convert SOP → Workflow (bidirectional)
- ✅ Store workflows as Journey artifacts (via Journey Orchestrator)
- ✅ Store SOPs as Journey artifacts (via Journey Orchestrator)

**Implementation Details:**

```python
class WorkflowConversionService(RealmServiceBase):
    async def convert_file_to_workflow(
        self, 
        file_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convert file to workflow.
        
        Returns:
            {
                "success": True,
                "workflow_id": "workflow_123",
                "workflow_definition": {...},  # BPMN format
                "journey_artifact_id": "artifact_123",  # ✅ Stored as Journey artifact
                "visualization": {...}  # For frontend display
            }
        """
        # 1. Retrieve file from Content realm
        # 2. Parse file to extract process steps
        # 3. Generate BPMN workflow definition
        # 4. Store as Journey artifact via Journey Orchestrator
        # 5. Generate visualization data for frontend
        pass
    
    async def convert_file_to_sop(
        self,
        file_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convert file to SOP.
        
        Returns:
            {
                "success": True,
                "sop_id": "sop_123",
                "sop_definition": {...},  # Structured SOP format
                "journey_artifact_id": "artifact_456",  # ✅ Stored as Journey artifact
                "visualization": {...}  # For frontend display
            }
        """
        pass
    
    async def convert_workflow_to_sop(
        self,
        workflow_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convert workflow to SOP (bidirectional conversion).
        
        Returns:
            {
                "success": True,
                "sop_id": "sop_789",
                "sop_definition": {...},
                "journey_artifact_id": "artifact_789",
                "source_workflow_id": workflow_id
            }
        """
        # 1. Retrieve workflow from Journey artifact
        # 2. Convert BPMN to structured SOP format
        # 3. Store new SOP as Journey artifact
        pass
    
    async def convert_sop_to_workflow(
        self,
        sop_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convert SOP to workflow (bidirectional conversion).
        
        Returns:
            {
                "success": True,
                "workflow_id": "workflow_789",
                "workflow_definition": {...},
                "journey_artifact_id": "artifact_789",
                "source_sop_id": sop_id
            }
        """
        # 1. Retrieve SOP from Journey artifact
        # 2. Convert structured SOP to BPMN format
        # 3. Store new workflow as Journey artifact
        pass
```

**Journey Artifact Storage:**
- Workflows stored via `JourneyOrchestratorService.create_journey_artifact()`
- SOPs stored via `JourneyOrchestratorService.create_journey_artifact()`
- Artifacts tracked in Journey realm, discoverable via Curator

### **1.2 SOPBuilderService - Wizard via Chat Agent**

**Location:** `backend/journey/services/sop_builder_service/`

**Key Requirements:**
- ✅ Wizard session management
- ✅ Step-by-step SOP creation
- ✅ Integration with Operations Liaison Agent (chat-triggered)
- ✅ Store completed SOPs as Journey artifacts

**Implementation Details:**

```python
class SOPBuilderService(RealmServiceBase):
    async def start_sop_wizard(
        self,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start SOP wizard session (can be triggered by agent).
        
        Returns:
            {
                "session_token": "session_123",
                "current_step": "purpose",
                "wizard_state": {...}
            }
        """
        pass
    
    async def process_wizard_step(
        self,
        session_token: str,
        step_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process wizard step (can be called by agent on behalf of user).
        
        Returns:
            {
                "success": True,
                "next_step": "scope",
                "wizard_state": {...},
                "is_complete": False
            }
        """
        pass
    
    async def generate_sop_from_wizard(
        self,
        session_token: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate SOP from completed wizard.
        
        Returns:
            {
                "success": True,
                "sop_id": "sop_123",
                "sop_definition": {...},
                "journey_artifact_id": "artifact_123"  # ✅ Stored as Journey artifact
            }
        """
        # 1. Retrieve wizard state
        # 2. Generate structured SOP from wizard data
        # 3. Store as Journey artifact
        pass
```

**Agent Integration:**
- Operations Liaison Agent can call `start_sop_wizard()` when user describes process
- Agent guides user through wizard steps via chat
- Agent calls `process_wizard_step()` based on user responses
- Agent calls `generate_sop_from_wizard()` when complete

### **1.3 CoexistenceAnalysisService - AI Optimization Evaluator**

**Location:** `backend/journey/services/coexistence_analysis_service/`

**Key Requirements:**
- ✅ Analyze current workflow/SOP for AI optimization opportunities
- ✅ Evaluate AI-human coexistence patterns
- ✅ Generate coexistence blueprint with analysis and recommendations
- ✅ Generate future state artifacts (AI-enabled SOP/workflow)
- ✅ Store blueprint as Journey artifact

**Implementation Details:**

```python
class CoexistenceAnalysisService(RealmServiceBase):
    async def analyze_coexistence(
        self,
        current_state: Dict[str, Any],  # Current workflow/SOP
        target_state: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze how AI can optimize the workflow/SOP process.
        
        Returns:
            {
                "success": True,
                "analysis": {
                    "ai_optimization_opportunities": [...],
                    "coexistence_patterns": [...],
                    "recommendations": [...],
                    "efficiency_gains": {...}
                }
            }
        """
        # 1. Analyze current workflow/SOP for AI opportunities
        # 2. Evaluate coexistence patterns (collaborative, delegated, augmented, autonomous)
        # 3. Generate optimization recommendations
        # 4. Calculate potential efficiency gains
        pass
    
    async def generate_coexistence_blueprint(
        self,
        analysis_result: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate coexistence blueprint with future state artifacts.
        
        Returns:
            {
                "success": True,
                "blueprint_id": "blueprint_123",
                "blueprint": {
                    "analysis": {...},
                    "recommendations": [...],
                    "future_state_sop": {...},  # AI-enabled SOP
                    "future_state_workflow": {...}  # AI-enabled workflow
                },
                "journey_artifact_id": "artifact_123"  # ✅ Stored as Journey artifact
            }
        """
        # 1. Generate future state SOP (with AI integration points)
        # 2. Generate future state workflow (with AI automation)
        # 3. Store blueprint as Journey artifact
        pass
```

**AI Optimization Analysis:**
- Identify tasks suitable for AI automation
- Identify tasks requiring human judgment
- Recommend coexistence patterns (collaborative, delegated, augmented, autonomous)
- Calculate efficiency gains (time savings, cost reduction, quality improvement)

### **1.4 OperationsOrchestrator - Complete Orchestration**

**Location:** `backend/journey/orchestrators/operations_orchestrator/`

**Key Requirements:**
- ✅ Orchestrate all Operations pillar workflows
- ✅ Integrate with Operations Liaison Agent
- ✅ Store all artifacts as Journey artifacts
- ✅ Provide API endpoints for frontend

**SOA APIs:**

```python
class OperationsOrchestrator(OrchestratorBase):
    # File-based generation
    async def generate_workflow_from_file(file_id, options)
    async def generate_sop_from_file(file_id, options)
    
    # Bidirectional conversion
    async def convert_workflow_to_sop(workflow_id, options)
    async def convert_sop_to_workflow(sop_id, options)
    
    # Coexistence analysis
    async def generate_coexistence_blueprint(current_state, target_state)
    
    # Agent-triggered workflows
    async def create_sop_from_description(description)  # Via Operations Liaison
    async def create_coexistence_from_description(description)  # Via Operations Liaison
    
    # Artifact retrieval
    async def get_workflow(workflow_id)  # Returns workflow + visualization
    async def get_sop(sop_id)  # Returns SOP + visualization
    async def get_coexistence_blueprint(blueprint_id)  # Returns blueprint
```

### **1.5 OperationsLiaisonAgent - Chat-Triggered Wizard**

**Location:** `backend/journey/agents/operations_liaison_agent/`

**Key Requirements:**
- ✅ Chat interface for SOP wizard
- ✅ Guide users through process description
- ✅ Trigger coexistence analysis from chat
- ✅ MCP tools for Operations orchestrator

**MCP Tools:**

```python
# SOP Wizard via Chat
"operations_start_sop_wizard" - Start SOP wizard session
"operations_process_wizard_step" - Process wizard step based on user chat
"operations_complete_sop_wizard" - Complete wizard and generate SOP

# Coexistence Analysis via Chat
"operations_analyze_coexistence" - Analyze current process for AI optimization
"operations_generate_coexistence" - Generate coexistence blueprint from description

# Workflow/SOP Management
"operations_generate_workflow_from_file" - Generate workflow from file
"operations_generate_sop_from_file" - Generate SOP from file
"operations_convert_workflow_to_sop" - Convert workflow to SOP
"operations_convert_sop_to_workflow" - Convert SOP to workflow
```

**Chat Flow Example:**
```
User: "I want to create an SOP for our customer onboarding process"
Agent: "Great! Let's start by understanding the purpose of this process..."
[Agent calls operations_start_sop_wizard]
Agent: "What is the main goal of your customer onboarding process?"
User: "To onboard new customers within 24 hours"
[Agent calls operations_process_wizard_step with step_data]
Agent: "Perfect! Now let's define the scope..."
[Continues through wizard steps]
Agent: "Your SOP is ready! Should I also analyze how AI could optimize this process?"
User: "Yes, please!"
[Agent calls operations_analyze_coexistence, then operations_generate_coexistence]
```

---

## 📋 Phase 2: Business Outcomes Pillar - Complete Implementation

### **2.1 RoadmapGenerationService - Flexible Pillar Input**

**Location:** `backend/solution/services/roadmap_generation_service/`

**Key Requirements:**
- ✅ Generate roadmap from pillar outputs (Content, Insights, Operations)
- ✅ Work with partial inputs (doesn't require all pillars)
- ✅ Store roadmap as Solution artifact
- ✅ Generate roadmap visualization

**Implementation Details:**

```python
class RoadmapGenerationService(RealmServiceBase):
    async def generate_roadmap(
        self,
        pillar_outputs: Dict[str, Any],  # Content, Insights, Operations (optional)
        business_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate strategic roadmap from pillar outputs.
        
        pillar_outputs structure:
        {
            "content": {...},  # Optional
            "insights": {...},  # Optional
            "operations": {...}  # Optional
        }
        
        Returns:
            {
                "success": True,
                "roadmap_id": "roadmap_123",
                "roadmap": {
                    "phases": [...],
                    "milestones": [...],
                    "timeline": {...},
                    "dependencies": [...]
                },
                "solution_artifact_id": "artifact_123",  # ✅ Stored as Solution artifact
                "visualization": {...}  # For frontend display
            }
        """
        # 1. Analyze available pillar outputs
        # 2. Generate roadmap phases based on available data
        # 3. Create timeline and milestones
        # 4. Store as Solution artifact via Solution Orchestrator
        # 5. Generate visualization data
        pass
```

**Flexible Input Handling:**
- If only Content: Generate roadmap focused on data migration/transformation
- If only Insights: Generate roadmap focused on analytics implementation
- If only Operations: Generate roadmap focused on process optimization
- If all three: Generate comprehensive roadmap combining all aspects

### **2.2 POCGenerationService - Comprehensive Proposals**

**Location:** `backend/solution/services/poc_generation_service/`

**Key Requirements:**
- ✅ Generate POC proposal from pillar outputs
- ✅ Calculate financials (ROI, NPV, IRR)
- ✅ Generate executive summary
- ✅ Store POC as Solution artifact
- ✅ Work with partial inputs

**Implementation Details:**

```python
class POCGenerationService(RealmServiceBase):
    async def generate_poc_proposal(
        self,
        pillar_outputs: Dict[str, Any],  # Content, Insights, Operations (optional)
        poc_type: str = "hybrid",
        options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive POC proposal.
        
        Returns:
            {
                "success": True,
                "poc_id": "poc_123",
                "proposal": {
                    "executive_summary": {...},
                    "objectives": [...],
                    "scope": {...},
                    "timeline": {...},
                    "financials": {
                        "roi": 150,
                        "npv": 500000,
                        "irr": 25,
                        "payback_period": 12
                    },
                    "risks": [...],
                    "success_criteria": [...]
                },
                "solution_artifact_id": "artifact_123",  # ✅ Stored as Solution artifact
            }
        """
        pass
```

### **2.3 BusinessOutcomesOrchestrator - Complete Orchestration**

**Location:** `backend/solution/orchestrators/business_outcomes_orchestrator/`

**Key Requirements:**
- ✅ Retrieve pillar summaries (flexible - works with partial data)
- ✅ Generate roadmap from available pillar outputs
- ✅ Generate POC proposal from available pillar outputs
- ✅ Store all artifacts as Solution artifacts
- ✅ Integrate with Solution Liaison Agent

**SOA APIs:**

```python
class BusinessOutcomesOrchestrator(OrchestratorBase):
    async def get_pillar_summaries(
        self,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get summaries from available pillars (doesn't require all).
        
        Returns:
            {
                "content": {...},  # If available
                "insights": {...},  # If available
                "operations": {...}  # If available
            }
        """
        pass
    
    async def generate_roadmap(
        self,
        pillar_outputs: Dict[str, Any],  # Flexible - any combination
        business_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate roadmap from available pillar outputs."""
        pass
    
    async def generate_poc_proposal(
        self,
        pillar_outputs: Dict[str, Any],  # Flexible - any combination
        poc_type: str = "hybrid",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate POC proposal from available pillar outputs."""
        pass
```

---

## 📋 Phase 3: Artifact Storage as Solutions/Journeys

### **3.1 Journey Artifacts (Workflows, SOPs, Coexistence Blueprints)**

**Storage Pattern:**
- Workflows stored via `JourneyOrchestratorService.create_journey_artifact()`
- SOPs stored via `JourneyOrchestratorService.create_journey_artifact()`
- Coexistence blueprints stored via `JourneyOrchestratorService.create_journey_artifact()`

**Implementation:**
```python
# In OperationsOrchestrator
async def _store_as_journey_artifact(
    self,
    artifact_type: str,  # "workflow", "sop", "coexistence_blueprint"
    artifact_data: Dict[str, Any],
    user_context: Dict[str, Any]
) -> str:
    """Store artifact as Journey artifact."""
    journey_orchestrator = await self.get_journey_orchestrator()
    artifact = await journey_orchestrator.create_journey_artifact(
        artifact_type=artifact_type,
        artifact_data=artifact_data,
        journey_id=None,  # Standalone artifact
        user_context=user_context
    )
    return artifact["artifact_id"]
```

**Benefits:**
- Artifacts discoverable via Curator
- Artifacts trackable via Conductor workflows
- Artifacts stored via Librarian
- Artifacts can be composed into larger journeys

### **3.2 Solution Artifacts (Roadmaps, POC Proposals)**

**Storage Pattern:**
- Roadmaps stored via `SolutionComposerService.create_solution_artifact()`
- POC proposals stored via `SolutionComposerService.create_solution_artifact()`

**Implementation:**
```python
# In BusinessOutcomesOrchestrator
async def _store_as_solution_artifact(
    self,
    artifact_type: str,  # "roadmap", "poc_proposal"
    artifact_data: Dict[str, Any],
    user_context: Dict[str, Any]
) -> str:
    """Store artifact as Solution artifact."""
    solution_composer = await self.get_solution_composer()
    artifact = await solution_composer.create_solution_artifact(
        artifact_type=artifact_type,
        artifact_data=artifact_data,
        solution_id=None,  # Standalone artifact
        user_context=user_context
    )
    return artifact["artifact_id"]
```

**Benefits:**
- Artifacts discoverable via Curator
- Artifacts trackable via Solution analytics
- Artifacts stored via Librarian
- Artifacts can be composed into larger solutions

---

## 📋 Phase 4: Frontend Integration - Visual Display

### **4.1 Workflow/SOP Visualization**

**Components:**
- `WorkflowVisualization.tsx` - BPMN diagram display
- `SOPVisualization.tsx` - Structured SOP document display
- `CoexistenceBlueprint.tsx` - Blueprint with analysis, recommendations, future state artifacts

**Requirements:**
- Display workflow as interactive BPMN diagram
- Display SOP as structured document with sections
- Display coexistence blueprint with:
  - Analysis section (AI optimization opportunities)
  - Recommendations section
  - Future state SOP/workflow side-by-side comparison

### **4.2 Roadmap/POC Visualization**

**Components:**
- `RoadmapVisualization.tsx` - Timeline, phases, milestones
- `POCProposal.tsx` - Executive summary, financials, timeline

**Requirements:**
- Display roadmap as interactive timeline
- Display POC proposal with financials (ROI, NPV, IRR)
- Show pillar summaries (what was used to generate)

---

## ✅ Implementation Checklist

### **Operations Pillar**
- [ ] WorkflowConversionService with bidirectional conversion
- [ ] SOPBuilderService with wizard pattern
- [ ] CoexistenceAnalysisService with AI optimization analysis
- [ ] OperationsOrchestrator with all APIs
- [ ] OperationsLiaisonAgent with chat-triggered wizard
- [ ] Journey artifact storage for workflows, SOPs, blueprints
- [ ] Frontend visualization components

### **Business Outcomes Pillar**
- [ ] RoadmapGenerationService with flexible input
- [ ] POCGenerationService with financials
- [ ] BusinessOutcomesOrchestrator with flexible APIs
- [ ] Solution artifact storage for roadmaps, POCs
- [ ] Frontend visualization components

### **Architectural Vision**
- [ ] Journey artifacts stored via Journey Orchestrator
- [ ] Solution artifacts stored via Solution Composer
- [ ] Artifacts discoverable via Curator
- [ ] Artifacts trackable via Conductor/Solution Analytics

---

## 📚 References

- MVP Description: `docs/MVP_Description_For_Business_and_Technical_Readiness.md`
- Journey/Solution Refactoring Plan: `docs/JOURNEY_SOLUTION_REALMS_REFACTORING_PLAN.md`
- MVP Showcase Implementation Plan: `docs/MVP_SHOWCASE_IMPLEMENTATION_PLAN.md`









