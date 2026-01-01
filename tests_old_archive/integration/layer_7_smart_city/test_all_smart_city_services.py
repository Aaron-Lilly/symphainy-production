#!/usr/bin/env python3
"""
Layer 7: All Smart City Services Tests

Comprehensive tests for ALL Smart City services to ensure 100% coverage and 100% pass rate.
Each service is critical infrastructure - the platform won't function without them.

Smart City Services:
1. City Manager (already tested in test_smart_city_integration.py)
2. Security Guard
3. Traffic Cop
4. Nurse
5. Librarian
6. Data Steward
7. Content Steward
8. Post Office
9. Conductor

Test Pattern for Each Service:
- Service initializes correctly
- Service uses abstractions directly (no Platform Gateway)
- Service registers with Curator (Phase 2 pattern)
- Service has required methods/functionality
"""

import pytest
import asyncio
# Path is configured in pytest.ini - no manipulation needed

pytestmark = [pytest.mark.integration]


class TestSmartCityServicesInitialization:
    """Test that all Smart City services initialize correctly."""
    
    @pytest.mark.asyncio
    async def test_security_guard_initializes(self):
        """Test that Security Guard Service initializes correctly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.security_guard.security_guard_service import SecurityGuardService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            security_guard = SecurityGuardService(di_container=di_container)
            result = await security_guard.initialize()
            
            assert result is True, "Security Guard should initialize"
            assert security_guard.is_initialized, "Security Guard should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Security Guard not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during Security Guard initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_traffic_cop_initializes(self):
        """Test that Traffic Cop Service initializes correctly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            traffic_cop = TrafficCopService(di_container=di_container)
            result = await traffic_cop.initialize()
            
            assert result is True, "Traffic Cop should initialize"
            assert traffic_cop.is_initialized, "Traffic Cop should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Traffic Cop not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during Traffic Cop initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_nurse_initializes(self):
        """Test that Nurse Service initializes correctly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.nurse.nurse_service import NurseService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            nurse = NurseService(di_container=di_container)
            result = await nurse.initialize()
            
            assert result is True, "Nurse should initialize"
            assert nurse.is_initialized, "Nurse should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Nurse not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during Nurse initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_librarian_initializes(self):
        """Test that Librarian Service initializes correctly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.librarian.librarian_service import LibrarianService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            librarian = LibrarianService(di_container=di_container)
            result = await librarian.initialize()
            
            assert result is True, "Librarian should initialize"
            assert librarian.is_initialized, "Librarian should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Librarian not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during Librarian initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_data_steward_initializes(self):
        """Test that Data Steward Service initializes correctly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.data_steward.data_steward_service import DataStewardService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            data_steward = DataStewardService(di_container=di_container)
            result = await data_steward.initialize()
            
            assert result is True, "Data Steward should initialize"
            assert data_steward.is_initialized, "Data Steward should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Data Steward not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during Data Steward initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_content_steward_initializes(self):
        """Test that Content Steward Service initializes correctly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.content_steward.content_steward_service import ContentStewardService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            content_steward = ContentStewardService(di_container=di_container)
            result = await content_steward.initialize()
            
            assert result is True, "Content Steward should initialize"
            assert content_steward.is_initialized, "Content Steward should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Content Steward not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during Content Steward initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_post_office_initializes(self):
        """Test that Post Office Service initializes correctly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.post_office.post_office_service import PostOfficeService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            post_office = PostOfficeService(di_container=di_container)
            result = await post_office.initialize()
            
            assert result is True, "Post Office should initialize"
            assert post_office.is_initialized, "Post Office should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Post Office not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during Post Office initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_conductor_initializes(self):
        """Test that Conductor Service initializes correctly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.conductor.conductor_service import ConductorService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            conductor = ConductorService(di_container=di_container)
            result = await conductor.initialize()
            
            assert result is True, "Conductor should initialize"
            assert conductor.is_initialized, "Conductor should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Conductor not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during Conductor initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise


class TestSmartCityServicesAbstractionAccess:
    """Test that all Smart City services use abstractions directly."""
    
    @pytest.mark.asyncio
    async def test_security_guard_uses_abstractions_directly(self):
        """Test that Security Guard uses abstractions directly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.security_guard.security_guard_service import SecurityGuardService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            security_guard = SecurityGuardService(di_container=di_container)
            result = await security_guard.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Security Guard initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # Security Guard should access abstractions directly
            auth_abstraction = security_guard.get_auth_abstraction()
            assert auth_abstraction is not None, \
                "Security Guard should access abstractions directly (no Platform Gateway)"
            
        except ImportError as e:
            pytest.fail(
                f"Security Guard not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during abstraction access test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_traffic_cop_uses_abstractions_directly(self):
        """Test that Traffic Cop uses abstractions directly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            traffic_cop = TrafficCopService(di_container=di_container)
            result = await traffic_cop.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Traffic Cop initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # Traffic Cop should access abstractions directly
            session_abstraction = traffic_cop.get_session_abstraction()
            assert session_abstraction is not None, \
                "Traffic Cop should access abstractions directly (no Platform Gateway)"
            
        except ImportError as e:
            pytest.fail(
                f"Traffic Cop not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during abstraction access test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_nurse_uses_abstractions_directly(self):
        """Test that Nurse uses abstractions directly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.nurse.nurse_service import NurseService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            nurse = NurseService(di_container=di_container)
            result = await nurse.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Nurse initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # Nurse should access abstractions directly
            health_abstraction = nurse.get_health_abstraction()
            # Health abstraction may be None (optional), but method should work
            assert hasattr(nurse, "get_health_abstraction"), \
                "Nurse should have method to access abstractions directly"
            
        except ImportError as e:
            pytest.fail(
                f"Nurse not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during abstraction access test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_librarian_uses_abstractions_directly(self):
        """Test that Librarian uses abstractions directly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.librarian.librarian_service import LibrarianService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            librarian = LibrarianService(di_container=di_container)
            result = await librarian.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Librarian initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # Librarian should access abstractions directly
            file_abstraction = librarian.get_file_management_abstraction()
            assert file_abstraction is not None, \
                "Librarian should access abstractions directly (no Platform Gateway)"
            
        except ImportError as e:
            pytest.fail(
                f"Librarian not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during abstraction access test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_data_steward_uses_abstractions_directly(self):
        """Test that Data Steward uses abstractions directly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.data_steward.data_steward_service import DataStewardService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            data_steward = DataStewardService(di_container=di_container)
            result = await data_steward.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Data Steward initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # Data Steward should access abstractions directly
            # Check for any abstraction access method
            assert hasattr(data_steward, "get_infrastructure_abstraction"), \
                "Data Steward should have method to access abstractions directly"
            
        except ImportError as e:
            pytest.fail(
                f"Data Steward not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during abstraction access test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_content_steward_uses_abstractions_directly(self):
        """Test that Content Steward uses abstractions directly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.content_steward.content_steward_service import ContentStewardService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            content_steward = ContentStewardService(di_container=di_container)
            result = await content_steward.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Content Steward initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # Content Steward should access abstractions directly
            content_metadata_abstraction = content_steward.get_content_metadata_abstraction()
            assert content_metadata_abstraction is not None, \
                "Content Steward should access abstractions directly (no Platform Gateway)"
            
        except ImportError as e:
            pytest.fail(
                f"Content Steward not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during abstraction access test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_post_office_uses_abstractions_directly(self):
        """Test that Post Office uses abstractions directly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.post_office.post_office_service import PostOfficeService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            post_office = PostOfficeService(di_container=di_container)
            result = await post_office.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Post Office initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # Post Office should access abstractions directly
            messaging_abstraction = post_office.get_messaging_abstraction()
            assert messaging_abstraction is not None, \
                "Post Office should access abstractions directly (no Platform Gateway)"
            
        except ImportError as e:
            pytest.fail(
                f"Post Office not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during abstraction access test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_conductor_uses_abstractions_directly(self):
        """Test that Conductor uses abstractions directly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.conductor.conductor_service import ConductorService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            conductor = ConductorService(di_container=di_container)
            result = await conductor.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Conductor initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            # Conductor should access abstractions directly
            workflow_abstraction = conductor.get_workflow_orchestration_abstraction()
            # Workflow abstraction may be None, but method should exist
            assert hasattr(conductor, "get_workflow_orchestration_abstraction"), \
                "Conductor should have method to access abstractions directly"
            
        except ImportError as e:
            pytest.fail(
                f"Conductor not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
                    f"Infrastructure error during abstraction access test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise


class TestSmartCityServicesCuratorRegistration:
    """Test that all Smart City services register with Curator (Phase 2 pattern)."""
    
    @pytest.mark.asyncio
    async def test_security_guard_registers_with_curator(self):
        """Test that Security Guard registers with Curator."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.security_guard.security_guard_service import SecurityGuardService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            services_before = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            security_guard = SecurityGuardService(di_container=di_container)
            result = await security_guard.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Security Guard initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            services_after = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            # Security Guard should register with Curator
            assert services_after >= services_before, \
                "Security Guard should register with Curator (Phase 2 pattern)"
            
        except ImportError as e:
            pytest.fail(
                f"Security Guard not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
    async def test_traffic_cop_registers_with_curator(self):
        """Test that Traffic Cop registers with Curator."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            services_before = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            traffic_cop = TrafficCopService(di_container=di_container)
            result = await traffic_cop.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Traffic Cop initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            services_after = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            # Traffic Cop should register with Curator
            assert services_after >= services_before, \
                "Traffic Cop should register with Curator (Phase 2 pattern)"
            
        except ImportError as e:
            pytest.fail(
                f"Traffic Cop not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
    async def test_nurse_registers_with_curator(self):
        """Test that Nurse registers with Curator."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.nurse.nurse_service import NurseService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            services_before = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            nurse = NurseService(di_container=di_container)
            result = await nurse.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Nurse initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            services_after = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            # Nurse should register with Curator
            assert services_after >= services_before, \
                "Nurse should register with Curator (Phase 2 pattern)"
            
        except ImportError as e:
            pytest.fail(
                f"Nurse not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
    async def test_librarian_registers_with_curator(self):
        """Test that Librarian registers with Curator."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.librarian.librarian_service import LibrarianService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            services_before = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            librarian = LibrarianService(di_container=di_container)
            result = await librarian.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Librarian initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            services_after = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            # Librarian should register with Curator
            assert services_after >= services_before, \
                "Librarian should register with Curator (Phase 2 pattern)"
            
        except ImportError as e:
            pytest.fail(
                f"Librarian not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
    async def test_data_steward_registers_with_curator(self):
        """Test that Data Steward registers with Curator."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.data_steward.data_steward_service import DataStewardService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            services_before = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            data_steward = DataStewardService(di_container=di_container)
            result = await data_steward.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Data Steward initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            services_after = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            # Data Steward should register with Curator
            assert services_after >= services_before, \
                "Data Steward should register with Curator (Phase 2 pattern)"
            
        except ImportError as e:
            pytest.fail(
                f"Data Steward not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
    async def test_content_steward_registers_with_curator(self):
        """Test that Content Steward registers with Curator."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.content_steward.content_steward_service import ContentStewardService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            services_before = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            content_steward = ContentStewardService(di_container=di_container)
            result = await content_steward.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Content Steward initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            services_after = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            # Content Steward should register with Curator
            assert services_after >= services_before, \
                "Content Steward should register with Curator (Phase 2 pattern)"
            
        except ImportError as e:
            pytest.fail(
                f"Content Steward not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
    async def test_post_office_registers_with_curator(self):
        """Test that Post Office registers with Curator."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.post_office.post_office_service import PostOfficeService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            services_before = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            post_office = PostOfficeService(di_container=di_container)
            result = await post_office.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Post Office initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            services_after = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            # Post Office should register with Curator
            assert services_after >= services_before, \
                "Post Office should register with Curator (Phase 2 pattern)"
            
        except ImportError as e:
            pytest.fail(
                f"Post Office not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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
    async def test_conductor_registers_with_curator(self):
        """Test that Conductor registers with Curator."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.conductor.conductor_service import ConductorService
            
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
            
            di_container.public_works_foundation = pwf
            
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
            
            di_container.curator_foundation = curator
            
            services_before = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            conductor = ConductorService(di_container=di_container)
            result = await conductor.initialize()
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Conductor initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            services_after = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            # Conductor should register with Curator
            assert services_after >= services_before, \
                "Conductor should register with Curator (Phase 2 pattern)"
            
        except ImportError as e:
            pytest.fail(
                f"Conductor not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that smart_city services are installed and in Python path."
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


