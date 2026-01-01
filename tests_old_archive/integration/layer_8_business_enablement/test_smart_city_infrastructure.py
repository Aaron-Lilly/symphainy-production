#!/usr/bin/env python3
"""
Smart City Infrastructure Fixture for Enabling Service Tests

Provides comprehensive test infrastructure that ensures all required Smart City services
are initialized and available for enabling service tests.

This fixture:
1. Initializes Public Works Foundation and Curator
2. Initializes all required Smart City services in correct order
3. Registers services with Curator for service discovery
4. Provides service APIs to enabling service tests
5. Provides clear diagnostics when services aren't available

Usage:
    @pytest.mark.asyncio
    async def test_my_service(self, smart_city_infrastructure):
        infra = smart_city_infrastructure
        service = MyService(
            service_name="MyService",
            realm_name="business_enablement",
            platform_gateway=infra["platform_gateway"],
            di_container=infra["di_container"]
        )
        # Service can now discover Smart City services via Curator
"""

import pytest
import asyncio
from typing import Dict, Any, Optional, List
from tests.utils.safe_docker import check_container_status


class SmartCityServiceManager:
    """Manages Smart City service initialization for tests."""
    
    # Startup order (dependencies considered)
    STARTUP_ORDER = [
        "security_guard",   # First: Security infrastructure
        "traffic_cop",      # Second: Traffic management
        "nurse",            # Third: Health monitoring
        "librarian",        # Fourth: Knowledge management
        "data_steward",     # Fifth: Data management
        "content_steward",  # Sixth: Content management
        "post_office",      # Seventh: Communication
        "conductor"         # Eighth: Workflow orchestration
    ]
    
    # Service class mappings
    SERVICE_CLASSES = {
        "security_guard": ("backend.smart_city.services.security_guard.security_guard_service", "SecurityGuardService"),
        "traffic_cop": ("backend.smart_city.services.traffic_cop.traffic_cop_service", "TrafficCopService"),
        "nurse": ("backend.smart_city.services.nurse.nurse_service", "NurseService"),
        "librarian": ("backend.smart_city.services.librarian.librarian_service", "LibrarianService"),
        "data_steward": ("backend.smart_city.services.data_steward.data_steward_service", "DataStewardService"),
        "content_steward": ("backend.smart_city.services.content_steward.content_steward_service", "ContentStewardService"),
        "post_office": ("backend.smart_city.services.post_office.post_office_service", "PostOfficeService"),
        "conductor": ("backend.smart_city.services.conductor.conductor_service", "ConductorService"),
    }
    
    def __init__(self, di_container: Any, curator: Any):
        """Initialize service manager."""
        self.di_container = di_container
        self.curator = curator
        self.services: Dict[str, Any] = {}
        self.initialization_errors: Dict[str, str] = {}
    
    async def initialize_all_services(self, timeout: float = 60.0) -> Dict[str, Any]:
        """
        Initialize all Smart City services in correct order.
        
        Args:
            timeout: Total timeout for all service initialization
            
        Returns:
            Dictionary with initialization results
        """
        results = {
            "initialized": [],
            "failed": [],
            "errors": {}
        }
        
        for service_name in self.STARTUP_ORDER:
            try:
                # Import service class
                module_path, class_name = self.SERVICE_CLASSES[service_name]
                module = __import__(module_path, fromlist=[class_name])
                service_class = getattr(module, class_name)
                
                # Create service instance
                service = service_class(di_container=self.di_container)
                
                # Initialize with timeout
                try:
                    init_result = await asyncio.wait_for(
                        service.initialize(),
                        timeout=30.0  # 30 seconds per service
                    )
                except asyncio.TimeoutError:
                    results["failed"].append(service_name)
                    results["errors"][service_name] = f"Initialization timed out after 30 seconds"
                    self.initialization_errors[service_name] = "timeout"
                    continue
                
                if init_result:
                    self.services[service_name] = service
                    results["initialized"].append(service_name)
                else:
                    results["failed"].append(service_name)
                    results["errors"][service_name] = "Initialization returned False"
                    self.initialization_errors[service_name] = "initialization_failed"
                    
            except ImportError as e:
                results["failed"].append(service_name)
                results["errors"][service_name] = f"Import error: {e}"
                self.initialization_errors[service_name] = f"import_error: {e}"
            except Exception as e:
                results["failed"].append(service_name)
                results["errors"][service_name] = f"Error: {e}"
                self.initialization_errors[service_name] = f"error: {e}"
        
        return results
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get initialized service by name."""
        return self.services.get(service_name)
    
    def get_diagnostics(self) -> str:
        """Get diagnostic information about service availability."""
        lines = []
        lines.append("Smart City Service Status:")
        lines.append("=" * 50)
        
        for service_name in self.STARTUP_ORDER:
            if service_name in self.services:
                lines.append(f"  ✅ {service_name}: Initialized")
            elif service_name in self.initialization_errors:
                error = self.initialization_errors[service_name]
                lines.append(f"  ❌ {service_name}: Failed ({error})")
            else:
                lines.append(f"  ⚠️  {service_name}: Not initialized")
        
        return "\n".join(lines)


@pytest.fixture(scope="function")
async def smart_city_infrastructure():
    """
    Comprehensive Smart City infrastructure fixture for enabling service tests.
    
    Initializes:
    - Public Works Foundation
    - Curator Foundation
    - Platform Gateway
    - All required Smart City services (Librarian, Data Steward, Content Steward, etc.)
    
    Returns:
        Dictionary with:
        - di_container: DIContainerService
        - public_works_foundation: PublicWorksFoundationService
        - curator: CuratorFoundationService
        - platform_gateway: PlatformInfrastructureGateway
        - smart_city_services: Dict of initialized Smart City services
        - service_manager: SmartCityServiceManager instance
    """
    from foundations.di_container.di_container_service import DIContainerService
    from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
    from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
    from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
    
    # 1. Initialize DI Container
    di_container = DIContainerService("test_platform")
    
    # 2. Initialize Public Works Foundation
    pwf = PublicWorksFoundationService(di_container=di_container)
    
    try:
        pwf_result = await asyncio.wait_for(
            pwf.initialize(),
            timeout=30.0
        )
    except asyncio.TimeoutError:
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
            f"Check logs: docker logs symphainy-consul"
        )
    
    if not pwf_result:
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
            f"Check logs: docker logs symphainy-consul"
        )
    
    di_container.public_works_foundation = pwf
    
    # 3. Initialize Curator Foundation
    curator = CuratorFoundationService(
        foundation_services=di_container,
        public_works_foundation=pwf
    )
    
    try:
        curator_result = await asyncio.wait_for(
            curator.initialize(),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        
        pytest.fail(
            f"Curator Foundation initialization timed out after 30 seconds.\n"
            f"Infrastructure status:\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
            f"restarts: {consul_status['restart_count']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
            f"restarts: {arango_status['restart_count']})\n\n"
            f"Check logs: docker logs symphainy-consul"
        )
    
    if not curator_result:
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        
        pytest.fail(
            f"Curator Foundation initialization failed.\n"
            f"Infrastructure status:\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
            f"restarts: {consul_status['restart_count']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
            f"restarts: {arango_status['restart_count']})\n\n"
            f"Check logs: docker logs symphainy-consul"
        )
    
    di_container.curator_foundation = curator
    
    # 4. Initialize Platform Gateway
    platform_gateway = PlatformInfrastructureGateway(
        public_works_foundation=pwf
    )
    
    # 5. Initialize Smart City Services
    service_manager = SmartCityServiceManager(di_container, curator)
    init_results = await service_manager.initialize_all_services(timeout=60.0)
    
    # Check if critical services initialized
    critical_services = ["librarian", "data_steward", "content_steward"]
    missing_critical = [svc for svc in critical_services if svc not in init_results["initialized"]]
    
    if missing_critical:
        diagnostics = service_manager.get_diagnostics()
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        error_details = []
        for svc in missing_critical:
            error_details.append(f"  {svc}: {init_results['errors'].get(svc, 'Unknown error')}")
        
        pytest.fail(
            f"Critical Smart City services failed to initialize:\n"
            f"{chr(10).join(error_details)}\n\n"
            f"{diagnostics}\n\n"
            f"Infrastructure status:\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
            f"restarts: {consul_status['restart_count']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
            f"restarts: {arango_status['restart_count']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
            f"restarts: {redis_status['restart_count']})\n\n"
            f"Fix: Ensure all Smart City services can initialize and register with Curator.\n"
            f"Check service logs for initialization errors."
        )
    
    # Return comprehensive infrastructure
    return {
        "di_container": di_container,
        "public_works_foundation": pwf,
        "curator": curator,
        "platform_gateway": platform_gateway,
        "smart_city_services": service_manager.services,
        "service_manager": service_manager,
        "initialization_results": init_results
    }

