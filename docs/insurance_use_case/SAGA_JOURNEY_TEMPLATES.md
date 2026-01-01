# Insurance Use Case: Saga Journey Templates

**Date:** December 2024  
**Service:** Saga Journey Orchestrator Service  
**Use Case:** Insurance Data Migration

---

## 🎯 Overview

This document defines Saga Journey templates for the Insurance Use Case, providing automatic compensation (rollback) for wave-based migration operations.

### **Key Concepts**

1. **Saga Pattern**: Sequence of local transactions with automatic compensation
2. **Compensation Handlers**: Domain-specific undo operations
3. **Reverse-Order Compensation**: Unwinds in reverse order of execution
4. **Idempotency**: Compensation operations are safe to retry

---

## 📋 Template 1: Insurance Wave Migration Saga

### **Purpose**

Orchestrates wave-based insurance data migration with automatic compensation on failure.

### **Template Definition**

```python
INSURANCE_WAVE_MIGRATION_SAGA = {
    "journey_type": "insurance_wave_migration",
    "name": "Insurance Wave Migration Saga",
    "description": "Wave-based migration with automatic compensation",
    "version": "1.0.0",
    "milestones": [
        {
            "milestone_id": "ingest_legacy_data",
            "name": "Ingest Legacy Data",
            "description": "Ingest legacy insurance data files",
            "service": "InsuranceMigrationOrchestrator",
            "operation": "ingest_legacy_data",
            "compensation_handler": "delete_ingested_data",
            "compensation_service": "InsuranceMigrationOrchestrator",
            "timeout": 3600,  # 1 hour
            "retry_count": 3
        },
        {
            "milestone_id": "map_to_canonical",
            "name": "Map to Canonical Model",
            "description": "Map legacy data to canonical policy model",
            "service": "CanonicalModelService",
            "operation": "map_to_canonical",
            "compensation_handler": "revert_canonical_mapping",
            "compensation_service": "CanonicalModelService",
            "timeout": 1800,  # 30 minutes
            "retry_count": 3
        },
        {
            "milestone_id": "route_policies",
            "name": "Route Policies",
            "description": "Evaluate routing rules and select target system",
            "service": "RoutingEngineService",
            "operation": "evaluate_routing",
            "compensation_handler": "revert_routing",
            "compensation_service": "RoutingEngineService",
            "timeout": 600,  # 10 minutes
            "retry_count": 2
        },
        {
            "milestone_id": "execute_migration",
            "name": "Execute Migration",
            "description": "Execute wave migration to target system",
            "service": "WaveOrchestrator",
            "operation": "execute_wave_migration",
            "compensation_handler": "rollback_migration",
            "compensation_service": "WaveOrchestrator",
            "timeout": 7200,  # 2 hours
            "retry_count": 1  # Only retry once for migration
        },
        {
            "milestone_id": "validate_results",
            "name": "Validate Results",
            "description": "Validate migrated data quality and completeness",
            "service": "PolicyTrackerOrchestrator",
            "operation": "validate_migration",
            "compensation_handler": "revert_validation",
            "compensation_service": "PolicyTrackerOrchestrator",
            "timeout": 1800,  # 30 minutes
            "retry_count": 2
        }
    ],
    "compensation_handlers": {
        "ingest_legacy_data": {
            "handler": "delete_ingested_data",
            "service": "InsuranceMigrationOrchestrator",
            "description": "Delete ingested files and metadata",
            "idempotent": True
        },
        "map_to_canonical": {
            "handler": "revert_canonical_mapping",
            "service": "CanonicalModelService",
            "description": "Revert canonical mapping and restore original data",
            "idempotent": True
        },
        "route_policies": {
            "handler": "revert_routing",
            "service": "RoutingEngineService",
            "description": "Revert routing decisions and restore original state",
            "idempotent": True
        },
        "execute_migration": {
            "handler": "rollback_migration",
            "service": "WaveOrchestrator",
            "description": "Rollback migrated policies to source system",
            "idempotent": True
        },
        "validate_results": {
            "handler": "revert_validation",
            "service": "PolicyTrackerOrchestrator",
            "description": "Revert validation results and restore previous state",
            "idempotent": True
        }
    }
}
```

### **Usage Example**

```python
# Design Saga Journey
saga_journey = await saga_orchestrator.design_saga_journey(
    journey_type="insurance_wave_migration",
    requirements={
        "wave_id": "wave_001",
        "policies": ["policy_123", "policy_456", "policy_789"],
        "target_system": "new_platform",
        "client_id": "client_abc"
    },
    compensation_handlers={
        "ingest_legacy_data": "delete_ingested_data",
        "map_to_canonical": "revert_canonical_mapping",
        "route_policies": "revert_routing",
        "execute_migration": "rollback_migration",
        "validate_results": "revert_validation"
    },
    user_context=user_context
)

# Execute Saga Journey
execution = await saga_orchestrator.execute_saga_journey(
    journey_id=saga_journey["journey_id"],
    user_id="user_123",
    context={
        "wave_id": "wave_001",
        "policies": ["policy_123", "policy_456", "policy_789"]
    },
    user_context=user_context
)

saga_id = execution["saga_id"]

# Advance milestones (automatic via milestone completion)
# If milestone 4 (execute_migration) fails:
# - Automatically compensates milestone 3 (route_policies)
# - Automatically compensates milestone 2 (map_to_canonical)
# - Automatically compensates milestone 1 (ingest_legacy_data)
```

---

## 📋 Template 2: Policy Mapping Saga

### **Purpose**

Orchestrates mapping of a single policy from legacy to canonical model with compensation.

### **Template Definition**

```python
POLICY_MAPPING_SAGA = {
    "journey_type": "policy_mapping",
    "name": "Policy Mapping Saga",
    "description": "Map single policy to canonical model with compensation",
    "version": "1.0.0",
    "milestones": [
        {
            "milestone_id": "extract_policy_data",
            "name": "Extract Policy Data",
            "description": "Extract policy data from legacy system",
            "service": "InsuranceMigrationOrchestrator",
            "operation": "extract_policy_data",
            "compensation_handler": "revert_extraction",
            "compensation_service": "InsuranceMigrationOrchestrator",
            "timeout": 300,  # 5 minutes
            "retry_count": 3
        },
        {
            "milestone_id": "validate_policy_data",
            "name": "Validate Policy Data",
            "description": "Validate policy data quality",
            "service": "DataSteward",
            "operation": "validate_schema",
            "compensation_handler": "revert_validation",
            "compensation_service": "DataSteward",
            "timeout": 120,  # 2 minutes
            "retry_count": 2
        },
        {
            "milestone_id": "map_to_canonical",
            "name": "Map to Canonical",
            "description": "Map policy data to canonical model",
            "service": "CanonicalModelService",
            "operation": "map_to_canonical",
            "compensation_handler": "revert_canonical_mapping",
            "compensation_service": "CanonicalModelService",
            "timeout": 180,  # 3 minutes
            "retry_count": 3
        },
        {
            "milestone_id": "store_canonical",
            "name": "Store Canonical",
            "description": "Store canonical policy model",
            "service": "CanonicalModelService",
            "operation": "store_canonical_policy",
            "compensation_handler": "delete_canonical_policy",
            "compensation_service": "CanonicalModelService",
            "timeout": 60,  # 1 minute
            "retry_count": 2
        }
    ],
    "compensation_handlers": {
        "extract_policy_data": {
            "handler": "revert_extraction",
            "service": "InsuranceMigrationOrchestrator",
            "description": "Revert policy data extraction",
            "idempotent": True
        },
        "validate_policy_data": {
            "handler": "revert_validation",
            "service": "DataSteward",
            "description": "Revert validation results",
            "idempotent": True
        },
        "map_to_canonical": {
            "handler": "revert_canonical_mapping",
            "service": "CanonicalModelService",
            "description": "Revert canonical mapping",
            "idempotent": True
        },
        "store_canonical": {
            "handler": "delete_canonical_policy",
            "service": "CanonicalModelService",
            "description": "Delete stored canonical policy",
            "idempotent": True
        }
    }
}
```

---

## 📋 Template 3: Wave Validation Saga

### **Purpose**

Validates completed wave migration with compensation if validation fails.

### **Template Definition**

```python
WAVE_VALIDATION_SAGA = {
    "journey_type": "wave_validation",
    "name": "Wave Validation Saga",
    "description": "Validate wave migration results with compensation",
    "version": "1.0.0",
    "milestones": [
        {
            "milestone_id": "validate_data_quality",
            "name": "Validate Data Quality",
            "description": "Validate migrated data quality",
            "service": "DataSteward",
            "operation": "validate_data_quality",
            "compensation_handler": "revert_quality_validation",
            "compensation_service": "DataSteward",
            "timeout": 600,  # 10 minutes
            "retry_count": 2
        },
        {
            "milestone_id": "reconcile_with_source",
            "name": "Reconcile with Source",
            "description": "Reconcile migrated data with source system",
            "service": "PolicyTrackerOrchestrator",
            "operation": "reconcile_policies",
            "compensation_handler": "revert_reconciliation",
            "compensation_service": "PolicyTrackerOrchestrator",
            "timeout": 1800,  # 30 minutes
            "retry_count": 2
        },
        {
            "milestone_id": "generate_audit_report",
            "name": "Generate Audit Report",
            "description": "Generate audit report for wave migration",
            "service": "PolicyTrackerOrchestrator",
            "operation": "generate_audit_report",
            "compensation_handler": "delete_audit_report",
            "compensation_service": "PolicyTrackerOrchestrator",
            "timeout": 300,  # 5 minutes
            "retry_count": 1
        }
    ],
    "compensation_handlers": {
        "validate_data_quality": {
            "handler": "revert_quality_validation",
            "service": "DataSteward",
            "description": "Revert quality validation results",
            "idempotent": True
        },
        "reconcile_with_source": {
            "handler": "revert_reconciliation",
            "service": "PolicyTrackerOrchestrator",
            "description": "Revert reconciliation results",
            "idempotent": True
        },
        "generate_audit_report": {
            "handler": "delete_audit_report",
            "service": "PolicyTrackerOrchestrator",
            "description": "Delete generated audit report",
            "idempotent": True
        }
    }
}
```

---

## 🔧 Compensation Handler Implementation

### **Handler Discovery**

Compensation handlers are discovered via Curator:

```python
# Saga Journey discovers compensation handler
compensation_handler = await curator.discover_service_by_name(
    compensation_service_name
)

# Call compensation handler
result = await compensation_handler[compensation_handler_name](
    saga_id=saga_id,
    milestone_id=milestone_id,
    context=context
)
```

### **Handler Requirements**

All compensation handlers must be:

1. **Idempotent**: Safe to retry multiple times
2. **Domain-Specific**: Understand what "undo" means in that domain
3. **Reliable**: Must eventually succeed (with retries)
4. **Logged**: All compensation operations logged via WAL

### **Example Handler Implementation**

```python
# InsuranceMigrationOrchestrator.delete_ingested_data()
async def delete_ingested_data(
    self,
    saga_id: str,
    milestone_id: str,
    context: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Compensation handler: Delete ingested legacy data.
    
    Idempotent: Safe to call multiple times.
    """
    # Write to WAL before compensation
    await self.data_steward.write_to_log(
        namespace="saga_compensation",
        payload={
            "saga_id": saga_id,
            "milestone_id": milestone_id,
            "operation": "delete_ingested_data",
            "context": context
        },
        target="compensation_queue",
        user_context=user_context
    )
    
    # Get file IDs from context
    file_ids = context.get("file_ids", [])
    
    # Delete files (idempotent - safe to retry)
    deleted_files = []
    for file_id in file_ids:
        try:
            # Check if file exists (idempotent check)
            file_exists = await self.content_steward.get_file_metadata(file_id)
            if file_exists:
                await self.content_steward.delete_file(file_id)
                deleted_files.append(file_id)
        except FileNotFoundError:
            # Already deleted (idempotent)
            pass
    
    return {
        "success": True,
        "deleted_files": deleted_files,
        "saga_id": saga_id,
        "milestone_id": milestone_id
    }
```

---

## 📊 Saga State Tracking

### **State Transitions**

```
IN_PROGRESS → COMPLETED (all milestones succeed)
IN_PROGRESS → COMPENSATING (milestone fails)
COMPENSATING → COMPLETED (compensation succeeds)
COMPENSATING → FAILED (compensation fails)
```

### **State Persistence**

Saga state is persisted via Librarian and WAL:

```python
# Saga state stored in Librarian
saga_state = {
    "saga_id": saga_id,
    "journey_id": journey_id,
    "status": SagaStatus.IN_PROGRESS,
    "completed_milestones": ["ingest_legacy_data", "map_to_canonical"],
    "compensated_milestones": [],
    "compensation_handlers": {...},
    "execution_history": [...]
}

# Also logged via WAL for audit
await data_steward.write_to_log(
    namespace="saga_execution",
    payload={
        "saga_id": saga_id,
        "status": "in_progress",
        "completed_milestones": ["ingest_legacy_data", "map_to_canonical"]
    },
    target="saga_state_queue"
)
```

---

## 🧪 Testing Scenarios

### **Scenario 1: Successful Execution**

```python
# All milestones succeed
saga = await saga_orchestrator.execute_saga_journey(...)
await saga_orchestrator.advance_saga_step(saga_id, milestone_1_result)
await saga_orchestrator.advance_saga_step(saga_id, milestone_2_result)
await saga_orchestrator.advance_saga_step(saga_id, milestone_3_result)
await saga_orchestrator.advance_saga_step(saga_id, milestone_4_result)
await saga_orchestrator.advance_saga_step(saga_id, milestone_5_result)

# Status: COMPLETED
status = await saga_orchestrator.get_saga_status(saga_id)
assert status["status"] == "completed"
```

### **Scenario 2: Failure with Compensation**

```python
# Milestone 4 fails
saga = await saga_orchestrator.execute_saga_journey(...)
await saga_orchestrator.advance_saga_step(saga_id, milestone_1_result)  # ✅
await saga_orchestrator.advance_saga_step(saga_id, milestone_2_result)  # ✅
await saga_orchestrator.advance_saga_step(saga_id, milestone_3_result)  # ✅
await saga_orchestrator.advance_saga_step(saga_id, {"status": "failed"})  # ❌

# Automatic compensation triggered:
# 1. Compensate milestone 3 (revert_routing)
# 2. Compensate milestone 2 (revert_canonical_mapping)
# 3. Compensate milestone 1 (delete_ingested_data)

# Status: COMPLETED (compensation succeeded)
status = await saga_orchestrator.get_saga_status(saga_id)
assert status["status"] == "completed"
assert len(status["compensated_milestones"]) == 3
```

### **Scenario 3: Compensation Failure**

```python
# Milestone 4 fails, compensation for milestone 3 fails
# Status: FAILED
status = await saga_orchestrator.get_saga_status(saga_id)
assert status["status"] == "failed"
assert status["compensation_error"] is not None
```

---

## 📚 Related Documentation

- [Saga Journey Orchestrator Guide](../symphainy-platform/backend/journey/docs/SAGA_JOURNEY_ORCHESTRATOR.md)
- [Saga Pattern Documentation](../distributed_transaction_management_saga_choreography.md)
- [Insurance Use Case Implementation Plan](./INSURANCE_USE_CASE_IMPLEMENTATION_PLAN_V2.md)

---

**Last Updated:** December 2024  
**Status:** Ready for Implementation











