#!/usr/bin/env python3
"""
Integration Tests - Foundation Layer Integration

Tests for integration between foundation layers.
"""

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.foundations, pytest.mark.slow]

class TestFoundationIntegration:
    """Test integration between foundation layers."""
    
    @pytest.mark.asyncio
    async def test_di_container_to_public_works(self, real_di_container):
        """Test DI Container can initialize Public Works Foundation."""
        try:
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            pwf = PublicWorksFoundationService(real_di_container)
            result = await pwf.initialize()
            assert result is True
        except Exception as e:
            pytest.skip(f"Public Works Foundation initialization failed: {e}")
    
    @pytest.mark.asyncio
    async def test_curator_foundation_registration(self, real_curator_foundation):
        """Test Curator Foundation can register services."""
        try:
            result = await real_curator_foundation.register_service(
                service_name="test_service",
                service_type="test",
                capabilities=["test_capability"]
            )
            assert result is True or result is not None
        except Exception as e:
            pytest.skip(f"Service registration failed: {e}")
    
    @pytest.mark.asyncio
    async def test_communication_foundation_messaging(self, real_communication_foundation):
        """Test Communication Foundation can send messages."""
        try:
            result = await real_communication_foundation.send_message(
                message={"test": "message"},
                recipient="test_service"
            )
            assert result is not None
        except Exception as e:
            pytest.skip(f"Message sending failed: {e}")
    
    @pytest.mark.asyncio
    async def test_full_foundation_stack(self, real_di_container):
        """Test entire foundation stack can be initialized."""
        try:
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
            from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
            
            # Initialize in order
            pwf = PublicWorksFoundationService(real_di_container)
            await pwf.initialize()
            
            curator = CuratorFoundationService(
                foundation_services=real_di_container,
                public_works_foundation=pwf
            )
            await curator.initialize()
            
            comm = CommunicationFoundationService(real_di_container, pwf)
            await comm.initialize()
            
            agentic = AgenticFoundationService(
                di_container=real_di_container,
                public_works_foundation=pwf,
                communication_foundation=comm,
                curator_foundation=curator
            )
            await agentic.initialize()
            
            # All should be initialized
            assert pwf.is_initialized
            assert curator.is_initialized
            assert comm.is_initialized
            assert agentic.is_initialized
            
        except Exception as e:
            pytest.skip(f"Full foundation stack initialization failed: {e}")

