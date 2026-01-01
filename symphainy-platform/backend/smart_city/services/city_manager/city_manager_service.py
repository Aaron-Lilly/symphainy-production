#!/usr/bin/env python3
"""
City Manager Service - Clean Micro-Modular Rebuild

Clean micro-modular implementation using base/protocol architecture
with proper infrastructure abstractions for bootstrapping and orchestration.

WHAT (Smart City Role): I bootstrap the platform by initializing manager hierarchy and orchestrating Smart City services
HOW (Service Implementation): I use SmartCityRoleBase with direct Public Works foundation access + direct library injection
"""

import asyncio
from typing import Dict, Any, List, Optional

# Import base and protocol
from bases.smart_city_role_base import SmartCityRoleBase
from backend.smart_city.protocols.city_manager_service_protocol import CityManagerServiceProtocol

# Import micro-modules
from .modules.initialization import Initialization
from .modules.bootstrapping import Bootstrapping
from .modules.realm_orchestration import RealmOrchestration
from .modules.service_management import ServiceManagement
from .modules.platform_governance import PlatformGovernance
from .modules.soa_mcp import SoaMcp
from .modules.utilities import Utilities


class CityManagerService(SmartCityRoleBase, CityManagerServiceProtocol):
    """
    City Manager Service - Clean Micro-Modular Rebuild
    
    Clean micro-modular implementation using base/protocol architecture
    with proper infrastructure abstractions for bootstrapping and orchestration.
    
    WHAT (Smart City Role): I bootstrap the platform by initializing manager hierarchy and orchestrating Smart City services
    HOW (Service Implementation): I use SmartCityRoleBase with direct Public Works foundation access + direct library injection
    """
    
    def __init__(self, di_container: Any):
        """Initialize City Manager Service with proper infrastructure mapping."""
        super().__init__(
            service_name="CityManagerService",
            role_name="city_manager",
            di_container=di_container
        )
        
        # City Manager specific state (not manager-specific properties)
        self.orchestration_scope = "platform_wide"  # Platform-wide orchestration
        self.governance_level = "high"  # High governance level
        
        # Infrastructure Abstractions (Public Works - swappable infrastructure)
        self.session_abstraction = None
        self.state_management_abstraction = None
        self.messaging_abstraction = None
        self.event_management_abstraction = None
        self.file_management_abstraction = None
        self.analytics_abstraction = None  # Optional
        self.health_abstraction = None
        self.telemetry_abstraction = None
        
        # Direct Library Injection (business logic)
        self.asyncio = asyncio  # asyncio for async coordination
        self.httpx = None  # httpx for health checks
        
        # Service State
        self.is_infrastructure_connected = False
        
        # Week 3 Enhancement: SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # City Manager specific state
        self.smart_city_services: Dict[str, Any] = {}
        self.manager_hierarchy: Dict[str, Any] = {}
        
        # Bootstrapping state
        self.bootstrapping_complete = False
        self.realm_startup_complete = False
        
        # Initialize micro-modules
        self.initialization_module = Initialization(self)
        self.bootstrapping_module = Bootstrapping(self)
        self.realm_orchestration_module = RealmOrchestration(self)
        self.service_management_module = ServiceManagement(self)
        self.platform_governance_module = PlatformGovernance(self)
        self.soa_mcp_module = SoaMcp(self)
        self.utilities_module = Utilities(self)
        
        # FIX 4: Data Path Bootstrap Module
        from .modules.data_path_bootstrap import DataPathBootstrap
        self.data_path_bootstrap_module = DataPathBootstrap(self)
        
        # Logger is initialized in base class
        if hasattr(self, 'logger') and self.logger:
            self.logger.info("✅ City Manager Service (Clean Micro-Modular Rebuild) initialized")
    
    async def initialize(self) -> bool:
        """Initialize City Manager Service with infrastructure and libraries."""
        try:
            if self.logger:
                self.logger.info("🚀 Initializing City Manager Service...")
            
            # Initialize infrastructure connections (Public Works)
            await self.initialization_module.initialize_infrastructure_connections()
            
            # Initialize direct library injection
            await self.initialization_module.initialize_direct_libraries()
            
            # Initialize City Manager capabilities
            await self.initialization_module.initialize_city_manager_capabilities()
            
            # Initialize SOA API exposure
            await self.soa_mcp_module.initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Register capabilities with Curator (Phase 2 pattern - simplified for Smart City)
            # City Manager registers itself via soa_mcp module's register_capabilities()
            # This ensures proper capability registration with contracts
            try:
                await self.soa_mcp_module.register_capabilities()
                if self.logger:
                    self.logger.info("✅ City Manager registered with Curator (Phase 2 pattern)")
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Failed to register City Manager with Curator: {e}")
            
            if self.logger:
                self.logger.info("✅ City Manager Service initialized successfully")
            self.is_initialized = True
            self.service_health = "healthy"
            return True
            
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            if self.logger:
                self.logger.error(f"❌ Failed to initialize City Manager Service: {str(e)}")
                self.logger.error(f"Traceback: {error_traceback}")
            # Also print to stdout for test visibility
            print(f"❌ City Manager initialization error: {str(e)}")
            print(f"Traceback:\n{error_traceback}")
            self.service_health = "unhealthy"
            return False
    
    # ============================================================================
    # BOOTSTRAPPING METHODS
    # ============================================================================
    
    async def bootstrap_manager_hierarchy(self, request: Optional[Any] = None) -> Any:
        """
        Bootstrap manager hierarchy starting from Solution Manager.
        
        Args:
            request: Optional BootstrapRequest or Dict with solution_context
        """
        # Handle both protocol request object and legacy dict format
        if request is None:
            solution_context = None
        elif hasattr(request, 'solution_context'):
            solution_context = request.solution_context
        else:
            solution_context = request
        
        result = await self.bootstrapping_module.bootstrap_manager_hierarchy(solution_context)
        
        # Convert to BootstrapResponse format if needed
        from backend.smart_city.protocols.city_manager_service_protocol import (
            BootstrapResponse, ManagerHierarchyStatus
        )
        return BootstrapResponse(
            success=result.get("success", False),
            hierarchy_status=ManagerHierarchyStatus.OPERATIONAL if result.get("success") else ManagerHierarchyStatus.FAILED,
            bootstrapped_managers=list(result.get("managers", {}).keys()),
            message=result.get("message"),
            timestamp=result.get("completed_at"),
            error=result.get("error")
        )
    
    async def get_manager_hierarchy_status(self) -> Dict[str, Any]:
        """Get manager hierarchy status and health."""
        return {
            "bootstrapped": self.bootstrapping_complete,
            "managers": self.manager_hierarchy,
            "status": "operational" if self.bootstrapping_complete else "not_bootstrapped"
        }
    
    # ============================================================================
    # REALM ORCHESTRATION METHODS
    # ============================================================================
    
    async def orchestrate_realm_startup(self, request: Optional[Any] = None) -> Any:
        """
        Orchestrate Smart City realm startup.
        
        Args:
            request: Optional RealmStartupRequest or List[str] of services
        """
        # Handle both protocol request object and legacy list format
        if request is None:
            services = None
        elif hasattr(request, 'services'):
            services = request.services
        else:
            services = request
        
        result = await self.realm_orchestration_module.orchestrate_realm_startup(services)
        
        # Convert to RealmStartupResponse format if needed
        from backend.smart_city.protocols.city_manager_service_protocol import RealmStartupResponse
        
        # Convert services dict to started/failed lists
        started_services = []
        failed_services = []
        if "services" in result:
            for service_name, service_result in result["services"].items():
                if service_result.get("success"):
                    started_services.append(service_name)
                else:
                    failed_services.append(service_name)
        
        return RealmStartupResponse(
            success=result.get("success", False),
            started_services=started_services,
            failed_services=failed_services,
            message=result.get("message"),
            timestamp=result.get("timestamp") or result.get("started_at"),
            error=result.get("error")
        )
    
    async def get_realm_status(self) -> Dict[str, Any]:
        """Get Smart City realm status."""
        return {
            "realm_startup_complete": self.realm_startup_complete,
            "smart_city_services": self.smart_city_services,
            "status": "operational" if self.realm_startup_complete else "initializing"
        }
    
    # ============================================================================
    # SERVICE MANAGEMENT METHODS
    # ============================================================================
    
    async def manage_smart_city_service(self, request: Any) -> Any:
        """
        Manage a Smart City service (start, stop, health check, restart).
        
        Args:
            request: ServiceManagementRequest or (service_name: str, action: str) tuple
        """
        # Handle both protocol request object and legacy tuple format
        if isinstance(request, tuple) or (isinstance(request, dict) and "service_name" in request and "action" in request):
            # Legacy format: (service_name, action) or {"service_name": ..., "action": ...}
            if isinstance(request, tuple):
                service_name, action = request
            else:
                service_name = request["service_name"]
                action = request["action"]
        else:
            # Protocol format: ServiceManagementRequest
            service_name = request.service_name
            action = request.action
        
        result = await self.service_management_module.manage_smart_city_service(service_name, action)
        
        # Convert to ServiceManagementResponse format if needed
        from backend.smart_city.protocols.city_manager_service_protocol import ServiceManagementResponse
        return ServiceManagementResponse(
            success=result.get("success", False),
            service_name=service_name,
            action=action,
            status=result.get("status"),
            message=result.get("message"),
            timestamp=result.get("timestamp"),
            error=result.get("error")
        )
    
    async def get_smart_city_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get Smart City service status."""
        if service_name in self.smart_city_services:
            return self.smart_city_services[service_name]
        return {"error": f"Service {service_name} not found"}
    
    # ============================================================================
    # PLATFORM GOVERNANCE METHODS
    # ============================================================================
    
    async def get_platform_governance(self, request: Optional[Any] = None) -> Any:
        """
        Get platform governance status and metrics.
        
        Args:
            request: Optional PlatformGovernanceRequest
        """
        result = await self.platform_governance_module.get_platform_governance()
        
        # Convert to PlatformGovernanceResponse format if needed
        from backend.smart_city.protocols.city_manager_service_protocol import (
            PlatformGovernanceResponse, PlatformStatus
        )
        return PlatformGovernanceResponse(
            success=True,
            governance_data=result,
            platform_status=PlatformStatus.OPERATIONAL if self.is_initialized else PlatformStatus.INITIALIZING,
            timestamp=result.get("timestamp")
        )
    
    async def get_platform_status(self) -> Dict[str, Any]:
        """Get overall platform status."""
        return {
            "platform_status": "operational" if self.is_initialized else "initializing",
            "bootstrapping_complete": self.bootstrapping_complete,
            "realm_startup_complete": self.realm_startup_complete,
            "smart_city_services": len(self.smart_city_services),
            "manager_hierarchy": len(self.manager_hierarchy)
        }
    
    async def coordinate_with_manager(self, request: Any) -> Any:
        """
        Coordinate with another manager for cross-dimensional orchestration.
        
        Args:
            request: ManagerCoordinationRequest or (manager_name: str, coordination_request: Dict) tuple
        """
        # Handle both protocol request object and legacy tuple format
        if isinstance(request, tuple) or (isinstance(request, dict) and "manager_name" in request):
            # Legacy format: (manager_name, coordination_request) or {"manager_name": ..., ...}
            if isinstance(request, tuple):
                manager_name, coordination_request = request
            else:
                manager_name = request["manager_name"]
                coordination_request = request
        else:
            # Protocol format: ManagerCoordinationRequest
            manager_name = request.manager_name
            coordination_request = request.coordination_data or {}
        
        result = await self.platform_governance_module.coordinate_with_manager(manager_name, coordination_request)
        
        # Convert to ManagerCoordinationResponse format if needed
        from backend.smart_city.protocols.city_manager_service_protocol import ManagerCoordinationResponse
        return ManagerCoordinationResponse(
            success=result.get("success", False),
            manager_name=manager_name,
            coordination_result=result,
            message=result.get("message"),
            timestamp=result.get("timestamp"),
            error=result.get("error")
        )
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate that City Manager is using correct infrastructure abstractions."""
        return await self.utilities_module.validate_infrastructure_mapping()
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get City Manager service capabilities."""
        return await self.utilities_module.get_service_capabilities()
