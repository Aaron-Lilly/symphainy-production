"""
Test Nurse Service - Smart City Role for Health Monitoring and Telemetry

Tests the Nurse service which handles system health monitoring, metric collection,
alert management, and telemetry data processing.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime
from typing import Dict, Any

from backend.smart_city.services.nurse.nurse_service import NurseService
from foundations.utility_foundation.utilities.security.security_service import UserContext
from tests.unit.layer_7_smart_city_roles.test_base import SmartCityRolesTestBase


class TestNurseService(SmartCityRolesTestBase):
    """Test Nurse Service implementation."""
    
    @pytest.mark.asyncio
    async def test_nurse_service_initialization(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Nurse service initialization."""
        service = NurseService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test basic initialization
        self.assert_service_initialization(service, [
            'utility_foundation', 'public_works_foundation', 'curator_foundation',
            'health_monitoring', 'telemetry_service', 'alert_manager'
        ])
        
        assert service.utility_foundation == mock_utility_foundation
        assert service.public_works_foundation == mock_public_works_foundation
        assert service.curator_foundation == mock_curator_foundation
    
    @pytest.mark.asyncio
    async def test_nurse_service_initialization_async(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Nurse service async initialization."""
        service = NurseService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test async initialization
        await service.initialize()
        
        # Verify health monitoring components are initialized
        assert service.health_monitoring is not None
        assert service.telemetry_service is not None
        assert service.alert_manager is not None
    
    @pytest.mark.asyncio
    async def test_nurse_health_monitoring_operations(self, mock_utility_foundation, mock_public_works_foundation, mock_curator_foundation, sample_user_context):
        """Test Nurse health monitoring operations."""
        service = NurseService(
            utility_foundation=mock_utility_foundation,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )
        
        await service.initialize()
        
        # Test perform_health_check
        health_check_result = await service.perform_health_check("analytics_service", sample_user_context)
        assert health_check_result is not None
        assert isinstance(health_check_result, dict)
        assert "status" in health_check_result
        assert "timestamp" in health_check_result
        
        # Test get_health_status
        health_status = await service.get_health_status("analytics_service", sample_user_context)
        assert health_status is not None
        assert isinstance(health_status, dict)
        assert "status" in health_status
        assert "last_check" in health_status
        
        # Test get_system_health
        system_health = await service.get_system_health(sample_user_context)
        assert system_health is not None
        assert isinstance(system_health, dict)
        assert "overall_status" in system_health
        assert "services" in system_health
    
    @pytest.mark.asyncio
    async def test_nurse_metric_collection_operations(self, mock_utility_foundation, mock_public_works_foundation, mock_curator_foundation, sample_user_context):
        """Test Nurse metric collection operations."""
        service = NurseService(
            utility_foundation=mock_utility_foundation,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )
        
        await service.initialize()
        
        # Test record_metric
        metric_data = {
            "metric_name": "response_time",
            "value": 150.5,
            "tags": {"service": "analytics", "endpoint": "/api/data"},
            "timestamp": datetime.utcnow().isoformat()
        }
        record_result = await service.record_metric(metric_data, sample_user_context)
        assert record_result is not None
        assert isinstance(record_result, dict)
        assert "recorded" in record_result
        
        # Test get_metrics
        metrics_result = await service.get_metrics("analytics_service", "response_time", sample_user_context)
        assert metrics_result is not None
        assert isinstance(metrics_result, list)
        
        # Test get_metric_summary
        summary_result = await service.get_metric_summary("analytics_service", sample_user_context)
        assert summary_result is not None
        assert isinstance(summary_result, dict)
        assert "total_metrics" in summary_result
        assert "average_values" in summary_result
    
    @pytest.mark.asyncio
    async def test_nurse_alert_management_operations(self, mock_utility_foundation, mock_public_works_foundation, mock_curator_foundation, sample_user_context):
        """Test Nurse alert management operations."""
        service = NurseService(
            utility_foundation=mock_utility_foundation,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )
        
        await service.initialize()
        
        # Test create_alert_rule
        alert_rule = {
            "rule_name": "high_response_time",
            "metric_name": "response_time",
            "threshold": 1000.0,
            "condition": "greater_than",
            "severity": "warning",
            "notification_channels": ["email", "slack"]
        }
        create_rule_result = await service.create_alert_rule(alert_rule, sample_user_context)
        assert create_rule_result is not None
        assert isinstance(create_rule_result, dict)
        assert "rule_id" in create_rule_result
        
        # Test get_active_alerts
        active_alerts = await service.get_active_alerts(sample_user_context)
        assert active_alerts is not None
        assert isinstance(active_alerts, list)
        
        # Test acknowledge_alert
        alert_id = "alert_001"
        ack_result = await service.acknowledge_alert(alert_id, sample_user_context)
        assert ack_result is not None
        assert isinstance(ack_result, dict)
        assert "acknowledged" in ack_result
        
        # Test resolve_alert
        resolve_result = await service.resolve_alert(alert_id, sample_user_context)
        assert resolve_result is not None
        assert isinstance(resolve_result, dict)
        assert "resolved" in resolve_result
    
    @pytest.mark.asyncio
    async def test_nurse_telemetry_operations(self, mock_utility_foundation, mock_public_works_foundation, mock_curator_foundation, sample_user_context):
        """Test Nurse telemetry operations."""
        service = NurseService(
            utility_foundation=mock_utility_foundation,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )
        
        await service.initialize()
        
        # Test collect_telemetry
        telemetry_data = {
            "service": "analytics",
            "operation": "data_query",
            "duration_ms": 250,
            "success": True,
            "metadata": {"query_type": "aggregation", "data_size": "large"}
        }
        collect_result = await service.collect_telemetry(telemetry_data, sample_user_context)
        assert collect_result is not None
        assert isinstance(collect_result, dict)
        assert "collected" in collect_result
        
        # Test get_telemetry_data
        telemetry_result = await service.get_telemetry_data("analytics", sample_user_context)
        assert telemetry_result is not None
        assert isinstance(telemetry_result, list)
        
        # Test get_telemetry_analytics
        analytics_result = await service.get_telemetry_analytics(sample_user_context)
        assert analytics_result is not None
        assert isinstance(analytics_result, dict)
        assert "total_operations" in analytics_result
        assert "success_rate" in analytics_result
        assert "average_duration" in analytics_result
    
    @pytest.mark.asyncio
    async def test_nurse_health_check(self, mock_utility_foundation, mock_public_works_foundation, mock_curator_foundation):
        """Test Nurse health check."""
        service = NurseService(
            utility_foundation=mock_utility_foundation,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )
        
        await service.initialize()
        
        # Test health check
        health_result = await service.get_service_health()
        self.assert_health_check(health_result)
        
        # Verify standard HealthService health check structure
        assert health_result["service"] == "NurseService"
        if "initialized" in health_result:
            assert health_result["initialized"] is True
    
    @pytest.mark.asyncio
    async def test_nurse_soa_protocol_compliance(self, mock_utility_foundation, mock_public_works_foundation, mock_curator_foundation):
        """Test Nurse SOA protocol compliance."""
        service = NurseService(
            utility_foundation=mock_utility_foundation,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )
        
        await service.initialize()
        
        # Test get_service_info
        service_info = service.get_service_info()
        assert service_info is not None
        assert hasattr(service_info, 'service_name')
        assert hasattr(service_info, 'version')
        assert hasattr(service_info, 'description')
        assert hasattr(service_info, 'endpoints')
        
        # Test get_openapi_spec
        openapi_spec = service.get_openapi_spec()
        assert openapi_spec is not None
        assert isinstance(openapi_spec, dict)
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        
        # Test get_docs
        docs = service.get_docs()
        assert docs is not None
        assert isinstance(docs, dict)
        assert "title" in docs
    
    @pytest.mark.asyncio
    async def test_nurse_error_handling(self, mock_utility_foundation, mock_public_works_foundation, mock_curator_foundation, sample_user_context):
        """Test Nurse error handling."""
        service = NurseService(
            utility_foundation=mock_utility_foundation,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )
        
        await service.initialize()
        
        # Test error handling for invalid service
        invalid_health_result = await service.get_health_status("invalid_service", sample_user_context)
        assert invalid_health_result is not None
        assert isinstance(invalid_health_result, dict)
        assert "error" in invalid_health_result or "status" in invalid_health_result
        
        # Test error handling for invalid metric
        invalid_metric_result = await service.get_metrics("analytics_service", "invalid_metric", sample_user_context)
        assert invalid_metric_result is not None
        assert isinstance(invalid_metric_result, list)  # Should return empty list or error list
        
        # Test error handling for invalid alert
        invalid_alert_result = await service.acknowledge_alert("invalid_alert", sample_user_context)
        assert invalid_alert_result is not None
        assert isinstance(invalid_alert_result, dict)
        assert "error" in invalid_alert_result or "acknowledged" in invalid_alert_result

