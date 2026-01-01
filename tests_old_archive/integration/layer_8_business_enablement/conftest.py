#!/usr/bin/env python3
"""
Layer 8 Business Enablement - Test Configuration and Fixtures

Provides shared fixtures for Layer 8 tests, including:
- smart_city_infrastructure: Comprehensive Smart City infrastructure fixture
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from tests.utils.safe_docker import check_container_status, check_container_health

# Add symphainy-platform to path for imports (set early for module-level imports)
project_root = Path(__file__).parent.parent.parent.parent.parent
symphainy_platform = project_root / "symphainy-platform"
if str(symphainy_platform) not in sys.path:
    sys.path.insert(0, str(symphainy_platform))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


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
        # Ensure path is set before importing services (services have module-level imports)
        # Use absolute path to avoid path resolution issues
        project_root = Path("/home/founders/demoversion/symphainy_source")
        symphainy_platform = project_root / "symphainy-platform"
        if str(symphainy_platform) not in sys.path:
            sys.path.insert(0, str(symphainy_platform))
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        results = {
            "initialized": [],
            "failed": [],
            "errors": {}
        }
        
        for service_name in self.STARTUP_ORDER:
            try:
                # Import service class using importlib for better path handling
                import importlib
                module_path, class_name = self.SERVICE_CLASSES[service_name]
                module = importlib.import_module(module_path)
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
@pytest.mark.timeout_180  # 3 minutes for full infrastructure initialization
async def smart_city_infrastructure():
    """
    Comprehensive Smart City infrastructure fixture for enabling service tests.
    
    Initializes:
    - Public Works Foundation
    - Curator Foundation
    - Platform Gateway
    - All required Smart City services (Librarian, Data Steward, Content Steward, etc.)
    
    CRITICAL: This fixture has a 180-second timeout to prevent SSH session crashes.
    If infrastructure is unavailable, tests will fail fast rather than hanging.
    
    Returns:
        Dictionary with:
        - di_container: DIContainerService
        - public_works_foundation: PublicWorksFoundationService
        - curator: CuratorFoundationService
        - platform_gateway: PlatformInfrastructureGateway
        - smart_city_services: Dict of initialized Smart City services
        - service_manager: SmartCityServiceManager instance
    """
    # CRITICAL: Early health check - fail fast if critical infrastructure is unavailable
    # This prevents hanging during adapter initialization
    # WRAP in asyncio.to_thread() to prevent blocking the event loop
    # Docker subprocess calls can hang if Docker is slow/unresponsive
    try:
        arango_healthy = await asyncio.wait_for(
            asyncio.to_thread(check_container_health, "symphainy-arangodb"),
            timeout=10.0  # 10 second timeout for Docker health check
        )
        consul_healthy = await asyncio.wait_for(
            asyncio.to_thread(check_container_health, "symphainy-consul"),
            timeout=10.0  # 10 second timeout for Docker health check
        )
        redis_healthy = await asyncio.wait_for(
            asyncio.to_thread(check_container_health, "symphainy-redis"),
            timeout=10.0  # 10 second timeout for Docker health check
        )
    except asyncio.TimeoutError:
        pytest.fail(
            "Docker health checks timed out after 10 seconds. "
            "Docker may be unresponsive or containers may be starting. "
            "Check: docker ps"
        )
    
    if not arango_healthy:
        pytest.skip("ArangoDB is not available - skipping test (prevents hanging)")
    if not consul_healthy:
        pytest.skip("Consul is not available - skipping test (prevents hanging)")
    if not redis_healthy:
        pytest.skip("Redis is not available - skipping test (prevents hanging)")
    
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
        # CRITICAL: Wrap blocking Docker status checks in asyncio.to_thread() to prevent SSH crashes
        try:
            consul_status, arango_status, redis_status = await asyncio.gather(
                asyncio.wait_for(asyncio.to_thread(check_container_status, "symphainy-consul"), timeout=5.0),
                asyncio.wait_for(asyncio.to_thread(check_container_status, "symphainy-arangodb"), timeout=5.0),
                asyncio.wait_for(asyncio.to_thread(check_container_status, "symphainy-redis"), timeout=5.0)
            )
        except asyncio.TimeoutError:
            # If status checks timeout, use fallback message
            consul_status = {"status": "unknown", "health": "unknown", "restart_count": 0}
            arango_status = {"status": "unknown", "health": "unknown", "restart_count": 0}
            redis_status = {"status": "unknown", "health": "unknown", "restart_count": 0}
        
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
        # CRITICAL: Wrap blocking Docker status checks in asyncio.to_thread() to prevent SSH crashes
        try:
            consul_status, arango_status, redis_status = await asyncio.gather(
                asyncio.wait_for(asyncio.to_thread(check_container_status, "symphainy-consul"), timeout=5.0),
                asyncio.wait_for(asyncio.to_thread(check_container_status, "symphainy-arangodb"), timeout=5.0),
                asyncio.wait_for(asyncio.to_thread(check_container_status, "symphainy-redis"), timeout=5.0)
            )
        except asyncio.TimeoutError:
            # If status checks timeout, use fallback message
            consul_status = {"status": "unknown", "health": "unknown", "restart_count": 0}
            arango_status = {"status": "unknown", "health": "unknown", "restart_count": 0}
            redis_status = {"status": "unknown", "health": "unknown", "restart_count": 0}
        
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
        # CRITICAL: Wrap blocking Docker status checks in asyncio.to_thread() to prevent SSH crashes
        try:
            consul_status, arango_status = await asyncio.gather(
                asyncio.wait_for(asyncio.to_thread(check_container_status, "symphainy-consul"), timeout=5.0),
                asyncio.wait_for(asyncio.to_thread(check_container_status, "symphainy-arangodb"), timeout=5.0)
            )
        except asyncio.TimeoutError:
            # If status checks timeout, use fallback message
            consul_status = {"status": "unknown", "health": "unknown", "restart_count": 0}
            arango_status = {"status": "unknown", "health": "unknown", "restart_count": 0}
        
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
        # CRITICAL: Wrap blocking Docker status checks in asyncio.to_thread() to prevent SSH crashes
        try:
            consul_status, arango_status = await asyncio.gather(
                asyncio.wait_for(asyncio.to_thread(check_container_status, "symphainy-consul"), timeout=5.0),
                asyncio.wait_for(asyncio.to_thread(check_container_status, "symphainy-arangodb"), timeout=5.0)
            )
        except asyncio.TimeoutError:
            # If status checks timeout, use fallback message
            consul_status = {"status": "unknown", "health": "unknown", "restart_count": 0}
            arango_status = {"status": "unknown", "health": "unknown", "restart_count": 0}
        
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
    # Ensure path is set before service manager tries to import services
    # (services have module-level imports that need the path)
    # Use absolute path to avoid path resolution issues
    project_root_fixture = Path("/home/founders/demoversion/symphainy_source")
    symphainy_platform_fixture = project_root_fixture / "symphainy-platform"
    if str(symphainy_platform_fixture) not in sys.path:
        sys.path.insert(0, str(symphainy_platform_fixture))
    if str(project_root_fixture) not in sys.path:
        sys.path.insert(0, str(project_root_fixture))
    
    service_manager = SmartCityServiceManager(di_container, curator)
    init_results = await service_manager.initialize_all_services(timeout=60.0)
    
    # Check if critical services initialized
    critical_services = ["librarian", "data_steward", "content_steward"]
    missing_critical = [svc for svc in critical_services if svc not in init_results["initialized"]]
    
    if missing_critical:
        diagnostics = service_manager.get_diagnostics()
        # CRITICAL: Wrap blocking Docker status checks in asyncio.to_thread() to prevent SSH crashes
        try:
            consul_status, arango_status, redis_status = await asyncio.gather(
                asyncio.wait_for(asyncio.to_thread(check_container_status, "symphainy-consul"), timeout=5.0),
                asyncio.wait_for(asyncio.to_thread(check_container_status, "symphainy-arangodb"), timeout=5.0),
                asyncio.wait_for(asyncio.to_thread(check_container_status, "symphainy-redis"), timeout=5.0)
            )
        except asyncio.TimeoutError:
            # If status checks timeout, use fallback message
            consul_status = {"status": "unknown", "health": "unknown", "restart_count": 0}
            arango_status = {"status": "unknown", "health": "unknown", "restart_count": 0}
            redis_status = {"status": "unknown", "health": "unknown", "restart_count": 0}
        
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


# ============================================================================
# UNIFIED INFRASTRUCTURE FIXTURES (Phase 2)
# ============================================================================

@pytest.fixture(scope="function")
async def infrastructure_storage(smart_city_infrastructure):
    """
    Unified storage infrastructure fixture.
    
    Provides access to:
    - GCS file storage (via Content Steward or FileManagementAbstraction)
    - Supabase metadata storage
    
    CRITICAL: This fixture NEVER touches GOOGLE_APPLICATION_CREDENTIALS.
    Uses existing Public Works Foundation initialization (which already protects SSH credentials).
    
    Returns:
        Dictionary with:
        - file_storage: Content Steward (preferred) or FileManagementAbstraction
        - metadata_storage: Supabase adapter
        - type: Type of file storage ("content_steward" or "file_management_abstraction")
    """
    infra = smart_city_infrastructure
    pwf = infra["public_works_foundation"]
    
    # Tier 1: Use Smart City services (recommended - uses SOA APIs)
    content_steward = infra["smart_city_services"].get("content_steward")
    if content_steward:
        return {
            "file_storage": content_steward,
            "metadata_storage": pwf.supabase_adapter,
            "type": "content_steward"
        }
    
    # Tier 2: Use FileManagementAbstraction (fallback)
    file_abstraction = pwf.get_file_management_abstraction()
    if file_abstraction:
        return {
            "file_storage": file_abstraction,
            "metadata_storage": pwf.supabase_adapter,
            "type": "file_management_abstraction"
        }
    
    pytest.fail(
        "Storage infrastructure not available. "
        "Ensure Content Steward or FileManagementAbstraction is initialized."
    )


@pytest.fixture(scope="function")
async def infrastructure_database(smart_city_infrastructure):
    """
    Unified database infrastructure fixture.
    
    Provides access to:
    - ArangoDB (metadata, graph data)
    - Redis (cache, sessions, state, messaging)
    
    CRITICAL: This fixture NEVER touches GOOGLE_APPLICATION_CREDENTIALS.
    Uses existing Public Works Foundation initialization.
    
    Returns:
        Dictionary with:
        - arangodb: ArangoDB adapter
        - redis: Redis adapter
    """
    infra = smart_city_infrastructure
    pwf = infra["public_works_foundation"]
    
    return {
        "arangodb": pwf.arango_adapter,
        "redis": pwf.redis_adapter,
    }


@pytest.fixture(scope="function")
async def infrastructure_ai(smart_city_infrastructure):
    """
    Unified AI infrastructure fixture.
    
    Provides access to:
    - LLM abstraction (OpenAI, Anthropic)
    - Document Intelligence abstraction
    
    CRITICAL: This fixture NEVER touches GOOGLE_APPLICATION_CREDENTIALS.
    Uses existing Public Works Foundation initialization.
    
    Returns:
        Dictionary with:
        - llm: LLM abstraction
        - document_intelligence: Document Intelligence abstraction
    """
    infra = smart_city_infrastructure
    pwf = infra["public_works_foundation"]
    
    return {
        "llm": pwf.get_llm_abstraction() if hasattr(pwf, 'get_llm_abstraction') else None,
        "document_intelligence": pwf.get_document_intelligence_abstraction() if hasattr(pwf, 'get_document_intelligence_abstraction') else None,
    }

