#!/usr/bin/env python3
"""
Insurance Use Case: Solution Composer Templates

Solution Composer templates for Insurance Use Case with multi-phase orchestration.
"""

from typing import Dict, Any, Optional

# Template 1: Insurance Migration Solution
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
                "execute_migration": "rollback_wave",
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

# Template 2: Insurance Discovery Journey (Phase 1)
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

# Template 3: Insurance Validation Journey (Phase 3)
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
            "operation": "reconcile_systems",
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

# Template registry
SOLUTION_TEMPLATES = {
    "insurance_migration": INSURANCE_MIGRATION_SOLUTION
}

JOURNEY_TEMPLATES = {
    "insurance_discovery": INSURANCE_DISCOVERY_JOURNEY,
    "insurance_validation": INSURANCE_VALIDATION_JOURNEY
}


async def register_solution_templates(
    solution_composer,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Register Solution Composer templates with Solution Composer Service.
    
    This function adds the insurance migration solution template to the service.
    
    Args:
        solution_composer: SolutionComposerService instance
        user_context: Optional user context
    
    Returns:
        Registration result
    """
    if not solution_composer:
        return {
            "success": False,
            "error": "Solution Composer Service not available"
        }
    
    try:
        # Add insurance migration solution template
        solution_composer.solution_templates["insurance_migration"] = INSURANCE_MIGRATION_SOLUTION
        
        solution_composer.logger.info(f"✅ Registered Solution template: insurance_migration")
        
        return {
            "success": True,
            "registered_count": 1,
            "templates": ["insurance_migration"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }











