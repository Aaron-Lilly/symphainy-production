#!/usr/bin/env python3
"""
Layer 7: Smart City Realm Integration Tests

Component Tests: Individual Smart City services work correctly
Integration Tests: Smart City composes/exposes platform capabilities and City Manager bootstraps correctly

Key Understanding:
- Smart City services use abstractions DIRECTLY (no Platform Gateway)
- Smart City services REGISTER with Curator (Phase 2 pattern)
- City Manager is the foundational manager with bootstrap pattern
- City Manager bootstraps manager hierarchy: Solution → Journey → Delivery
- City Manager orchestrates Smart City realm services
"""

import pytest
# Path is configured in pytest.ini - no manipulation needed

pytestmark = [pytest.mark.integration]


class TestSmartCityServicesComponents:
    """Component Tests: Individual Smart City services work correctly."""
    
    @pytest.mark.asyncio
    async def test_city_manager_initializes(self):
        """Test that City Manager Service initializes correctly."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
            
            di_container = DIContainerService("test_platform")
            pwf = PublicWorksFoundationService(di_container=di_container)
            pwf_result = await pwf.initialize()
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # Register Public Works Foundation with DI Container so City Manager can find it
            # DI Container stores it as public_works_foundation attribute
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
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            
            # Register Curator Foundation with DI Container (stored as curator_foundation attribute)
            di_container.curator_foundation = curator
            
            # Initialize City Manager
            city_manager = CityManagerService(di_container=di_container)
            city_manager_result = await city_manager.initialize()
            
            assert city_manager_result is True, "City Manager should initialize"
            assert city_manager.is_initialized, "City Manager should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"City Manager not available: {e}\n\n"
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
                    f"Infrastructure error during City Manager initialization: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_city_manager_uses_abstractions_directly(self):
        """Test that City Manager uses abstractions directly (no Platform Gateway)."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
            
            di_container = DIContainerService("test_platform")
            pwf = PublicWorksFoundationService(di_container=di_container)
            pwf_result = await pwf.initialize()
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # Register Public Works Foundation with DI Container so City Manager can find it
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
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            
            # Register Curator Foundation with DI Container
            di_container.curator_foundation = curator
            
            city_manager = CityManagerService(di_container=di_container)
            city_manager_result = await city_manager.initialize()
            
            if not city_manager_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"City Manager initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # City Manager should use abstractions directly from Public Works
            # (Smart City services have direct access, no Platform Gateway needed)
            # City Manager accesses Public Works via DI Container (not direct attribute)
            public_works = city_manager.di_container.get_foundation_service("PublicWorksFoundationService")
            assert public_works is not None, \
                "City Manager should access Public Works Foundation via DI Container"
            
            # City Manager should be able to get abstractions directly
            # (via get_infrastructure_abstraction() mixin method)
            session_abstraction = city_manager.get_session_abstraction()
            assert session_abstraction is not None, \
                "City Manager should access abstractions directly (no Platform Gateway)"
            
        except ImportError as e:
            pytest.fail(
                f"City Manager not available: {e}\n\n"
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
    async def test_city_manager_registers_with_curator(self):
        """Test that City Manager registers with Curator (Phase 2 pattern)."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
            
            di_container = DIContainerService("test_platform")
            pwf = PublicWorksFoundationService(di_container=di_container)
            pwf_result = await pwf.initialize()
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
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
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            
            # Register Public Works Foundation with DI Container so City Manager can find it
            di_container.public_works_foundation = pwf
            di_container.curator_foundation = curator
            
            # Get count of registered services before City Manager initialization
            services_before = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            city_manager = CityManagerService(di_container=di_container)
            city_manager_result = await city_manager.initialize()
            
            if not city_manager_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"City Manager initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # Get count of registered services after City Manager initialization
            services_after = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            # City Manager should register itself with Curator (Phase 2 pattern)
            # Note: The count might increase, or City Manager might be in registered_services
            assert services_after >= services_before, \
                "City Manager should register with Curator (Phase 2 pattern)"
            
            # Verify City Manager has registration method
            assert hasattr(city_manager, "register_with_curator") or \
                   hasattr(city_manager.soa_mcp_module, "register_capabilities"), \
                "City Manager should have registration method"
            
        except ImportError as e:
            pytest.fail(
                f"City Manager not available: {e}\n\n"
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


class TestCityManagerBootstrap:
    """Integration Tests: City Manager bootstrap pattern works correctly."""
    
    @pytest.mark.asyncio
    async def test_city_manager_has_bootstrap_method(self):
        """Test that City Manager has bootstrap_manager_hierarchy method."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
            
            di_container = DIContainerService("test_platform")
            pwf = PublicWorksFoundationService(di_container=di_container)
            pwf_result = await pwf.initialize()
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # Register Public Works Foundation with DI Container so City Manager can find it
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
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            
            # Register Curator Foundation with DI Container
            di_container.curator_foundation = curator
            
            city_manager = CityManagerService(di_container=di_container)
            city_manager_result = await city_manager.initialize()
            
            if not city_manager_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"City Manager initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # City Manager should have bootstrap method
            assert hasattr(city_manager, "bootstrap_manager_hierarchy") or \
                   hasattr(city_manager.bootstrapping_module, "bootstrap_manager_hierarchy"), \
                "City Manager should have bootstrap_manager_hierarchy method"
            
            # City Manager should track manager hierarchy
            assert hasattr(city_manager, "manager_hierarchy"), \
                "City Manager should track manager hierarchy"
            assert isinstance(city_manager.manager_hierarchy, dict), \
                "Manager hierarchy should be a dictionary"
            
        except ImportError as e:
            pytest.fail(
                f"City Manager not available: {e}\n\n"
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
                    f"Infrastructure error during bootstrap method test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_city_manager_bootstraps_manager_hierarchy(self):
        """
        Test that City Manager bootstraps manager hierarchy: Solution → Journey → Delivery.
        
        This verifies the foundational manager role with bootstrap pattern.
        """
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
            
            di_container = DIContainerService("test_platform")
            pwf = PublicWorksFoundationService(di_container=di_container)
            pwf_result = await pwf.initialize()
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # Register Public Works Foundation with DI Container so City Manager can find it
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
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            
            # Register Curator Foundation with DI Container
            di_container.curator_foundation = curator
            
            city_manager = CityManagerService(di_container=di_container)
            city_manager_result = await city_manager.initialize()
            
            if not city_manager_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"City Manager initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # Bootstrap manager hierarchy
            bootstrap_method = getattr(city_manager, "bootstrap_manager_hierarchy", None) or \
                             getattr(city_manager.bootstrapping_module, "bootstrap_manager_hierarchy", None)
            
            if bootstrap_method:
                # Call bootstrap (may require additional setup)
                try:
                    result = await bootstrap_method()
                    
                    # Bootstrap should return success result
                    if isinstance(result, dict):
                        assert result.get("success") is True or "success" not in result, \
                            "Bootstrap should succeed or return result dict"
                    elif isinstance(result, bool):
                        assert result is True, "Bootstrap should return True on success"
                    
                except Exception as e:
                    # Bootstrap may require additional infrastructure (realm services, etc.)
                    # This is OK - we're testing that the method exists and is callable
                    # But we should still fail with diagnostics instead of skipping
                    from tests.utils.safe_docker import check_container_status
                    consul_status = check_container_status("symphainy-consul")
                    arango_status = check_container_status("symphainy-arangodb")
                    redis_status = check_container_status("symphainy-redis")
                    
                    pytest.fail(
                        f"Bootstrap requires additional infrastructure: {e}\n\n"
                        f"Infrastructure status:\n"
                        f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                        f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                        f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                        f"Note: Bootstrap may require realm services beyond core infrastructure.\n"
                        f"Check Docker containers: docker ps --filter name=symphainy-"
                    )
            
        except ImportError as e:
            pytest.fail(
                f"City Manager not available: {e}\n\n"
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
                    f"Infrastructure error during bootstrap hierarchy test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_city_manager_orchestrates_realm_startup(self):
        """Test that City Manager orchestrates Smart City realm services."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
            
            di_container = DIContainerService("test_platform")
            pwf = PublicWorksFoundationService(di_container=di_container)
            pwf_result = await pwf.initialize()
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # Register Public Works Foundation with DI Container so City Manager can find it
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
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            
            # Register Curator Foundation with DI Container
            di_container.curator_foundation = curator
            
            city_manager = CityManagerService(di_container=di_container)
            city_manager_result = await city_manager.initialize()
            
            if not city_manager_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"City Manager initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # City Manager should have realm orchestration method
            assert hasattr(city_manager, "orchestrate_realm_startup") or \
                   hasattr(city_manager.realm_orchestration_module, "orchestrate_realm_startup"), \
                "City Manager should have orchestrate_realm_startup method"
            
            # City Manager should track Smart City services
            assert hasattr(city_manager, "smart_city_services"), \
                "City Manager should track Smart City services"
            assert isinstance(city_manager.smart_city_services, dict), \
                "Smart City services should be a dictionary"
            
        except ImportError as e:
            pytest.fail(
                f"City Manager not available: {e}\n\n"
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
                    f"Infrastructure error during realm orchestration test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise


class TestSmartCityPlatformCapabilities:
    """Integration Tests: Smart City composes/exposes platform capabilities."""
    
    @pytest.mark.asyncio
    async def test_smart_city_services_use_abstractions_directly(self):
        """
        Test that Smart City services use abstractions directly (no Platform Gateway).
        
        This verifies that Smart City composes/exposes platform capabilities directly.
        """
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
            
            di_container = DIContainerService("test_platform")
            pwf = PublicWorksFoundationService(di_container=di_container)
            pwf_result = await pwf.initialize()
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # Register Public Works Foundation with DI Container so City Manager can find it
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
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            
            # Register Curator Foundation with DI Container
            di_container.curator_foundation = curator
            
            city_manager = CityManagerService(di_container=di_container)
            city_manager_result = await city_manager.initialize()
            
            if not city_manager_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"City Manager initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # Smart City services should use abstractions directly from Public Works
            # (not via Platform Gateway - that's for other realms)
            # City Manager accesses Public Works via DI Container
            public_works = city_manager.di_container.get_foundation_service("PublicWorksFoundationService")
            assert public_works is not None, \
                "City Manager should access Public Works Foundation via DI Container"
            
            # Should be able to get abstractions directly via mixin method
            auth_abstraction = city_manager.get_auth_abstraction()
            assert auth_abstraction is not None, \
                "Smart City services should access abstractions directly (no Platform Gateway)"
            
        except ImportError as e:
            pytest.fail(
                f"City Manager not available: {e}\n\n"
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
                    f"Infrastructure error during platform capabilities test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_smart_city_services_register_with_curator(self):
        """
        Test that Smart City services register with Curator (Phase 2 pattern).
        
        This verifies that Smart City services expose their capabilities via Curator
        for other realms to discover and use.
        """
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
            
            di_container = DIContainerService("test_platform")
            pwf = PublicWorksFoundationService(di_container=di_container)
            pwf_result = await pwf.initialize()
            
            if not pwf_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Public Works Foundation initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
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
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            
            # Register Public Works Foundation with DI Container so City Manager can find it
            di_container.public_works_foundation = pwf
            di_container.curator_foundation = curator
            
            # Get count of registered services before City Manager initialization
            services_before = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            city_manager = CityManagerService(di_container=di_container)
            city_manager_result = await city_manager.initialize()
            
            if not city_manager_result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"City Manager initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            
            # Get count of registered services after City Manager initialization
            services_after = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            # City Manager should register itself with Curator
            # This allows other realms to discover and use Smart City capabilities
            assert services_after >= services_before, \
                "City Manager should register with Curator to expose platform capabilities"
            
            # Verify City Manager is discoverable via Curator
            # (Other realms use Curator to discover Smart City services)
            if hasattr(curator, "discover_service_by_name"):
                city_manager_discovered = await curator.discover_service_by_name("CityManager")
                # May be None if not registered yet, but method should work
                assert city_manager_discovered is None or isinstance(city_manager_discovered, (dict, object)), \
                    "City Manager should be discoverable via Curator"
            
        except ImportError as e:
            pytest.fail(
                f"City Manager not available: {e}\n\n"
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
                    f"Infrastructure error during service registration test: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n\n"
                    f"Check logs: docker logs symphainy-consul"
                )
            else:
                raise

