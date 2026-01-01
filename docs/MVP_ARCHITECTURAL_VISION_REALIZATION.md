# MVP Architectural Vision Realization

**Date:** December 15, 2024  
**Status:** 🎯 **ARCHITECTURAL VISION DOCUMENT**  
**Goal:** Ensure MVP artifacts are actual solutions/journeys in the platform

---

## 🎯 Core Architectural Vision

**Key Principle:** MVP "artifacts" (workflows, SOPs, coexistence blueprints, roadmaps, POC proposals) are not just display objects - they are **actual solutions and journeys** stored in the platform.

---

## 🏗️ Artifact Storage Architecture

### **Journey Artifacts (Operations Pillar)**

**What Are Journey Artifacts:**
- Workflows (BPMN format)
- SOPs (structured document format)
- Coexistence Blueprints (analysis + recommendations + future state artifacts)

**How They're Stored:**
```python
# Via Journey Orchestrator Service
journey_artifact = await journey_orchestrator.create_journey_artifact(
    artifact_type="workflow",  # or "sop", "coexistence_blueprint"
    artifact_data={
        "workflow_definition": {...},  # BPMN format
        "visualization": {...}  # For frontend display
    },
    journey_id=None,  # Standalone artifact (can be part of journey later)
    user_context=user_context
)
```

**Benefits:**
- ✅ Discoverable via Curator (`get_journey_artifact(artifact_id)`)
- ✅ Trackable via Conductor (can be part of workflow orchestration)
- ✅ Stored via Librarian (persistent storage)
- ✅ Can be composed into larger journeys
- ✅ Versioned and auditable

**Example Journey Composition:**
```python
# A user's Operations pillar journey could be:
journey = {
    "journey_id": "operations_journey_123",
    "milestones": [
        {
            "milestone_id": "m1",
            "artifact_id": "workflow_123",  # Generated workflow
            "type": "workflow"
        },
        {
            "milestone_id": "m2",
            "artifact_id": "sop_456",  # Generated SOP
            "type": "sop"
        },
        {
            "milestone_id": "m3",
            "artifact_id": "blueprint_789",  # Coexistence blueprint
            "type": "coexistence_blueprint"
        }
    ]
}
```

### **Solution Artifacts (Business Outcomes Pillar)**

**What Are Solution Artifacts:**
- Roadmaps (strategic planning with phases, milestones, timeline)
- POC Proposals (comprehensive proposals with financials, timeline, success criteria)

**How They're Stored:**
```python
# Via Solution Composer Service
solution_artifact = await solution_composer.create_solution_artifact(
    artifact_type="roadmap",  # or "poc_proposal"
    artifact_data={
        "roadmap": {
            "phases": [...],
            "milestones": [...],
            "timeline": {...}
        },
        "pillar_outputs": {
            "content": {...},
            "insights": {...},
            "operations": {...}
        },
        "visualization": {...}  # For frontend display
    },
    solution_id=None,  # Standalone artifact (can be part of solution later)
    user_context=user_context
)
```

**Benefits:**
- ✅ Discoverable via Curator (`get_solution_artifact(artifact_id)`)
- ✅ Trackable via Solution Analytics (progress tracking, ROI measurement)
- ✅ Stored via Librarian (persistent storage)
- ✅ Can be composed into larger solutions
- ✅ Versioned and auditable

**Example Solution Composition:**
```python
# A user's Business Outcomes pillar solution could be:
solution = {
    "solution_id": "business_outcomes_solution_123",
    "phases": [
        {
            "phase_id": "p1",
            "artifact_id": "roadmap_123",  # Generated roadmap
            "type": "roadmap"
        },
        {
            "phase_id": "p2",
            "artifact_id": "poc_proposal_456",  # Generated POC
            "type": "poc_proposal"
        }
    ],
    "pillar_outputs": {
        "content": {...},
        "insights": {...},
        "operations": {...}
    }
}
```

---

## 🔄 Artifact Lifecycle

### **Creation Flow (Operations Pillar)**

1. **User generates workflow from file:**
   ```
   User → OperationsOrchestrator.generate_workflow_from_file()
   → WorkflowConversionService.convert_file_to_workflow()
   → Journey Orchestrator.create_journey_artifact()
   → Returns workflow_id + journey_artifact_id
   ```

2. **User generates SOP from workflow (bidirectional):**
   ```
   User → OperationsOrchestrator.convert_workflow_to_sop()
   → WorkflowConversionService.convert_workflow_to_sop()
   → Journey Orchestrator.create_journey_artifact()
   → Returns sop_id + journey_artifact_id
   ```

3. **User creates SOP via chat wizard:**
   ```
   User → OperationsLiaisonAgent (chat)
   → Agent calls operations_start_sop_wizard()
   → SOPBuilderService.start_sop_wizard()
   → Agent guides user through steps
   → Agent calls operations_complete_sop_wizard()
   → SOPBuilderService.generate_sop_from_wizard()
   → Journey Orchestrator.create_journey_artifact()
   → Returns sop_id + journey_artifact_id
   ```

4. **User generates coexistence blueprint:**
   ```
   User → OperationsOrchestrator.generate_coexistence_blueprint()
   → CoexistenceAnalysisService.analyze_coexistence()  # Evaluates AI optimization
   → CoexistenceAnalysisService.generate_coexistence_blueprint()
   → Journey Orchestrator.create_journey_artifact()
   → Returns blueprint_id + journey_artifact_id
   ```

### **Creation Flow (Business Outcomes Pillar)**

1. **User generates roadmap:**
   ```
   User → BusinessOutcomesOrchestrator.generate_roadmap()
   → RoadmapGenerationService.generate_roadmap()
   → Solution Composer.create_solution_artifact()
   → Returns roadmap_id + solution_artifact_id
   ```

2. **User generates POC proposal:**
   ```
   User → BusinessOutcomesOrchestrator.generate_poc_proposal()
   → POCGenerationService.generate_poc_proposal()
   → Solution Composer.create_solution_artifact()
   → Returns poc_id + solution_artifact_id
   ```

### **Retrieval Flow (Frontend Display)**

1. **Frontend requests workflow:**
   ```
   Frontend → GET /api/v1/operations-pillar/workflow/{workflow_id}
   → OperationsOrchestrator.get_workflow()
   → Journey Orchestrator.get_journey_artifact()
   → Returns workflow_definition + visualization data
   ```

2. **Frontend requests roadmap:**
   ```
   Frontend → GET /api/v1/business-outcomes-pillar/roadmap/{roadmap_id}
   → BusinessOutcomesOrchestrator.get_roadmap()
   → Solution Composer.get_solution_artifact()
   → Returns roadmap + visualization data
   ```

---

## 🎯 MVP Functionality Guarantees

### **Operations Pillar - All Requirements Met:**

1. ✅ **Display Workflow and SOP**
   - Workflows displayed as BPMN diagrams (via `WorkflowVisualization.tsx`)
   - SOPs displayed as structured documents (via `SOPVisualization.tsx`)
   - Both retrieved from Journey artifacts

2. ✅ **Bidirectional Conversion**
   - `convert_workflow_to_sop()` - Workflow → SOP
   - `convert_sop_to_workflow()` - SOP → Workflow
   - Both create new Journey artifacts

3. ✅ **Wizard Agent via Chat**
   - Operations Liaison Agent can trigger SOP wizard via chat
   - Agent guides user through wizard steps
   - Agent completes wizard and generates SOP
   - SOP stored as Journey artifact

4. ✅ **Coexistence Optimizer**
   - `analyze_coexistence()` evaluates AI optimization opportunities
   - `generate_coexistence_blueprint()` creates blueprint with:
     - Analysis (AI opportunities, coexistence patterns)
     - Recommendations
     - Future state artifacts (AI-enabled SOP/workflow)
   - Blueprint stored as Journey artifact

### **Business Outcomes Pillar - All Requirements Met:**

1. ✅ **Combine Pillar Outputs**
   - Roadmap generated from Content, Insights, Operations outputs
   - POC proposal generated from Content, Insights, Operations outputs
   - Both stored as Solution artifacts

2. ✅ **Flexible Input**
   - Works with partial pillar outputs (doesn't require all)
   - If only Content: Focus on data migration roadmap
   - If only Insights: Focus on analytics roadmap
   - If only Operations: Focus on process optimization roadmap
   - If all three: Comprehensive roadmap

3. ✅ **Artifact Storage**
   - Roadmaps stored as Solution artifacts
   - POC proposals stored as Solution artifacts
   - Both discoverable, trackable, versioned

---

## 🔗 Platform Integration

### **Curator Discovery**

```python
# Artifacts are discoverable via Curator
workflow_artifact = await curator.get_journey_artifact("artifact_123")
roadmap_artifact = await curator.get_solution_artifact("artifact_456")
```

### **Conductor Workflow Integration**

```python
# Artifacts can be part of workflows
workflow = await conductor.create_workflow(
    workflow_definition={
        "steps": [
            {"type": "journey_artifact", "artifact_id": "workflow_123"},
            {"type": "journey_artifact", "artifact_id": "sop_456"}
        ]
    }
)
```

### **Solution Analytics Integration**

```python
# Solution artifacts tracked via Solution Analytics
analytics = await solution_analytics.track_solution_progress(
    solution_id="solution_123",
    artifact_id="roadmap_123"
)
```

---

## ✅ Verification Checklist

### **Operations Pillar**
- [ ] Workflows stored as Journey artifacts
- [ ] SOPs stored as Journey artifacts
- [ ] Coexistence blueprints stored as Journey artifacts
- [ ] Artifacts discoverable via Curator
- [ ] Artifacts trackable via Conductor
- [ ] Bidirectional conversion creates new artifacts
- [ ] Chat wizard creates artifacts
- [ ] Frontend displays artifacts from Journey storage

### **Business Outcomes Pillar**
- [ ] Roadmaps stored as Solution artifacts
- [ ] POC proposals stored as Solution artifacts
- [ ] Artifacts discoverable via Curator
- [ ] Artifacts trackable via Solution Analytics
- [ ] Flexible input handling (partial pillar outputs)
- [ ] Frontend displays artifacts from Solution storage

### **Architectural Vision**
- [ ] All artifacts are actual solutions/journeys (not just display objects)
- [ ] Artifacts can be composed into larger journeys/solutions
- [ ] Artifacts are versioned and auditable
- [ ] Artifacts integrate with platform services (Curator, Conductor, Librarian)

---

## 📚 References

- MVP Functionality Implementation Plan: `docs/MVP_FUNCTIONALITY_IMPLEMENTATION_PLAN.md`
- Journey/Solution Refactoring Plan: `docs/JOURNEY_SOLUTION_REALMS_REFACTORING_PLAN.md`
- MVP Showcase Implementation Plan: `docs/MVP_SHOWCASE_IMPLEMENTATION_PLAN.md`









