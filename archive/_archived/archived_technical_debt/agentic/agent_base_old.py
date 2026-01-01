"""
Agent Base - Core Agent Class

Base class for all policy-aware, Smart City-integrated agents with multi-tenancy support.
Provides unified governance, security, observability, and structured output capabilities.

WHAT (Agent): I provide intelligent agent capabilities with full foundation integration and multi-tenancy
HOW (Foundation Service): I inherit from FoundationServiceBase and integrate with all foundations
"""

import sys
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

# Using absolute imports from project root

from bases.foundation_service_base import FoundationServiceBase
from utilities import UserContext
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from backend.smart_city.protocols.multi_tenant_protocol import IMultiTenantProtocol
from .mcp_client_manager import MCPClientManager
from .policy_integration import PolicyIntegration
from .agui_output_formatter import AGUIOutputFormatter
from .tool_composition import ToolComposition
from agentic.agui_schema_registry import get_agui_schema_registry, AGUISchema, AGUIComponent

# Direct utility imports
from utilities import (
    ConfigurationUtility, SmartCityLoggingService, SmartCityErrorHandler,
    HealthManagementUtility, TelemetryReportingUtility, SecurityAuthorizationUtility
)


class AgentBase(FoundationServiceBase, IMultiTenantProtocol, ABC):
    """
    Base class for all policy-aware, Smart City-integrated agents with multi-tenancy support.
    
    Provides:
    - Multi-tenant awareness and isolation
    - Agentic business abstraction integration
    - Smart City role integration via MCP tools
    - Policy-aware tool execution
    - Security and governance integration
    - Structured AGUI output generation
    - Unified observability and monitoring
    - Direct utility consumption
    """
    
    def __init__(self, agent_name: str, capabilities: List[str], required_roles: List[str], 
                 agui_schema: AGUISchema, utility_foundation=None, curator_foundation=None, 
                 public_works_foundation: PublicWorksFoundationService = None,
                 metadata_foundation=None, expertise: str = None, specialization_config: Dict[str, Any] = None, **kwargs):
        """
        Initialize the agent with full foundation integration and multi-tenancy support.
        
        Args:
            agent_name: Unique name for the agent
            capabilities: List of agent capabilities
            required_roles: List of required Smart City roles
            agui_schema: AGUI output schema definition (REQUIRED)
            utility_foundation: Utility Foundation Service for logging, health, telemetry, security
            curator_foundation: Curator Foundation Service for capability registration
            public_works_foundation: Public Works Foundation Service for agentic business abstractions
            metadata_foundation: Metadata Foundation Service for data lineage
            expertise: Optional expertise domain (deprecated, use specialization_config)
            specialization_config: Specialization configuration dict
        """
        # Initialize Foundation Service Base FIRST
        super().__init__(agent_name, utility_foundation)
        
        # Agent-specific properties (agent_name is set by FoundationServiceBase as service_name)
        self.agent_name = agent_name  # Alias for compatibility
        self.capabilities = capabilities
        self.required_roles = required_roles
        self.agui_schema = agui_schema
        self.curator_foundation = curator_foundation
        self.public_works_foundation = public_works_foundation
        self.metadata_foundation = metadata_foundation
        
        # Multi-tenant awareness
        self.tenant_context = None
        self.tenant_isolation_enabled = True
        self.tenant_id = None
        self.tenant_user_id = None
        
        # Agentic business abstractions from public works
        self.agentic_abstractions = {}
        
        # Direct utility consumption
        self.config_utility = ConfigurationUtility("agent_base")
        self.logging_utility = SmartCityLoggingService("agent_base")
        self.error_utility = SmartCityErrorHandler("agent_base")
        self.health_utility = HealthManagementUtility("agent_base")
        self.telemetry_utility = TelemetryReportingUtility("agent_base")
        self.security_utility = SecurityAuthorizationUtility("agent_base")
        
        # Validate and register AGUI schema
        self._validate_and_register_agui_schema()
        
        # Handle specialization configuration
        if specialization_config:
            self.specialization_config = specialization_config
            self.expertise = specialization_config.get("id", expertise)
            self.specialization_name = specialization_config.get("name", "General")
            self.specialization_description = specialization_config.get("description", "")
            self.specialization_pillar = specialization_config.get("pillar", "general")
            self.specialization_capabilities = specialization_config.get("capabilities", [])
            self.system_prompt_template = specialization_config.get("system_prompt_template", "")
        else:
            # Backward compatibility
            self.specialization_config = None
            self.expertise = expertise
            self.specialization_name = "General"
            self.specialization_description = ""
            self.specialization_pillar = "general"
            self.specialization_capabilities = []
            self.system_prompt_template = ""
        
        self.agent_id = f"{agent_name}_{int(datetime.now().timestamp())}"
        
        # Initialize Smart City connections via MCP tools
        self.mcp_manager = MCPClientManager(public_works_foundation)
        self.policy_integration = PolicyIntegration()
        self.agui_formatter = AGUIOutputFormatter()
        self.tool_composition = ToolComposition()
        
        # Agent state
        self.session_id = None
        self.user_context = None
        
        # Connect to required roles via MCP tools
        self.role_connections = {}
        for role in required_roles:
            self.role_connections[role] = None
        
        self.logging_utility.info(f"🤖 Agent {agent_name} initialized with multi-tenancy support and roles: {required_roles}")
    
    def _validate_and_register_agui_schema(self):
        """Validate and register the AGUI schema for this agent."""
        try:
            # Get AGUI schema registry
            schema_registry = get_agui_schema_registry()
            
            # Validate schema
            validation_result = schema_registry.validate_schema(self.agui_schema)
            if not validation_result["valid"]:
                error_msg = f"AGUI schema validation failed for {self.agent_name}: {validation_result['errors']}"
                self.logging_utility.error(error_msg)
                raise ValueError(error_msg)
            
            # Register schema
            success = schema_registry.register_agent_schema(self.agent_name, self.agui_schema)
            if not success:
                self.logging_utility.warning(f"Failed to register AGUI schema for {self.agent_name}")
            else:
                self.logging_utility.info(f"AGUI schema registered for {self.agent_name}")
                
        except Exception as e:
            self.logging_utility.error(f"AGUI schema validation/registration failed for {self.agent_name}: {e}")
            raise
    
    async def initialize(self, session_id: str = None, user_context: UserContext = None, tenant_context: Dict[str, Any] = None):
        """Initialize the agent with session, user context, and tenant context."""
        try:
            # Initialize Foundation Service Base
            await super().initialize()
            
            # Set tenant context
            if tenant_context:
                await self.set_tenant_context(tenant_context)
            
            self.session_id = session_id or f"session_{int(datetime.now().timestamp())}"
            self.user_context = user_context
            
            # Load agentic business abstractions from public works
            if self.public_works_foundation:
                await self._load_agentic_abstractions()
            
            # Connect to required Smart City roles via MCP tools
            for role in self.required_roles:
                connection = await self.mcp_manager.connect_to_role(role, tenant_context)
                self.role_connections[role] = connection
                self.logging_utility.info(f"Connected to {role} role via MCP tools")
            
            # Initialize policy integration with tenant awareness
            await self.policy_integration.initialize(self.agent_id, self.required_roles, tenant_context)
            
            # Register with Curator Foundation if available
            if self.curator_foundation:
                await self.register_with_curator(user_context, tenant_context)
            
            # Register with Metadata Foundation if available
            if self.metadata_foundation:
                await self.register_with_metadata_foundation(user_context, tenant_context)
            
            self.logging_utility.info(f"🤖 Agent {self.agent_name} initialized successfully with multi-tenancy support")
            
        except Exception as e:
            self.logging_utility.error(f"Failed to initialize agent {self.agent_name}: {e}")
            await self.error_utility.handle_error(e)
            raise
    
    async def _load_agentic_abstractions(self):
        """Load agentic business abstractions from public works foundation."""
        try:
            if self.public_works_foundation:
                # Get agentic abstractions from public works
                self.agentic_abstractions = await self.public_works_foundation.get_agentic_abstractions()
                self.logging_utility.info(f"Loaded {len(self.agentic_abstractions)} agentic business abstractions")
            else:
                self.logging_utility.warning("Public works foundation not available - using limited abstractions")
        except Exception as e:
            self.logging_utility.error(f"Failed to load agentic abstractions: {e}")
            self.agentic_abstractions = {}
    
    # ============================================================================
    # MULTI-TENANT PROTOCOL IMPLEMENTATION
    # ============================================================================
    
    async def set_tenant_context(self, tenant_context: Dict[str, Any]) -> bool:
        """Set tenant context for multi-tenant operations."""
        try:
            if not tenant_context:
                return False
            
            self.tenant_context = tenant_context
            self.tenant_id = tenant_context.get("tenant_id")
            self.tenant_user_id = tenant_context.get("tenant_user_id")
            
            # Validate tenant context
            if not self.tenant_id:
                self.logging_utility.error("Tenant ID is required in tenant context")
                return False
            
            self.logging_utility.info(f"Tenant context set for tenant: {self.tenant_id}")
            return True
            
        except Exception as e:
            self.logging_utility.error(f"Failed to set tenant context: {e}")
            return False
    
    async def validate_tenant_access(self, resource: str, action: str) -> bool:
        """Validate tenant access to a resource."""
        try:
            if not self.tenant_isolation_enabled:
                return True
            
            if not self.tenant_context:
                self.logging_utility.error("No tenant context available for validation")
                return False
            
            # Use security utility for tenant validation
            validation_result = await self.security_utility.validate_tenant_access(
                tenant_id=self.tenant_id,
                tenant_user_id=self.tenant_user_id,
                resource=resource,
                action=action
            )
            
            return validation_result.get("authorized", False)
            
        except Exception as e:
            self.logging_utility.error(f"Failed to validate tenant access: {e}")
            return False
    
    async def get_tenant_info(self) -> Dict[str, Any]:
        """Get current tenant information."""
        return {
            "tenant_id": self.tenant_id,
            "tenant_user_id": self.tenant_user_id,
            "tenant_context": self.tenant_context,
            "isolation_enabled": self.tenant_isolation_enabled
        }
    
    # ============================================================================
    # AGENTIC BUSINESS ABSTRACTION OPERATIONS
    # ============================================================================
    
    async def coordinate_agents(self, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate agents using agentic business abstractions."""
        try:
            # Validate tenant access
            if not await self.validate_tenant_access("agent_coordination", "coordinate"):
                return {"error": "Tenant access denied for agent coordination"}
            
            # Get agentic business abstraction
            agentic_abstraction = self.agentic_abstractions.get("agent_coordination")
            if agentic_abstraction:
                return await agentic_abstraction.coordinate_agents(coordination_request)
            else:
                # Fallback behavior
                return await self._fallback_agent_coordination(coordination_request)
        except Exception as e:
            self.logging_utility.error(f"Error coordinating agents: {e}")
            return {"error": str(e)}
    
    async def manage_agent_workflow(self, workflow_request: Dict[str, Any]) -> Dict[str, Any]:
        """Manage agent workflow using agentic business abstractions."""
        try:
            # Validate tenant access
            if not await self.validate_tenant_access("agent_workflow", "manage"):
                return {"error": "Tenant access denied for agent workflow management"}
            
            # Get agentic business abstraction
            agentic_abstraction = self.agentic_abstractions.get("agent_workflow_management")
            if agentic_abstraction:
                return await agentic_abstraction.manage_agent_workflow(workflow_request)
            else:
                # Fallback behavior
                return await self._fallback_agent_workflow_management(workflow_request)
        except Exception as e:
            self.logging_utility.error(f"Error managing agent workflow: {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # SMART CITY ROLE INTERACTION VIA MCP TOOLS
    # ============================================================================
    
    async def interact_with_smart_city_role(self, role_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Interact with smart city role using MCP tools."""
        try:
            # Validate tenant access
            if not await self.validate_tenant_access(f"smart_city_role_{role_name}", "interact"):
                return {"error": f"Tenant access denied for {role_name} interaction"}
            
            # Use MCP tool to interact with smart city role
            mcp_tool = self.mcp_manager.get_mcp_tool(role_name)
            
            if mcp_tool:
                # Add tenant context to request
                request_with_tenant = {
                    **request,
                    "tenant_context": self.tenant_context
                }
                return await mcp_tool.execute(request_with_tenant)
            else:
                # Fallback behavior
                return await self._fallback_smart_city_interaction(role_name, request)
        except Exception as e:
            self.logging_utility.error(f"Error interacting with {role_name}: {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # FALLBACK METHODS
    # ============================================================================
    
    async def _fallback_agent_coordination(self, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback agent coordination when abstractions unavailable."""
        return {
            "coordinated": True,
            "coordination_id": f"fallback_{int(datetime.now().timestamp())}",
            "coordination_data": coordination_request,
            "coordinated_at": datetime.utcnow().isoformat(),
            "fallback": True
        }
    
    async def _fallback_agent_workflow_management(self, workflow_request: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback agent workflow management when abstractions unavailable."""
        return {
            "managed": True,
            "workflow_id": f"fallback_{int(datetime.now().timestamp())}",
            "workflow_data": workflow_request,
            "managed_at": datetime.utcnow().isoformat(),
            "fallback": True
        }
    
    async def _fallback_smart_city_interaction(self, role_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback smart city interaction when MCP tools unavailable."""
        return {
            "interacted": True,
            "role_name": role_name,
            "interaction_data": request,
            "interacted_at": datetime.utcnow().isoformat(),
            "fallback": True
        }
    
    # ============================================================================
    # ABSTRACTION ACCESS METHODS
    # ============================================================================
    
    def get_agentic_abstraction(self, abstraction_name: str) -> Any:
        """Get a specific agentic business abstraction."""
        return self.agentic_abstractions.get(abstraction_name)
    
    def has_agentic_abstraction(self, abstraction_name: str) -> bool:
        """Check if an agentic business abstraction is available."""
        return abstraction_name in self.agentic_abstractions
    
    def get_all_agentic_abstractions(self) -> Dict[str, Any]:
        """Get all available agentic business abstractions."""
        return self.agentic_abstractions.copy()
    
    def get_agentic_abstraction_names(self) -> List[str]:
        """Get names of all available agentic business abstractions."""
        return list(self.agentic_abstractions.keys())
    
    # ============================================================================
    # EXISTING METHODS (UPDATED FOR MULTI-TENANCY)
    # ============================================================================
    
    async def execute_with_governance(self, tool_chain: List[str], context: Dict[str, Any], 
                                    user_context: UserContext = None) -> Dict[str, Any]:
        """
        Execute tools with full Smart City governance and multi-tenant awareness.
        
        Args:
            tool_chain: List of tools to execute
            context: Execution context
            user_context: User context for security and audit
            
        Returns:
            Dict containing execution results with governance metadata
        """
        try:
            if not self.is_initialized:
                raise RuntimeError("Agent not initialized. Call initialize() first.")
            
            # Validate tenant access
            if not await self.validate_tenant_access("tool_execution", "execute"):
                return {"error": "Tenant access denied for tool execution"}
            
            # 1. Policy check via City Manager (via MCP tools)
            policy_result = await self.policy_integration.check_policies(
                agent_id=self.agent_id,
                tools=tool_chain,
                context=context,
                user_context=user_context or self.user_context,
                tenant_context=self.tenant_context
            )
            
            if not policy_result.get("approved", False):
                raise PermissionError(f"Policy violation: {policy_result.get('reason', 'Unknown')}")
            
            # 2. Security validation via Security Guard (via MCP tools)
            security_result = await self.policy_integration.validate_security(
                agent_id=self.agent_id,
                tools=tool_chain,
                user_context=user_context or self.user_context,
                tenant_context=self.tenant_context
            )
            
            if not security_result.get("valid", False):
                raise PermissionError(f"Security validation failed: {security_result.get('reason', 'Unknown')}")
            
            # 3. Execute tools with governance
            execution_result = await self.tool_composition.execute_tool_chain(
                tool_chain=tool_chain,
                context=context,
                user_context=user_context or self.user_context,
                tenant_context=self.tenant_context
            )
            
            # 4. Record telemetry
            await self.telemetry_utility.record_agent_execution(
                agent_id=self.agent_id,
                tools=tool_chain,
                result=execution_result,
                tenant_context=self.tenant_context
            )
            
            return {
                "success": True,
                "execution_result": execution_result,
                "governance_metadata": {
                    "policy_approved": True,
                    "security_validated": True,
                    "tenant_context": self.tenant_context
                }
            }
            
        except Exception as e:
            self.logging_utility.error(f"Tool execution failed: {e}")
            await self.error_utility.handle_error(e)
            return {"error": str(e), "success": False}
    
    async def register_with_curator(self, user_context: UserContext = None, tenant_context: Dict[str, Any] = None):
        """Register agent with Curator Foundation for capability management."""
        try:
            if not self.curator_foundation:
                return
            
            # Register agent capabilities with tenant context
            registration_data = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "capabilities": self.capabilities,
                "required_roles": self.required_roles,
                "specialization": self.specialization_name,
                "tenant_context": tenant_context
            }
            
            await self.curator_foundation.register_agent_capabilities(registration_data)
            self.logging_utility.info(f"Agent {self.agent_name} registered with Curator Foundation")
            
        except Exception as e:
            self.logging_utility.error(f"Failed to register with Curator Foundation: {e}")
    
    async def register_with_metadata_foundation(self, user_context: UserContext = None, tenant_context: Dict[str, Any] = None):
        """Register agent with Metadata Foundation for data lineage."""
        try:
            if not self.metadata_foundation:
                return
            
            # Register agent metadata with tenant context
            metadata = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "capabilities": self.capabilities,
                "specialization": self.specialization_name,
                "tenant_context": tenant_context
            }
            
            await self.metadata_foundation.register_agent_metadata(metadata)
            self.logging_utility.info(f"Agent {self.agent_name} registered with Metadata Foundation")
            
        except Exception as e:
            self.logging_utility.error(f"Failed to register with Metadata Foundation: {e}")
    
    # ============================================================================
    # SERVICE HEALTH AND STATUS
    # ============================================================================
    
    def get_agent_health(self) -> Dict[str, Any]:
        """Get agent health status with multi-tenant information."""
        return {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "is_initialized": self.is_initialized,
            "tenant_context": self.tenant_context,
            "agentic_abstractions_loaded": len(self.agentic_abstractions),
            "agentic_abstraction_names": self.get_agentic_abstraction_names(),
            "role_connections": list(self.role_connections.keys()),
            "status": "healthy" if self.is_initialized else "not_initialized"
        }
    
    # ============================================================================
    # ABSTRACT METHODS (TO BE IMPLEMENTED BY SUBCLASSES)
    # ============================================================================
    
    @abstractmethod
    async def execute_workflow_step(self, step_data: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """
        Execute a workflow step - to be implemented by subclasses.
        
        Args:
            step_data: Data for the workflow step
            user_context: User context for execution
            
        Returns:
            Dict containing step execution results
        """
        pass
    
    @abstractmethod
    async def generate_response(self, input_data: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """
        Generate agent response - to be implemented by subclasses.
        
        Args:
            input_data: Input data for response generation
            user_context: User context for generation
            
        Returns:
            Dict containing generated response
        """
        pass