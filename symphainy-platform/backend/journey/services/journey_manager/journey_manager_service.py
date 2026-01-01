#!/usr/bin/env python3
"""
Journey Manager Service - Clean Micro-Modular Rebuild

Clean micro-modular implementation using base/protocol architecture
with proper infrastructure abstractions for journey orchestration.

WHAT (Manager Role): I orchestrate journeys and coordinate experience flow (Journey → Experience)
HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
"""

import logging
from typing import Dict, Any, Optional

# Import base and protocol
from bases.manager_service_base import ManagerServiceBase, ManagerServiceType, OrchestrationScope, GovernanceLevel
from bases.protocols.manager_service_protocol import ManagerServiceProtocol

# Import micro-modules
from .modules.initialization import Initialization
from .modules.journey_design import JourneyDesign
from .modules.experience_orchestration import ExperienceOrchestration
from .modules.roadmap_management import RoadmapManagement
from .modules.soa_mcp import SoaMcp
from .modules.utilities import Utilities


class JourneyManagerService(ManagerServiceBase, ManagerServiceProtocol):
    """
    Journey Manager Service - Clean Micro-Modular Rebuild
    
    Clean micro-modular implementation using base/protocol architecture
    with proper infrastructure abstractions for journey orchestration.
    
    WHAT (Manager Role): I orchestrate journeys and coordinate experience flow (Journey → Experience)
    HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
    """
    
    def __init__(self, di_container: Any, platform_gateway: Any = None):
        """Initialize Journey Manager Service with proper infrastructure mapping."""
        # Get Platform Gateway from DI Container if not provided
        if platform_gateway is None:
            try:
                platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
            except:
                pass  # Will be set later if needed
        
        super().__init__(
            service_name="JourneyManagerService",
            realm_name="journey",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Manager-specific initialization
        self.manager_type = ManagerServiceType.JOURNEY_MANAGER
        self.orchestration_scope = OrchestrationScope.CROSS_DIMENSIONAL
        self.governance_level = GovernanceLevel.MODERATE
        
        # Infrastructure Abstractions (Public Works - swappable infrastructure for low-level ops)
        self.session_abstraction = None
        self.state_management_abstraction = None
        
        # Smart City Services (discovered via Curator for business-level operations)
        self.traffic_cop = None  # Session routing, state sync
        self.conductor = None  # Workflow orchestration
        self.post_office = None  # Structured messaging
        
        # Service State
        self.is_infrastructure_connected = False
        
        # SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Journey Manager specific state
        self.journey_services: Dict[str, Any] = {}
        self.journey_templates: Dict[str, Any] = {}
        self.active_journeys: Dict[str, Any] = {}
        
        # Initialize micro-modules
        self.initialization_module = Initialization(self)
        self.journey_design_module = JourneyDesign(self)
        self.experience_orchestration_module = ExperienceOrchestration(self)
        self.roadmap_management_module = RoadmapManagement(self)
        self.soa_mcp_module = SoaMcp(self)
        self.utilities_module = Utilities(self)
        
        # Initialize state tracking
        self.is_initialized = False
        
        # Logger is initialized in base class
        if hasattr(self, 'logger') and self.logger:
            self.logger.info("✅ Journey Manager Service (Clean Micro-Modular Rebuild) initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize Journey Manager Service with infrastructure and libraries.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "journey_manager_initialize_start",
            success=True
        )
        
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("🚀 Initializing Journey Manager Service...")
            
            # Initialize infrastructure connections
            await self.initialization_module.initialize_infrastructure_connections()
            
            # Initialize Journey Manager capabilities
            await self.initialization_module.initialize_journey_manager_capabilities()
            
            # Discover Journey realm services via Curator
            await self.initialization_module.discover_journey_realm_services()
            
            # Initialize SOA API exposure
            await self.soa_mcp_module.initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Initialize MCP Server (exposes journey manager methods as MCP tools)
            from .mcp_server.journey_manager_mcp_server import JourneyManagerMCPServer
            self.mcp_server = JourneyManagerMCPServer(
                journey_manager=self,
                di_container=self.di_container
            )
            # MCP server registers tools in __init__, ready to use
            if hasattr(self, 'logger') and self.logger:
                self.logger.info(f"✅ {self.service_name} MCP Server initialized")
            
            # Register with Curator (Phase 2 pattern)
            await self.soa_mcp_module.register_journey_manager_capabilities()
            
            self.is_initialized = True
            
            # Record health metric
            await self.record_health_metric(
                "journey_manager_initialized",
                1.0,
                {"service": self.service_name, "active_journeys": len(self.active_journeys)}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "journey_manager_initialize_complete",
                success=True
            )
            
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("✅ Journey Manager Service initialized successfully")
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "journey_manager_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "journey_manager_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            import traceback
            error_details = traceback.format_exc()
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"❌ Failed to initialize Journey Manager Service: {str(e)}")
                self.logger.error(f"Traceback: {error_details}")
            # Also print for immediate visibility
            print(f"❌ Journey Manager initialization failed: {str(e)}")
            print(f"Traceback: {error_details}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown Journey Manager Service gracefully."""
        try:
            if self.logger:
                self.logger.info("🛑 Shutting down Journey Manager Service...")
            
            # Clear state
            self.journey_services.clear()
            self.journey_templates.clear()
            self.active_journeys.clear()
            self.soa_apis.clear()
            self.mcp_tools.clear()
            
            self.is_initialized = False
            
            if self.logger:
                self.logger.info("✅ Journey Manager Service shutdown complete")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error during Journey Manager Service shutdown: {str(e)}")
            return False
    
    # ============================================================================
    # SOA API METHODS (Delegated to Modules)
    # ============================================================================
    
    async def design_journey(
        self,
        journey_request: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Design a journey based on requirements (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "design_journey_start",
            success=True,
            details={"journey_type": journey_request.get("journey_type", "unknown")}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "design_journey", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "design_journey",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("design_journey_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("design_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "design_journey",
                    details={"tenant_id": tenant_id}
                )
                await self.record_health_metric("design_journey_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("design_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            result = await self.journey_design_module.design_journey(journey_request, user_context=user_context)
            
            if result.get("success"):
                # Record health metric (success)
                await self.record_health_metric("design_journey_success", 1.0, {"journey_id": result.get("journey_design", {}).get("journey_id")})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("design_journey_complete", success=True, details={"journey_id": result.get("journey_design", {}).get("journey_id")})
            else:
                # End telemetry tracking with failure
                await self.log_operation_with_telemetry("design_journey_complete", success=False, details={"error": result.get("error")})
            
            return result
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "design_journey", details={"journey_request": journey_request})
            
            # Record health metric (failure)
            await self.record_health_metric("design_journey_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("design_journey_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_roadmap(
        self,
        roadmap_request: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a roadmap for a journey (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "create_roadmap_start",
            success=True,
            details={"journey_id": roadmap_request.get("journey_id")}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "create_roadmap", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "create_roadmap",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("create_roadmap_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("create_roadmap_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "create_roadmap",
                    details={"tenant_id": tenant_id}
                )
                await self.record_health_metric("create_roadmap_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("create_roadmap_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            result = await self.roadmap_management_module.create_roadmap(roadmap_request, user_context=user_context)
            
            if result.get("success"):
                # Record health metric (success)
                await self.record_health_metric("create_roadmap_success", 1.0, {"journey_id": roadmap_request.get("journey_id")})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("create_roadmap_complete", success=True, details={"journey_id": roadmap_request.get("journey_id")})
            else:
                # End telemetry tracking with failure
                await self.log_operation_with_telemetry("create_roadmap_complete", success=False, details={"error": result.get("error")})
            
            return result
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "create_roadmap", details={"roadmap_request": roadmap_request})
            
            # Record health metric (failure)
            await self.record_health_metric("create_roadmap_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("create_roadmap_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def track_milestones(
        self,
        tracking_request: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track milestones for a journey (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "track_milestones_start",
            success=True,
            details={"journey_id": tracking_request.get("journey_id")}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "track_milestones", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "track_milestones",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("track_milestones_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("track_milestones_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "track_milestones",
                    details={"tenant_id": tenant_id}
                )
                await self.record_health_metric("track_milestones_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("track_milestones_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            result = await self.roadmap_management_module.track_milestones(tracking_request, user_context=user_context)
            
            if result.get("success"):
                # Record health metric (success)
                await self.record_health_metric("track_milestones_success", 1.0, {"journey_id": tracking_request.get("journey_id")})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("track_milestones_complete", success=True, details={"journey_id": tracking_request.get("journey_id")})
            else:
                # End telemetry tracking with failure
                await self.log_operation_with_telemetry("track_milestones_complete", success=False, details={"error": result.get("error")})
            
            return result
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "track_milestones", details={"tracking_request": tracking_request})
            
            # Record health metric (failure)
            await self.record_health_metric("track_milestones_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("track_milestones_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def orchestrate_experience(
        self,
        experience_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate experience via Experience Manager (SOA API - top-down flow).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "orchestrate_experience_start",
            success=True,
            details={"journey_id": experience_context.get("journey_id")}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "orchestrate_experience", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "orchestrate_experience",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("orchestrate_experience_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("orchestrate_experience_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "orchestrate_experience",
                    details={"tenant_id": tenant_id}
                )
                await self.record_health_metric("orchestrate_experience_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("orchestrate_experience_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            result = await self.experience_orchestration_module.orchestrate_experience(experience_context, user_context=user_context)
            
            if result.get("success"):
                # Record health metric (success)
                await self.record_health_metric("orchestrate_experience_success", 1.0, {"journey_id": experience_context.get("journey_id")})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("orchestrate_experience_complete", success=True, details={"journey_id": experience_context.get("journey_id")})
            else:
                # End telemetry tracking with failure
                await self.log_operation_with_telemetry("orchestrate_experience_complete", success=False, details={"error": result.get("error")})
            
            return result
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "orchestrate_experience", details={"experience_context": experience_context})
            
            # Record health metric (failure)
            await self.record_health_metric("orchestrate_experience_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("orchestrate_experience_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================================================
    # PROTOCOL COMPLIANCE METHODS
    # ============================================================================
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (ManagerServiceProtocol)."""
        return self.utilities_module.get_service_capabilities()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check (ManagerServiceProtocol)."""
        return {
            "service_name": self.service_name,
            "status": "healthy" if self.is_initialized else "unhealthy",
            "is_infrastructure_connected": self.is_infrastructure_connected,
            "active_journeys": len(self.active_journeys),
            "infrastructure": self.utilities_module.validate_infrastructure_mapping()
        }


