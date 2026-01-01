#!/usr/bin/env python3
"""
Solution Manager Service - Clean Micro-Modular Rebuild

Clean micro-modular implementation using base/protocol architecture
with proper infrastructure abstractions for solution orchestration.

WHAT (Manager Role): I orchestrate solutions and coordinate journey flow (Solution → Journey)
HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
"""

import logging
from typing import Dict, Any, List, Optional

# Import base and protocol
from bases.manager_service_base import ManagerServiceBase, ManagerServiceType, OrchestrationScope, GovernanceLevel
from bases.protocols.manager_service_protocol import ManagerServiceProtocol

# Import micro-modules
from .modules.initialization import Initialization
from .modules.solution_design import SolutionDesign
from .modules.journey_orchestration import JourneyOrchestration
from .modules.capability_composition import CapabilityComposition
from .modules.platform_governance import PlatformGovernance
from .modules.soa_mcp import SoaMcp
from .modules.utilities import Utilities


class SolutionManagerService(ManagerServiceBase, ManagerServiceProtocol):
    """
    Solution Manager Service - Clean Micro-Modular Rebuild
    
    Clean micro-modular implementation using base/protocol architecture
    with proper infrastructure abstractions for solution orchestration.
    
    WHAT (Manager Role): I orchestrate solutions and coordinate journey flow (Solution → Journey)
    HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
    """
    
    def __init__(self, di_container: Any, platform_gateway: Any = None):
        """Initialize Solution Manager Service with proper infrastructure mapping."""
        # Get Platform Gateway from DI Container if not provided
        if platform_gateway is None:
            try:
                platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
            except:
                pass  # Will be set later if needed
        
        super().__init__(
            service_name="SolutionManagerService",
            realm_name="solution",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Manager-specific initialization
        self.manager_type = ManagerServiceType.SOLUTION_MANAGER
        self.orchestration_scope = OrchestrationScope.CROSS_DIMENSIONAL
        self.governance_level = GovernanceLevel.STRICT  # Changed from HIGH to STRICT
        
        # Infrastructure Abstractions (Public Works - swappable infrastructure for low-level ops)
        self.session_abstraction = None
        self.state_management_abstraction = None
        self.analytics_abstraction = None  # Optional
        
        # Smart City Services (discovered via Curator for business-level operations)
        self.security_guard = None  # Authentication/Authorization
        self.traffic_cop = None  # Session routing, state sync
        self.conductor = None  # Workflow orchestration
        self.post_office = None  # Structured messaging
        
        # Service State
        self.is_infrastructure_connected = False
        
        # SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Solution Manager specific state
        self.solution_initiators: Dict[str, Any] = {}
        self.platform_governance: Dict[str, Any] = {}
        
        # Capability flags
        self.platform_orchestration_enabled = False
        self.solution_discovery_enabled = False
        self.cross_solution_coordination_enabled = False
        self.platform_governance_enabled = False
        
        # Initialize micro-modules
        self.initialization_module = Initialization(self)
        self.solution_design_module = SolutionDesign(self)
        self.journey_orchestration_module = JourneyOrchestration(self)
        self.capability_composition_module = CapabilityComposition(self)
        self.platform_governance_module = PlatformGovernance(self)
        self.soa_mcp_module = SoaMcp(self)
        self.utilities_module = Utilities(self)
        
        # Initialize state tracking
        self.is_initialized = False
        
        # Logger is initialized in base class
        if hasattr(self, 'logger') and self.logger:
            self.logger.info("✅ Solution Manager Service (Clean Micro-Modular Rebuild) initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize Solution Manager Service with infrastructure and libraries.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "solution_manager_initialize_start",
            success=True
        )
        
        try:
            # Logger is initialized in RealmServiceBase parent class
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("🚀 Initializing Solution Manager Service...")
            
            # Initialize infrastructure connections
            await self.initialization_module.initialize_infrastructure_connections()
            
            # ✅ Bootstrap Solution foundation services (EAGER)
            # This ensures foundational services (like DataSolutionOrchestratorService) are available
            # before dependent services (like ContentOrchestrator) try to use them
            await self.initialization_module.bootstrap_solution_foundation_services()
            
            # Initialize Solution Manager capabilities
            await self.initialization_module.initialize_solution_manager_capabilities()
            
            # Discover Solution realm services via Curator
            # DataSolutionOrchestratorService will now be found (bootstrapped above)
            await self.initialization_module.discover_solution_realm_services()
            
            # Initialize SOA API exposure
            await self.soa_mcp_module.initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Initialize MCP Server (exposes solution manager methods as MCP tools)
            from .mcp_server.solution_manager_mcp_server import SolutionManagerMCPServer
            self.mcp_server = SolutionManagerMCPServer(
                solution_manager=self,
                di_container=self.di_container
            )
            # MCP server registers tools in __init__, ready to use
            if hasattr(self, 'logger') and self.logger:
                self.logger.info(f"✅ {self.service_name} MCP Server initialized")
            
            # Register with Curator (Phase 2 pattern)
            await self.soa_mcp_module.register_solution_manager_capabilities()
            
            self.is_initialized = True
            
            # Record health metric
            await self.record_health_metric(
                "solution_manager_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "solution_manager_initialize_complete",
                success=True
            )
            
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("✅ Solution Manager Service initialized successfully")
            
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "solution_manager_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "solution_manager_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            import traceback
            error_details = traceback.format_exc()
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"❌ Failed to initialize Solution Manager Service: {str(e)}")
                self.logger.error(f"Traceback: {error_details}")
            # Also print for immediate visibility
            print(f"❌ Solution Manager initialization failed: {str(e)}")
            print(f"Traceback: {error_details}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown Solution Manager Service gracefully."""
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("🛑 Shutting down Solution Manager Service...")
            
            # Clear state
            self.solution_initiators.clear()
            self.platform_governance.clear()
            self.soa_apis.clear()
            self.mcp_tools.clear()
            
            self.is_initialized = False
            
            if hasattr(self, 'logger') and self.logger:
                self.logger.info("✅ Solution Manager Service shutdown complete")
            
            return True
            
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"❌ Error during Solution Manager Service shutdown: {str(e)}")
            return False
    
    # ============================================================================
    # SOA API METHODS (Delegated to Modules)
    # ============================================================================
    
    async def design_solution(
        self,
        solution_request: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Design a solution based on requirements (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "design_solution_start",
            success=True,
            details={"solution_type": solution_request.get("solution_type", "unknown")}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "design_solution", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "design_solution",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("design_solution_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("design_solution_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "design_solution",
                    details={"tenant_id": tenant_id}
                )
                await self.record_health_metric("design_solution_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("design_solution_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            result = await self.solution_design_module.design_solution(solution_request, user_context=user_context)
            
            if result.get("success"):
                # Record health metric (success)
                await self.record_health_metric("design_solution_success", 1.0, {"solution_type": solution_request.get("solution_type")})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("design_solution_complete", success=True, details={"solution_type": solution_request.get("solution_type")})
            else:
                # End telemetry tracking with failure
                await self.log_operation_with_telemetry("design_solution_complete", success=False, details={"error": result.get("error")})
            
            return result
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "design_solution", details={"solution_request": solution_request})
            
            # Record health metric (failure)
            await self.record_health_metric("design_solution_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("design_solution_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def compose_capabilities(
        self,
        capability_request: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compose capabilities from multiple sources (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "compose_capabilities_start",
            success=True
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "compose_capabilities", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "compose_capabilities",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("compose_capabilities_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("compose_capabilities_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "compose_capabilities",
                    details={"tenant_id": tenant_id}
                )
                await self.record_health_metric("compose_capabilities_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("compose_capabilities_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            result = await self.capability_composition_module.compose_capabilities(capability_request, user_context=user_context)
            
            if result.get("success"):
                # Record health metric (success)
                await self.record_health_metric("compose_capabilities_success", 1.0, {})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("compose_capabilities_complete", success=True)
            else:
                # End telemetry tracking with failure
                await self.log_operation_with_telemetry("compose_capabilities_complete", success=False, details={"error": result.get("error")})
            
            return result
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "compose_capabilities", details={"capability_request": capability_request})
            
            # Record health metric (failure)
            await self.record_health_metric("compose_capabilities_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("compose_capabilities_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_poc(
        self,
        poc_request: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate proof of concept for a solution (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "generate_poc_start",
            success=True,
            details={"solution_type": poc_request.get("solution_type", "unknown")}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "generate_poc", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "generate_poc",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("generate_poc_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("generate_poc_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "generate_poc",
                    details={"tenant_id": tenant_id}
                )
                await self.record_health_metric("generate_poc_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("generate_poc_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            result = await self.solution_design_module.generate_poc(poc_request, user_context=user_context)
            
            if result.get("success"):
                # Record health metric (success)
                await self.record_health_metric("generate_poc_success", 1.0, {"solution_type": poc_request.get("solution_type")})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("generate_poc_complete", success=True, details={"solution_type": poc_request.get("solution_type")})
            else:
                # End telemetry tracking with failure
                await self.log_operation_with_telemetry("generate_poc_complete", success=False, details={"error": result.get("error")})
            
            return result
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "generate_poc", details={"poc_request": poc_request})
            
            # Record health metric (failure)
            await self.record_health_metric("generate_poc_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("generate_poc_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def orchestrate_journey(
        self,
        journey_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate journey via Journey Manager (SOA API - top-down flow).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "orchestrate_journey_start",
            success=True,
            details={"journey_id": journey_context.get("journey_id")}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "orchestrate_journey", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "orchestrate_journey",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("orchestrate_journey_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("orchestrate_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "orchestrate_journey",
                    details={"tenant_id": tenant_id}
                )
                await self.record_health_metric("orchestrate_journey_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("orchestrate_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            result = await self.journey_orchestration_module.orchestrate_journey(journey_context, user_context=user_context)
            
            if result.get("success"):
                # Record health metric (success)
                await self.record_health_metric("orchestrate_journey_success", 1.0, {"journey_id": journey_context.get("journey_id")})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("orchestrate_journey_complete", success=True, details={"journey_id": journey_context.get("journey_id")})
            else:
                # End telemetry tracking with failure
                await self.log_operation_with_telemetry("orchestrate_journey_complete", success=False, details={"error": result.get("error")})
            
            return result
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "orchestrate_journey", details={"journey_context": journey_context})
            
            # Record health metric (failure)
            await self.record_health_metric("orchestrate_journey_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("orchestrate_journey_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def discover_solutions(
        self,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Discover available solutions on the platform (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "discover_solutions_start",
            success=True
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "discover_solutions", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "discover_solutions",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("discover_solutions_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("discover_solutions_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "discover_solutions",
                    details={"tenant_id": tenant_id}
                )
                await self.record_health_metric("discover_solutions_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("discover_solutions_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            result = await self.solution_design_module.discover_solutions(user_context=user_context)
            
            if result.get("success"):
                # Record health metric (success)
                await self.record_health_metric("discover_solutions_success", 1.0, {"solution_count": len(result.get("solutions", []))})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("discover_solutions_complete", success=True, details={"solution_count": len(result.get("solutions", []))})
            else:
                # End telemetry tracking with failure
                await self.log_operation_with_telemetry("discover_solutions_complete", success=False, details={"error": result.get("error")})
            
            return result
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "discover_solutions")
            
            # Record health metric (failure)
            await self.record_health_metric("discover_solutions_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("discover_solutions_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_platform_health(
        self,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get overall platform health (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_platform_health_start",
            success=True
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "get_platform_health", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_platform_health",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_platform_health_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_platform_health_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "get_platform_health",
                    details={"tenant_id": tenant_id}
                )
                await self.record_health_metric("get_platform_health_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("get_platform_health_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            result = await self.platform_governance_module.get_platform_health(user_context=user_context)
            
            if result.get("success"):
                # Record health metric (success)
                await self.record_health_metric("get_platform_health_success", 1.0, {})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_platform_health_complete", success=True)
            else:
                # End telemetry tracking with failure
                await self.log_operation_with_telemetry("get_platform_health_complete", success=False, details={"error": result.get("error")})
            
            return result
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_platform_health")
            
            # Record health metric (failure)
            await self.record_health_metric("get_platform_health_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_platform_health_complete", success=False, details={"error": str(e)})
            
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
            "capabilities_enabled": {
                "platform_orchestration": self.platform_orchestration_enabled,
                "solution_discovery": self.solution_discovery_enabled,
                "cross_solution_coordination": self.cross_solution_coordination_enabled,
                "platform_governance": self.platform_governance_enabled
            },
            "infrastructure": self.utilities_module.validate_infrastructure_mapping()
        }


