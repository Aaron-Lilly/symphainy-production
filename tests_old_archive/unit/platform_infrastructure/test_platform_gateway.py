#!/usr/bin/env python3
"""
PlatformInfrastructureGateway Tests

Tests for PlatformInfrastructureGateway in isolation.
Verifies gateway enforces realm access policies correctly.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestPlatformInfrastructureGateway:
    """Test PlatformInfrastructureGateway functionality."""
    
    @pytest.fixture
    def mock_public_works_foundation(self):
        """Mock Public Works Foundation."""
        foundation = MagicMock()
        foundation.get_abstraction = MagicMock(return_value=MagicMock())
        return foundation
    
    @pytest.fixture
    def gateway(self, mock_public_works_foundation):
        """Create PlatformInfrastructureGateway instance."""
        from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
        
        gateway = PlatformInfrastructureGateway(mock_public_works_foundation)
        return gateway
    
    @pytest.mark.asyncio
    async def test_gateway_initializes(self, gateway):
        """Test gateway initializes correctly."""
        result = await gateway.initialize()
        assert result is True
        assert gateway.is_initialized is True
    
    @pytest.mark.asyncio
    async def test_get_realm_abstractions(self, gateway):
        """Test gateway can get realm abstractions."""
        abstractions = gateway.get_realm_abstractions("business_enablement")
        assert isinstance(abstractions, list)
        assert "file_management" in abstractions
        assert "llm" in abstractions
        assert "content_metadata" in abstractions
    
    @pytest.mark.asyncio
    async def test_validate_realm_access_allowed(self, gateway):
        """Test gateway validates allowed access."""
        # business_enablement should have access to file_management
        result = gateway.validate_realm_access("business_enablement", "file_management")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_realm_access_denied(self, gateway):
        """Test gateway validates denied access."""
        # business_enablement should NOT have access to session
        result = gateway.validate_realm_access("business_enablement", "session")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_abstraction_allowed(self, gateway, mock_public_works_foundation):
        """Test gateway grants access to allowed abstraction."""
        await gateway.initialize()
        
        abstraction = gateway.get_abstraction("business_enablement", "file_management")
        assert abstraction is not None
        mock_public_works_foundation.get_abstraction.assert_called_once_with("file_management")
    
    @pytest.mark.asyncio
    async def test_get_abstraction_denied(self, gateway):
        """Test gateway denies access to disallowed abstraction."""
        await gateway.initialize()
        
        with pytest.raises(ValueError, match="cannot access"):
            gateway.get_abstraction("business_enablement", "session")
    
    @pytest.mark.asyncio
    async def test_get_realm_capabilities(self, gateway):
        """Test gateway can get realm capabilities."""
        capabilities = gateway.get_realm_capabilities("business_enablement")
        assert capabilities is not None
        assert capabilities.realm_name == "business_enablement"
        assert "file_management" in capabilities.abstractions
        assert capabilities.byoi_support is False
    
    @pytest.mark.asyncio
    async def test_get_all_realm_abstractions(self, gateway, mock_public_works_foundation):
        """Test gateway can get all abstractions for a realm."""
        await gateway.initialize()
        
        abstractions = gateway.get_all_realm_abstractions("business_enablement")
        assert isinstance(abstractions, dict)
        assert len(abstractions) > 0
    
    @pytest.mark.asyncio
    async def test_access_metrics(self, gateway, mock_public_works_foundation):
        """Test gateway tracks access metrics."""
        await gateway.initialize()
        
        # Make some requests
        gateway.get_abstraction("business_enablement", "file_management")
        
        metrics = gateway.get_access_metrics()
        assert metrics["total_requests"] > 0
        assert metrics["successful_requests"] > 0
        assert "business_enablement" in metrics["realm_access_counts"]
    
    @pytest.mark.asyncio
    async def test_health_check(self, gateway, mock_public_works_foundation):
        """Test gateway health check."""
        await gateway.initialize()
        
        health = gateway.health_check()
        assert health["status"] == "healthy"
        assert health["public_works_connected"] is True
        assert health["realm_mappings_loaded"] > 0
    
    @pytest.mark.asyncio
    async def test_list_all_realms(self, gateway):
        """Test gateway can list all realms."""
        realms = gateway.list_all_realms()
        assert isinstance(realms, list)
        assert "business_enablement" in realms
        assert "experience" in realms
        assert "solution" in realms
        assert "journey" in realms
        assert "smart_city" in realms
    
    @pytest.mark.asyncio
    async def test_realm_specific_access(self, gateway, mock_public_works_foundation):
        """Test gateway enforces realm-specific access correctly."""
        await gateway.initialize()
        
        # Experience realm should have access to session, auth, authorization, tenant
        assert gateway.validate_realm_access("experience", "session") is True
        assert gateway.validate_realm_access("experience", "auth") is True
        assert gateway.validate_realm_access("experience", "authorization") is True
        assert gateway.validate_realm_access("experience", "tenant") is True
        
        # Experience realm should NOT have access to file_management
        assert gateway.validate_realm_access("experience", "file_management") is False
        
        # Solution realm should have access to llm, content_metadata, file_management
        assert gateway.validate_realm_access("solution", "llm") is True
        assert gateway.validate_realm_access("solution", "content_metadata") is True
        assert gateway.validate_realm_access("solution", "file_management") is True
        
        # Journey realm should have access to llm, session, content_metadata
        assert gateway.validate_realm_access("journey", "llm") is True
        assert gateway.validate_realm_access("journey", "session") is True
        assert gateway.validate_realm_access("journey", "content_metadata") is True

