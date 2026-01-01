# Insurance Use Case: Solution Composer Templates

**Date:** December 2024  
**Service:** Solution Composer Service  
**Use Case:** Insurance Data Migration

---

## 🎯 Overview

This document defines Solution Composer templates for the Insurance Use Case, providing multi-phase solution orchestration that composes Journey orchestrators.

### **Key Concepts**

1. **Solution**: Complete end-to-end solution composed of multiple phases
2. **Phase**: Single phase of solution execution (uses Journey orchestrator)
3. **Journey Types**: Structured, Session, MVP, or Saga Journey
4. **Phase Progression**: Automatic or manual progression between phases

---

## 📋 Template 1: Insurance Migration Solution

### **Purpose**

Complete insurance data migration solution with 3 phases: Discovery, Wave Migration, and Validation.

### **Template Definition**

```python
INSURANCE_MIGRATION_SOLUTION = {
    "solution_type": "insurance_migration",
    "name": "Insurance Data Migration Solution",
    "description": "Multi-phase insurance data migration with wave-based orchestration",
    "version": "1.0.0",
    "phases": [
        {
            "phase_id": "discovery",
            "name": "Discovery & Profiling",
            "description": "Ingest, profile, and analyze legacy insurance data",
            "journey_type": "structured",
            "journey_template": "insurance_discovery",
            "estimated_duration": "2-4 weeks",
            "dependencies": [],
            "next_phases": ["wave_migration"],
            "completion_criteria": {
                "files_ingested": True,
                "data_profiled": True,
                "metadata_extracted": True,
                "quality_assessed": True
            }
        },
        {
            "phase_id": "wave_migration",
            "name": "Wave-Based Migration",
            "description": "Wave-based migration with automatic compensation",
            "journey_type": "saga",  # ⭐ Uses Saga Journey!
            "journey_template": "insurance_wave_migration",
            "estimated_duration": "4-8 weeks",
            "dependencies": ["discovery"],
            "next_phases": ["validation"],
            "completion_criteria": {
                "waves_executed": True,
                "policies_migrated": True,
                "quality_gates_passed": True
            },
            "compensation_handlers": {
                "ingest_legacy_data": "delete_ingested_data",
                "map_to_canonical": "revert_canonical_mapping",
                "route_policies": "revert_routing",
                "execute_migration": "rollback_migration",
                "validate_results": "revert_validation"
            }
        },
        {
            "phase_id": "validation",
            "name": "Validation & Reconciliation",
            "description": "Validate migrated data and reconcile with source",
            "journey_type": "structured",
            "journey_template": "insurance_validation",
            "estimated_duration": "2-4 weeks",
            "dependencies": ["wave_migration"],
            "next_phases": [],
            "completion_criteria": {
                "data_validated": True,
                "reconciliation_complete": True,
                "audit_report_generated": True
            }
        }
    ],
    "metadata": {
        "client_id": None,  # Set during solution design
        "source_system": None,
        "target_system": None,
        "migration_strategy": "wave_based",
        "estimated_total_duration": "8-16 weeks"
    }
}
```

### **Usage Example**

```python
# Design Insurance Migration Solution
solution = await solution_composer.design_solution(
    solution_type="insurance_migration",
    requirements={
        "client_id": "client_abc",
        "source_system": "legacy_mainframe",
        "target_system": "new_platform",
        "migration_strategy": "wave_based",
        "wave_config": {
            "wave_0_size": 100,
            "wave_1_size": 500,
            "wave_2_size": 1000
        }
    },
    user_context=user_context
)

solution_id = solution["solution_id"]

# Deploy Solution
deployment = await solution_composer.deploy_solution(
    solution_id=solution_id,
    user_id="user_123",
    context={
        "client_id": "client_abc",
        "source_system": "legacy_mainframe",
        "target_system": "new_platform"
    },
    user_context=user_context
)

# Execute Phase 1: Discovery
phase_1_result = await solution_composer.execute_solution_phase(
    solution_id=solution_id,
    phase_id="discovery",
    user_id="user_123",
    user_context=user_context
)

# Execute Phase 2: Wave Migration (Saga Journey)
phase_2_result = await solution_composer.execute_solution_phase(
    solution_id=solution_id,
    phase_id="wave_migration",
    user_id="user_123",
    user_context=user_context
)

# Execute Phase 3: Validation
phase_3_result = await solution_composer.execute_solution_phase(
    solution_id=solution_id,
    phase_id="validation",
    user_id="user_123",
    user_context=user_context
)
```

---

## 📋 Template 2: Insurance Discovery Journey (Phase 1)

### **Purpose**

Structured journey for Phase 1: Discovery & Profiling.

### **Template Definition**

```python
INSURANCE_DISCOVERY_JOURNEY = {
    "journey_type": "insurance_discovery",
    "name": "Insurance Discovery Journey",
    "description": "Structured journey for legacy data discovery and profiling",
    "version": "1.0.0",
    "milestones": [
        {
            "milestone_id": "ingest_files",
            "name": "Ingest Legacy Files",
            "description": "Upload and ingest legacy insurance data files",
            "service": "ContentAnalysisOrchestrator",
            "operation": "upload_file",
            "next_milestones": ["profile_data"],
            "completion_criteria": {
                "files_uploaded": True,
                "files_parsed": True
            }
        },
        {
            "milestone_id": "profile_data",
            "name": "Profile Data",
            "description": "Profile ingested data for quality and structure",
            "service": "ContentAnalysisOrchestrator",
            "operation": "profile_file",
            "next_milestones": ["extract_metadata"],
            "completion_criteria": {
                "data_profiled": True,
                "quality_metrics_calculated": True
            }
        },
        {
            "milestone_id": "extract_metadata",
            "name": "Extract Metadata",
            "description": "Extract metadata and schema information",
            "service": "Librarian",
            "operation": "extract_metadata",
            "next_milestones": ["assess_quality"],
            "completion_criteria": {
                "metadata_extracted": True,
                "schema_identified": True
            }
        },
        {
            "milestone_id": "assess_quality",
            "name": "Assess Data Quality",
            "description": "Assess data quality and identify issues",
            "service": "DataSteward",
            "operation": "assess_data_quality",
            "next_milestones": [],
            "completion_criteria": {
                "quality_assessed": True,
                "quality_report_generated": True
            }
        }
    ]
}
```

---

## 📋 Template 3: Insurance Validation Journey (Phase 3)

### **Purpose**

Structured journey for Phase 3: Validation & Reconciliation.

### **Template Definition**

```python
INSURANCE_VALIDATION_JOURNEY = {
    "journey_type": "insurance_validation",
    "name": "Insurance Validation Journey",
    "description": "Structured journey for migrated data validation",
    "version": "1.0.0",
    "milestones": [
        {
            "milestone_id": "validate_data_quality",
            "name": "Validate Data Quality",
            "description": "Validate migrated data quality",
            "service": "DataSteward",
            "operation": "validate_data_quality",
            "next_milestones": ["reconcile_with_source"],
            "completion_criteria": {
                "quality_validated": True,
                "quality_score_acceptable": True
            }
        },
        {
            "milestone_id": "reconcile_with_source",
            "name": "Reconcile with Source",
            "description": "Reconcile migrated data with source system",
            "service": "PolicyTrackerOrchestrator",
            "operation": "reconcile_policies",
            "next_milestones": ["generate_audit_report"],
            "completion_criteria": {
                "reconciliation_complete": True,
                "discrepancies_resolved": True
            }
        },
        {
            "milestone_id": "generate_audit_report",
            "name": "Generate Audit Report",
            "description": "Generate comprehensive audit report",
            "service": "PolicyTrackerOrchestrator",
            "operation": "generate_audit_report",
            "next_milestones": [],
            "completion_criteria": {
                "audit_report_generated": True,
                "audit_report_approved": True
            }
        }
    ]
}
```

---

## 🔧 Solution Execution Flow

### **Phase Execution**

```python
# Solution Composer executes phase
async def execute_solution_phase(
    self,
    solution_id: str,
    phase_id: str,
    user_id: str,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute solution phase using appropriate Journey orchestrator.
    """
    # Get solution and phase configuration
    solution = await self.get_solution(solution_id)
    phase = solution["phases"][phase_id]
    
    # Get appropriate journey orchestrator based on type
    if phase["journey_type"] == "saga":
        orchestrator = self.saga_journey_orchestrator
    elif phase["journey_type"] == "structured":
        orchestrator = self.structured_journey_orchestrator
    elif phase["journey_type"] == "session":
        orchestrator = self.session_journey_orchestrator
    elif phase["journey_type"] == "mvp":
        orchestrator = self.mvp_journey_orchestrator
    
    # Design journey from template
    journey = await orchestrator.design_journey(
        journey_type=phase["journey_template"],
        requirements=solution["metadata"]
    )
    
    # Execute journey
    if phase["journey_type"] == "saga":
        # Saga Journey execution
        result = await orchestrator.execute_saga_journey(
            journey_id=journey["journey_id"],
            user_id=user_id,
            context=solution["metadata"]
        )
    else:
        # Structured/Session/MVP execution
        result = await orchestrator.execute_journey(
            journey_id=journey["journey_id"],
            user_id=user_id,
            context=solution["metadata"]
        )
    
    # Track phase completion
    await self.track_phase_completion(solution_id, phase_id, result)
    
    return result
```

### **Phase Progression**

```python
# Automatic progression after phase completion
if phase.get("completion"):
    # Solution complete
    deployment["status"] = "completed"
else:
    # Move to next phase
    next_phases = phase.get("next_phases", [])
    if next_phases:
        deployment["current_phase"] = next_phases[0]
```

---

## 📊 Solution State Management

### **Solution State**

```python
solution_state = {
    "solution_id": solution_id,
    "solution_type": "insurance_migration",
    "status": "in_progress",  # in_progress | paused | completed | failed
    "current_phase": "discovery",
    "completed_phases": [],
    "phase_results": {
        "discovery": {...},
        "wave_migration": {...},
        "validation": {...}
    },
    "metadata": {
        "client_id": "client_abc",
        "source_system": "legacy_mainframe",
        "target_system": "new_platform"
    },
    "started_at": "2024-12-01T10:00:00Z",
    "completed_at": None
}
```

### **State Persistence**

Solution state is persisted via Librarian:

```python
# Store solution state
await self.store_document(
    document_data=solution_state,
    metadata={
        "type": "solution_deployment",
        "solution_id": solution_id,
        "user_id": user_id
    }
)
```

---

## 🧪 Testing Scenarios

### **Scenario 1: Complete Solution Execution**

```python
# Design solution
solution = await solution_composer.design_solution(
    solution_type="insurance_migration",
    requirements={...}
)

# Deploy solution
deployment = await solution_composer.deploy_solution(
    solution_id=solution["solution_id"],
    user_id="user_123",
    context={...}
)

# Execute all phases
await solution_composer.execute_solution_phase(
    solution_id=solution["solution_id"],
    phase_id="discovery",
    user_id="user_123"
)

await solution_composer.execute_solution_phase(
    solution_id=solution["solution_id"],
    phase_id="wave_migration",
    user_id="user_123"
)

await solution_composer.execute_solution_phase(
    solution_id=solution["solution_id"],
    phase_id="validation",
    user_id="user_123"
)

# Verify completion
status = await solution_composer.get_solution_status(
    solution_id=solution["solution_id"],
    user_id="user_123"
)
assert status["status"] == "completed"
```

### **Scenario 2: Phase Failure with Rollback**

```python
# Phase 2 (Saga Journey) fails
phase_2_result = await solution_composer.execute_solution_phase(
    solution_id=solution["solution_id"],
    phase_id="wave_migration",
    user_id="user_123"
)

# Saga Journey automatically compensates
# Solution status: paused (waiting for resolution)
status = await solution_composer.get_solution_status(
    solution_id=solution["solution_id"],
    user_id="user_123"
)
assert status["status"] == "paused"
```

---

## 📚 Related Documentation

- [Solution Composer Service](../symphainy-platform/backend/solution/services/solution_composer_service/solution_composer_service.py)
- [Solution Realm Complete](../symphainy-platform/backend/solution/SOLUTION_REALM_COMPLETE.md)
- [Saga Journey Templates](./SAGA_JOURNEY_TEMPLATES.md)
- [Insurance Use Case Implementation Plan](./INSURANCE_USE_CASE_IMPLEMENTATION_PLAN_V2.md)

---

**Last Updated:** December 2024  
**Status:** Ready for Implementation











