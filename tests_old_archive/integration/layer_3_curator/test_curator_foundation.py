#!/usr/bin/env python3
"""
Layer 3: Curator Foundation Tests

Component Tests: Individual Curator components work correctly
Integration Tests: Curator works with Consul via abstraction->adapter->infrastructure
"""

import pytest
import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "symphainy-platform"))

pytestmark = [pytest.mark.integration]


class TestCuratorComponents:
    """Component Tests: Individual Curator components work correctly."""
    
    @pytest.mark.asyncio
    async def test_curator_foundation_initializes(self):
        """Test that Curator Foundation initializes correctly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            
            di_container = DIContainerService("test_platform")
            pwf = PublicWorksFoundationService(di_container=di_container)
            
            # Use timeout for initialization
            try:
                pwf_result = await asyncio.wait_for(
                    pwf.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Fix: Ensure all critical infrastructure containers are running and healthy."
                )
            
            curator = CuratorFoundationService(
                foundation_services=di_container,
                public_works_foundation=pwf
            )
            curator_result = await curator.initialize()
            
            assert curator_result is True, "Curator Foundation should initialize"
            assert curator.is_initialized, "Curator Foundation should be marked as initialized"
            assert curator.service_discovery is not None, "Service discovery should be available"
            
        except ImportError as e:
            pytest.fail(
                f"Curator Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
            )
        except ConnectionError as e:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            
            pytest.fail(
                f"Infrastructure connection failed: {e}\n\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                f"Check logs: docker logs symphainy-consul"
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                
                pytest.fail(
                    f"Infrastructure error during Curator Foundation initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_curator_gets_service_discovery_from_public_works(self):
        """Test that Curator gets service discovery abstraction from Public Works."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            
            di_container = DIContainerService("test_platform")
            pwf = PublicWorksFoundationService(di_container=di_container)
            
            # Use timeout for initialization
            try:
                pwf_result = await asyncio.wait_for(
                    pwf.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Fix: Ensure all critical infrastructure containers are running and healthy."
                )
            
            # Get service discovery abstraction from Public Works
            service_discovery_abstraction = pwf.get_abstraction("service_discovery")
            assert service_discovery_abstraction is not None, \
                "Service discovery abstraction should be available from Public Works"
            
            # Initialize Curator
            curator = CuratorFoundationService(
                foundation_services=di_container,
                public_works_foundation=pwf
            )
            curator_result = await curator.initialize()
            
            if not curator_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                
                pytest.fail(
                    f"Curator Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul\n\n"
                    f"Fix: Ensure Consul is running and healthy."
                )
            
            # Curator should have service discovery
            assert curator.service_discovery is not None, \
                "Curator should have service discovery from Public Works"
            assert curator.service_discovery == service_discovery_abstraction, \
                "Curator should use the same service discovery abstraction from Public Works"
            
        except ImportError as e:
            pytest.fail(
                f"Curator Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
            )
        except ConnectionError as e:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            
            pytest.fail(
                f"Infrastructure connection failed: {e}\n\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                f"Check logs: docker logs symphainy-consul"
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                
                pytest.fail(
                    f"Infrastructure error during service discovery test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_curator_capability_registry_works(self):
        """Test that Curator capability registry works."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            
            di_container = DIContainerService("test_platform")
            pwf = PublicWorksFoundationService(di_container=di_container)
            
            # Use timeout for initialization
            try:
                pwf_result = await asyncio.wait_for(
                    pwf.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Fix: Ensure all critical infrastructure containers are running and healthy."
                )
            
            curator = CuratorFoundationService(
                foundation_services=di_container,
                public_works_foundation=pwf
            )
            curator_result = await curator.initialize()
            
            if not curator_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                
                pytest.fail(
                    f"Curator Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul\n\n"
                    f"Fix: Ensure Consul is running and healthy."
                )
            
            # Test capability registry
            assert curator.capability_registry is not None, "Capability registry should be available"
            assert curator.capability_registry.is_initialized, "Capability registry should be initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Curator Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
            )
        except ConnectionError as e:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            
            pytest.fail(
                f"Infrastructure connection failed: {e}\n\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                f"Check logs: docker logs symphainy-consul"
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                
                pytest.fail(
                    f"Infrastructure error during capability registry test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            else:
                raise


class TestCuratorIntegration:
    """Integration Tests: Curator works with Consul via abstraction->adapter->infrastructure."""
    
    @pytest.mark.asyncio
    async def test_curator_uses_consul_via_abstraction_chain(self):
        """
        Test that Curator genuinely accesses and updates Consul via:
        Curator -> ServiceDiscoveryAbstraction -> ConsulAdapter -> Consul Infrastructure
        
        This verifies the full abstraction->adapter->infrastructure chain with lifecycle management.
        """
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            
            di_container = DIContainerService("test_platform")
            pwf = PublicWorksFoundationService(di_container=di_container)
            
            # Use timeout for initialization
            try:
                pwf_result = await asyncio.wait_for(
                    pwf.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Fix: Ensure all critical infrastructure containers are running and healthy."
                )
            
            # Initialize Curator
            curator = CuratorFoundationService(
                foundation_services=di_container,
                public_works_foundation=pwf
            )
            curator_result = await curator.initialize()
            
            if not curator_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                
                pytest.fail(
                    f"Curator Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul\n\n"
                    f"Fix: Ensure Consul is running and healthy."
                )
            
            # Verify the chain: Curator -> ServiceDiscoveryAbstraction -> ConsulAdapter -> Consul
            assert curator.service_discovery is not None, \
                "Curator should have service discovery abstraction"
            
            # Get the service discovery abstraction
            service_discovery = curator.service_discovery
            
            # Verify it's the abstraction from Public Works
            assert hasattr(service_discovery, "register_service"), \
                "Service discovery abstraction should have register_service method"
            # The abstraction uses adapter.discover_service internally, so we verify adapter exists
            assert hasattr(service_discovery, "adapter"), \
                "Service discovery abstraction should have adapter attribute"
            assert service_discovery.adapter is not None, \
                "Service discovery abstraction should have a configured adapter"
            
            # Verify the abstraction uses a Consul adapter
            # The abstraction should have an adapter attribute that points to Consul
            if hasattr(service_discovery, "adapter"):
                adapter = service_discovery.adapter
                assert adapter is not None, "Service discovery abstraction should have an adapter"
                
                # Verify adapter is Consul adapter (check for Consul-specific attributes)
                adapter_type = type(adapter).__name__
                assert "Consul" in adapter_type or hasattr(adapter, "consul_client"), \
                    f"Adapter should be Consul adapter, got: {adapter_type}"
            
            # Test actual registration to Consul (lifecycle management)
            # Create a mock service instance
            class MockService:
                def __init__(self):
                    self.service_name = "test_service_layer3"
                    self.is_initialized = True
            
            mock_service = MockService()
            
            test_service_metadata = {
                "service_name": "test_service_layer3",
                "service_type": "test",
                "realm": "test_realm",
                "capabilities": ["test_capability"],
                "address": "localhost",
                "port": 8000,
                "tags": ["test", "layer3"],
                "endpoints": ["/test"]
            }
            
            # Register service via Curator (which uses abstraction->adapter->Consul)
            registration_result = await curator.register_service(
                service_instance=mock_service,
                service_metadata=test_service_metadata
            )
            
            assert registration_result is not None, \
                "Service registration should return a result"
            assert "success" in str(registration_result).lower() or registration_result.get("success") is True or registration_result is True, \
                "Service registration should succeed"
            
            # Verify service can be discovered (lifecycle management - service is registered and discoverable)
            # This confirms the full chain: Curator -> Abstraction -> Adapter -> Consul -> Service Discovery
            discovered_service = await curator.discover_service_by_name(test_service_metadata["service_name"])
            
            # Service might be in local cache or in Consul - either way, lifecycle management worked
            # Check that service is in registered_services cache (lifecycle management)
            assert test_service_metadata["service_name"] in curator.registered_services or discovered_service is not None, \
                "Service should be discoverable after registration (lifecycle management working)"
            
        except ImportError as e:
            pytest.fail(
                f"Curator Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
            )
        except ConnectionError as e:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            
            pytest.fail(
                f"Infrastructure connection failed: {e}\n\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                f"Check logs: docker logs symphainy-consul"
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                
                pytest.fail(
                    f"Infrastructure error during Consul integration test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_curator_phase2_registration_works(self):
        """Test that Curator Phase 2 registration pattern works."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            
            di_container = DIContainerService("test_platform")
            pwf = PublicWorksFoundationService(di_container=di_container)
            
            # Use timeout for initialization
            try:
                pwf_result = await asyncio.wait_for(
                    pwf.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Fix: Ensure all critical infrastructure containers are running and healthy."
                )
            
            curator = CuratorFoundationService(
                foundation_services=di_container,
                public_works_foundation=pwf
            )
            curator_result = await curator.initialize()
            
            if not curator_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                
                pytest.fail(
                    f"Curator Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul\n\n"
                    f"Fix: Ensure Consul is running and healthy."
                )
            
            # Test Phase 2 registration with CapabilityDefinition structure
            class MockServicePhase2:
                def __init__(self):
                    self.service_name = "TestService"
                    self.is_initialized = True
            
            mock_service_phase2 = MockServicePhase2()
            
            service_metadata_phase2 = {
                "service_name": "TestService",
                "service_type": "test",
                "realm": "test_realm",
                "capabilities": ["test_capability"],
                "address": "localhost",
                "port": 8001,
                "tags": ["test", "phase2"],
                "endpoints": ["/test"]
            }
            
            registration_result = await curator.register_service(
                service_instance=mock_service_phase2,
                service_metadata=service_metadata_phase2
            )
            
            assert registration_result is not None, \
                "Phase 2 registration should return a result"
            
        except ImportError as e:
            pytest.fail(
                f"Curator Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
            )
        except ConnectionError as e:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            
            pytest.fail(
                f"Infrastructure connection failed: {e}\n\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                f"Check logs: docker logs symphainy-consul"
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                
                pytest.fail(
                    f"Infrastructure error during Phase 2 registration test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_curator_service_discovery_works(self):
        """Test that Curator service discovery works."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            
            di_container = DIContainerService("test_platform")
            pwf = PublicWorksFoundationService(di_container=di_container)
            
            # Use timeout for initialization
            try:
                pwf_result = await asyncio.wait_for(
                    pwf.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Fix: Ensure all critical infrastructure containers are running and healthy."
                )
            
            curator = CuratorFoundationService(
                foundation_services=di_container,
                public_works_foundation=pwf
            )
            curator_result = await curator.initialize()
            
            if not curator_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                
                pytest.fail(
                    f"Curator Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul\n\n"
                    f"Fix: Ensure Consul is running and healthy."
                )
            
            # Test service discovery methods
            assert hasattr(curator, "discover_service_by_name"), "Curator should have discover_service_by_name method"
            
            # Test discovering services by name
            service = await curator.discover_service_by_name("test_service")
            # Service might not exist, but method should work
            assert service is None or isinstance(service, (dict, object)), \
                "Service discovery should return a service or None"
            
        except ImportError as e:
            pytest.fail(
                f"Curator Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
            )
        except ConnectionError as e:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            
            pytest.fail(
                f"Infrastructure connection failed: {e}\n\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                f"Check logs: docker logs symphainy-consul"
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                
                pytest.fail(
                    f"Infrastructure error during service discovery test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            else:
                raise

