#!/usr/bin/env python3
"""
Layer 2.1: Public Works Adapters - Initialization Tests

Component Tests: Individual adapters initialize correctly
Integration Tests: All adapters work together
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


class TestAdaptersInitialization:
    """Component Tests: Individual adapters initialize correctly."""
    
    @pytest.mark.asyncio
    async def test_redis_adapter_initializes(self):
        """Test that Redis adapter initializes correctly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.public_works_foundation.infrastructure_adapters.redis_adapter import RedisAdapter
            
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
            
            # Get Redis adapter from Public Works Foundation
            redis_adapter = pwf.redis_adapter
            assert redis_adapter is not None, "Redis adapter should be available"
            assert hasattr(redis_adapter, "get"), "Redis adapter should have get method"
            assert hasattr(redis_adapter, "set"), "Redis adapter should have set method"
            
        except ImportError as e:
            pytest.fail(
                f"Redis adapter not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
            )
        except ConnectionError as e:
            from tests.utils.safe_docker import check_container_status
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Redis connection failed: {e}\n\n"
                f"Infrastructure status:\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs: docker logs symphainy-redis"
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Infrastructure error during Redis adapter initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-redis"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_arangodb_adapter_initializes(self):
        """Test that ArangoDB adapter initializes correctly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            
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
            
            # Get ArangoDB adapter from Public Works Foundation (attribute is arango_adapter)
            arangodb_adapter = pwf.arango_adapter
            assert arangodb_adapter is not None, "ArangoDB adapter should be available"
            assert hasattr(arangodb_adapter, "create_document") or hasattr(arangodb_adapter, "db"), \
                "ArangoDB adapter should have create_document method or db attribute"
            
        except ImportError as e:
            pytest.fail(
                f"ArangoDB adapter not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
            )
        except ConnectionError as e:
            from tests.utils.safe_docker import check_container_status
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"ArangoDB connection failed: {e}\n\n"
                f"Infrastructure status:\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n\n"
                f"Check logs: docker logs symphainy-arangodb"
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                arango_status = check_container_status("symphainy-arangodb")
                
                pytest.fail(
                    f"Infrastructure error during ArangoDB adapter initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-arangodb"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_meilisearch_adapter_initializes(self):
        """Test that Meilisearch adapter initializes correctly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            
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
            
            # Get Meilisearch adapter from Public Works Foundation
            # Check if meilisearch_knowledge_adapter exists
            if hasattr(pwf, "meilisearch_knowledge_adapter"):
                meilisearch_adapter = pwf.meilisearch_knowledge_adapter
                assert meilisearch_adapter is not None, "Meilisearch adapter should be available"
                assert hasattr(meilisearch_adapter, "add_documents"), "Meilisearch adapter should have add_documents method"
                assert hasattr(meilisearch_adapter, "search"), "Meilisearch adapter should have search method"
            else:
                pytest.fail(
                    "Meilisearch adapter not available in Public Works Foundation.\n"
                    "This indicates a configuration or implementation issue.\n"
                    "Check that Meilisearch adapter is properly configured."
                )
            
        except ImportError as e:
            pytest.fail(
                f"Meilisearch adapter not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
            )
        except ConnectionError as e:
            from tests.utils.safe_docker import check_container_status
            # Meilisearch might not have a container, but check if it's configured
            pytest.fail(
                f"Meilisearch connection failed: {e}\n\n"
                f"Check Meilisearch configuration and ensure it's running."
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                pytest.fail(
                    f"Infrastructure error during Meilisearch adapter initialization: {e}\n\n"
                    f"Check Meilisearch configuration and ensure it's running."
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_all_adapters_initialized(self):
        """Test that all critical adapters are initialized."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            
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
            
            # Check critical adapters are initialized
            critical_adapters = [
                ("redis_adapter", "Redis"),
                ("arango_adapter", "ArangoDB"),  # Note: attribute is arango_adapter, not arangodb_adapter
                ("supabase_adapter", "Supabase"),
            ]
            
            for adapter_attr, adapter_name in critical_adapters:
                if hasattr(pwf, adapter_attr):
                    adapter = getattr(pwf, adapter_attr)
                    assert adapter is not None, f"{adapter_name} adapter should be initialized"
                else:
                    pytest.fail(
                        f"{adapter_name} adapter not available in Public Works Foundation.\n"
                        f"This indicates a configuration or implementation issue.\n"
                        f"Check that {adapter_name} adapter is properly configured."
                    )
            
        except ImportError as e:
            pytest.fail(
                f"Public Works Foundation not available: {e}\n\n"
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
                    f"Infrastructure error during adapter initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise


class TestAdaptersIntegration:
    """Integration Tests: All adapters work together."""
    
    @pytest.mark.asyncio
    async def test_adapters_work_with_real_infrastructure(self):
        """Test that adapters work with real infrastructure simultaneously."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            
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
            
            # Test Redis adapter with real Redis
            if hasattr(pwf, "redis_adapter") and pwf.redis_adapter:
                redis_adapter = pwf.redis_adapter
                # Test basic operations
                test_key = "test_key_layer2"
                test_value = "test_value_layer2"
                
                # Set value
                set_result = await redis_adapter.set(test_key, test_value)
                assert set_result is True, "Redis set should work"
                
                # Get value
                get_result = await redis_adapter.get(test_key)
                assert get_result == test_value, "Redis get should return correct value"
                
                # Delete value
                delete_result = await redis_adapter.delete(test_key)
                assert delete_result is True, "Redis delete should work"
            
            # Test ArangoDB adapter with real ArangoDB
            if hasattr(pwf, "arango_adapter") and pwf.arango_adapter:
                arangodb_adapter = pwf.arango_adapter
                # Test connection
                assert arangodb_adapter.db is not None, "ArangoDB connection should be available"
            
            # Test Meilisearch adapter with real Meilisearch
            if hasattr(pwf, "meilisearch_knowledge_adapter") and pwf.meilisearch_knowledge_adapter:
                meilisearch_adapter = pwf.meilisearch_knowledge_adapter
                # Test connection
                assert meilisearch_adapter.client is not None, "Meilisearch client should be available"
            
        except ImportError as e:
            pytest.fail(
                f"Public Works Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
            )
        except ConnectionError as e:
            from tests.utils.safe_docker import check_container_status
            redis_status = check_container_status("symphainy-redis")
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"Infrastructure connection failed: {e}\n\n"
                f"Infrastructure status:\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-redis\n"
                f"  docker logs symphainy-arangodb"
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                redis_status = check_container_status("symphainy-redis")
                arango_status = check_container_status("symphainy-arangodb")
                
                pytest.fail(
                    f"Infrastructure error during adapter operations: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-redis\n"
                    f"  docker logs symphainy-arangodb"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_adapters_error_handling(self):
        """Test that adapters handle errors gracefully."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            
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
            
            # Test Redis adapter error handling
            if hasattr(pwf, "redis_adapter") and pwf.redis_adapter:
                redis_adapter = pwf.redis_adapter
                # Try to get non-existent key
                result = await redis_adapter.get("non_existent_key_12345")
                # Should return None or empty, not raise exception
                assert result is None or result == "", "Redis get should handle non-existent keys gracefully"
            
        except ImportError as e:
            pytest.fail(
                f"Public Works Foundation not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that foundations are installed and in Python path."
            )
        except ConnectionError as e:
            from tests.utils.safe_docker import check_container_status
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Infrastructure connection failed: {e}\n\n"
                f"Infrastructure status:\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                f"Check logs: docker logs symphainy-redis"
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Infrastructure error during adapter error handling test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-redis"
                )
            else:
                raise

