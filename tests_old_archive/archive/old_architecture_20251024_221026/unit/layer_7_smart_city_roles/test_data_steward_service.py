"""
Test Data Steward Service - Smart City Role for Data Governance

Tests the Data Steward service which handles data governance, file management,
metadata management, and data lifecycle operations.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime
from typing import Dict, Any

from backend.smart_city.services.data_steward.data_steward_service import DataStewardService
from foundations.utility_foundation.utilities.security.security_service import UserContext
from tests.unit.layer_7_smart_city_roles.test_base import SmartCityRolesTestBase


class TestDataStewardService(SmartCityRolesTestBase):
    """Test Data Steward Service implementation."""
    
    @pytest.mark.asyncio
    async def test_data_steward_service_initialization(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Data Steward service initialization."""
        service = DataStewardService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test basic initialization
        self.assert_service_initialization(service, [
            'public_works_foundation', 'environment', 'env_loader', 'config',
            'gcs_abstraction', 'supabase_abstraction', 'redis_abstraction',
            'file_storage_module', 'metadata_management_module', 'data_governance_module',
            'data_lifecycle_module', 'data_quality_module', 'access_control_module'
        ])
        
        assert service.public_works_foundation == mock_public_works_foundation
        assert service.env_loader is not None
        assert service.config is not None
    
    @pytest.mark.asyncio
    async def test_data_steward_service_initialization_async(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Data Steward service async initialization."""
        service = DataStewardService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test async initialization
        await service.initialize()
        
        # Verify initialization completed
        assert hasattr(service, 'logger')
        assert service.logger is not None
    
    @pytest.mark.asyncio
    async def test_data_steward_file_operations(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Data Steward file management operations."""
        service = DataStewardService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        await service.initialize()
        
        # Test file upload
        upload_result = await service.upload_file(
            file_data=b"test file content",
            filename="test_file.txt",
            content_type="text/plain",
            metadata={"description": "Test file"},
            user_context={"user_id": "user_001", "tenant_id": "tenant_001"}
        )
        assert upload_result is not None
        assert isinstance(upload_result, dict)
        assert "file_id" in upload_result
        assert "storage_url" in upload_result
        
        # Test file download
        download_result = await service.download_file(
            file_id="file_001",
            user_context={"user_id": "user_001", "tenant_id": "tenant_001"}
        )
        assert download_result is not None
        assert isinstance(download_result, dict)
        assert "file_data" in download_result
        assert "metadata" in download_result
    
    @pytest.mark.asyncio
    async def test_data_steward_metadata_management(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Data Steward metadata management operations."""
        service = DataStewardService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        await service.initialize()
        
        # Test metadata creation
        metadata_result = await service.create_metadata(
            file_id="file_001",
            metadata={"title": "Test File", "category": "test", "tags": ["test", "data"]},
            user_context={"user_id": "user_001", "tenant_id": "tenant_001"}
        )
        assert metadata_result is not None
        assert isinstance(metadata_result, dict)
        assert "metadata_id" in metadata_result
        
        # Test metadata retrieval
        retrieve_result = await service.get_metadata(
            file_id="file_001",
            user_context={"user_id": "user_001", "tenant_id": "tenant_001"}
        )
        assert retrieve_result is not None
        assert isinstance(retrieve_result, dict)
        assert "metadata" in retrieve_result
        
        # Test metadata update
        update_result = await service.update_metadata(
            file_id="file_001",
            metadata_updates={"description": "Updated test file"},
            user_context={"user_id": "user_001", "tenant_id": "tenant_001"}
        )
        assert update_result is not None
        assert isinstance(update_result, dict)
        assert "updated" in update_result
    
    @pytest.mark.asyncio
    async def test_data_steward_data_governance(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Data Steward data governance operations."""
        service = DataStewardService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        await service.initialize()
        
        # Test governance policy creation
        policy_result = await service.create_governance_policy(
            policy_name="test_policy",
            policy_rules={"retention_days": 365, "access_level": "restricted"},
            user_context={"user_id": "user_001", "tenant_id": "tenant_001"}
        )
        assert policy_result is not None
        assert isinstance(policy_result, dict)
        assert "policy_id" in policy_result
        
        # Test compliance check
        compliance_result = await service.check_compliance(
            file_id="file_001",
            policy_id="policy_001",
            user_context={"user_id": "user_001", "tenant_id": "tenant_001"}
        )
        assert compliance_result is not None
        assert isinstance(compliance_result, dict)
        assert "compliant" in compliance_result
        assert "violations" in compliance_result
    
    @pytest.mark.asyncio
    async def test_data_steward_data_lifecycle(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Data Steward data lifecycle operations."""
        service = DataStewardService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        await service.initialize()
        
        # Test lifecycle policy creation
        lifecycle_result = await service.create_lifecycle_policy(
            policy_name="test_lifecycle",
            stages=[{"name": "active", "duration_days": 90}, {"name": "archive", "duration_days": 365}],
            user_context={"user_id": "user_001", "tenant_id": "tenant_001"}
        )
        assert lifecycle_result is not None
        assert isinstance(lifecycle_result, dict)
        assert "policy_id" in lifecycle_result
        
        # Test lifecycle transition
        transition_result = await service.transition_lifecycle_stage(
            file_id="file_001",
            new_stage="archive",
            user_context={"user_id": "user_001", "tenant_id": "tenant_001"}
        )
        assert transition_result is not None
        assert isinstance(transition_result, dict)
        assert "transitioned" in transition_result
    
    @pytest.mark.asyncio
    async def test_data_steward_data_quality(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Data Steward data quality operations."""
        service = DataStewardService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        await service.initialize()
        
        # Test quality assessment
        quality_result = await service.assess_data_quality(
            file_id="file_001",
            quality_metrics=["completeness", "accuracy", "consistency"],
            user_context={"user_id": "user_001", "tenant_id": "tenant_001"}
        )
        assert quality_result is not None
        assert isinstance(quality_result, dict)
        assert "quality_score" in quality_result
        assert "metrics" in quality_result
        
        # Test quality report
        report_result = await service.generate_quality_report(
            file_id="file_001",
            user_context={"user_id": "user_001", "tenant_id": "tenant_001"}
        )
        assert report_result is not None
        assert isinstance(report_result, dict)
        assert "report_id" in report_result
        assert "summary" in report_result
    
    @pytest.mark.asyncio
    async def test_data_steward_health_check(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Data Steward health check (inherited from SOAServiceBase)."""
        service = DataStewardService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        await service.initialize()
        
        # Test health check (inherited from SOAServiceBase)
        health_result = await service.get_service_health()
        self.assert_health_check(health_result)
        
        # Verify service name
        assert health_result["service"] == "DataStewardService"
    
    @pytest.mark.asyncio
    async def test_data_steward_error_handling(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Data Steward error handling."""
        service = DataStewardService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        await service.initialize()
        
        # Test error handling for invalid file
        invalid_file_result = await service.download_file(
            file_id="invalid_file",
            user_context={"user_id": "user_001", "tenant_id": "tenant_001"}
        )
        assert invalid_file_result is not None
        assert isinstance(invalid_file_result, dict)
        
        # Test error handling for invalid metadata
        invalid_metadata_result = await service.get_metadata(
            file_id="invalid_file",
            user_context={"user_id": "user_001", "tenant_id": "tenant_001"}
        )
        assert invalid_metadata_result is not None
        assert isinstance(invalid_metadata_result, dict)
