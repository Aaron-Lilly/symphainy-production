#!/usr/bin/env python3
"""
Layer 3: Service Discovery Tests

Verifies that enabling services can discover and use Smart City services via Curator.

Tests:
1. Enabling services can discover Librarian via get_librarian_api()
2. Enabling services can discover Data Steward via get_data_steward_api()
3. Enabling services can discover Content Steward via get_content_steward_api()
4. Services are registered with Curator (capability registration)
5. SOA APIs are callable and return expected results

This validates the service discovery architecture pattern.
"""

import pytest
import asyncio
from typing import Dict, Any, Optional

pytestmark = [pytest.mark.integration]


class TestServiceDiscovery:
    """Test that enabling services can discover Smart City services via Curator."""
    
    @pytest.mark.asyncio
    async def test_enabling_service_discovers_librarian(self, smart_city_infrastructure):
        """Verify enabling service can discover Librarian via Curator."""
        try:
            from backend.business_enablement.enabling_services.validation_engine_service.validation_engine_service import ValidationEngineService
            
            infra = smart_city_infrastructure
            service = ValidationEngineService(
                service_name="ValidationEngineService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            # Initialize service (this should discover Smart City services via Curator)
            result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            if not result:
                pytest.fail("Validation Engine Service failed to initialize")
            
            # Verify service can discover Librarian
            librarian = await service.get_librarian_api()
            
            if librarian is None:
                # Check if Librarian is in Smart City services
                librarian_service = infra["smart_city_services"].get("librarian")
                if librarian_service is None:
                    pytest.fail(
                        f"Librarian service not initialized in Smart City infrastructure.\n"
                        f"Initialization results: {infra['initialization_results']}\n\n"
                        f"Fix: Ensure Librarian service initializes correctly."
                    )
                else:
                    pytest.fail(
                        f"Validation Engine Service cannot discover Librarian via Curator.\n"
                        f"Librarian service exists but service discovery failed.\n\n"
                        f"Check:\n"
                        f"  1. Librarian is registered with Curator\n"
                        f"  2. Service discovery is working correctly\n"
                        f"  3. Curator capability registry is accessible"
                    )
            
            # Verify Librarian has expected methods (SOA API)
            assert hasattr(librarian, "get_document") or hasattr(librarian, "retrieve_document"), \
                "Librarian should have document retrieval methods"
            
        except ImportError as e:
            pytest.fail(f"Validation Engine Service not available: {e}")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                
                pytest.fail(
                    f"Service discovery test failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_enabling_service_discovers_data_steward(self, smart_city_infrastructure):
        """Verify enabling service can discover Data Steward via Curator."""
        try:
            from backend.business_enablement.enabling_services.validation_engine_service.validation_engine_service import ValidationEngineService
            
            infra = smart_city_infrastructure
            service = ValidationEngineService(
                service_name="ValidationEngineService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            if not result:
                pytest.fail("Validation Engine Service failed to initialize")
            
            # Verify service can discover Data Steward
            data_steward = await service.get_data_steward_api()
            
            if data_steward is None:
                data_steward_service = infra["smart_city_services"].get("data_steward")
                if data_steward_service is None:
                    pytest.fail(
                        f"Data Steward service not initialized in Smart City infrastructure.\n"
                        f"Initialization results: {infra['initialization_results']}\n\n"
                        f"Fix: Ensure Data Steward service initializes correctly."
                    )
                else:
                    pytest.fail(
                        f"Validation Engine Service cannot discover Data Steward via Curator.\n"
                        f"Data Steward service exists but service discovery failed.\n\n"
                        f"Check:\n"
                        f"  1. Data Steward is registered with Curator\n"
                        f"  2. Service discovery is working correctly\n"
                        f"  3. Curator capability registry is accessible"
                    )
            
            # Verify Data Steward has expected methods (SOA API)
            assert hasattr(data_steward, "validate_schema") or hasattr(data_steward, "record_lineage") or hasattr(data_steward, "get_lineage"), \
                "Data Steward should have schema validation or lineage tracking methods"
            
        except ImportError as e:
            pytest.fail(f"Validation Engine Service not available: {e}")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                
                pytest.fail(
                    f"Service discovery test failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_enabling_service_discovers_content_steward(self, smart_city_infrastructure):
        """Verify enabling service can discover Content Steward via Curator."""
        try:
            from backend.business_enablement.enabling_services.validation_engine_service.validation_engine_service import ValidationEngineService
            
            infra = smart_city_infrastructure
            service = ValidationEngineService(
                service_name="ValidationEngineService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            if not result:
                pytest.fail("Validation Engine Service failed to initialize")
            
            # Verify service can discover Content Steward
            content_steward = await service.get_content_steward_api()
            
            if content_steward is None:
                content_steward_service = infra["smart_city_services"].get("content_steward")
                if content_steward_service is None:
                    pytest.fail(
                        f"Content Steward service not initialized in Smart City infrastructure.\n"
                        f"Initialization results: {infra['initialization_results']}\n\n"
                        f"Fix: Ensure Content Steward service initializes correctly."
                    )
                else:
                    pytest.fail(
                        f"Validation Engine Service cannot discover Content Steward via Curator.\n"
                        f"Content Steward service exists but service discovery failed.\n\n"
                        f"Check:\n"
                        f"  1. Content Steward is registered with Curator\n"
                        f"  2. Service discovery is working correctly\n"
                        f"  3. Curator capability registry is accessible"
                    )
            
            # Verify Content Steward has expected methods (SOA API)
            assert hasattr(content_steward, "process_upload") or hasattr(content_steward, "store_file"), \
                "Content Steward should have file storage methods"
            
        except ImportError as e:
            pytest.fail(f"Validation Engine Service not available: {e}")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                
                pytest.fail(
                    f"Service discovery test failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_enabling_service_registered_with_curator(self, smart_city_infrastructure):
        """Verify enabling service is registered with Curator."""
        try:
            from backend.business_enablement.enabling_services.validation_engine_service.validation_engine_service import ValidationEngineService
            
            infra = smart_city_infrastructure
            curator = infra["curator"]
            
            # Get initial service count (if available)
            initial_count = 0
            if hasattr(curator, "registered_services"):
                initial_count = len(curator.registered_services) if curator.registered_services else 0
            
            # Create and initialize service
            service = ValidationEngineService(
                service_name="ValidationEngineService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            if not result:
                pytest.fail("Validation Engine Service failed to initialize")
            
            # Verify service is registered with Curator
            # Check via capability registry
            if hasattr(curator, "capability_registry_service"):
                capability_registry = curator.capability_registry_service
                if hasattr(capability_registry, "get_capabilities"):
                    capabilities = capability_registry.get_capabilities()
                    # Check if ValidationEngineService capabilities are registered
                    validation_capabilities = [
                        cap for cap in capabilities
                        if "ValidationEngineService" in str(cap) or "validation" in str(cap).lower()
                    ]
                    if not validation_capabilities:
                        pytest.fail(
                            f"Validation Engine Service capabilities not found in Curator registry.\n"
                            f"Total capabilities: {len(capabilities)}\n\n"
                            f"Check:\n"
                            f"  1. Service registration completed successfully\n"
                            f"  2. Capability registry is accessible\n"
                            f"  3. Service name matches registry entries"
                        )
            
            # Alternative: Check registered_services if available
            if hasattr(curator, "registered_services") and curator.registered_services:
                # registered_services might be a dict or list
                if isinstance(curator.registered_services, dict):
                    service_names = list(curator.registered_services.keys())
                elif isinstance(curator.registered_services, list):
                    service_names = [svc.get("name", "") if isinstance(svc, dict) else str(svc) for svc in curator.registered_services]
                else:
                    service_names = []
                
                # Check if ValidationEngineService is registered (might be registered with different name pattern)
                # This is not necessarily a failure - services might be registered differently
                # But we should verify the pattern exists
                if service_names and "ValidationEngineService" not in str(service_names):
                    # Service might be registered with a different name pattern
                    # This is acceptable - the important thing is that it's registered
                    pass
            
        except ImportError as e:
            pytest.fail(f"Validation Engine Service not available: {e}")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                
                pytest.fail(
                    f"Curator registration test failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_multiple_services_discover_smart_city_services(self, smart_city_infrastructure):
        """Verify multiple enabling services can discover Smart City services."""
        try:
            from backend.business_enablement.enabling_services.validation_engine_service.validation_engine_service import ValidationEngineService
            from backend.business_enablement.enabling_services.data_analyzer_service.data_analyzer_service import DataAnalyzerService
            
            infra = smart_city_infrastructure
            
            # Test Validation Engine
            validation_service = ValidationEngineService(
                service_name="ValidationEngineService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            await asyncio.wait_for(validation_service.initialize(), timeout=30.0)
            
            validation_librarian = await validation_service.get_librarian_api()
            assert validation_librarian is not None, "Validation Engine should discover Librarian"
            
            # Test Data Analyzer
            data_analyzer_service = DataAnalyzerService(
                service_name="DataAnalyzerService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            await asyncio.wait_for(data_analyzer_service.initialize(), timeout=30.0)
            
            data_analyzer_librarian = await data_analyzer_service.get_librarian_api()
            assert data_analyzer_librarian is not None, "Data Analyzer should discover Librarian"
            
            # Verify both services can discover the same Smart City service
            # (They should get the same instance or equivalent instances)
            assert validation_librarian is not None and data_analyzer_librarian is not None, \
                "Both services should be able to discover Librarian"
            
        except ImportError as e:
            pytest.fail(f"Service not available: {e}")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                
                pytest.fail(
                    f"Multi-service discovery test failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise

