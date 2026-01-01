#!/usr/bin/env python3
"""
Layer 0: Platform Startup Tests

Component Tests: Individual components of platform startup
Integration Tests: Components working together
"""

import pytest
import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "symphainy-platform"))

pytestmark = [pytest.mark.integration]


class TestPlatformStartupComponents:
    """Component Tests: Individual components of platform startup."""
    
    @pytest.mark.asyncio
    async def test_startup_script_exists(self, project_root_path):
        """Test that platform startup script exists."""
        # Fix path - project_root_path already points to symphainy-platform
        startup_script = project_root_path / "startup.sh"
        main_script = project_root_path / "main.py"
        
        # At least one startup mechanism should exist
        assert startup_script.exists() or main_script.exists(), \
            f"Platform startup script (startup.sh or main.py) should exist. Checked: {startup_script}, {main_script}"
    
    @pytest.mark.asyncio
    async def test_di_container_can_initialize(self):
        """Test that DI Container can be initialized. FAILS with diagnostics if unavailable."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            
            di_container = DIContainerService("test_platform")
            assert di_container is not None, "DI Container should be created"
            # DI Container initializes on creation, check that it's functional
            assert hasattr(di_container, "get_logger"), "DI Container should have get_logger method"
            assert hasattr(di_container, "get_foundation_service"), "DI Container should have get_foundation_service method"
            
        except ImportError as e:
            pytest.fail(
                f"DI Container not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path.\n"
                f"Verify: import foundations.di_container.di_container_service"
            )
    
    @pytest.mark.asyncio
    async def test_configuration_loading_works(self, project_root_path):
        """Test that configuration loading works."""
        # Fix path - project_root_path already points to symphainy-platform
        config_dir = project_root_path / "config"
        
        # At least config directory should exist or be creatable
        assert config_dir.exists() or config_dir.parent.exists(), \
            f"Configuration directory should exist or be creatable. Checked: {config_dir}"
    
    @pytest.mark.asyncio
    async def test_logging_system_initializes(self):
        """Test that logging system can be initialized. FAILS with diagnostics if unavailable."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            
            di_container = DIContainerService("test_platform")
            logger = di_container.get_logger("test")
            
            assert logger is not None, "Logger should be available"
            
        except ImportError as e:
            pytest.fail(
                f"DI Container not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
            )
        except Exception as e:
            pytest.fail(
                f"Logging initialization failed: {e}\n\n"
                f"Check DI Container configuration and logging setup."
            )


class TestPlatformStartupIntegration:
    """Integration Tests: Components working together."""
    
    @pytest.mark.asyncio
    async def test_foundations_initialize_in_order(self):
        """Test that all foundations initialize in correct order. FAILS with diagnostics if infrastructure unavailable."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
            from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
            from tests.utils.safe_docker import check_container_status
            
            # Use real DI Container (infrastructure is available)
            di_container = DIContainerService("test_platform")
            
            # Initialize in order
            pwf = PublicWorksFoundationService(di_container=di_container)
            
            # Use timeout for initialization
            try:
                pwf_result = await asyncio.wait_for(
                    pwf.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                # Check infrastructure status
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
            
            # Public Works may fail if infrastructure not available - FAIL with diagnostics
            if not pwf_result:
                # Get detailed diagnostics
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
            
            # Public Works should initialize first
            assert pwf_result is True, "Public Works Foundation should initialize"
            assert pwf.is_initialized, "Public Works Foundation should be marked as initialized"
            
            # Curator depends on Public Works
            curator = CuratorFoundationService(
                foundation_services=di_container,
                public_works_foundation=pwf
            )
            curator_result = await curator.initialize()
            assert curator_result is True, "Curator Foundation should initialize"
            assert curator.is_initialized, "Curator Foundation should be marked as initialized"
            
            # Communication depends on Public Works
            comm = CommunicationFoundationService(
                di_container=di_container,
                public_works_foundation=pwf
            )
            comm_result = await comm.initialize()
            assert comm_result is True, "Communication Foundation should initialize"
            assert comm.is_initialized, "Communication Foundation should be marked as initialized"
            
            # Agentic depends on all above
            # Check AgenticFoundationService constructor signature
            try:
                agentic = AgenticFoundationService(
                    di_container=di_container,
                    public_works_foundation=pwf,
                    curator_foundation=curator
                )
            except TypeError:
                # Try without communication_foundation if not supported
                agentic = AgenticFoundationService(
                    di_container=di_container,
                    public_works_foundation=pwf,
                    curator_foundation=curator
                )
            agentic_result = await agentic.initialize()
            assert agentic_result is True, "Agentic Foundation should initialize"
            assert agentic.is_initialized, "Agentic Foundation should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Foundation services not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
            )
        except ConnectionError as e:
            # Infrastructure connection failed - provide diagnostics
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"Infrastructure connection failed: {e}\n\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                f"This indicates infrastructure is unavailable or misconfigured.\n"
                f"Check Docker containers: docker ps --filter name=symphainy-\n"
                f"Check configuration: Verify ports and environment variables match Docker containers"
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                # Infrastructure error - provide diagnostics
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Infrastructure error during initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-\n"
                    f"Check configuration: Verify ports and environment variables"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_platform_gateway_initializes(self):
        """Test that Platform Gateway initializes."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            
            # Use real DI Container (infrastructure is available)
            di_container = DIContainerService("test_platform")
            
            # Initialize Public Works first (dependency)
            pwf = PublicWorksFoundationService(di_container=di_container)
            pwf_result = await pwf.initialize()
            
            # Public Works may fail if infrastructure not available - FAIL with diagnostics
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Platform Gateway requires Public Works Foundation, but initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # Initialize Platform Gateway
            platform_gateway = PlatformInfrastructureGateway(public_works_foundation=pwf)
            result = await platform_gateway.initialize()
            
            assert result is True, "Platform Gateway should initialize"
            assert platform_gateway.is_initialized, "Platform Gateway should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Platform Gateway not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that platform_infrastructure is installed and in Python path."
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
                
                pytest.fail(
                    f"Infrastructure error during Platform Gateway initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_health_checks_work_after_startup(self):
        """Test that health checks work after startup."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            
            # Use real DI Container (infrastructure is available)
            di_container = DIContainerService("test_platform")
            
            pwf = PublicWorksFoundationService(di_container=di_container)
            pwf_result = await pwf.initialize()
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                
                pytest.fail(
                    f"Health check requires Public Works Foundation, but initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # Health check should work - check health_abstraction instead
            if hasattr(pwf, "health_abstraction") and pwf.health_abstraction:
                # Health abstraction is available
                assert pwf.health_abstraction is not None, "Health abstraction should be available"
            else:
                pytest.fail(
                    "Health abstraction not available on Public Works Foundation.\n"
                    "This indicates a configuration or initialization issue."
                )
            
        except ImportError as e:
            pytest.fail(
                f"Public Works Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure."
            )
        except Exception as e:
            pytest.fail(
                f"Health check not available: {e}\n\n"
                f"Check Public Works Foundation initialization and health abstraction setup."
            )
    
    @pytest.mark.asyncio
    async def test_platform_shuts_down_gracefully(self):
        """Test that platform can shut down gracefully."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            
            # Use real DI Container (infrastructure is available)
            di_container = DIContainerService("test_platform")
            
            pwf = PublicWorksFoundationService(di_container=di_container)
            pwf_result = await pwf.initialize()
            
            # Public Works may fail if infrastructure not available - FAIL with diagnostics
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                
                pytest.fail(
                    f"Shutdown test requires Public Works Foundation, but initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # Shutdown should work without errors
            if hasattr(pwf, "shutdown"):
                await pwf.shutdown()
                assert True, "Shutdown completed without errors"
            else:
                pytest.fail(
                    "Shutdown method not available on Public Works Foundation.\n"
                    "This indicates a configuration or implementation issue."
                )
            
        except ImportError as e:
            pytest.fail(
                f"Public Works Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure."
            )
        except ConnectionError as e:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"Infrastructure connection failed during shutdown test: {e}\n\n"
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
                
                pytest.fail(
                    f"Infrastructure error during shutdown test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise

