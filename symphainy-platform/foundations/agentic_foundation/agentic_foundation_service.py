#!/usr/bin/env python3
"""
Agentic Foundation Service - Agentic SDK and Capabilities

Provides agentic SDK and capabilities to all realms by wrapping the existing agentic capabilities.
This foundation service enables agentic capabilities without requiring Smart City dependencies.

WHAT (Agentic Foundation Role): I provide agentic SDK and capabilities to all realms
HOW (Agentic Foundation Implementation): I wrap existing agentic capabilities and provide foundation interface
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

# Import foundation base
from bases.foundation_service_base import FoundationServiceBase

# Import existing agentic capabilities
from foundations.agentic_foundation.agent_sdk.agent_base import AgentBase
# Note: MCPClientManager is imported from agent_sdk (not infrastructure_enablement) - it uses Curator for discovery
from foundations.agentic_foundation.agent_sdk.policy_integration import PolicyIntegration
from foundations.agentic_foundation.infrastructure_enablement.agui_output_formatter import AGUIOutputFormatter
from foundations.agentic_foundation.agent_sdk.tool_composition import ToolComposition
from foundations.agentic_foundation.agent_sdk.business_abstraction_helper import BusinessAbstractionHelper
from foundations.agentic_foundation.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
from foundations.agentic_foundation.agent_sdk.dimension_specialist_agent import DimensionSpecialistAgent
from foundations.agentic_foundation.agent_sdk.global_guide_agent import GlobalGuideAgent
from foundations.agentic_foundation.agent_sdk.global_orchestrator_agent import GlobalOrchestratorAgent
from foundations.agentic_foundation.agent_sdk.lightweight_llm_agent import LightweightLLMAgent
from foundations.agentic_foundation.agent_sdk.task_llm_agent import TaskLLMAgent

# Import existing agentic services
from foundations.agentic_foundation.agent_dashboard_service import AgentDashboardService
from foundations.agentic_foundation.specialization_registry import SpecializationRegistry
from foundations.agentic_foundation.infrastructure_enablement.agui_schema_registry import AGUISchemaRegistry

# Import infrastructure enablement services
from foundations.agentic_foundation.infrastructure_enablement.tool_registry_service import ToolRegistryService
from foundations.agentic_foundation.infrastructure_enablement.tool_discovery_service import ToolDiscoveryService
from foundations.agentic_foundation.infrastructure_enablement.health_service import HealthService
from foundations.agentic_foundation.infrastructure_enablement.policy_service import PolicyService
from foundations.agentic_foundation.infrastructure_enablement.session_service import SessionService


class AgenticFoundationService(FoundationServiceBase):
    """
    Agentic Foundation Service - Agentic SDK and Capabilities
    
    Provides agentic SDK and capabilities to all realms by wrapping the existing agentic capabilities.
    This foundation service enables agentic capabilities without requiring Smart City dependencies.
    
    WHAT (Agentic Foundation Role): I provide agentic SDK and capabilities to all realms
    HOW (Agentic Foundation Implementation): I wrap existing agentic capabilities and provide foundation interface
    
    Responsibilities:
    - Provide agentic SDK components (AgentBase, MCPClientManager, etc.)
    - Provide agentic services (AgentDashboardService, etc.)
    - Enable agentic capabilities for all realms
    - Manage agentic lifecycle and health monitoring
    - Govern agents across the platform
    - Coordinate agent deployment and health monitoring
    """
    
    def __init__(self, di_container, public_works_foundation=None, curator_foundation=None):
        """Initialize Agentic Foundation Service."""
        super().__init__(
            service_name="agentic_foundation",
            di_container=di_container,
            security_provider=None,  # Will be set by DI container
            authorization_guard=None  # Will be set by DI container
        )
        
        # Foundation dependencies
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        
        # Agentic SDK components (existing)
        self.agent_base = AgentBase
        self.mcp_client_manager = None  # Will be initialized with MCP infrastructure
        self.policy_integration = PolicyIntegration
        self.agui_formatter = None  # Will be initialized with Post Office service
        self.tool_composition = ToolComposition
        self.business_abstraction_helper = BusinessAbstractionHelper
        
        # Agentic agent types (existing)
        self.dimension_liaison_agent = DimensionLiaisonAgent
        self.dimension_specialist_agent = DimensionSpecialistAgent
        self.global_guide_agent = GlobalGuideAgent
        self.global_orchestrator_agent = GlobalOrchestratorAgent
        self.lightweight_llm_agent = LightweightLLMAgent
        self.task_llm_agent = TaskLLMAgent
        
        # Agentic services (existing)
        self.agent_dashboard_service = None
        self.specialization_registry = None
        self.agui_schema_registry = None  # Will be initialized as business service
        
        # Infrastructure enablement services (agent-specific business services)
        self.tool_registry_service = None
        self.tool_discovery_service = None
        self.health_service = None
        self.policy_service = None
        self.session_service = None
        
        # Agentic capabilities registry
        self.agentic_capabilities = {}
        
        # Agent factory - tracks all created agents
        self._agents: Dict[str, Any] = {}  # Track agents by agent_name
        
        self.logger.info("🏗️ Agentic Foundation Service initialized with existing agentic capabilities")
    
    async def initialize(self):
        """Initialize Agentic Foundation Service with enhanced platform capabilities."""
        try:
            # Use enhanced logging with telemetry
            await self.log_operation_with_telemetry("agentic_foundation_initialize", success=True)
            
            # Initialize the original agentic capabilities (preserving existing functionality)
            await self._initialize_agentic_services()
            await self._initialize_agentic_capabilities()
            
            # Initialize enhanced platform capabilities
            await self._initialize_enhanced_platform_capabilities()
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            # Record health metric
            await self.record_health_metric("agentic_foundation_initialized", 1.0, {"service": "agentic_foundation"})
            
            # Use enhanced logging with telemetry
            await self.log_operation_with_telemetry("agentic_foundation_initialize_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "agentic_foundation_initialize")
            self.service_health = "error"
            raise
    
    async def _initialize_agentic_services(self):
        """Initialize existing agentic services."""
        try:
            self.logger.info("🔧 Initializing existing agentic services...")
            
            # Initialize MCP Client Manager (uses Curator for endpoint discovery)
            # MCPClientManager now uses foundation_services (DI Container) and agentic_foundation
            try:
                from foundations.agentic_foundation.agent_sdk.mcp_client_manager import MCPClientManager
                
                # Get DI Container from foundation services
                di_container = self.di_container if hasattr(self, 'di_container') else None
                if not di_container:
                    # Try to get from service registry
                    di_container = self.service_registry.get("DIContainerService") if hasattr(self, 'service_registry') else None
                
                if di_container:
                    self.mcp_client_manager = MCPClientManager(
                        foundation_services=di_container,
                        agentic_foundation=self
                    )
                    # Initialize MCP Client Manager (discovers endpoint via Curator)
                    await self.mcp_client_manager.initialize()
                    self.logger.info("✅ MCP Client Manager initialized with Curator-based discovery")
                else:
                    self.logger.warning("⚠️ DI Container not available for MCP Client Manager")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize MCP Client Manager: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
            
            # Initialize AGUI Output Formatter with Post Office service
            # Post Office is a Smart City service, not a Public Works composition service
            # We'll get it via Curator if available, otherwise skip
            post_office_service = None
            if self.curator_foundation:
                try:
                    # Try to discover Post Office service via Curator
                    post_office_service = self.curator_foundation.get_registered_service("PostOfficeService")
                except:
                    pass
            
            if post_office_service:
                self.agui_formatter = AGUIOutputFormatter(post_office_service, di_container=self.di_container)
                self.logger.info("✅ AGUI Output Formatter initialized with Post Office service")
            else:
                self.logger.warning("⚠️ Post Office service not available for AGUI Output Formatter, skipping")
            
            # Initialize AGUI Schema Registry as business service
            self.agui_schema_registry = AGUISchemaRegistry(di_container=self.di_container)
            self.logger.info("✅ AGUI Schema Registry initialized as business service")
            
            # Initialize Agent Dashboard Service
            self.agent_dashboard_service = AgentDashboardService(
                di_container=self.di_container,
                public_works_foundation=self.public_works_foundation
            )
            
            # Initialize Specialization Registry
            self.specialization_registry = SpecializationRegistry(di_container=self.di_container)
            
            # Initialize infrastructure enablement services (agent-specific business services)
            if self.public_works_foundation:
                await self._initialize_infrastructure_enablement_services()
            
            self.logger.info("✅ Existing agentic services initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize existing agentic services: {e}")
            raise
    
    async def _initialize_infrastructure_enablement_services(self):
        """Initialize infrastructure enablement services for agent-specific capabilities."""
        try:
            self.logger.info("🔧 Initializing infrastructure enablement services...")
            
            # Tool Registry Service
            try:
                tool_storage = self.public_works_foundation.get_tool_storage_abstraction()
                if tool_storage:
                    self.tool_registry_service = ToolRegistryService(
                        tool_storage_abstraction=tool_storage,
                        curator_foundation=self.curator_foundation,
                        di_container=self.di_container
                    )
                    self.logger.info("✅ Tool Registry Service initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to initialize Tool Registry Service: {e}")
            
            # Tool Discovery Service
            try:
                if self.tool_registry_service:
                    self.tool_discovery_service = ToolDiscoveryService(
                        tool_registry_service=self.tool_registry_service,
                        curator_foundation=self.curator_foundation,
                        di_container=self.di_container
                    )
                    self.logger.info("✅ Tool Discovery Service initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to initialize Tool Discovery Service: {e}")
            
            # Health Service
            try:
                health_abstraction = self.public_works_foundation.get_health_abstraction()
                # HealthCompositionService may not have a getter, try to access directly
                health_composition = None
                if hasattr(self.public_works_foundation, 'health_composition_service'):
                    health_composition = self.public_works_foundation.health_composition_service
                elif hasattr(self.public_works_foundation, 'get_health_composition_service'):
                    health_composition = self.public_works_foundation.get_health_composition_service()
                
                if health_abstraction:
                    # HealthCompositionService is optional - can create a minimal one if needed
                    if not health_composition:
                        from foundations.public_works_foundation.composition_services.health_composition_service import HealthCompositionService
                        health_composition = HealthCompositionService(health_abstraction, di_container=self.di_container)
                    
                    self.health_service = HealthService(
                        health_abstraction=health_abstraction,
                        health_composition_service=health_composition,
                        curator_foundation=self.curator_foundation,
                        di_container=self.di_container
                    )
                    self.logger.info("✅ Health Service initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to initialize Health Service: {e}")
            
            # Policy Service
            try:
                policy_abstraction = self.public_works_foundation.get_policy_abstraction()
                policy_composition = self.public_works_foundation.get_policy_composition_service()
                if policy_abstraction and policy_composition:
                    self.policy_service = PolicyService(
                        policy_abstraction=policy_abstraction,
                        policy_composition_service=policy_composition,
                        curator_foundation=self.curator_foundation,
                        di_container=self.di_container
                    )
                    self.logger.info("✅ Policy Service initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to initialize Policy Service: {e}")
            
            # Session Service
            try:
                # Try to get session abstraction (may be called session_management_abstraction)
                session_abstraction = None
                if hasattr(self.public_works_foundation, 'get_session_abstraction'):
                    session_abstraction = self.public_works_foundation.get_session_abstraction()
                elif hasattr(self.public_works_foundation, 'session_management_abstraction'):
                    session_abstraction = self.public_works_foundation.session_management_abstraction
                
                # SessionCompositionService may not have a getter, try to access directly
                session_composition = None
                if hasattr(self.public_works_foundation, 'session_composition_service'):
                    session_composition = self.public_works_foundation.session_composition_service
                elif hasattr(self.public_works_foundation, 'get_session_composition_service'):
                    session_composition = self.public_works_foundation.get_session_composition_service()
                
                if session_abstraction and session_composition:
                    self.session_service = SessionService(
                        session_abstraction=session_abstraction,
                        session_composition_service=session_composition,
                        curator_foundation=self.curator_foundation,
                        di_container=self.di_container
                    )
                    self.logger.info("✅ Session Service initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to initialize Session Service: {e}")
            
            self.logger.info("✅ Infrastructure enablement services initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize infrastructure enablement services: {e}")
            # Don't raise - these are optional services
    
    async def _initialize_agentic_capabilities(self):
        """Initialize agentic capabilities registry."""
        try:
            self.logger.info("🔧 Initializing agentic capabilities registry...")
            
            # Agentic capabilities for all realms
            self.agentic_capabilities = {
                "agent_sdk": {
                    "agent_base": self.agent_base,
                    "mcp_client_manager": self.mcp_client_manager,
                    "policy_integration": self.policy_integration,
                    "agui_formatter": self.agui_formatter,
                    "tool_composition": self.tool_composition,
                    "business_abstraction_helper": self.business_abstraction_helper
                },
                "agent_types": {
                    "dimension_liaison_agent": self.dimension_liaison_agent,
                    "dimension_specialist_agent": self.dimension_specialist_agent,
                    "global_guide_agent": self.global_guide_agent,
                    "global_orchestrator_agent": self.global_orchestrator_agent,
                    "lightweight_llm_agent": self.lightweight_llm_agent,
                    "task_llm_agent": self.task_llm_agent,
                    # NEW - Week 2 Enhancement: Additional agent types for architectural alignment
                    "simple_llm_agent": self._create_simple_llm_agent,
                    "tool_enabled_agent": self._create_tool_enabled_agent,
                    "orchestration_agent": self._create_orchestration_agent
                },
                "agentic_services": {
                    "agent_dashboard_service": self.agent_dashboard_service,
                    "specialization_registry": self.specialization_registry,
                    "agui_schema_registry": self.agui_schema_registry
                }
            }
            
            self.logger.info("✅ Agentic capabilities registry initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize agentic capabilities registry: {e}")
            raise
    
    # ============================================================================
    # FOUNDATION SERVICE CAPABILITIES
    # ============================================================================
    
    async def get_agentic_capabilities(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agentic capabilities for all realms."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agentic_capabilities_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agentic_capabilities", "read"):
                        await self.record_health_metric("get_agentic_capabilities_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_agentic_capabilities_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            result = {
                "foundation_name": self.service_name,
                "agent_sdk": self.agentic_capabilities.get("agent_sdk", {}),
                "agent_types": list(self.agentic_capabilities.get("agent_types", {}).keys()),
                "agentic_services": list(self.agentic_capabilities.get("agentic_services", {}).keys()),
                "infrastructure_abstractions": {
                    "llm_abstraction": "Available for agent interpretation and guidance",
                    "mcp_client_abstraction": "Available for role communication",
                    "tool_registry_abstraction": "Available for tool management"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("get_agentic_capabilities_success", 1.0, {"agent_types_count": len(result["agent_types"])})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agentic_capabilities_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agentic_capabilities")
            self.logger.error(f"❌ Failed to get agentic capabilities: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    # ============================================================================
    # INFRASTRUCTURE ENABLEMENT FOR AGENTS
    # ============================================================================
    
    # ============================================================================
    # INFRASTRUCTURE ENABLEMENT SERVICE WRAPPERS
    # ============================================================================
    # These methods wrap infrastructure enablement service calls with utilities
    # Following Option B pattern: utilities via AgenticFoundationService
    
    async def register_agent_tool(self, tool_definition: Any, agent_id: str = None,
                                  user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register a tool for an agent (wraps ToolRegistryService).
        
        Args:
            tool_definition: Tool definition to register
            agent_id: ID of the agent registering the tool
            user_context: User context for security and tenant validation
            
        Returns:
            Dict containing registration result
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_agent_tool_start", success=True, 
                                                   details={"tool_name": getattr(tool_definition, 'name', 'unknown'), "agent_id": agent_id})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "tool_registry", "write"):
                        await self.record_health_metric("register_agent_tool_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("register_agent_tool_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            tenant_context = self._extract_tenant_context(user_context)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_agent_tool_tenant_denied", 1.0, {"agent_id": agent_id})
                            await self.log_operation_with_telemetry("register_agent_tool_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            # Call infrastructure enablement service
            if not self.tool_registry_service:
                await self.record_health_metric("register_agent_tool_service_unavailable", 1.0, {})
                await self.log_operation_with_telemetry("register_agent_tool_complete", success=False)
                return {"success": False, "error": "Tool Registry Service not available"}
            
            result = await self.tool_registry_service.register_tool(
                tool_definition=tool_definition,
                agent_id=agent_id,
                tenant_context=tenant_context
            )
            
            # Record success metric
            await self.record_health_metric("register_agent_tool_success", 1.0, {"agent_id": agent_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_agent_tool_complete", success=True, 
                                                   details={"tool_name": getattr(tool_definition, 'name', 'unknown')})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_agent_tool", 
                                              details={"agent_id": agent_id, "tool_name": getattr(tool_definition, 'name', 'unknown')})
            raise
    
    async def discover_agent_tools(self, capability_name: str = None, realm: str = None,
                                   pillar: str = None, user_context: Dict[str, Any] = None) -> List[Any]:
        """
        Discover tools for agents (wraps ToolDiscoveryService).
        
        Args:
            capability_name: Name of the capability to discover
            realm: Specific realm to search
            pillar: Specific pillar to search
            user_context: User context for security and tenant validation
            
        Returns:
            List of discovered tool definitions
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("discover_agent_tools_start", success=True, 
                                                   details={"capability_name": capability_name, "realm": realm, "pillar": pillar})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "tool_discovery", "read"):
                        await self.record_health_metric("discover_agent_tools_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("discover_agent_tools_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            tenant_context = self._extract_tenant_context(user_context)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("discover_agent_tools_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("discover_agent_tools_complete", success=False)
                            return []
            
            # Call infrastructure enablement service
            if not self.tool_discovery_service:
                await self.record_health_metric("discover_agent_tools_service_unavailable", 1.0, {})
                await self.log_operation_with_telemetry("discover_agent_tools_complete", success=False)
                return []
            
            if capability_name:
                result = await self.tool_discovery_service.discover_tools_by_capability(
                    capability_name=capability_name,
                    realm=realm,
                    pillar=pillar,
                    tenant_context=tenant_context
                )
            else:
                result = await self.tool_discovery_service.discover_available_tools(tenant_context=tenant_context)
            
            # Record success metric
            await self.record_health_metric("discover_agent_tools_success", 1.0, {"tools_count": len(result) if isinstance(result, list) else 0})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("discover_agent_tools_complete", success=True, 
                                                   details={"tools_count": len(result) if isinstance(result, list) else 0})
            
            return result if isinstance(result, list) else []
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "discover_agent_tools", 
                                              details={"capability_name": capability_name})
            return []
    
    async def monitor_agent_health_wrapper(self, operation_type: str, context: Any,
                                          operation_data: Dict[str, Any] = None,
                                          user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Monitor health for agent operations (wraps HealthService).
        
        Args:
            operation_type: Type of operation (llm_health, mcp_health, tool_health, agent_health)
            context: Health context
            operation_data: Optional operation data
            user_context: User context for security and tenant validation
            
        Returns:
            Dict containing health monitoring result
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("monitor_agent_health_wrapper_start", success=True, 
                                                   details={"operation_type": operation_type})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_health", "read"):
                        await self.record_health_metric("monitor_agent_health_wrapper_access_denied", 1.0, {"operation_type": operation_type})
                        await self.log_operation_with_telemetry("monitor_agent_health_wrapper_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            tenant_context = self._extract_tenant_context(user_context)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("monitor_agent_health_wrapper_tenant_denied", 1.0, {"operation_type": operation_type})
                            await self.log_operation_with_telemetry("monitor_agent_health_wrapper_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            # Call infrastructure enablement service
            if not self.health_service:
                await self.record_health_metric("monitor_agent_health_wrapper_service_unavailable", 1.0, {})
                await self.log_operation_with_telemetry("monitor_agent_health_wrapper_complete", success=False)
                return {"success": False, "error": "Health Service not available"}
            
            result = await self.health_service.monitor_agent_health(
                operation_type=operation_type,
                context=context,
                operation_data=operation_data
            )
            
            # Record success metric
            await self.record_health_metric("monitor_agent_health_wrapper_success", 1.0, {"operation_type": operation_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("monitor_agent_health_wrapper_complete", success=True, 
                                                   details={"operation_type": operation_type})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "monitor_agent_health_wrapper", 
                                              details={"operation_type": operation_type})
            raise
    
    async def enforce_agent_policy_wrapper(self, operation_type: str, context: Any,
                                         operation_data: Dict[str, Any] = None,
                                         user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enforce policies for agent operations (wraps PolicyService).
        
        Args:
            operation_type: Type of operation (llm_operations, mcp_operations, tool_operations, agent_behavior)
            context: Policy context
            operation_data: Optional operation data
            user_context: User context for security and tenant validation
            
        Returns:
            Dict containing policy enforcement result
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("enforce_agent_policy_wrapper_start", success=True, 
                                                   details={"operation_type": operation_type})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_policy", "write"):
                        await self.record_health_metric("enforce_agent_policy_wrapper_access_denied", 1.0, {"operation_type": operation_type})
                        await self.log_operation_with_telemetry("enforce_agent_policy_wrapper_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Call infrastructure enablement service
            if not self.policy_service:
                await self.record_health_metric("enforce_agent_policy_wrapper_service_unavailable", 1.0, {})
                await self.log_operation_with_telemetry("enforce_agent_policy_wrapper_complete", success=False)
                return {"success": False, "error": "Policy Service not available"}
            
            result = await self.policy_service.enforce_agent_policies(
                operation_type=operation_type,
                context=context,
                operation_data=operation_data
            )
            
            # Record success metric
            await self.record_health_metric("enforce_agent_policy_wrapper_success", 1.0, {"operation_type": operation_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("enforce_agent_policy_wrapper_complete", success=True, 
                                                   details={"operation_type": operation_type})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "enforce_agent_policy_wrapper", 
                                              details={"operation_type": operation_type})
            raise
    
    async def manage_agent_session_wrapper(self, operation_type: str, context: Any,
                                          operation_data: Dict[str, Any] = None,
                                          user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Manage sessions for agent operations (wraps SessionService).
        
        Args:
            operation_type: Type of operation (llm_session, mcp_session, tool_session, agent_session)
            context: Session context
            operation_data: Optional operation data
            user_context: User context for security and tenant validation
            
        Returns:
            Dict containing session management result
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("manage_agent_session_wrapper_start", success=True, 
                                                   details={"operation_type": operation_type})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_session", "write"):
                        await self.record_health_metric("manage_agent_session_wrapper_access_denied", 1.0, {"operation_type": operation_type})
                        await self.log_operation_with_telemetry("manage_agent_session_wrapper_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            tenant_context = self._extract_tenant_context(user_context)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("manage_agent_session_wrapper_tenant_denied", 1.0, {"operation_type": operation_type})
                            await self.log_operation_with_telemetry("manage_agent_session_wrapper_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            # Call infrastructure enablement service
            if not self.session_service:
                await self.record_health_metric("manage_agent_session_wrapper_service_unavailable", 1.0, {})
                await self.log_operation_with_telemetry("manage_agent_session_wrapper_complete", success=False)
                return {"success": False, "error": "Session Service not available"}
            
            result = await self.session_service.manage_agent_session(
                operation_type=operation_type,
                context=context,
                operation_data=operation_data
            )
            
            # Record success metric
            await self.record_health_metric("manage_agent_session_wrapper_success", 1.0, {"operation_type": operation_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("manage_agent_session_wrapper_complete", success=True, 
                                                   details={"operation_type": operation_type})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "manage_agent_session_wrapper", 
                                              details={"operation_type": operation_type})
            raise
    
    def _extract_tenant_context(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract tenant context from user context."""
        if not user_context:
            return None
        tenant_id = user_context.get("tenant_id")
        if tenant_id:
            return {
                "tenant_id": tenant_id,
                "realm": user_context.get("realm", "agentic"),
                "pillar": user_context.get("pillar", "agentic")
            }
        return None
    
    async def get_tenant_abstraction(self):
        """Get tenant abstraction for agents through infrastructure enablement."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_tenant_abstraction_start", success=True)
            
            if self.public_works_foundation:
                result = self.public_works_foundation.get_tenant_abstraction()
                # Record success metric
                await self.record_health_metric("get_tenant_abstraction_success", 1.0, {"available": result is not None})
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_tenant_abstraction_complete", success=True)
                return result
            
            # Record success metric
            await self.record_health_metric("get_tenant_abstraction_success", 1.0, {"available": False})
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_tenant_abstraction_complete", success=True)
            return None
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_tenant_abstraction")
            self.logger.error(f"Failed to get tenant abstraction: {e}")
            return None
    
    async def get_mcp_abstraction(self):
        """Get MCP abstraction for agents through infrastructure enablement."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_mcp_abstraction_start", success=True)
            
            if self.public_works_foundation:
                result = self.public_works_foundation.get_mcp_abstraction()
                # Record success metric
                await self.record_health_metric("get_mcp_abstraction_success", 1.0, {"available": result is not None})
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_mcp_abstraction_complete", success=True)
                return result
            
            # Record success metric
            await self.record_health_metric("get_mcp_abstraction_success", 1.0, {"available": False})
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_mcp_abstraction_complete", success=True)
            return None
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_mcp_abstraction")
            self.logger.error(f"Failed to get MCP abstraction: {e}")
            return None
    
    async def get_llm_abstraction(self):
        """Get LLM abstraction for agents through infrastructure enablement."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_llm_abstraction_start", success=True)
            
            if self.public_works_foundation:
                result = self.public_works_foundation.get_llm_business_abstraction()
                # Record success metric
                await self.record_health_metric("get_llm_abstraction_success", 1.0, {"available": result is not None})
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_llm_abstraction_complete", success=True)
                return result
            
            # Record success metric
            await self.record_health_metric("get_llm_abstraction_success", 1.0, {"available": False})
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_llm_abstraction_complete", success=True)
            return None
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_llm_abstraction")
            self.logger.error(f"Failed to get LLM abstraction: {e}")
            return None
    
    async def get_tool_abstraction(self):
        """Get tool abstraction for agents through infrastructure enablement."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_tool_abstraction_start", success=True)
            
            if self.public_works_foundation:
                result = self.public_works_foundation.get_tool_registry_abstraction()
                # Record success metric
                await self.record_health_metric("get_tool_abstraction_success", 1.0, {"available": result is not None})
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_tool_abstraction_complete", success=True)
                return result
            
            # Record success metric
            await self.record_health_metric("get_tool_abstraction_success", 1.0, {"available": False})
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_tool_abstraction_complete", success=True)
            return None
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_tool_abstraction")
            self.logger.error(f"Failed to get tool abstraction: {e}")
            return None
    
    async def create_agent(self, agent_type: str, agent_config: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create agent for realms using existing agentic capabilities."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("create_agent_start", success=True)
            
            agent_name = agent_config.get('agent_name', 'unknown')
            self.logger.info(f"🤖 Creating {agent_type} agent with config: {agent_name}")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_creation", "write"):
                        await self.record_health_metric("create_agent_access_denied", 1.0, {"agent_type": agent_type, "agent_name": agent_name})
                        await self.log_operation_with_telemetry("create_agent_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("create_agent_tenant_denied", 1.0, {"agent_type": agent_type, "agent_name": agent_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("create_agent_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            # Get agent type class
            agent_class = self.agentic_capabilities.get("agent_types", {}).get(agent_type)
            if not agent_class:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            # Create agent using existing agentic capabilities
            agent = agent_class(
                agent_name=agent_config.get("agent_name"),
                capabilities=agent_config.get("capabilities", []),
                required_roles=agent_config.get("required_roles", []),
                agui_schema=agent_config.get("agui_schema"),
                foundation_services=self.di_container,
                agentic_foundation=self,
                mcp_client_manager=self.mcp_client_manager(
                    di_container=self.di_container,
                    agentic_foundation=self
                ),
                policy_integration=self.policy_integration(
                    di_container=self.di_container,
                    agentic_foundation=self
                ),
                tool_composition=self.tool_composition(
                    di_container=self.di_container,
                    agentic_foundation=self
                ),
                agui_formatter=self.agui_formatter(
                    di_container=self.di_container,
                    agentic_foundation=self
                ),
                curator_foundation=self.curator_foundation
            )
            
            result = {
                "success": True,
                "agent": agent,
                "agent_type": agent_type,
                "agent_name": agent_config.get("agent_name"),
                "capabilities": agent_config.get("capabilities", []),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("create_agent_success", 1.0, {"agent_type": agent_type, "agent_name": agent_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_agent_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "create_agent")
            self.logger.error(f"❌ Failed to create {agent_type} agent: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def orchestrate_agents(self, orchestration_request: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Orchestrate agents across the platform."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("orchestrate_agents_start", success=True)
            
            orchestration_type = orchestration_request.get('orchestration_type', 'unknown')
            self.logger.info(f"🎯 Orchestrating agents: {orchestration_type}")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_orchestration", "write"):
                        await self.record_health_metric("orchestrate_agents_access_denied", 1.0, {"orchestration_type": orchestration_type})
                        await self.log_operation_with_telemetry("orchestrate_agents_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("orchestrate_agents_tenant_denied", 1.0, {"orchestration_type": orchestration_type, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("orchestrate_agents_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            # Agent orchestration logic (simplified - can be enhanced later)
            result = {
                "success": True,
                "orchestration_result": {"status": "orchestrated"},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("orchestrate_agents_success", 1.0, {"orchestration_type": orchestration_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("orchestrate_agents_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "orchestrate_agents")
            self.logger.error(f"❌ Failed to orchestrate agents: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def govern_agents(self, governance_context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Govern agents across the platform."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("govern_agents_start", success=True)
            
            self.logger.info(f"🛡️ Governing agents with context: {governance_context}")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_governance", "write"):
                        await self.record_health_metric("govern_agents_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("govern_agents_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("govern_agents_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("govern_agents_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            # Get all agents
            all_agents = await self._get_all_agents()
            
            # Apply governance policies
            governance_results = {}
            for agent in all_agents:
                agent_id = agent.get("id")
                if agent_id:
                    governance_result = await self._apply_governance_policy(agent_id, governance_context)
                    governance_results[agent_id] = governance_result
            
            result = {
                "governance_type": "agent_governance",
                "context": governance_context,
                "governance_results": governance_results,
                "status": "governed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("govern_agents_success", 1.0, {"agents_governed": len(governance_results)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("govern_agents_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "govern_agents")
            self.logger.error(f"❌ Failed to govern agents: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__, "status": "failed"}
    
    async def get_agent_governance_status(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent governance status."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_governance_status_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_governance", "read"):
                        await self.record_health_metric("get_agent_governance_status_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_agent_governance_status_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Get overall agent health
            overall_health = await self._get_overall_agent_health()
            
            result = {
                "overall_status": "healthy" if overall_health.get("health_percentage", 0) >= 80 else "degraded",
                "governed_agents": overall_health.get("total_agents", 0),
                "healthy_agents": overall_health.get("healthy_agents", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("get_agent_governance_status_success", 1.0, {"total_agents": result["governed_agents"]})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_governance_status_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_governance_status")
            self.logger.error(f"❌ Failed to get agent governance status: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__, "status": "failed"}
    
    async def coordinate_agent_deployment(self, agent_context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Coordinate agent deployment."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("coordinate_agent_deployment_start", success=True)
            
            agent_id = agent_context.get("agent_id", "unknown")
            self.logger.info(f"Coordinating agent deployment: {agent_id}")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_deployment", "write"):
                        await self.record_health_metric("coordinate_agent_deployment_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("coordinate_agent_deployment_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("coordinate_agent_deployment_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("coordinate_agent_deployment_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            result = {
                "agent_id": agent_id,
                "deployment_context": agent_context,
                "status": "deployed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("coordinate_agent_deployment_success", 1.0, {"agent_id": agent_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("coordinate_agent_deployment_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "coordinate_agent_deployment")
            self.logger.error(f"❌ Failed to coordinate agent deployment: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__, "status": "failed"}
    
    async def get_agent_deployment_status(self, agent_id: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent deployment status."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_deployment_status_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_id, "read"):
                        await self.record_health_metric("get_agent_deployment_status_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("get_agent_deployment_status_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Check agent registry for deployment status
            agent_info = await self._get_agent_info(agent_id)
            
            result = {
                "agent_id": agent_id,
                "deployment_status": "healthy" if agent_info.get("status") == "active" else "unhealthy",
                "agent_info": agent_info,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("get_agent_deployment_status_success", 1.0, {"agent_id": agent_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_deployment_status_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_deployment_status")
            self.logger.error(f"❌ Failed to get agent deployment status: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__, "status": "failed"}
    
    async def monitor_agent_performance(self, agent_id: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Monitor agent performance."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("monitor_agent_performance_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_id, "read"):
                        await self.record_health_metric("monitor_agent_performance_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("monitor_agent_performance_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            tenant_context = self._extract_tenant_context(user_context)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("monitor_agent_performance_tenant_denied", 1.0, {"agent_id": agent_id})
                            await self.log_operation_with_telemetry("monitor_agent_performance_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            # Get agent performance metrics
            performance_metrics = await self._get_agent_performance_metrics(agent_id)
            
            result = {
                "agent_id": agent_id,
                "performance_metrics": performance_metrics,
                "status": "monitored",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("monitor_agent_performance_success", 1.0, {"agent_id": agent_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("monitor_agent_performance_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "monitor_agent_performance")
            self.logger.error(f"❌ Failed to monitor agent performance: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__, "status": "failed"}
    
    async def get_agent_performance_metrics(self, agent_id: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent performance metrics."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_performance_metrics_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_id, "read"):
                        await self.record_health_metric("get_agent_performance_metrics_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("get_agent_performance_metrics_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Get performance metrics from agent performance analytics
            metrics = await self._get_agent_metrics(agent_id)
            
            result = {
                "agent_id": agent_id,
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("get_agent_performance_metrics_success", 1.0, {"agent_id": agent_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_performance_metrics_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_performance_metrics")
            self.logger.error(f"❌ Failed to get agent performance metrics: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__, "status": "failed"}
    
    async def enforce_agent_policy(self, agent_id: str, policy: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enforce agent policy."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("enforce_agent_policy_start", success=True)
            
            self.logger.info(f"Enforcing policy {policy} on agent {agent_id}")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_id, "write"):
                        await self.record_health_metric("enforce_agent_policy_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("enforce_agent_policy_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("enforce_agent_policy_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("enforce_agent_policy_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            # Apply policy to agent
            policy_result = await self._apply_agent_policy(agent_id, policy)
            
            result = {
                "agent_id": agent_id,
                "policy": policy,
                "policy_result": policy_result,
                "status": "enforced",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("enforce_agent_policy_success", 1.0, {"agent_id": agent_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("enforce_agent_policy_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "enforce_agent_policy")
            self.logger.error(f"❌ Failed to enforce agent policy: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__, "status": "failed"}
    
    # ============================================================================
    # COORDINATION WITH OTHER MANAGERS
    # ============================================================================
    
    async def coordinate_with_manager(self, manager_name: str, startup_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Coordinate with a specific manager."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("coordinate_with_manager_start", success=True, 
                                                   details={"manager_name": manager_name})
            
            result = None
            if manager_name == "city_manager":
                result = await self._coordinate_with_city_manager(startup_context)
            elif manager_name == "delivery_manager":
                result = await self._coordinate_with_delivery_manager(startup_context)
            elif manager_name == "experience_manager":
                result = await self._coordinate_with_experience_manager(startup_context)
            elif manager_name == "journey_manager":
                result = await self._coordinate_with_journey_manager(startup_context)
            else:
                result = {"error": f"Unknown manager: {manager_name}", "status": "failed"}
            
            # Record success metric
            await self.record_health_metric("coordinate_with_manager_success", 1.0, {"manager_name": manager_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("coordinate_with_manager_complete", success=True, 
                                                   details={"manager_name": manager_name})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "coordinate_with_manager", 
                                              details={"manager_name": manager_name})
            return {"error": str(e), "status": "failed"}
    
    async def _coordinate_with_city_manager(self, startup_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Coordinate with City Manager."""
        try:
            return {
                "manager_name": "city_manager",
                "coordination_type": "agentic_to_city",
                "startup_context": startup_context,
                "status": "coordinated",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    async def _coordinate_with_delivery_manager(self, startup_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Coordinate with Delivery Manager."""
        try:
            return {
                "manager_name": "delivery_manager",
                "coordination_type": "agentic_to_delivery",
                "startup_context": startup_context,
                "status": "coordinated",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    async def _coordinate_with_experience_manager(self, startup_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Coordinate with Experience Manager."""
        try:
            return {
                "manager_name": "experience_manager",
                "coordination_type": "agentic_to_experience",
                "startup_context": startup_context,
                "status": "coordinated",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    async def _coordinate_with_journey_manager(self, startup_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Coordinate with Journey Manager."""
        try:
            return {
                "manager_name": "journey_manager",
                "coordination_type": "agentic_to_journey",
                "startup_context": startup_context,
                "status": "coordinated",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    async def _get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all agents across the platform."""
        # Get agents from factory cache
        factory_agents = await self.list_agents()
        
        # Also discover via Curator
        curator_agents = await self.discover_agents_via_curator()
        
        # Combine and format
        all_agents = []
        for agent_name, agent_info in factory_agents.items():
            all_agents.append({
                "id": agent_name,
                "domain": agent_info.get("realm", "unknown"),
                "type": agent_info.get("agent_type", "unknown"),
                "status": "active" if agent_info.get("initialized", False) else "inactive"
            })
        
        # Add Curator-discovered agents (avoid duplicates)
        curator_agent_ids = {a["id"] for a in all_agents}
        for agent_name, agent_info in curator_agents.get("agents", {}).items():
            if agent_name not in curator_agent_ids:
                all_agents.append({
                    "id": agent_name,
                    "domain": agent_info.get("realm", "unknown"),
                    "type": agent_info.get("agent_type", "unknown"),
                    "status": "active"
                })
        
        return all_agents
    
    async def _get_overall_agent_health(self) -> Dict[str, Any]:
        """Get overall agent health."""
        all_agents = await self._get_all_agents()
        healthy_count = sum(1 for agent in all_agents if agent.get("status") == "active")
        total_count = len(all_agents)
        
        return {
            "total_agents": total_count,
            "healthy_agents": healthy_count,
            "health_percentage": (healthy_count / total_count * 100) if total_count > 0 else 0.0
        }
    
    async def _apply_governance_policy(self, agent_id: str, governance_context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply governance policy to an agent."""
        # Mock implementation - in real scenario, this would apply actual governance policies
        return {
            "agent_id": agent_id,
            "policy_applied": True,
            "status": "governed"
        }
    
    async def _get_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """Get agent information."""
        # Try factory cache first
        agent = await self.get_agent(agent_id)
        if agent:
            return {
                "id": agent_id,
                "status": "active" if getattr(agent, 'is_initialized', False) else "inactive",
                "domain": getattr(agent, 'business_domain', 'unknown')
            }
        
        # Try Curator
        agent = await self.get_agent_via_curator(agent_id)
        if agent:
            return {
                "id": agent_id,
                "status": "active",
                "domain": getattr(agent, 'business_domain', 'unknown')
            }
        
        return {
            "id": agent_id,
            "status": "unknown",
            "domain": "unknown"
        }
    
    async def _get_agent_performance_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get agent performance metrics."""
        # Mock implementation - in real scenario, this would query performance analytics
        return {
            "response_time": "50ms",
            "throughput": "100 req/min",
            "cpu_usage": "15%",
            "memory_usage": "128MB",
            "error_rate": "0.1%"
        }
    
    async def _get_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get agent metrics."""
        # Mock implementation - in real scenario, this would query metrics from analytics service
        return {
            "response_time": "50ms",
            "throughput": "100 req/min",
            "cpu_usage": "15%",
            "memory_usage": "128MB",
            "error_rate": "0.1%"
        }
    
    async def _apply_agent_policy(self, agent_id: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Apply policy to an agent."""
        # Mock implementation - in real scenario, this would apply actual policies
        return {
            "agent_id": agent_id,
            "policy_applied": True,
            "status": "enforced"
        }
    
    # ============================================================================
    # AGENT DASHBOARD METHODS (for AgentDashboardService)
    # ============================================================================
    
    async def get_agent_overview(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get unified agent overview across all domains."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_overview_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_overview", "read"):
                        await self.record_health_metric("get_agent_overview_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_agent_overview_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            all_agents = await self._get_all_agents()
            governance_status = await self.get_agent_governance_status(user_context)
            
            result = {
                "total_agents": len(all_agents),
                "healthy_agents": governance_status.get("healthy_agents", 0),
                "overall_status": governance_status.get("overall_status", "unknown"),
                "agents": all_agents,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("get_agent_overview_success", 1.0, {"total_agents": result["total_agents"]})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_overview_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_overview")
            self.logger.error(f"❌ Failed to get agent overview: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    async def get_all_agents(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get all agents in a format compatible with AgentDashboardService."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_all_agents_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_list", "read"):
                        await self.record_health_metric("get_all_agents_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_all_agents_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED", "agents": [], "total_agents": 0}
            
            all_agents = await self._get_all_agents()
            
            result = {
                "agents": all_agents,
                "total_agents": len(all_agents),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("get_all_agents_success", 1.0, {"total_agents": result["total_agents"]})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_all_agents_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_all_agents")
            self.logger.error(f"❌ Failed to get all agents: {e}")
            return {"success": False, "agents": [], "total_agents": 0, "error": str(e), "error_code": type(e).__name__}
    
    async def get_agent_health(self, agent_id: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get health status for a specific agent."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_health_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_id, "read"):
                        await self.record_health_metric("get_agent_health_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("get_agent_health_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            agent_info = await self._get_agent_info(agent_id)
            deployment_status = await self.get_agent_deployment_status(agent_id, user_context)
            
            result = {
                "agent_id": agent_id,
                "status": agent_info.get("status", "unknown"),
                "deployment_status": deployment_status.get("deployment_status", "unknown"),
                "health_percentage": 100.0 if agent_info.get("status") == "active" else 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("get_agent_health_success", 1.0, {"agent_id": agent_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_health_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_health")
            self.logger.error(f"❌ Failed to get agent health for {agent_id}: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__, "status": "unknown"}
    
    async def get_agent_performance(self, agent_id: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get performance metrics for a specific agent."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_performance_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_id, "read"):
                        await self.record_health_metric("get_agent_performance_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("get_agent_performance_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            tenant_context = self._extract_tenant_context(user_context)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_agent_performance_tenant_denied", 1.0, {"agent_id": agent_id})
                            await self.log_operation_with_telemetry("get_agent_performance_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            metrics = await self.get_agent_performance_metrics(agent_id, user_context)
            
            result = {
                "agent_id": agent_id,
                "metrics": metrics.get("metrics", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("get_agent_performance_success", 1.0, {"agent_id": agent_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_performance_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_performance")
            self.logger.error(f"❌ Failed to get agent performance for {agent_id}: {e}")
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    async def get_domain_agents(self, domain: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get all agents for a specific domain."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_domain_agents_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, domain, "read"):
                        await self.record_health_metric("get_domain_agents_access_denied", 1.0, {"domain": domain})
                        await self.log_operation_with_telemetry("get_domain_agents_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED", "domain": domain, "agent_count": 0, "agents": []}
            
            all_agents = await self._get_all_agents()
            domain_agents = [agent for agent in all_agents if agent.get("domain") == domain]
            
            result = {
                "domain": domain,
                "agent_count": len(domain_agents),
                "agents": domain_agents,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("get_domain_agents_success", 1.0, {"domain": domain, "agent_count": result["agent_count"]})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_domain_agents_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_domain_agents")
            self.logger.error(f"❌ Failed to get domain agents for {domain}: {e}")
            return {"success": False, "domain": domain, "agent_count": 0, "agents": [], "error": str(e), "error_code": type(e).__name__}
    
    async def monitor_agents(self, monitoring_request: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Monitor agents using existing agent dashboard service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("monitor_agents_start", success=True)
            
            monitoring_type = monitoring_request.get('monitoring_type', 'unknown')
            self.logger.info(f"📊 Monitoring agents: {monitoring_type}")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_monitoring", "read"):
                        await self.record_health_metric("monitor_agents_access_denied", 1.0, {"monitoring_type": monitoring_type})
                        await self.log_operation_with_telemetry("monitor_agents_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            tenant_context = self._extract_tenant_context(user_context)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("monitor_agents_tenant_denied", 1.0, {"monitoring_type": monitoring_type})
                            await self.log_operation_with_telemetry("monitor_agents_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            # Use existing agent dashboard service for monitoring
            monitoring_result = await self.agent_dashboard_service.monitor_agents(
                monitoring_request
            )
            
            result = {
                "success": True,
                "monitoring_result": monitoring_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("monitor_agents_success", 1.0, {"monitoring_type": monitoring_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("monitor_agents_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "monitor_agents")
            self.logger.error(f"❌ Failed to monitor agents: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # ENHANCED PLATFORM CAPABILITIES
    # ============================================================================
    
    async def _initialize_enhanced_platform_capabilities(self):
        """Initialize enhanced platform capabilities while preserving agentic functionality."""
        try:
            self.logger.info("🚀 Initializing enhanced platform capabilities for agentic foundation...")
            
            # Enhanced security patterns (zero-trust, policy engine, tenant isolation)
            await self._initialize_enhanced_security()
            
            # Enhanced utility patterns (logging, error handling, health monitoring)
            await self._initialize_enhanced_utilities()
            
            # Platform capabilities (SOA communication, service discovery, capability registry)
            await self._initialize_platform_capabilities()
            
            self.logger.info("✅ Enhanced platform capabilities initialized for agentic foundation")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize enhanced platform capabilities: {e}")
            raise
    
    async def _initialize_enhanced_security(self):
        """Initialize enhanced security patterns for agentic foundation."""
        try:
            self.logger.info("🔒 Initializing enhanced security patterns for agentic foundation...")
            
            # Zero-trust security is already initialized in the base class
            # Policy engine is already initialized in the base class
            # Tenant isolation is already initialized in the base class
            # Security audit is already initialized in the base class
            
            # Agent-specific security enhancements
            await self._initialize_agent_security()
            
            self.logger.info("✅ Enhanced security patterns initialized for agentic foundation")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize enhanced security: {e}")
            raise
    
    async def _initialize_agent_security(self):
        """Initialize agent-specific security enhancements."""
        try:
            self.logger.info("🤖 Initializing agent-specific security enhancements...")
            
            # Agent access control
            self.agent_access_control = {
                "cross_realm_agents": ["global_guide_agent", "global_orchestrator_agent"],
                "realm_specific_agents": ["dimension_liaison_agent", "dimension_specialist_agent"],
                "task_agents": ["lightweight_llm_agent", "task_llm_agent"]
            }
            
            # Agent policy enforcement
            self.agent_policy_enforcement = {
                "agent_deployment_policy": "require_approval_for_cross_realm_agents",
                "agent_resource_limits": "cpu_memory_limits_per_agent_type",
                "agent_communication_policy": "encrypted_inter_agent_communication"
            }
            
            # Agent tenant isolation
            self.agent_tenant_isolation = {
                "agent_context_isolation": True,
                "agent_data_isolation": True,
                "agent_capability_isolation": True
            }
            
            self.logger.info("✅ Agent-specific security enhancements initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize agent security: {e}")
            raise
    
    async def _initialize_enhanced_utilities(self):
        """Initialize enhanced utility patterns for agentic foundation."""
        try:
            self.logger.info("🛠️ Initializing enhanced utility patterns for agentic foundation...")
            
            # Enhanced logging is already initialized in the base class
            # Enhanced error handling is already initialized in the base class
            # Health monitoring is already initialized in the base class
            # Performance monitoring is already initialized in the base class
            
            # Agent-specific utility enhancements
            await self._initialize_agent_utilities()
            
            self.logger.info("✅ Enhanced utility patterns initialized for agentic foundation")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize enhanced utilities: {e}")
            raise
    
    async def _initialize_agent_utilities(self):
        """Initialize agent-specific utility enhancements."""
        try:
            self.logger.info("🤖 Initializing agent-specific utility enhancements...")
            
            # Agent-specific logging
            self.agent_logging = {
                "agent_activity_logging": True,
                "agent_performance_logging": True,
                "agent_error_logging": True,
                "agent_communication_logging": True
            }
            
            # Agent-specific error handling
            self.agent_error_handling = {
                "agent_failure_recovery": True,
                "agent_graceful_degradation": True,
                "agent_error_propagation": True
            }
            
            # Agent-specific health monitoring
            self.agent_health_monitoring = {
                "agent_health_checks": True,
                "agent_performance_metrics": True,
                "agent_resource_usage": True,
                "agent_availability_monitoring": True
            }
            
            self.logger.info("✅ Agent-specific utility enhancements initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize agent utilities: {e}")
            raise
    
    async def _initialize_platform_capabilities(self):
        """Initialize platform capabilities for agentic foundation."""
        try:
            self.logger.info("🌐 Initializing platform capabilities for agentic foundation...")
            
            # SOA communication is already initialized in the base class
            # Service discovery is already initialized in the base class
            # Capability registry is already initialized in the base class
            # Performance monitoring is already initialized in the base class
            
            # Agent-specific platform capabilities
            await self._initialize_agent_platform_capabilities()
            
            self.logger.info("✅ Platform capabilities initialized for agentic foundation")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize platform capabilities: {e}")
            raise
    
    async def _initialize_agent_platform_capabilities(self):
        """Initialize agent-specific platform capabilities."""
        try:
            self.logger.info("🤖 Initializing agent-specific platform capabilities...")
            
            # Agent SOA communication
            self.agent_soa_communication = {
                "agent_to_agent_communication": True,
                "agent_to_service_communication": True,
                "agent_to_realm_communication": True
            }
            
            # Agent service discovery
            self.agent_service_discovery = {
                "agent_capability_discovery": True,
                "agent_service_discovery": True,
                "agent_endpoint_discovery": True
            }
            
            # Agent capability registry
            self.agent_capability_registry = {
                "agent_capabilities": self.agentic_capabilities,
                "agent_types": ["dimension_liaison", "dimension_specialist", "global_guide", "global_orchestrator", "lightweight_llm", "task_llm"],
                "agent_tools": ["mcp_client", "policy_integration", "tool_composition", "business_abstraction_helper"]
            }
            
            self.logger.info("✅ Agent-specific platform capabilities initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize agent platform capabilities: {e}")
            raise
    
    # ============================================================================
    # REQUIRED ABSTRACT METHODS (FoundationServiceBase)
    # ============================================================================
    
    # ============================================================================
    # AGENT FACTORY METHODS (NEW - Week 2 Enhancement)
    # ============================================================================
    
    async def _create_simple_llm_agent(self, agent_config: Dict[str, Any]) -> Any:
        """
        Create a Simple LLM Agent for stateless operations.
        
        This aligns with the LLM Business Abstraction pattern for stateless operations.
        Uses LightweightLLMAgent via factory pattern.
        """
        try:
            from foundations.agentic_foundation.agent_sdk.lightweight_llm_agent import LightweightLLMAgent
            
            return await self.create_agent(
                agent_class=LightweightLLMAgent,
                agent_name=agent_config.get("agent_name", "SimpleLLMAgent"),
                agent_type="lightweight_llm",
                realm_name=agent_config.get("realm_name", "agentic"),
                di_container=self.di_container,
                orchestrator=None,
                capabilities=agent_config.get("capabilities", ["text_generation", "content_analysis"]),
                required_roles=agent_config.get("required_roles", []),
                agui_schema=agent_config.get("agui_schema"),
                **agent_config.get("kwargs", {})
            )
        except Exception as e:
            self.logger.error(f"❌ Failed to create Simple LLM Agent: {e}")
            raise
    
    async def _create_tool_enabled_agent(self, agent_config: Dict[str, Any]) -> Any:
        """
        Create a Tool Enabled Agent for MCP tool integration.
        
        This agent can use real MCP tools for enhanced capabilities.
        Uses TaskLLMAgent via factory pattern (has MCP tool integration).
        """
        try:
            from foundations.agentic_foundation.agent_sdk.task_llm_agent import TaskLLMAgent
            
            return await self.create_agent(
                agent_class=TaskLLMAgent,
                agent_name=agent_config.get("agent_name", "ToolEnabledAgent"),
                agent_type="task_llm",
                realm_name=agent_config.get("realm_name", "agentic"),
                di_container=self.di_container,
                orchestrator=None,
                capabilities=agent_config.get("capabilities", ["tool_execution", "mcp_integration"]),
                required_roles=agent_config.get("required_roles", []),
                agui_schema=agent_config.get("agui_schema"),
                **agent_config.get("kwargs", {})
            )
        except Exception as e:
            self.logger.error(f"❌ Failed to create Tool Enabled Agent: {e}")
            raise
    
    async def _create_orchestration_agent(self, agent_config: Dict[str, Any]) -> Any:
        """
        Create an Orchestration Agent for SOA API integration.
        
        This agent can use real SOA APIs for platform orchestration.
        Uses GlobalOrchestratorAgent via factory pattern.
        """
        try:
            from foundations.agentic_foundation.agent_sdk.global_orchestrator_agent import GlobalOrchestratorAgent
            
            return await self.create_agent(
                agent_class=GlobalOrchestratorAgent,
                agent_name=agent_config.get("agent_name", "OrchestrationAgent"),
                agent_type="global_orchestrator",
                realm_name=agent_config.get("realm_name", "agentic"),
                di_container=self.di_container,
                orchestrator=None,
                capabilities=agent_config.get("capabilities", ["soa_orchestration", "platform_coordination"]),
                required_roles=agent_config.get("required_roles", []),
                agui_schema=agent_config.get("agui_schema"),
                **agent_config.get("kwargs", {})
            )
        except Exception as e:
            self.logger.error(f"❌ Failed to create Orchestration Agent: {e}")
            raise
    
    # ============================================================================
    # AGENT FACTORY (Unified Agent Creation)
    # ============================================================================
    
    async def create_agent(
        self,
        agent_class: type,
        agent_name: str,
        agent_type: str,  # "liaison", "specialist", "guide", etc.
        realm_name: str,
        di_container: Any,
        orchestrator: Optional[Any] = None,  # Optional orchestrator reference
        user_context: Dict[str, Any] = None,
        **kwargs
    ) -> Optional[Any]:
        """
        Create and initialize an agent using full Agentic SDK.
        
        This is the unified agent factory - all agents must use this.
        No backward compatibility - all agents must use full SDK.
        
        All LLM usage runs through SDK for proper governance and visibility.
        
        Args:
            agent_class: Agent class to instantiate
            agent_name: Unique name for the agent
            agent_type: Type of agent ("liaison", "specialist", "guide", etc.)
            realm_name: Realm name (e.g., "business_enablement")
            di_container: DI container for foundation services
            orchestrator: Optional orchestrator that owns this agent
            user_context: User context for security and tenant validation
            **kwargs: Additional agent-specific parameters (capabilities, required_roles, etc.)
        
        Returns:
            Initialized agent or None if creation failed
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("create_agent_start", success=True, 
                                                   details={"agent_name": agent_name, "agent_type": agent_type, "realm_name": realm_name})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_creation", "write"):
                        await self.record_health_metric("create_agent_access_denied", 1.0, {"agent_name": agent_name, "agent_type": agent_type})
                        await self.log_operation_with_telemetry("create_agent_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("create_agent_tenant_denied", 1.0, {"agent_name": agent_name, "agent_type": agent_type, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("create_agent_complete", success=False)
                            return None
            
            # Check if agent already exists
            if agent_name in self._agents:
                await self.record_health_metric("create_agent_cached", 1.0, {"agent_name": agent_name})
                await self.log_operation_with_telemetry("create_agent_complete", success=True, details={"agent_name": agent_name, "cached": True})
                self.logger.debug(f"✅ Agent {agent_name} already exists, returning cached instance")
                return self._agents[agent_name]
            
            self.logger.info(f"🏭 Creating agent: {agent_name} (type: {agent_type}, realm: {realm_name})")
            
            # Get all required dependencies
            public_works = di_container.get_foundation_service("PublicWorksFoundationService")
            if not public_works:
                self.logger.error("❌ Public Works Foundation not available")
                return None
            
            curator = di_container.get_foundation_service("CuratorFoundationService")
            if not curator:
                self.logger.warning("⚠️ Curator Foundation not available - agent won't be registered")
            
            # Get Agentic Foundation components
            # MCP Client Manager is optional (may not be available if MCP infrastructure not configured)
            mcp_client_manager = self.mcp_client_manager
            if not mcp_client_manager:
                self.logger.warning("⚠️ MCP Client Manager not initialized - agent will have limited MCP capabilities")
            
            # Policy Integration is required - instantiate from class
            if not self.policy_integration:
                self.logger.error("❌ Policy Integration class not available")
                return None
            policy_integration = self.policy_integration(di_container, self)
            
            # Tool Composition is required - instantiate from class
            if not self.tool_composition:
                self.logger.error("❌ Tool Composition class not available")
                return None
            tool_composition = self.tool_composition(di_container, self)
            
            # AGUI formatter is optional (may not be available if Post Office not initialized)
            agui_formatter = self.agui_formatter
            if not agui_formatter:
                self.logger.warning("⚠️ AGUI Formatter not available - agent will have limited UI capabilities")
            
            # Create AGUI schema (can be simplified for now)
            from foundations.agentic_foundation.agui_schema_registry import AGUISchema, AGUIComponent
            agui_schema = kwargs.get("agui_schema")
            if not agui_schema:
                # Create default AGUI schema with at least one component (required by validation)
                # Add a message_card component for liaison agents to enable communication
                default_components = [
                    AGUIComponent(
                        type="message_card",
                        title="Agent Communication",
                        description="Display agent messages and notifications",
                        required=True,
                        properties={
                            "message": "Default message property for agent communication"
                        }
                    )
                ]
                agui_schema = AGUISchema(
                    agent_name=agent_name,
                    version="1.0.0",
                    description=f"AGUI schema for {agent_name}",
                    components=default_components,
                    metadata={"created_by": "agent_factory"}
                )
            
            # Create agent with all dependencies
            # Note: DeclarativeAgentBase gets agent_name from config file, so don't pass it here
            # Filter out agent_name from kwargs to avoid conflicts
            filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ["capabilities", "required_roles", "agui_schema", "agent_name"]}
            
            # Check if this is a DeclarativeAgentBase (gets agent_name from config)
            # DeclarativeAgentBase is optional - only needed for legacy agents
            DeclarativeAgentBase = None
            try:
                from backend.business_enablement.agents.declarative_agent_base import DeclarativeAgentBase
            except ImportError:
                pass  # Not available, agents should use AgentBase instead
            is_declarative = DeclarativeAgentBase is not None and issubclass(agent_class, DeclarativeAgentBase)
            
            if is_declarative:
                # Declarative agents get agent_name from config file, don't pass it
                agent = agent_class(
                    foundation_services=di_container,
                    agentic_foundation=self,
                    mcp_client_manager=mcp_client_manager,  # May be None if MCP not configured
                    policy_integration=policy_integration,
                    tool_composition=tool_composition,
                    agui_formatter=agui_formatter,
                    curator_foundation=curator,
                    metadata_foundation=None,  # Can be added later if needed
                    public_works_foundation=public_works,
                    **filtered_kwargs
                )
            else:
                # Non-declarative agents need agent_name passed explicitly
                agent = agent_class(
                    agent_name=agent_name,
                    business_domain=realm_name,
                    capabilities=kwargs.get("capabilities", []),
                    required_roles=kwargs.get("required_roles", []),
                    agui_schema=agui_schema,
                    foundation_services=di_container,
                    agentic_foundation=self,
                    public_works_foundation=public_works,
                    mcp_client_manager=mcp_client_manager,  # May be None if MCP not configured
                    policy_integration=policy_integration,
                    tool_composition=tool_composition,
                    agui_formatter=agui_formatter,
                    curator_foundation=curator,
                    metadata_foundation=None,  # Can be added later if needed
                    **filtered_kwargs
                )
            
            # Validate capabilities are provided (fail fast)
            if not kwargs.get("capabilities"):
                error_msg = f"Agent {agent_name} created without capabilities - capabilities are required"
                self.logger.error(f"❌ {error_msg}")
                await self.record_health_metric("create_agent_missing_capabilities", 1.0, {"agent_name": agent_name})
                await self.log_operation_with_telemetry("create_agent_complete", success=False)
                raise ValueError(error_msg)
            
            # Initialize agent
            if hasattr(agent, 'initialize'):
                init_success = await agent.initialize()
                if not init_success:
                    self.logger.error(f"❌ Agent {agent_name} initialization returned False")
                    return None
            else:
                self.logger.warning(f"⚠️ Agent {agent_name} does not have initialize() method")
            
            # Track agent
            self._agents[agent_name] = agent
            
            # Register with Curator for service discovery
            if curator:
                await self._register_agent_with_curator(
                    agent=agent,
                    agent_name=agent_name,
                    agent_type=agent_type,
                    realm_name=realm_name,
                    orchestrator=orchestrator
                )
            
            # Record success metric
            await self.record_health_metric("create_agent_success", 1.0, {"agent_name": agent_name, "agent_type": agent_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_agent_complete", success=True, 
                                                   details={"agent_name": agent_name, "agent_type": agent_type})
            
            self.logger.info(f"✅ Agent {agent_name} created and initialized successfully")
            return agent
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "create_agent", 
                                              details={"agent_name": agent_name, "agent_type": agent_type, "realm_name": realm_name})
            self.logger.error(f"❌ Failed to create agent {agent_name}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def _register_agent_with_curator(
        self,
        agent: Any,
        agent_name: str,
        agent_type: str,
        realm_name: str,
        orchestrator: Optional[Any] = None
    ) -> bool:
        """
        Register agent with Curator using Phase 2 register_agent() pattern.
        
        Agentic Foundation owns agent registration (similar to Experience Foundation owning routes).
        Agents register their capabilities, specialization, and metadata - NOT MCP tools.
        
        Args:
            agent: Agent instance
            agent_name: Agent name
            agent_type: Agent type ("liaison", "specialist", "guide", etc.)
            realm_name: Realm name
            orchestrator: Optional orchestrator reference
        
        Returns:
            True if registration successful, False otherwise
        """
        try:
            curator = self.di_container.get_foundation_service("CuratorFoundationService")
            if not curator:
                self.logger.warning(f"⚠️ Curator not available - cannot register {agent_name}")
                return False
            
            # Extract agent capabilities (standardized pattern)
            capabilities = []
            if hasattr(agent, 'capabilities') and agent.capabilities:
                capabilities = agent.capabilities
            elif hasattr(agent, 'get_agent_capabilities'):
                try:
                    capabilities = await agent.get_agent_capabilities()
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to get capabilities from {agent_name}: {e}")
                    capabilities = []
            
            # If still empty, try specialization_config
            if not capabilities and hasattr(agent, 'specialization_config'):
                capabilities = agent.specialization_config.get("capabilities", [])
            
            # Validate capabilities were found
            if not capabilities:
                self.logger.error(f"❌ Agent {agent_name} has no capabilities - cannot register")
                return False
            
            # Extract specialization config
            specialization_config = {}
            if hasattr(agent, 'specialization_config') and agent.specialization_config:
                specialization_config = agent.specialization_config
            else:
                # Build from agent attributes if available
                specialization_config = {
                    "specialization": getattr(agent, 'specialization_name', None) or getattr(agent, 'specialization', None),
                    "required_roles": getattr(agent, 'required_roles', []),
                    "agui_schema": getattr(agent, 'agui_schema', {}).schema_name if hasattr(getattr(agent, 'agui_schema', None), 'schema_name') else None
                }
            
            # Build characteristics (agent metadata - what the agent IS)
            characteristics = {
                "capabilities": capabilities,  # What the agent CAN do
                "realm": realm_name,  # Which realm (cross-realm organizational unit)
                "specialization": specialization_config.get("specialization"),  # Optional user-driven customization
                "required_roles": specialization_config.get("required_roles", []),
                "agui_schema": specialization_config.get("agui_schema") or (agent.agui_schema.schema_name if hasattr(agent, 'agui_schema') and agent.agui_schema else None)
            }
            
            # Build contracts (agent API - how services can access the agent)
            # NOTE: Agents are Python objects, not REST services
            # Services access agents via direct Python method calls
            contracts = {
                "agent_api": {
                    "service_name": agent_name,
                    "realm": realm_name,
                    "agent_type": agent_type,
                    "orchestrator": orchestrator.service_name if orchestrator else None,
                    "agent_id": getattr(agent, 'agent_id', agent_name),
                    "access_pattern": "direct_python_method_calls",
                    "interface": "python_object"  # Not REST API
                }
                # NOTE: MCP tools are NOT registered here - agents USE MCP tools, they don't expose them
                # MCP servers expose tools, agents consume them via mcp_client_manager
            }
            
            # Register with Curator using Phase 2 pattern
            success = await curator.register_agent(
                agent_id=getattr(agent, 'agent_id', agent_name),
                agent_name=agent_name,
                characteristics=characteristics,
                contracts=contracts,
                user_context=None  # Internal registration (no user context)
            )
            
            if success:
                self.logger.info(f"   📝 Agent {agent_name} registered with Curator (Phase 2)")
                return True
            else:
                self.logger.warning(f"   ⚠️ Agent {agent_name} Curator registration failed")
                return False
        
        except Exception as e:
            self.logger.error(f"❌ Failed to register agent {agent_name} with Curator: {e}")
            import traceback
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def get_agent(self, agent_name: str, user_context: Dict[str, Any] = None) -> Optional[Any]:
        """Get an agent by name (wraps with utilities)."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_start", success=True, details={"agent_name": agent_name})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent", "read"):
                        await self.record_health_metric("get_agent_access_denied", 1.0, {"agent_name": agent_name})
                        await self.log_operation_with_telemetry("get_agent_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_agent_tenant_denied", 1.0, {"agent_name": agent_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_agent_complete", success=False)
                            return None
            
            # Get agent from cache
            agent = self._agents.get(agent_name)
            
            if agent:
                # Record success metric
                await self.record_health_metric("get_agent_success", 1.0, {"agent_name": agent_name, "found": True})
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_agent_complete", success=True, details={"agent_name": agent_name, "found": True})
            else:
                # Record not found metric
                await self.record_health_metric("get_agent_not_found", 1.0, {"agent_name": agent_name})
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_agent_complete", success=True, details={"agent_name": agent_name, "found": False})
            
            return agent
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent", details={"agent_name": agent_name})
            self.logger.error(f"❌ Failed to get agent {agent_name}: {e}")
            return None
    
    async def _get_agent_internal(self, agent_name: str, user_context: Dict[str, Any] = None) -> Optional[Any]:
        """
        Get an agent by name (from agent factory cache).
        
        Args:
            agent_name: Name of the agent
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Agent instance or None if not found
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_name, "read"):
                        await self.record_health_metric("get_agent_access_denied", 1.0, {"agent_name": agent_name})
                        await self.log_operation_with_telemetry("get_agent_complete", success=False)
                        return None
            
            agent = self._agents.get(agent_name)
            
            # Record success metric
            await self.record_health_metric("get_agent_success", 1.0, {"agent_name": agent_name, "found": agent is not None})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_complete", success=True)
            
            return agent
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent")
            self.logger.error(f"❌ Failed to get agent {agent_name}: {e}")
            return None
    
    async def list_agents(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        List all agents created by the factory.
        
        Args:
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Dictionary of agent_name -> agent_info
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("list_agents_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_list", "read"):
                        await self.record_health_metric("list_agents_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("list_agents_complete", success=False)
                        return {}
            
            # Tenant validation (multi-tenant support)
            tenant_context = self._extract_tenant_context(user_context)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("list_agents_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("list_agents_complete", success=False)
                            return {}
            
            result = {
                agent_name: {
                    "agent_name": agent_name,
                    "agent_type": getattr(agent, 'agent_type', 'unknown'),
                    "realm": getattr(agent, 'business_domain', 'unknown'),
                    "initialized": getattr(agent, 'is_initialized', False)
                }
                for agent_name, agent in self._agents.items()
            }
            
            # Record success metric
            await self.record_health_metric("list_agents_success", 1.0, {"agent_count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("list_agents_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "list_agents")
            self.logger.error(f"❌ Failed to list agents: {e}")
            return {}
    
    async def discover_agents_via_curator(
        self,
        agent_type: Optional[str] = None,
        realm_name: Optional[str] = None,
        orchestrator_name: Optional[str] = None,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Discover agents via Curator Foundation.
        
        This method queries Curator for all registered agents, allowing
        services to discover agents that were created by other orchestrators
        or services.
        
        Args:
            agent_type: Filter by agent type ("liaison", "specialist", "guide", etc.)
            realm_name: Filter by realm name
            orchestrator_name: Filter by orchestrator name
            user_context: User context for security and tenant validation
        
        Returns:
            Dictionary with total_agents and agents dict
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("discover_agents_via_curator_start", success=True, 
                                                   details={"agent_type": agent_type, "realm_name": realm_name})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_discovery", "read"):
                        await self.record_health_metric("discover_agents_via_curator_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("discover_agents_via_curator_complete", success=False)
                        return {"total_agents": 0, "agents": {}}
            
            if not self.curator_foundation:
                await self.record_health_metric("discover_agents_via_curator_curator_unavailable", 1.0, {})
                await self.log_operation_with_telemetry("discover_agents_via_curator_complete", success=True)
                self.logger.warning("⚠️ Curator Foundation not available for agent discovery")
                return {"total_agents": 0, "agents": {}}
            
            result = await self.curator_foundation.discover_agents(
                agent_type=agent_type,
                realm_name=realm_name,
                orchestrator_name=orchestrator_name
            )
            
            # Tenant validation (multi-tenant support)
            tenant_context = self._extract_tenant_context(user_context)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("discover_agents_via_curator_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("discover_agents_via_curator_complete", success=False)
                            return {"total_agents": 0, "agents": {}}
            
            # Record success metric
            await self.record_health_metric("discover_agents_via_curator_success", 1.0, {"total_agents": result.get("total_agents", 0)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("discover_agents_via_curator_complete", success=True, 
                                                   details={"total_agents": result.get("total_agents", 0)})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "discover_agents_via_curator", 
                                              details={"agent_type": agent_type, "realm_name": realm_name})
            self.logger.error(f"Failed to discover agents via Curator: {e}")
            return {"total_agents": 0, "agents": {}}
    
    async def get_agent_via_curator(self, agent_name: str, user_context: Dict[str, Any] = None) -> Optional[Any]:
        """
        Get an agent instance by name from Curator.
        
        This method queries Curator for the agent, allowing services to
        access agents that were created by other orchestrators.
        
        Args:
            agent_name: Name of the agent
            user_context: User context for security and tenant validation
        
        Returns:
            Agent instance or None if not found
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_via_curator_start", success=True, details={"agent_name": agent_name})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_access", "read"):
                        await self.record_health_metric("get_agent_via_curator_access_denied", 1.0, {"agent_name": agent_name})
                        await self.log_operation_with_telemetry("get_agent_via_curator_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            tenant_context = self._extract_tenant_context(user_context)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_agent_via_curator_tenant_denied", 1.0, {"agent_name": agent_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_agent_via_curator_complete", success=False)
                            return None
            
            # First check factory cache (fast path)
            cached_agent = await self.get_agent(agent_name)
            if cached_agent:
                await self.record_health_metric("get_agent_via_curator_cached", 1.0, {"agent_name": agent_name})
                await self.log_operation_with_telemetry("get_agent_via_curator_complete", success=True, details={"agent_name": agent_name, "cached": True})
                return cached_agent
            
            # Then check Curator (discovery path)
            if not self.curator_foundation:
                await self.record_health_metric("get_agent_via_curator_curator_unavailable", 1.0, {"agent_name": agent_name})
                await self.log_operation_with_telemetry("get_agent_via_curator_complete", success=True)
                self.logger.warning(f"⚠️ Curator Foundation not available for agent discovery: {agent_name}")
                return None
            
            result = await self.curator_foundation.get_agent(agent_name)
            
            # Record success metric
            await self.record_health_metric("get_agent_via_curator_success", 1.0, {"agent_name": agent_name, "found": result is not None})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_via_curator_complete", success=True, 
                                                   details={"agent_name": agent_name, "found": result is not None})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_via_curator", details={"agent_name": agent_name})
            self.logger.error(f"Failed to get agent via Curator {agent_name}: {e}")
            return None
    
    # ============================================================================
    # WEBSOCKET SDK (NEW - Phase 2)
    # ============================================================================
    
    async def create_agent_websocket_sdk(self) -> Any:
        """
        Create Agent WebSocket SDK using Communication Foundation.
        
        Returns:
            AgentWebSocketSDK instance
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("create_agent_websocket_sdk_start", success=True)
            
            # Get Experience Foundation (WebSocket is now in Experience Foundation SDK)
            experience_foundation = self.di_container.get_foundation_service("ExperienceFoundationService")
            if not experience_foundation:
                self.logger.error("❌ Experience Foundation not available")
                await self.log_operation_with_telemetry("create_agent_websocket_sdk_complete", success=False)
                return None
            
            # Get WebSocket SDK from Experience Foundation
            websocket_sdk = await experience_foundation.get_websocket_sdk()
            if not websocket_sdk:
                self.logger.error("❌ WebSocket SDK not available from Experience Foundation")
                await self.log_operation_with_telemetry("create_agent_websocket_sdk_complete", success=False)
                return None
            
            # Get WebSocket Foundation Service from SDK (for backward compatibility)
            websocket_foundation = websocket_sdk.websocket_foundation
            if not websocket_foundation:
                self.logger.error("❌ WebSocket Foundation Service not available from WebSocket SDK")
                await self.log_operation_with_telemetry("create_agent_websocket_sdk_complete", success=False)
                return None
            
            # Import and create Agent WebSocket SDK
            from foundations.agentic_foundation.agent_sdk.agent_websocket_sdk import AgentWebSocketSDK
            
            websocket_sdk = AgentWebSocketSDK(
                websocket_foundation=websocket_foundation,
                di_container=self.di_container
            )
            
            # Record success metric
            await self.record_health_metric("create_agent_websocket_sdk_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_agent_websocket_sdk_complete", success=True)
            
            self.logger.info("✅ Agent WebSocket SDK created successfully")
            return websocket_sdk
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "create_agent_websocket_sdk")
            self.logger.error(f"❌ Failed to create Agent WebSocket SDK: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    # ============================================================================
    
    async def shutdown(self):
        """Shutdown the Agentic Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("agentic_foundation_shutdown_start", success=True)
            
            # Shutdown agentic services
            if self.agent_dashboard_service and hasattr(self.agent_dashboard_service, 'shutdown'):
                await self.agent_dashboard_service.shutdown()
            
            if self.specialization_registry and hasattr(self.specialization_registry, 'shutdown'):
                await self.specialization_registry.shutdown()
            
            if self.agui_schema_registry and hasattr(self.agui_schema_registry, 'shutdown'):
                await self.agui_schema_registry.shutdown()
            
            # Shutdown agentic capabilities
            for capability_name, capability in self.agentic_capabilities.items():
                if hasattr(capability, 'shutdown'):
                    await capability.shutdown()
            
            # Shutdown all agents created by factory
            agents_shutdown = 0
            for agent_name, agent in self._agents.items():
                if hasattr(agent, 'shutdown'):
                    try:
                        await agent.shutdown()
                        agents_shutdown += 1
                        self.logger.info(f"   ✅ Agent {agent_name} shut down")
                    except Exception as e:
                        # Use enhanced error handling with audit for agent shutdown errors
                        await self.handle_error_with_audit(e, "shutdown_agent", details={"agent_name": agent_name})
                        self.logger.warning(f"   ⚠️ Error shutting down agent {agent_name}: {e}")
            
            self._agents.clear()
            
            # Record success metric
            await self.record_health_metric("agentic_foundation_shutdown_success", 1.0, {"agents_shutdown": agents_shutdown})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("agentic_foundation_shutdown_complete", success=True, 
                                                   details={"agents_shutdown": agents_shutdown})
            
            self.is_initialized = False
            
            # Record shutdown metric
            await self.record_health_metric("agentic_foundation_shutdown", 1.0, {"service": "agentic_foundation"})
            
            # Use enhanced logging with telemetry
            await self.log_operation_with_telemetry("agentic_foundation_shutdown_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "agentic_foundation_shutdown")
    