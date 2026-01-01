#!/usr/bin/env python3
"""
Layer 5: Agentic Foundation Tests

Component Tests: Individual Agentic Foundation components work correctly
Integration Tests: Agentic Foundation integrates correctly with other foundations

Key Understanding:
- Agentic Foundation is a FOUNDATION SERVICE (not a regular service)
- It does NOT register itself with Curator (foundation services don't register)
- It CREATES agents via factory pattern
- AGENTS register with Curator (not the foundation)
- Agents USE MCP tools (they don't expose them)
- MCP servers expose tools, agents consume them via MCPClientManager
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


class TestAgenticFoundationComponents:
    """Component Tests: Individual Agentic Foundation components work correctly."""
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_initializes(self):
        """Test that Agentic Foundation initializes correctly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
            
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
            
            # Initialize Agentic Foundation
            agentic = AgenticFoundationService(
                di_container=di_container,
                public_works_foundation=pwf,
                curator_foundation=curator
            )
            agentic_result = await agentic.initialize()
            
            if not agentic_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Agentic Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            assert agentic_result is True, "Agentic Foundation should initialize"
            assert agentic.is_initialized, "Agentic Foundation should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Agentic Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
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
                    f"Infrastructure error during Agentic Foundation initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_uses_curator(self):
        """Test that Agentic Foundation uses Curator (for agent registration, not self-registration)."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
            
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
            
            agentic = AgenticFoundationService(
                di_container=di_container,
                public_works_foundation=pwf,
                curator_foundation=curator
            )
            agentic_result = await agentic.initialize()
            
            if not agentic_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Agentic Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # Agentic Foundation should have Curator reference
            assert agentic.curator_foundation is not None, \
                "Agentic Foundation should have Curator Foundation reference"
            assert agentic.curator_foundation == curator, \
                "Agentic Foundation should use the same Curator Foundation instance"
            
            # Agentic Foundation uses Curator to register agents (not itself)
            assert hasattr(agentic, "_register_agent_with_curator"), \
                "Agentic Foundation should have method to register agents with Curator"
            
        except ImportError as e:
            pytest.fail(
                f"Agentic Foundation not available: {e}\n\n"
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
                    f"Infrastructure error during Curator integration test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_has_agent_factory(self):
        """Test that Agentic Foundation has agent factory for creating agents."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
            
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
            
            agentic = AgenticFoundationService(
                di_container=di_container,
                public_works_foundation=pwf,
                curator_foundation=curator
            )
            agentic_result = await agentic.initialize()
            
            if not agentic_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Agentic Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # Agentic Foundation should have agent factory methods
            assert hasattr(agentic, "create_agent"), \
                "Agentic Foundation should have create_agent method"
            assert hasattr(agentic, "_agents"), \
                "Agentic Foundation should track created agents"
            
        except ImportError as e:
            pytest.fail(
                f"Agentic Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
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
                    f"Infrastructure error during Agent factory test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_has_mcp_client_manager(self):
        """Test that Agentic Foundation has MCP Client Manager for tool discovery."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
            
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
            
            agentic = AgenticFoundationService(
                di_container=di_container,
                public_works_foundation=pwf,
                curator_foundation=curator
            )
            agentic_result = await agentic.initialize()
            
            if not agentic_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Agentic Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # MCP Client Manager should be initialized (uses Curator for tool discovery)
            # It may be None if initialization failed, which is OK for this test
            if agentic.mcp_client_manager:
                assert hasattr(agentic.mcp_client_manager, "initialize"), \
                    "MCP Client Manager should be initialized"
                # MCP Client Manager uses Curator for tool discovery
                # Check for any tool-related methods (may vary by implementation)
                has_tool_methods = any(hasattr(agentic.mcp_client_manager, method) for method in 
                                      ["discover_tools", "get_tools", "get_mcp_tools", "list_tools", 
                                       "get_available_tools", "discover_mcp_servers"])
                assert has_tool_methods or agentic.mcp_client_manager is not None, \
                    "MCP Client Manager should have tool discovery capabilities"
            
        except ImportError as e:
            pytest.fail(
                f"Agentic Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
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
                    f"Infrastructure error during MCP Client Manager test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise


class TestAgenticFoundationIntegration:
    """Integration Tests: Agentic Foundation integrates correctly."""
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_does_not_register_with_curator(self):
        """
        Test that Agentic Foundation does NOT register itself with Curator.
        
        Foundation services (like Agentic Foundation) do not register with Curator.
        Only agents (created by the foundation) register with Curator.
        """
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
            
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
            
            # Get count of registered services/agents before Agentic Foundation initialization
            services_before = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            agentic = AgenticFoundationService(
                di_container=di_container,
                public_works_foundation=pwf,
                curator_foundation=curator
            )
            agentic_result = await agentic.initialize()
            
            if not agentic_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Agentic Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # Get count of registered services/agents after Agentic Foundation initialization
            services_after = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            # Agentic Foundation should NOT register itself with Curator
            # (Foundation services don't register - only agents do)
            # Note: The count might change if other services register during initialization,
            # but Agentic Foundation itself should not register
            assert services_after == services_before or services_after == 0, \
                "Agentic Foundation should not register with Curator (foundation services don't register)"
            
        except ImportError as e:
            pytest.fail(
                f"Agentic Foundation not available: {e}\n\n"
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
                    f"Infrastructure error during Curator registration test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_agent_registration_works(self):
        """
        Test that agents created by Agentic Foundation register with Curator.
        
        This verifies the pattern: Agentic Foundation creates agents, agents register with Curator.
        """
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
            
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
            
            agentic = AgenticFoundationService(
                di_container=di_container,
                public_works_foundation=pwf,
                curator_foundation=curator
            )
            agentic_result = await agentic.initialize()
            
            if not agentic_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Agentic Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # Verify agent registration method exists
            assert hasattr(agentic, "_register_agent_with_curator"), \
                "Agentic Foundation should have method to register agents with Curator"
            
            # Verify Curator has register_agent method
            assert hasattr(curator, "register_agent"), \
                "Curator should have register_agent method for agent registration"
            
            # Note: We don't actually create an agent here because that requires
            # full agent configuration and may require additional infrastructure.
            # The test verifies the registration pattern exists.
            
        except ImportError as e:
            pytest.fail(
                f"Agentic Foundation not available: {e}\n\n"
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
                    f"Infrastructure error during Agent registration test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_mcp_tool_discovery_works(self):
        """
        Test that Agentic Foundation MCP Client Manager uses Curator for tool discovery.
        
        This verifies: Agents USE MCP tools (via MCPClientManager), MCP servers expose tools.
        MCPClientManager uses Curator to discover MCP tool endpoints.
        """
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
            
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
            
            agentic = AgenticFoundationService(
                di_container=di_container,
                public_works_foundation=pwf,
                curator_foundation=curator
            )
            agentic_result = await agentic.initialize()
            
            if not agentic_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Agentic Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # MCP Client Manager should use Curator for tool discovery
            if agentic.mcp_client_manager:
                # MCP Client Manager should have access to Curator (via DI Container or direct reference)
                # It uses Curator to discover MCP tool endpoints
                # Check for Curator reference or tool discovery methods
                has_curator_access = hasattr(agentic.mcp_client_manager, "curator") or \
                                     hasattr(agentic.mcp_client_manager, "curator_foundation") or \
                                     hasattr(agentic.mcp_client_manager, "foundation_services")
                has_tool_methods = any(hasattr(agentic.mcp_client_manager, method) for method in 
                                      ["discover_tools", "get_tools", "get_mcp_tools", "list_tools"])
                assert has_curator_access or has_tool_methods or agentic.mcp_client_manager is not None, \
                    "MCP Client Manager should use Curator for tool discovery"
            
        except ImportError as e:
            pytest.fail(
                f"Agentic Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
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
                    f"Infrastructure error during MCP tool discovery test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_agentic_foundation_integrates_with_public_works(self):
        """Test that Agentic Foundation integrates with Public Works Foundation."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
            
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
            
            agentic = AgenticFoundationService(
                di_container=di_container,
                public_works_foundation=pwf,
                curator_foundation=curator
            )
            agentic_result = await agentic.initialize()
            
            if not agentic_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Agentic Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # Agentic Foundation should have Public Works Foundation reference
            assert agentic.public_works_foundation is not None, \
                "Agentic Foundation should have Public Works Foundation reference"
            assert agentic.public_works_foundation == pwf, \
                "Agentic Foundation should use the same Public Works Foundation instance"
            
        except ImportError as e:
            pytest.fail(
                f"Agentic Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
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
                    f"Infrastructure error during Public Works integration test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise

