#!/usr/bin/env python3
"""
Delivery Manager Service - Clean Micro-Modular Rebuild

Clean micro-modular implementation using base/protocol architecture
with proper infrastructure abstractions for business enablement orchestration.

WHAT (Manager Role): I orchestrate business enablement and coordinate all 5 pillars (Delivery → Business Enablement)
HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
"""

from typing import Dict, Any, Optional

# Import base and protocol
from bases.manager_service_base import ManagerServiceBase, ManagerServiceType, OrchestrationScope, GovernanceLevel
from bases.protocols.manager_service_protocol import ManagerServiceProtocol

# Import micro-modules
from .modules.initialization import Initialization
from .modules.business_enablement_orchestration import BusinessEnablementOrchestration
from .modules.soa_mcp import SoaMcp
from .modules.utilities import Utilities


class DeliveryManagerService(ManagerServiceBase, ManagerServiceProtocol):
    """
    Delivery Manager Service - Clean Micro-Modular Rebuild
    
    Clean micro-modular implementation using base/protocol architecture
    with proper infrastructure abstractions for business enablement orchestration.
    
    WHAT (Manager Role): I orchestrate business enablement and coordinate all 5 pillars (Delivery → Business Enablement)
    HOW (Service Implementation): I use ManagerServiceBase with Public Works abstractions + direct library injection
    """
    
    def __init__(self, di_container: Any, platform_gateway: Any = None):
        """Initialize Delivery Manager Service with proper infrastructure mapping."""
        # Get Platform Gateway from DI Container if not provided
        if platform_gateway is None:
            try:
                platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
            except:
                pass  # Will be set later if needed
        
        super().__init__(
            service_name="DeliveryManagerService",
            realm_name="business_enablement",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Manager-specific initialization
        self.manager_type = ManagerServiceType.DELIVERY_MANAGER
        self.orchestration_scope = OrchestrationScope.CROSS_DIMENSIONAL
        self.governance_level = GovernanceLevel.MODERATE
        
        # Infrastructure Abstractions (Public Works - swappable infrastructure for low-level ops)
        self.session_abstraction = None
        self.state_management_abstraction = None
        
        # Smart City Services (discovered via Curator for business-level operations)
        self.conductor = None  # Workflow orchestration for pillar delivery
        self.post_office = None  # Pillar coordination messaging
        
        # Service State
        self.is_infrastructure_connected = False
        
        # SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Delivery Manager specific state
        self.business_pillars: Dict[str, Any] = {}
        self.business_orchestrator: Any = None
        self.cross_realm_coordination_enabled = False
        
        # MVP Pillar Orchestrators (directly managed)
        self.mvp_pillar_orchestrators: Dict[str, Any] = {
            "content_analysis": None,
            "insights": None,
            "operations": None,
            "business_outcomes": None
        }
        
        # ========================================================================
        # ✅ REMOVED: Data Solution Orchestrator is in Solution realm and discovered via Curator
        # ContentJourneyOrchestrator no longer needs temporary registration
        # DataSolutionOrchestratorService discovers ContentJourneyOrchestrator via Curator
        # ========================================================================
        
        # Initialize micro-modules
        self.initialization_module = Initialization(self)
        self.business_enablement_orchestration_module = BusinessEnablementOrchestration(self)
        self.soa_mcp_module = SoaMcp(self)
        self.utilities_module = Utilities(self)
        
        # Logger is initialized in base class
        if hasattr(self, 'logger') and self.logger:
            self.logger.info("✅ Delivery Manager Service (Clean Micro-Modular Rebuild) initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize Delivery Manager Service with infrastructure and libraries.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "delivery_manager_initialize_start",
            success=True
        )
        
        try:
            if self.logger:
                self.logger.info("🚀 Initializing Delivery Manager Service...")
            
            # Initialize infrastructure connections
            await self.initialization_module.initialize_infrastructure_connections()
            
            # Initialize Delivery Manager capabilities
            await self.initialization_module.initialize_delivery_manager_capabilities()
            
            # Initialize MVP pillar orchestrators
            await self._initialize_mvp_pillar_orchestrators()
            
            # ========================================================================
            # Data Solution Orchestrator is now in Solution realm and discovered via Curator
            # No initialization needed here - ContentAnalysisOrchestrator discovers it via Curator
            
            # Initialize SOA API exposure
            await self.soa_mcp_module.initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Register with Curator (Phase 2 pattern)
            await self.soa_mcp_module.register_delivery_manager_capabilities()
            
            self.is_initialized = True
            
            # Record health metric
            await self.record_health_metric(
                "delivery_manager_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "delivery_manager_initialize_complete",
                success=True
            )
            
            if self.logger:
                self.logger.info("✅ Delivery Manager Service initialized successfully")
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "delivery_manager_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "delivery_manager_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            if self.logger:
                self.logger.error(f"❌ Failed to initialize Delivery Manager Service: {str(e)}")
            return False
    
    async def _initialize_mvp_pillar_orchestrators(self):
        """Initialize MVP pillar orchestrators (direct management pattern)."""
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "initialize_mvp_pillar_orchestrators_start",
            success=True
        )
        
        try:
            if self.logger:
                self.logger.info("🎯 Initializing MVP pillar orchestrators...")
            
            # Import orchestrators
            from .mvp_pillar_orchestrators.content_orchestrator.content_orchestrator import ContentOrchestrator
            # DEPRECATED: InsightsOrchestrator has been archived - use InsightsSolutionOrchestratorService → InsightsJourneyOrchestrator instead
            # from .mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator
            from .mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator import OperationsOrchestrator
            from .mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
            
            # Initialize each orchestrator with Delivery Manager as parent
            self.mvp_pillar_orchestrators["content"] = ContentOrchestrator(self)
            await self.mvp_pillar_orchestrators["content"].initialize()
            if self.logger:
                self.logger.info("✅ ContentOrchestrator initialized")
                # Debug logging to understand orchestrator creation
                self.logger.debug(f"🔍 Created ContentOrchestrator: {type(self.mvp_pillar_orchestrators['content']).__name__}")
                self.logger.debug(f"🔍 ContentOrchestrator object: {self.mvp_pillar_orchestrators['content'] is not None}")
                self.logger.debug(f"🔍 Stored in mvp_pillar_orchestrators['content']: {self.mvp_pillar_orchestrators['content']}")
            
            # DEPRECATED: InsightsOrchestrator has been archived
            # Use InsightsSolutionOrchestratorService → InsightsJourneyOrchestrator instead
            # self.mvp_pillar_orchestrators["insights"] = InsightsOrchestrator(self)
            # await self.mvp_pillar_orchestrators["insights"].initialize()
            if self.logger:
                self.logger.warning("⚠️ InsightsOrchestrator has been archived - use InsightsSolutionOrchestratorService → InsightsJourneyOrchestrator instead")
            
            self.mvp_pillar_orchestrators["operations"] = OperationsOrchestrator(self)
            await self.mvp_pillar_orchestrators["operations"].initialize()
            if self.logger:
                self.logger.info("✅ OperationsOrchestrator initialized")
            
            self.mvp_pillar_orchestrators["business_outcomes"] = BusinessOutcomesOrchestrator(self)
            await self.mvp_pillar_orchestrators["business_outcomes"].initialize()
            if self.logger:
                self.logger.info("✅ BusinessOutcomesOrchestrator initialized")
            
            # Record health metric
            await self.record_health_metric(
                "mvp_pillar_orchestrators_initialized",
                1.0,
                {"orchestrator_count": len(self.mvp_pillar_orchestrators)}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "initialize_mvp_pillar_orchestrators_complete",
                success=True,
                details={"orchestrator_count": len(self.mvp_pillar_orchestrators)}
            )
            
            if self.logger:
                self.logger.info(f"✅ Initialized {len(self.mvp_pillar_orchestrators)} MVP pillar orchestrators")
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "initialize_mvp_pillar_orchestrators")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "initialize_mvp_pillar_orchestrators_complete",
                success=False,
                details={"error": str(e)}
            )
            
            if self.logger:
                self.logger.error(f"❌ Failed to initialize MVP pillar orchestrators: {str(e)}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't raise - allow Delivery Manager to continue with partial initialization
    
        # Data Solution Orchestrator initialization removed - now in Solution realm
        # Discovered via Curator by ContentAnalysisOrchestrator
    
    async def shutdown(self) -> bool:
        """Shutdown Delivery Manager Service gracefully."""
        try:
            if self.logger:
                self.logger.info("🛑 Shutting down Delivery Manager Service...")
            
            # Clear state
            self.business_pillars.clear()
            self.mvp_pillar_orchestrators.clear()
            self.soa_apis.clear()
            self.mcp_tools.clear()
            
            self.is_initialized = False
            
            if self.logger:
                self.logger.info("✅ Delivery Manager Service shutdown complete")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error during Delivery Manager Service shutdown: {str(e)}")
            return False
    
    # ============================================================================
    # SOA API METHODS (Delegated to Modules)
    # ============================================================================
    
    async def deliver_capability(
        self,
        capability_request: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Deliver a business capability via business enablement pillars (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        return await self.business_enablement_orchestration_module.deliver_capability(
            capability_request,
            user_context=user_context
        )
    
    async def orchestrate_pillars(
        self,
        business_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate all 5 business enablement pillars (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        return await self.business_enablement_orchestration_module.orchestrate_business_enablement(
            business_context,
            user_context=user_context
        )
    
    async def track_outcomes(
        self,
        outcome_request: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track business outcomes (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        return await self.business_enablement_orchestration_module.track_outcomes(
            outcome_request,
            user_context=user_context
        )
    
    async def orchestrate_business_enablement(
        self,
        business_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate business enablement via Business Orchestrator (SOA API - top-down flow).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        return await self.business_enablement_orchestration_module.orchestrate_business_enablement(
            business_context,
            user_context=user_context
        )
    
    # ============================================================================
    # PROTOCOL COMPLIANCE METHODS
    # ============================================================================
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (ManagerServiceProtocol)."""
        return self.utilities_module.get_service_capabilities()
    
    async def get_business_orchestrator(self) -> Any:
        """
        Get Business Orchestrator (lazy-load if needed).
        
        This implements the lazy-hydrating service mesh pattern:
        - Business Orchestrator is only initialized when first accessed
        - Returns the initialized Business Orchestrator instance
        """
        try:
            # Check if already loaded and initialized
            if self.business_orchestrator and hasattr(self.business_orchestrator, 'is_initialized') and self.business_orchestrator.is_initialized:
                return self.business_orchestrator
            
            # Check DI container first (might already exist)
            # Try service registry first (where it's registered)
            business_orchestrator = self.di_container.service_registry.get("BusinessOrchestratorService")
            if not business_orchestrator:
                # Try manager services
                business_orchestrator = self.di_container.get_manager_service("BusinessOrchestratorService")
            if not business_orchestrator:
                # Try foundation services
                business_orchestrator = self.di_container.get_foundation_service("BusinessOrchestratorService")
            
            if business_orchestrator:
                # Check if initialized
                if hasattr(business_orchestrator, 'is_initialized') and business_orchestrator.is_initialized:
                    self.business_orchestrator = business_orchestrator
                    if self.logger:
                        self.logger.debug("✅ Business Orchestrator already exists and initialized")
                    return business_orchestrator
                else:
                    # Initialize it
                    if self.logger:
                        self.logger.info("🔄 Initializing existing Business Orchestrator...")
                    init_success = await business_orchestrator.initialize()
                    if init_success:
                        self.business_orchestrator = business_orchestrator
                        if self.logger:
                            self.logger.info("✅ Business Orchestrator initialized")
                        return business_orchestrator
                    else:
                        if self.logger:
                            self.logger.error("❌ Business Orchestrator initialization failed")
                        return None
            
            # Business Orchestrator doesn't exist - create and initialize it
            if self.logger:
                self.logger.info("🔄 Lazy-loading Business Orchestrator...")
            
            from backend.business_enablement.business_orchestrator.business_orchestrator_service import BusinessOrchestratorService
            
            # Create Business Orchestrator instance
            business_orchestrator = BusinessOrchestratorService(
                service_name="BusinessOrchestratorService",
                realm_name="business_enablement",
                platform_gateway=self.platform_gateway,
                di_container=self.di_container
            )
            
            # Initialize Business Orchestrator
            init_success = await business_orchestrator.initialize()
            if not init_success:
                if self.logger:
                    self.logger.error("❌ Business Orchestrator initialization returned False")
                return None
            
            # Store in Delivery Manager
            self.business_orchestrator = business_orchestrator
            
            # Register in DI container for service discovery
            self.di_container.service_registry["BusinessOrchestratorService"] = business_orchestrator
            
            if self.logger:
                self.logger.info("✅ Business Orchestrator lazy-loaded and initialized")
            
            return business_orchestrator
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to lazy-load Business Orchestrator: {e}")
            import traceback
            if self.logger:
                self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check (ManagerServiceProtocol)."""
        return {
            "service_name": self.service_name,
            "status": "healthy" if self.is_initialized else "unhealthy",
            "is_infrastructure_connected": self.is_infrastructure_connected,
            "business_pillars": len(self.business_pillars),
            "business_orchestrator_loaded": self.business_orchestrator is not None and hasattr(self.business_orchestrator, 'is_initialized') and self.business_orchestrator.is_initialized,
            "infrastructure": self.utilities_module.validate_infrastructure_mapping()
        }


