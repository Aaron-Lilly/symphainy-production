#!/usr/bin/env python3
"""
Layer 1: DI Foundation Tests

Component Tests: Individual DI Container functionality
Integration Tests: DI Container working with services
"""

import pytest
import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "symphainy-platform"))

pytestmark = [pytest.mark.integration]


class TestDIContainerComponents:
    """Component Tests: Individual DI Container functionality."""
    
    @pytest.mark.asyncio
    async def test_di_container_creates_successfully(self):
        """Test that DI Container can be created."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            
            di_container = DIContainerService("test_platform")
            assert di_container is not None, "DI Container should be created"
            assert hasattr(di_container, "get_logger"), "DI Container should have get_logger method"
            
        except ImportError as e:
            pytest.fail(
                f"DI Container not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path.\n"
                f"Verify: import foundations.di_container.di_container_service"
            )
    
    @pytest.mark.asyncio
    async def test_logger_utility_works(self):
        """Test that logger utility works."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            
            di_container = DIContainerService("test_platform")
            logger = di_container.get_logger("test_logger")
            
            assert logger is not None, "Logger should be available"
            assert hasattr(logger, "info"), "Logger should have info method"
            assert hasattr(logger, "error"), "Logger should have error method"
            
        except ImportError as e:
            pytest.fail(
                f"DI Container not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path.\n"
                f"Verify: import foundations.di_container.di_container_service"
            )
    
    @pytest.mark.asyncio
    async def test_config_utility_works(self):
        """Test that config utility works."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            
            di_container = DIContainerService("test_platform")
            
            # Check if get_config method exists
            if hasattr(di_container, "get_config"):
                config = di_container.get_config()
                assert config is not None, "Config should be available"
                # Config might be a UnifiedConfigurationManager, not a dict
                assert hasattr(config, "get") or isinstance(config, dict), \
                    "Config should be accessible (dict or UnifiedConfigurationManager)"
            else:
                # Config might be accessed via unified_config_manager
                if hasattr(di_container, "unified_config_manager"):
                    config = di_container.unified_config_manager
                    assert config is not None, "Config should be available"
                else:
                    pytest.fail(
                        "Config access method not available on DI Container.\n"
                        "This indicates a configuration or implementation issue.\n"
                        "Check that DI Container has get_config() or unified_config_manager attribute."
                    )
            
        except ImportError as e:
            pytest.fail(
                f"DI Container not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path.\n"
                f"Verify: import foundations.di_container.di_container_service"
            )
    
    @pytest.mark.asyncio
    async def test_foundation_service_access_works(self):
        """Test that foundation service access works."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            
            di_container = DIContainerService("test_platform")
            
            # Test getting Public Works Foundation
            pwf = di_container.get_foundation_service("PublicWorksFoundationService")
            assert pwf is not None, "Public Works Foundation should be available"
            
            # Test getting Curator Foundation
            curator = di_container.get_foundation_service("CuratorFoundationService")
            assert curator is not None, "Curator Foundation should be available"
            
        except ImportError as e:
            pytest.fail(
                f"DI Container not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path.\n"
                f"Verify: import foundations.di_container.di_container_service"
            )
    
    @pytest.mark.asyncio
    async def test_platform_gateway_access_works(self):
        """Test that Platform Gateway access works."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            
            di_container = DIContainerService("test_platform")
            
            # Test getting Platform Gateway
            platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
            assert platform_gateway is not None, "Platform Gateway should be available"
            assert hasattr(platform_gateway, "is_initialized"), "Platform Gateway should have is_initialized"
            
        except ImportError as e:
            pytest.fail(
                f"DI Container not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path.\n"
                f"Verify: import foundations.di_container.di_container_service"
            )
    
    @pytest.mark.asyncio
    async def test_service_registry_works(self):
        """Test that service registry works."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            
            di_container = DIContainerService("test_platform")
            
            # Check service registry exists
            assert hasattr(di_container, "service_registry"), "DI Container should have service_registry"
            assert isinstance(di_container.service_registry, dict), "Service registry should be a dictionary"
            
            # Check that Platform Gateway is registered
            assert "PlatformInfrastructureGateway" in di_container.service_registry, \
                "Platform Gateway should be in service registry"
            
        except ImportError as e:
            pytest.fail(
                f"DI Container not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path.\n"
                f"Verify: import foundations.di_container.di_container_service"
            )


class TestDIContainerIntegration:
    """Integration Tests: DI Container working with services."""
    
    @pytest.mark.asyncio
    async def test_di_container_provides_all_utilities(self):
        """Test that DI Container provides all utility foundations."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            
            di_container = DIContainerService("test_platform")
            
            # Test utility foundations - these are accessed via Public Works Foundation
            # Utilities are provided through Public Works Foundation, not directly via DI Container
            pwf = di_container.get_foundation_service("PublicWorksFoundationService")
            assert pwf is not None, "Public Works Foundation should be available"
            
            # Initialize Public Works Foundation to access utilities
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
            
            # Utilities are accessed through Public Works Foundation abstractions
            # Check that Public Works Foundation provides utility abstractions
            assert hasattr(pwf, "get_abstraction"), \
                "Public Works Foundation should provide get_abstraction method"
            
        except ImportError as e:
            pytest.fail(
                f"DI Container not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path.\n"
                f"Verify: import foundations.di_container.di_container_service"
            )
        except ConnectionError as e:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"Infrastructure connection failed: {e}\n\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                f"Check Docker containers: docker ps --filter name=symphainy-"
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Infrastructure error during utility access: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_services_can_access_dependencies(self):
        """Test that services can access dependencies via DI Container."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            
            di_container = DIContainerService("test_platform")
            
            # Create a service that uses DI Container
            pwf = PublicWorksFoundationService(di_container=di_container)
            
            # Service should be able to access utilities via DI Container
            assert pwf.di_container is not None, "Service should have access to DI Container"
            assert pwf.di_container == di_container, "Service should reference the same DI Container"
            
        except ImportError as e:
            pytest.fail(
                f"DI Container or Public Works Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
            )
    
    @pytest.mark.asyncio
    async def test_foundation_services_initialized(self):
        """Test that foundation services are initialized via DI Container."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            
            di_container = DIContainerService("test_platform")
            
            # Get Public Works Foundation
            pwf = di_container.get_foundation_service("PublicWorksFoundationService")
            assert pwf is not None, "Public Works Foundation should be available"
            
            # Initialize Public Works Foundation
            pwf_result = await pwf.initialize()
            assert pwf_result is True, "Public Works Foundation should initialize"
            assert pwf.is_initialized, "Public Works Foundation should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"DI Container not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path.\n"
                f"Verify: import foundations.di_container.di_container_service"
            )
        except ConnectionError as e:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Infrastructure connection failed: {e}\n\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                f"Check Docker containers: docker ps --filter name=symphainy-"
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Infrastructure error during foundation initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise

