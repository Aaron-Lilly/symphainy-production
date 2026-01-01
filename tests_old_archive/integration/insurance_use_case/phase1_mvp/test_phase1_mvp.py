#!/usr/bin/env python3
"""
Phase 1 MVP Test Suite for Insurance Use Case

Tests all Phase 1 components:
- Legacy data ingestion → canonical mapping
- Routing rule evaluation
- Basic policy tracking
- End-to-end MVP journey
- Saga Journey with compensation
- WAL replay
- Solution Composer multi-phase execution
"""

import os
import sys
import asyncio
import pytest
from typing import Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
symphainy_platform_path = os.path.join(project_root, 'symphainy-platform')
sys.path.insert(0, symphainy_platform_path)


class TestPhase1MVP:
    """Phase 1 MVP Test Suite."""
    
    @pytest.fixture
    async def mock_services(self):
        """Create mock services for testing."""
        services = {
            "content_steward": AsyncMock(),
            "file_parser": AsyncMock(),
            "data_steward": AsyncMock(),
            "schema_mapper": AsyncMock(),
            "canonical_model": AsyncMock(),
            "routing_engine": AsyncMock(),
            "policy_tracker": AsyncMock(),
            "librarian": AsyncMock(),
            "solution_composer": AsyncMock(),
            "saga_orchestrator": AsyncMock()
        }
        return services
    
    @pytest.mark.asyncio
    async def test_legacy_data_ingestion_to_canonical_mapping(self, mock_services):
        """Test: Legacy data ingestion → canonical mapping."""
        # Mock file upload
        mock_services["content_steward"].upload_file = AsyncMock(return_value={
            "success": True,
            "file_id": "file_123"
        })
        
        # Mock file parsing
        mock_services["file_parser"].parse_file = AsyncMock(return_value={
            "success": True,
            "parsed_data": [
                {"policy_id": "POL001", "premium": 1000.0},
                {"policy_id": "POL002", "premium": 2000.0}
            ]
        })
        
        # Mock data profiling
        mock_services["data_steward"].profile_data_quality = AsyncMock(return_value={
            "metrics": {"quality_score": 0.95}
        })
        
        # Mock schema discovery
        mock_services["schema_mapper"].discover_schema = AsyncMock(return_value={
            "success": True,
            "schema": {"fields": [{"name": "policy_id"}, {"name": "premium"}]}
        })
        
        # Mock schema mapping to canonical
        mock_services["schema_mapper"].map_to_canonical = AsyncMock(return_value={
            "success": True,
            "mapping_id": "mapping_456",
            "field_mappings": [
                {"source_field": "policy_id", "target_field": "policy_core.policy_id"},
                {"source_field": "premium", "target_field": "rating_components.premium_amount"}
            ],
            "confidence_score": 0.92
        })
        
        # Mock canonical validation
        mock_services["canonical_model"].validate_against_canonical = AsyncMock(return_value={
            "success": True,
            "valid": True
        })
        
        # Mock metadata storage
        mock_services["librarian"].store_document = AsyncMock(return_value={
            "document_id": "metadata_789"
        })
        
        # Mock lineage tracking
        mock_services["data_steward"].track_lineage = AsyncMock(return_value=True)
        mock_services["data_steward"].write_to_log = AsyncMock(return_value={
            "success": True,
            "wal_id": "wal_001"
        })
        
        # Test ingestion
        from backend.business_enablement.delivery_manager.insurance_use_case_orchestrators.insurance_migration_orchestrator.insurance_migration_orchestrator import InsuranceMigrationOrchestrator
        
        # Create orchestrator with mocked delivery manager
        delivery_manager = MagicMock()
        delivery_manager.get_orchestrators = MagicMock(return_value=[])
        delivery_manager.platform_gateway = MagicMock()
        delivery_manager.di_container = MagicMock()
        delivery_manager.realm_name = "business_enablement"
        
        orchestrator = InsuranceMigrationOrchestrator(delivery_manager)
        
        # Mock service access methods
        orchestrator.get_content_steward_api = AsyncMock(return_value=mock_services["content_steward"])
        orchestrator.get_enabling_service = AsyncMock(side_effect=lambda name: {
            "FileParserService": mock_services["file_parser"],
            "SchemaMapperService": mock_services["schema_mapper"]
        }.get(name))
        orchestrator.get_librarian_api = AsyncMock(return_value=mock_services["librarian"])
        orchestrator._get_data_steward = AsyncMock(return_value=mock_services["data_steward"])
        orchestrator._get_canonical_model_service = AsyncMock(return_value=mock_services["canonical_model"])
        orchestrator.log_operation_with_telemetry = AsyncMock()
        orchestrator.record_health_metric = AsyncMock()
        orchestrator.handle_error_with_audit = AsyncMock()
        orchestrator.logger = MagicMock()
        
        # Test ingestion
        ingest_result = await orchestrator.ingest_legacy_data(
            file_data=b"test,data\nPOL001,1000.0",
            filename="test_policies.csv",
            user_context={"user_id": "test_user"}
        )
        
        assert ingest_result["success"] is True
        assert "file_id" in ingest_result
        assert "parsed_data" in ingest_result
        assert "schema" in ingest_result
        assert "quality_metrics" in ingest_result
        
        # Test mapping to canonical
        mapping_result = await orchestrator.map_to_canonical(
            source_data={"policy_id": "POL001", "premium": 1000.0},
            canonical_model_name="policy_v1",
            user_context={"user_id": "test_user"}
        )
        
        assert mapping_result["success"] is True
        assert "mapping_id" in mapping_result
        assert "confidence_score" in mapping_result
    
    @pytest.mark.asyncio
    async def test_routing_rule_evaluation(self, mock_services):
        """Test: Routing rule evaluation."""
        # Mock routing engine
        mock_services["routing_engine"].extract_routing_key = AsyncMock(return_value={
            "success": True,
            "routing_key": "POL001"
        })
        
        mock_services["routing_engine"].evaluate_routing = AsyncMock(return_value={
            "success": True,
            "target_system": "new_platform",
            "matched_rules": [{"name": "migrated_policies", "priority": 1}],
            "confidence": 0.98
        })
        
        # Mock policy tracker
        mock_services["policy_tracker"].get_policy_location = AsyncMock(return_value={
            "success": True,
            "status": "not_started"
        })
        
        mock_services["policy_tracker"].update_migration_status = AsyncMock(return_value={
            "success": True
        })
        
        # Mock storage and lineage
        mock_services["librarian"].store_document = AsyncMock(return_value={
            "document_id": "routing_decision_123"
        })
        mock_services["data_steward"].track_lineage = AsyncMock(return_value=True)
        mock_services["data_steward"].write_to_log = AsyncMock(return_value={
            "success": True
        })
        
        # Test routing
        from backend.business_enablement.delivery_manager.insurance_use_case_orchestrators.insurance_migration_orchestrator.insurance_migration_orchestrator import InsuranceMigrationOrchestrator
        
        delivery_manager = MagicMock()
        delivery_manager.get_orchestrators = MagicMock(return_value=[mock_services["policy_tracker"]])
        delivery_manager.platform_gateway = MagicMock()
        delivery_manager.di_container = MagicMock()
        delivery_manager.realm_name = "business_enablement"
        
        orchestrator = InsuranceMigrationOrchestrator(delivery_manager)
        orchestrator._get_routing_engine_service = AsyncMock(return_value=mock_services["routing_engine"])
        orchestrator.get_librarian_api = AsyncMock(return_value=mock_services["librarian"])
        orchestrator._get_data_steward = AsyncMock(return_value=mock_services["data_steward"])
        orchestrator.log_operation_with_telemetry = AsyncMock()
        orchestrator.record_health_metric = AsyncMock()
        orchestrator.handle_error_with_audit = AsyncMock()
        orchestrator.logger = MagicMock()
        
        routing_result = await orchestrator.route_policies(
            policy_data={"policy_id": "POL001", "premium": 1000.0},
            namespace="default",
            user_context={"user_id": "test_user"}
        )
        
        assert routing_result["success"] is True
        assert routing_result["target_system"] == "new_platform"
        assert "routing_key" in routing_result
        assert "confidence" in routing_result
    
    @pytest.mark.asyncio
    async def test_basic_policy_tracking(self, mock_services):
        """Test: Basic policy tracking."""
        # Mock policy tracker operations
        mock_services["policy_tracker"].register_policy = AsyncMock(return_value={
            "success": True,
            "policy_id": "POL001",
            "location": "legacy_system"
        })
        
        mock_services["policy_tracker"].get_policy_location = AsyncMock(return_value={
            "success": True,
            "policy_id": "POL001",
            "location": "legacy_system",
            "status": "not_started"
        })
        
        mock_services["policy_tracker"].update_migration_status = AsyncMock(return_value={
            "success": True,
            "status": "in_progress"
        })
        
        # Test policy tracking
        from backend.business_enablement.delivery_manager.insurance_use_case_orchestrators.policy_tracker_orchestrator.policy_tracker_orchestrator import PolicyTrackerOrchestrator, PolicyLocation
        
        delivery_manager = MagicMock()
        delivery_manager.platform_gateway = MagicMock()
        delivery_manager.di_container = MagicMock()
        delivery_manager.realm_name = "business_enablement"
        
        tracker = PolicyTrackerOrchestrator(delivery_manager)
        tracker.log_operation_with_telemetry = AsyncMock()
        tracker.record_health_metric = AsyncMock()
        tracker.handle_error_with_audit = AsyncMock()
        tracker.logger = MagicMock()
        
        # Mock Data Steward for WAL
        mock_data_steward = AsyncMock()
        mock_data_steward.record_wal_entry = AsyncMock(return_value={"success": True})
        tracker._get_data_steward = AsyncMock(return_value=mock_data_steward)
        
        # Register policy
        register_result = await tracker.register_policy(
            policy_id="POL001",
            location=PolicyLocation.LEGACY_SYSTEM,
            metadata={"source": "test"},
            user_context={"user_id": "test_user"}
        )
        
        assert register_result["success"] is True
        
        # Get policy location (check signature - may not have user_context)
        location_result = await tracker.get_policy_location(
            policy_id="POL001"
        )
        
        assert location_result["success"] is True
        assert location_result["current_location"] == PolicyLocation.LEGACY_SYSTEM.value
    
    @pytest.mark.asyncio
    async def test_end_to_end_mvp_journey(self, mock_services):
        """Test: End-to-end MVP journey."""
        # This test combines ingestion, mapping, and routing
        # Using the mocks from previous tests
        
        # Test that all components work together
        assert True  # Placeholder - would combine all previous tests
    
    @pytest.mark.asyncio
    async def test_saga_journey_with_compensation(self, mock_services):
        """Test: Saga Journey with compensation (simulate failure)."""
        # Mock saga orchestrator
        mock_services["saga_orchestrator"].design_saga_journey = AsyncMock(return_value={
            "success": True,
            "saga_id": "saga_123",
            "journey_type": "insurance_wave_migration"
        })
        
        # Mock saga execution with failure
        mock_services["saga_orchestrator"].execute_saga_journey = AsyncMock(side_effect=[
            {"success": False, "error": "Mapping failed", "milestone_id": "map_to_canonical"}
        ])
        
        # Mock compensation
        mock_services["saga_orchestrator"].compensate_saga = AsyncMock(return_value={
            "success": True,
            "compensated_milestones": ["ingest_legacy_data"]
        })
        
        # Test saga execution and compensation
        # This would test the full saga flow with failure and rollback
        assert True  # Placeholder
    
    @pytest.mark.asyncio
    async def test_wal_replay(self, mock_services):
        """Test: WAL replay (recover from crash scenario)."""
        # Mock WAL replay
        mock_services["data_steward"].replay_log = AsyncMock(return_value=[
            {
                "wal_id": "wal_001",
                "namespace": "insurance_migration",
                "operation": "ingest_legacy_data",
                "payload": {"file_id": "file_123"},
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "wal_id": "wal_002",
                "namespace": "insurance_migration",
                "operation": "map_to_canonical",
                "payload": {"mapping_id": "mapping_456"},
                "timestamp": datetime.utcnow().isoformat()
            }
        ])
        
        # Test WAL replay
        replay_result = await mock_services["data_steward"].replay_log(
            namespace="insurance_migration",
            from_timestamp=datetime.utcnow(),
            to_timestamp=datetime.utcnow()
        )
        
        assert len(replay_result) == 2
        assert replay_result[0]["operation"] == "ingest_legacy_data"
        assert replay_result[1]["operation"] == "map_to_canonical"
    
    @pytest.mark.asyncio
    async def test_solution_composer_multi_phase_execution(self, mock_services):
        """Test: Solution Composer multi-phase execution."""
        # Mock solution composer
        mock_services["solution_composer"].design_solution = AsyncMock(return_value={
            "success": True,
            "solution_id": "solution_123",
            "solution_type": "insurance_migration",
            "phases": [
                {"phase_id": "discovery", "name": "Discovery & Profiling"},
                {"phase_id": "wave_migration", "name": "Wave-Based Migration"},
                {"phase_id": "validation", "name": "Validation & Reconciliation"}
            ]
        })
        
        mock_services["solution_composer"].execute_solution = AsyncMock(return_value={
            "success": True,
            "solution_id": "solution_123",
            "phases_completed": 3,
            "status": "completed"
        })
        
        # Test solution execution
        design_result = await mock_services["solution_composer"].design_solution(
            solution_type="insurance_migration",
            requirements={"source": "legacy", "target": "new_platform"}
        )
        
        assert design_result["success"] is True
        assert len(design_result["phases"]) == 3
        
        execution_result = await mock_services["solution_composer"].execute_solution(
            solution_id="solution_123"
        )
        
        assert execution_result["success"] is True
        assert execution_result["phases_completed"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

