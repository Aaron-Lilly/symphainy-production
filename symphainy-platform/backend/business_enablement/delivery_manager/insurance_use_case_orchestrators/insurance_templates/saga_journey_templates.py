#!/usr/bin/env python3
"""
Insurance Use Case: Saga Journey Templates

Saga Journey templates for Insurance Use Case with automatic compensation.
"""

from typing import Dict, Any, Optional

# Template 1: Insurance Wave Migration Saga
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
            "operation": "execute_wave",
            "compensation_handler": "rollback_wave",
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
            "handler": "rollback_wave",
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

# Template 2: Policy Mapping Saga
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
            "operation": "ingest_legacy_data",
            "compensation_handler": "delete_ingested_data",
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
            "handler": "delete_ingested_data",
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

# Template 3: Wave Validation Saga
WAVE_VALIDATION_SAGA = {
    "journey_type": "wave_validation",
    "name": "Wave Validation Saga",
    "description": "Validate completed wave migration with compensation if validation fails",
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
            "operation": "reconcile_systems",
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

# Template registry
SAGA_TEMPLATES = {
    "insurance_wave_migration": INSURANCE_WAVE_MIGRATION_SAGA,
    "policy_mapping": POLICY_MAPPING_SAGA,
    "wave_validation": WAVE_VALIDATION_SAGA
}


async def register_saga_templates(
    saga_orchestrator,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Register Saga Journey templates with Saga Journey Orchestrator.
    
    This function pre-registers the templates so they can be used via journey_type.
    
    Args:
        saga_orchestrator: SagaJourneyOrchestratorService instance
        user_context: Optional user context
    
    Returns:
        Registration result
    """
    if not saga_orchestrator:
        return {
            "success": False,
            "error": "Saga Journey Orchestrator not available"
        }
    
    try:
        registered_count = 0
        
        for journey_type, template in SAGA_TEMPLATES.items():
            # Extract compensation handlers from template
            compensation_handlers = {}
            for milestone in template.get("milestones", []):
                milestone_id = milestone.get("milestone_id")
                compensation_handler = milestone.get("compensation_handler")
                if milestone_id and compensation_handler:
                    compensation_handlers[milestone_id] = compensation_handler
            
            # Design saga journey (this registers it)
            result = await saga_orchestrator.design_saga_journey(
                journey_type=journey_type,
                requirements={
                    "template": template,
                    "name": template.get("name"),
                    "description": template.get("description")
                },
                compensation_handlers=compensation_handlers,
                user_context=user_context
            )
            
            if result.get("success"):
                registered_count += 1
                saga_orchestrator.logger.info(f"✅ Registered Saga template: {journey_type}")
            else:
                saga_orchestrator.logger.warning(f"⚠️ Failed to register Saga template {journey_type}: {result.get('error')}")
        
        return {
            "success": True,
            "registered_count": registered_count,
            "templates": list(SAGA_TEMPLATES.keys())
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }











