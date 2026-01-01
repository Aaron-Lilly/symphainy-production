#!/usr/bin/env python3
"""
Agent Base - Core Agent Class (Refactored with Pure DI)

Base class for all policy-aware, Smart City-integrated agents with multi-tenancy support.
Provides unified governance, security, observability, and structured output capabilities.

WHAT (Agent): I provide intelligent agent capabilities with full foundation integration and multi-tenancy
HOW (Agent Base): I use pure dependency injection and integrate with all foundations
"""

import sys
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

# Import DIContainerService DI container
from foundations.di_container.di_container_service import DIContainerService

# Import required protocols and services
from utilities import UserContext
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.public_works_foundation.abstraction_contracts.tenant_protocol import TenantProtocol
from foundations.agentic_foundation.agui_schema_registry import get_agui_schema_registry, AGUISchema, AGUIComponent

# Import Agentic SDK components
from .mcp_client_manager import MCPClientManager
from .policy_integration import PolicyIntegration
from .agui_output_formatter import AGUIOutputFormatter
from .tool_composition import ToolComposition
from .business_abstraction_helper import BusinessAbstractionHelper


class AgentBase(ABC, TenantProtocol):
    """
    Base class for all policy-aware, Smart City-integrated agents with multi-tenancy support.
    
    Refactored to use pure dependency injection through DIContainerService.
    
    Provides:
    - Multi-tenant awareness and isolation
    - Agentic business abstraction integration
    - Smart City role integration via MCP tools
    - Policy-aware tool execution
    - Security and governance integration
    - Structured AGUI output generation
    - Unified observability and monitoring
    - Foundation service integration via dependency injection
    """
    
    def __init__(self, agent_name: str, capabilities: List[str], required_roles: List[str], 
                 agui_schema: AGUISchema, foundation_services: DIContainerService,
                 agentic_foundation: 'AgenticFoundationService',
                 mcp_client_manager: MCPClientManager,
                 policy_integration: PolicyIntegration,
                 tool_composition: ToolComposition,
                 agui_formatter: AGUIOutputFormatter,
                 curator_foundation=None, metadata_foundation=None, 
                 expertise: str = None, specialization_config: Dict[str, Any] = None, **kwargs):
        """
        Initialize the agent with pure dependency injection and multi-tenancy support.
        
        Args:
            agent_name: Unique name for the agent
            capabilities: List of agent capabilities
            required_roles: List of required Smart City roles
            agui_schema: AGUI output schema definition (REQUIRED)
            foundation_services: DIContainerService DI container
            agentic_foundation: Agentic Foundation Service for agentic capabilities and infrastructure enablement
            mcp_client_manager: MCP Client Manager for Smart City role connections
            policy_integration: Policy Integration for governance and security
            tool_composition: Tool Composition for tool chaining and orchestration
            agui_formatter: AGUI Output Formatter for structured outputs
            curator_foundation: Curator Foundation Service for capability registration
            metadata_foundation: Metadata Foundation Service for data lineage
            expertise: Optional expertise domain (deprecated, use specialization_config)
            specialization_config: Specialization configuration dict
        """
        # Store dependencies
        self.agent_name = agent_name
        self.foundation_services = foundation_services
        self.agentic_foundation = agentic_foundation
        self.mcp_client_manager = mcp_client_manager
        self.policy_integration = policy_integration
        self.tool_composition = tool_composition
        self.agui_formatter = agui_formatter
        self.curator_foundation = curator_foundation
        self.metadata_foundation = metadata_foundation
        
        # Get utilities from foundation services DI container
        self.logger = foundation_services.get_logger(agent_name)
        self.config = foundation_services.get_config()
        self.health = foundation_services.get_health()
        self.telemetry = foundation_services.get_telemetry()
        self.security = foundation_services.get_security()
        
        # Agent-specific properties
        self.capabilities = capabilities
        self.required_roles = required_roles
        self.agui_schema = agui_schema
        
        # Multi-tenant awareness
        self.tenant_context = None
        self.tenant_isolation_enabled = True
        self.tenant_id = None
        self.tenant_user_id = None
        
        # Agentic business abstractions from public works
        self.agentic_abstractions = {}
        
        # Business abstraction helper for convenient access
        self.business_helper = None
        
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
        
        # Agent state
        self.session_id = None
        self.user_context = None
        self.is_initialized = False
        
        # Connect to required roles via MCP tools
        self.role_connections = {}
        for role in required_roles:
            self.role_connections[role] = None
        
        self.logger.info(f"🤖 Agent {agent_name} initialized with pure DI and multi-tenancy support, roles: {required_roles}")
    
    def _validate_and_register_agui_schema(self):
        """
        Validate and register the AGUI schema for this agent.
        
        Note: Schema validation is deferred to async initialize() method since
        validate_schema is async and cannot be called from synchronous __init__.
        """
        # Defer validation to async initialize() - just mark that validation is needed
        self._agui_schema_validation_pending = True
    
    async def _validate_and_register_agui_schema_async(self):
        """Async validation and registration of AGUI schema (called from initialize())."""
        try:
            # Get AGUI schema registry (pass di_container to ensure it's initialized)
            schema_registry = get_agui_schema_registry(di_container=self.foundation_services)
            
            if schema_registry is None:
                self.logger.warning("AGUI schema registry not available - skipping validation and registration")
                return
            
            # Validate schema (async)
            validation_result = await schema_registry.validate_schema(self.agui_schema)
            if not validation_result["valid"]:
                # Handle both 'errors' and 'error' keys in validation result
                error_details = validation_result.get('errors', validation_result.get('error', 'Unknown validation error'))
                error_msg = f"AGUI schema validation failed for {self.agent_name}: {error_details}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Register schema (async)
            success = await schema_registry.register_agent_schema(self.agent_name, self.agui_schema)
            if not success:
                self.logger.warning(f"Failed to register AGUI schema for {self.agent_name}")
            else:
                self.logger.info(f"AGUI schema registered for {self.agent_name}")
                
        except Exception as e:
            self.logger.error(f"AGUI schema validation/registration failed for {self.agent_name}: {e}")
            raise
    
    async def initialize(self, session_id: str = None, user_context: UserContext = None, tenant_context: Dict[str, Any] = None):
        """Initialize the agent with session, user context, and tenant context."""
        try:
            self.logger.info(f"🚀 Initializing agent {self.agent_name}...")
            
            # Validate and register AGUI schema (async, deferred from __init__)
            if hasattr(self, '_agui_schema_validation_pending') and self._agui_schema_validation_pending:
                await self._validate_and_register_agui_schema_async()
                self._agui_schema_validation_pending = False
            
            # Set tenant context
            if tenant_context:
                await self.set_tenant_context(tenant_context)
            
            self.session_id = session_id or f"session_{int(datetime.now().timestamp())}"
            self.user_context = user_context
            
            # Load agentic business abstractions from agentic foundation
            if self.agentic_foundation:
                await self._load_agentic_abstractions()
                
                # Initialize business abstraction helper
                # BusinessAbstractionHelper needs public_works_foundation, get it from agentic_foundation or DI container
                public_works = None
                if hasattr(self.agentic_foundation, 'public_works_foundation'):
                    public_works = self.agentic_foundation.public_works_foundation
                elif self.foundation_services:
                    try:
                        public_works = self.foundation_services.get_foundation_service("PublicWorksFoundationService")
                    except:
                        pass
                
                if public_works:
                    self.business_helper = BusinessAbstractionHelper(
                        self.agent_name, 
                        public_works, 
                        self.logger
                    )
                else:
                    self.logger.warning("Public Works Foundation not available - business_helper will not be initialized")
            
            # Connect to required Smart City roles via MCP tools
            for role in self.required_roles:
                connection = await self.mcp_client_manager.connect_to_role(role, tenant_context)
                self.role_connections[role] = connection
                self.logger.info(f"Connected to {role} role via MCP tools")
            
            # Initialize policy integration with tenant awareness
            await self.policy_integration.initialize(self.agent_id, self.required_roles, tenant_context)
            
            # Registration handled by factory (Agentic Foundation owns agent registry)
            # Removed: await self.register_with_curator(user_context, tenant_context)
            
            # Register with Metadata Foundation if available
            if self.metadata_foundation:
                await self.register_with_metadata_foundation(user_context, tenant_context)
            
            self.is_initialized = True
            self.logger.info(f"✅ Agent {self.agent_name} initialized successfully with multi-tenancy support")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize agent {self.agent_name}: {e}")
            self.is_initialized = False
            raise
    
    async def _load_agentic_abstractions(self):
        """Load agentic business abstractions from public works foundation."""
        try:
            if self.agentic_foundation:
                # Try to get agentic abstractions if the method exists
                if hasattr(self.agentic_foundation, 'get_agentic_abstractions'):
                    self.agentic_abstractions = await self.agentic_foundation.get_agentic_abstractions()
                    self.logger.info(f"Loaded {len(self.agentic_abstractions)} agentic business abstractions")
                else:
                    # Method doesn't exist, use empty dict (abstractions will be loaded via business_helper)
                    self.agentic_abstractions = {}
                    self.logger.debug("get_agentic_abstractions() not available on AgenticFoundationService - using business_helper instead")
            else:
                self.logger.warning("Agentic foundation not available - using limited abstractions")
                self.agentic_abstractions = {}
        except Exception as e:
            self.logger.error(f"Failed to load agentic abstractions: {e}")
            self.agentic_abstractions = {}
    
    # ============================================================================
    # MULTI-TENANT PROTOCOL IMPLEMENTATION
    # ============================================================================
    
    async def set_tenant_context(self, tenant_context: Dict[str, Any]) -> bool:
        """Set tenant context for multi-tenant operations."""
        try:
            if not tenant_context:
                self.logger.warning("Empty tenant context provided")
                return False
            
            self.tenant_context = tenant_context
            self.tenant_id = tenant_context.get("tenant_id")
            self.tenant_user_id = tenant_context.get("user_id")
            
            # Set tenant context in all components
            if hasattr(self.mcp_client_manager, 'set_tenant_context'):
                await self.mcp_client_manager.set_tenant_context(tenant_context)
            
            if hasattr(self.policy_integration, 'set_tenant_context'):
                self.policy_integration.set_tenant_context(tenant_context)
            
            if hasattr(self.tool_composition, 'set_tenant_context'):
                self.tool_composition.set_tenant_context(tenant_context)
            
            if hasattr(self.agui_formatter, 'set_tenant_context'):
                await self.agui_formatter.set_tenant_context(tenant_context)
            
            self.logger.info(f"Tenant context set for agent {self.agent_name}: {self.tenant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set tenant context: {e}")
            return False
    
    async def get_tenant_context(self) -> Optional[Dict[str, Any]]:
        """Get current tenant context."""
        return self.tenant_context
    
    async def is_tenant_isolated(self) -> bool:
        """Check if tenant isolation is enabled."""
        return self.tenant_isolation_enabled
    
    # ============================================================================
    # TENANT PROTOCOL IMPLEMENTATION
    # ============================================================================
    
    async def get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant configuration using Agentic Foundation's infrastructure enablement."""
        try:
            if self.agentic_foundation:
                # Get tenant abstraction through agentic foundation's infrastructure enablement
                tenant_abstraction = await self.agentic_foundation.get_tenant_abstraction()
                if tenant_abstraction:
                    return await tenant_abstraction.get_tenant_config(tenant_id)
            
            # Fallback to local tenant context
            if self.tenant_context and self.tenant_id == tenant_id:
                return self.tenant_context
            
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get tenant config for {tenant_id}: {e}")
            return {}
    
    async def validate_tenant_access(self, user_tenant: str, resource_tenant: str) -> bool:
        """Validate tenant access using Agentic Foundation's infrastructure enablement."""
        try:
            if self.agentic_foundation:
                tenant_abstraction = await self.agentic_foundation.get_tenant_abstraction()
                if tenant_abstraction:
                    return await tenant_abstraction.validate_tenant_access(user_tenant, resource_tenant)
            
            # Fallback to simple tenant ID comparison
            return user_tenant == resource_tenant
        except Exception as e:
            self.logger.error(f"Failed to validate tenant access: {e}")
            return False
    
    async def get_tenant_features(self, tenant_id: str) -> List[str]:
        """Get tenant features using Public Works Foundation."""
        try:
            if self.agentic_foundation:
                tenant_abstraction = await self.agentic_foundation.get_tenant_abstraction()
                if tenant_abstraction:
                    return await tenant_abstraction.get_tenant_features(tenant_id)
            
            # Fallback to default features
            return ["agentic_capabilities", "multi_tenant_support"]
        except Exception as e:
            self.logger.error(f"Failed to get tenant features for {tenant_id}: {e}")
            return []
    
    async def is_feature_enabled(self, tenant_id: str, feature: str) -> bool:
        """Check if feature is enabled for tenant using Public Works Foundation."""
        try:
            if self.agentic_foundation:
                tenant_abstraction = await self.agentic_foundation.get_tenant_abstraction()
                if tenant_abstraction:
                    return await tenant_abstraction.is_feature_enabled(tenant_id, feature)
            
            # Fallback to checking tenant context
            if self.tenant_context and self.tenant_id == tenant_id:
                features = self.tenant_context.get("features", [])
                return feature in features
            
            return False
        except Exception as e:
            self.logger.error(f"Failed to check feature {feature} for tenant {tenant_id}: {e}")
            return False
    
    async def get_tenant_limits(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant limits using Public Works Foundation."""
        try:
            if self.agentic_foundation:
                tenant_abstraction = await self.agentic_foundation.get_tenant_abstraction()
                if tenant_abstraction:
                    return await tenant_abstraction.get_tenant_limits(tenant_id)
            
            # Fallback to default limits
            return {
                "max_agents": 10,
                "max_sessions": 100,
                "max_tools": 50
            }
        except Exception as e:
            self.logger.error(f"Failed to get tenant limits for {tenant_id}: {e}")
            return {}
    
    async def create_tenant_context(self, tenant_id: str, tenant_type: str, tenant_name: str) -> 'TenantContext':
        """Create tenant context using Public Works Foundation."""
        try:
            if self.agentic_foundation:
                tenant_abstraction = await self.agentic_foundation.get_tenant_abstraction()
                if tenant_abstraction:
                    return await tenant_abstraction.create_tenant_context(tenant_id, tenant_type, tenant_name)
            
            # Fallback to creating local tenant context
            from foundations.public_works_foundation.abstraction_contracts.tenant_protocol import TenantContext
            return TenantContext(
                tenant_id=tenant_id,
                tenant_name=tenant_name,
                tenant_type=tenant_type,
                max_users=100,
                features=["agentic_capabilities", "multi_tenant_support"],
                limits={"max_agents": 10, "max_sessions": 100}
            )
        except Exception as e:
            self.logger.error(f"Failed to create tenant context for {tenant_id}: {e}")
            # Return minimal tenant context
            from foundations.public_works_foundation.abstraction_contracts.tenant_protocol import TenantContext
            return TenantContext(
                tenant_id=tenant_id,
                tenant_name=tenant_name,
                tenant_type=tenant_type,
                max_users=10,
                features=[],
                limits={}
            )
    
    # ============================================================================
    # AGENTIC BUSINESS ABSTRACTION ACCESS
    # ============================================================================
    
    async def get_agentic_abstraction(self, abstraction_name: str) -> Optional[Any]:
        """Get a specific agentic business abstraction."""
        return self.agentic_abstractions.get(abstraction_name)
    
    async def list_agentic_abstractions(self) -> Dict[str, Any]:
        """List all available agentic business abstractions."""
        return self.agentic_abstractions.copy()
    
    # ============================================================================
    # ENHANCED PLATFORM CAPABILITIES ACCESS FOR AGENTS
    # ============================================================================
    
    async def get_enhanced_tool_discovery(self) -> Dict[str, Any]:
        """Get enhanced tool discovery capabilities for this agent."""
        try:
            if self.mcp_client_manager:
                return await self.mcp_client_manager.get_enhanced_tool_discovery()
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get enhanced tool discovery: {e}")
            return {}
    
    async def get_enhanced_security_capabilities(self) -> Dict[str, Any]:
        """Get enhanced security capabilities for this agent."""
        try:
            if self.mcp_client_manager:
                return await self.mcp_client_manager.get_enhanced_security_capabilities()
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get enhanced security capabilities: {e}")
            return {}
    
    async def get_enhanced_utility_capabilities(self) -> Dict[str, Any]:
        """Get enhanced utility capabilities for this agent."""
        try:
            if self.mcp_client_manager:
                return await self.mcp_client_manager.get_enhanced_utility_capabilities()
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get enhanced utility capabilities: {e}")
            return {}
    
    async def get_enhanced_security_policies(self) -> Dict[str, Any]:
        """Get enhanced security policies for this agent."""
        try:
            if self.policy_integration:
                return await self.policy_integration.get_enhanced_security_policies()
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get enhanced security policies: {e}")
            return {}
    
    async def apply_enhanced_security_policies(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply enhanced security policies for this agent's action."""
        try:
            if self.policy_integration:
                return await self.policy_integration.apply_enhanced_security_policies(self.agent_id, action, context)
            return {"success": False, "error": "Policy integration not available"}
        except Exception as e:
            self.logger.error(f"Failed to apply enhanced security policies: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_enhanced_tool_capabilities(self) -> Dict[str, Any]:
        """Get enhanced tool capabilities for this agent."""
        try:
            if self.tool_composition:
                return await self.tool_composition.get_enhanced_tool_capabilities()
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get enhanced tool capabilities: {e}")
            return {}
    
    async def discover_agent_tools(self, agent_type: str = None) -> List[str]:
        """Discover tools available for this agent type."""
        try:
            if self.tool_composition:
                if agent_type is None:
                    agent_type = self.__class__.__name__.lower().replace('agent', '')
                return await self.tool_composition.discover_agent_tools(agent_type)
            return []
        except Exception as e:
            self.logger.error(f"Failed to discover agent tools: {e}")
            return []
    
    async def get_tool_execution_capabilities(self) -> Dict[str, Any]:
        """Get tool execution capabilities for this agent."""
        try:
            if self.tool_composition:
                return await self.tool_composition.get_tool_execution_capabilities()
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get tool execution capabilities: {e}")
            return {}
    
    async def get_all_enhanced_capabilities(self) -> Dict[str, Any]:
        """Get all enhanced platform capabilities for this agent."""
        try:
            return {
                "tool_discovery": await self.get_enhanced_tool_discovery(),
                "security_capabilities": await self.get_enhanced_security_capabilities(),
                "utility_capabilities": await self.get_enhanced_utility_capabilities(),
                "security_policies": await self.get_enhanced_security_policies(),
                "tool_capabilities": await self.get_enhanced_tool_capabilities(),
                "tool_execution": await self.get_tool_execution_capabilities(),
                "agent_type": self.__class__.__name__,
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get all enhanced capabilities: {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # BUSINESS ABSTRACTION CONVENIENCE METHODS
    # ============================================================================
    
    async def get_business_abstraction(self, abstraction_name: str) -> Optional[Any]:
        """Get a business abstraction using the helper."""
        if self.business_helper:
            return await self.business_helper.get_abstraction(abstraction_name)
        return await self.get_agentic_abstraction(abstraction_name)
    
    async def list_available_business_abstractions(self) -> Dict[str, str]:
        """List all available business abstractions with descriptions."""
        if self.business_helper:
            return await self.business_helper.list_available_abstractions()
        return {}
    
    # MVP Business Abstraction convenience methods
    async def process_cobol_data(self, copybook_content: str, **kwargs) -> Dict[str, Any]:
        """Process COBOL data using the COBOL processing abstraction."""
        if self.business_helper:
            return await self.business_helper.process_cobol_data(copybook_content, **kwargs)
        return {"success": False, "error": "Business helper not available"}
    
    async def create_sop(self, sop_content: str, **kwargs) -> Dict[str, Any]:
        """Create SOP using the SOP processing abstraction."""
        if self.business_helper:
            return await self.business_helper.create_sop(sop_content, **kwargs)
        return {"success": False, "error": "Business helper not available"}
    
    async def generate_poc_proposal(self, business_context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate POC proposal using the POC generation abstraction."""
        if self.business_helper:
            return await self.business_helper.generate_poc_proposal(business_context, **kwargs)
        return {"success": False, "error": "Business helper not available"}
    
    async def create_roadmap(self, project_context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create roadmap using the roadmap generation abstraction."""
        if self.business_helper:
            return await self.business_helper.create_roadmap(project_context, **kwargs)
        return {"success": False, "error": "Business helper not available"}
    
    async def evaluate_coexistence(self, process_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Evaluate human-AI coexistence using the coexistence evaluation abstraction."""
        if self.business_helper:
            return await self.business_helper.evaluate_coexistence(process_data, **kwargs)
        return {"success": False, "error": "Business helper not available"}
    
    async def check_business_abstraction_health(self) -> Dict[str, Any]:
        """Check health of all business abstractions."""
        if self.business_helper:
            return await self.business_helper.health_check_abstractions()
        return {"error": "Business helper not available"}
    
    def get_business_abstraction_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for business abstractions."""
        if self.business_helper:
            return self.business_helper.get_usage_statistics()
        return {"error": "Business helper not available"}
    
    # ============================================================================
    # LLM CAPABILITIES (via Business Abstraction Helper)
    # ============================================================================
    
    async def interpret_analysis_results(self, results: Dict[str, Any], context: str, 
                                       expertise: str = None) -> Dict[str, Any]:
        """Interpret analysis results using LLM."""
        if self.business_helper:
            return await self.business_helper.interpret_analysis_results(
                results=results,
                context=context,
                expertise=expertise
            )
        return {"success": False, "error": "Business helper not available"}
    
    async def guide_user_with_llm(self, user_input: str, available_tools: List[str], 
                                 context: str, expertise: str = None) -> Dict[str, Any]:
        """Guide user using LLM."""
        if self.business_helper:
            return await self.business_helper.guide_user_with_llm(
                user_input=user_input,
                available_tools=available_tools,
                context=context,
                expertise=expertise
            )
        return {"success": False, "error": "Business helper not available"}
    
    async def generate_llm_response(self, prompt: str, agent_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response using LLM."""
        if self.business_helper:
            return await self.business_helper.generate_agent_response(
                prompt=prompt,
                agent_context=agent_context
            )
        return {"success": False, "error": "Business helper not available"}
    
    # ============================================================================
    # SMART CITY ROLE INTEGRATION
    # ============================================================================
    
    async def get_role_connection(self, role_name: str) -> Optional[Any]:
        """Get connection to a specific Smart City role."""
        return self.role_connections.get(role_name)
    
    async def execute_role_tool(self, role_name: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on a specific Smart City role."""
        try:
            connection = await self.get_role_connection(role_name)
            if not connection:
                return {"status": "error", "message": f"No connection to {role_name}"}
            
            # Use MCP client manager to execute tool
            result = await self.mcp_client_manager.execute_tool(role_name, tool_name, parameters, self.tenant_context)
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute tool {tool_name} on {role_name}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_nurse_api(self) -> Optional[Any]:
        """
        Get Nurse service API for observability tracking (Phase 2.3).
        
        Agents can use Nurse to record agent executions for observability.
        
        Returns:
            Nurse service instance or None if not available
        """
        try:
            # Try to get Nurse via Curator Foundation
            if self.curator_foundation:
                # Get service from Curator's registered services
                # Nurse service is registered as "NurseService" or "nurse"
                service_variants = ["NurseService", "nurse", "Nurse"]
                
                for variant in service_variants:
                    try:
                        # Check if service is registered
                        if hasattr(self.curator_foundation, 'registered_services'):
                            services = self.curator_foundation.registered_services
                            if isinstance(services, dict):
                                # Try different key formats
                                for key in [variant, variant.lower(), f"{variant}Service"]:
                                    if key in services:
                                        service_info = services[key]
                                        if isinstance(service_info, dict) and "service_instance" in service_info:
                                            return service_info["service_instance"]
                                        elif hasattr(service_info, "service_instance"):
                                            return service_info.service_instance
                        
                        # Try get_service method if available
                        if hasattr(self.curator_foundation, 'get_service'):
                            service = await self.curator_foundation.get_service(variant)
                            if service:
                                return service
                    except Exception as e:
                        self.logger.debug(f"Failed to get Nurse via variant {variant}: {e}")
                        continue
            
            # Fallback: Try to get via foundation_services DI container
            if self.foundation_services:
                try:
                    # Try to get Nurse service from DI container
                    if hasattr(self.foundation_services, 'get_foundation_service'):
                        nurse = self.foundation_services.get_foundation_service("NurseService")
                        if nurse:
                            return nurse
                except Exception as e:
                    self.logger.debug(f"Failed to get Nurse from DI container: {e}")
            
            self.logger.debug("Nurse service not available for observability tracking")
            return None
            
        except Exception as e:
            self.logger.debug(f"Failed to get Nurse API: {e}")
            return None
    
    # ============================================================================
    # AGENTIC CORRELATION PATTERN (Platform Data Sidecar for Agents)
    # ============================================================================
    
    async def get_security_guard_api(self) -> Optional[Any]:
        """Get Security Guard API via MCP."""
        if not hasattr(self, '_security_guard'):
            # Try via MCP client manager
            if self.mcp_client_manager:
                try:
                    self._security_guard = await self.mcp_client_manager.connect_to_role("security_guard")
                except Exception as e:
                    self.logger.debug(f"Failed to connect to security_guard: {e}")
                    self._security_guard = None
        return getattr(self, '_security_guard', None)
    
    async def get_traffic_cop_api(self) -> Optional[Any]:
        """Get Traffic Cop API via MCP."""
        if not hasattr(self, '_traffic_cop'):
            if self.mcp_client_manager:
                try:
                    self._traffic_cop = await self.mcp_client_manager.connect_to_role("traffic_cop")
                except Exception as e:
                    self.logger.debug(f"Failed to connect to traffic_cop: {e}")
                    self._traffic_cop = None
        return getattr(self, '_traffic_cop', None)
    
    async def get_conductor_api(self) -> Optional[Any]:
        """Get Conductor API via MCP."""
        if not hasattr(self, '_conductor'):
            if self.mcp_client_manager:
                try:
                    self._conductor = await self.mcp_client_manager.connect_to_role("conductor")
                except Exception as e:
                    self.logger.debug(f"Failed to connect to conductor: {e}")
                    self._conductor = None
        return getattr(self, '_conductor', None)
    
    async def get_post_office_api(self) -> Optional[Any]:
        """Get Post Office API via MCP."""
        if not hasattr(self, '_post_office'):
            if self.mcp_client_manager:
                try:
                    self._post_office = await self.mcp_client_manager.connect_to_role("post_office")
                except Exception as e:
                    self.logger.debug(f"Failed to connect to post_office: {e}")
                    self._post_office = None
        return getattr(self, '_post_office', None)
    
    async def _orchestrate_agentic_correlation(
        self,
        operation: str,
        correlation_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate agentic correlation data to follow agent execution.
        
        "One Stop Shopping" for all agentic correlation:
        - Security Guard: Validate auth & tenant (if needed)
        - Traffic Cop: Manage agent session/state (if stateful)
        - Conductor: Track agent workflow steps
        - Post Office: Publish agent events
        - Nurse: Record agent execution (prompts, LLM calls, tool usage, costs, performance)
        
        Args:
            operation: Operation name (e.g., "agent_execute", "llm_call", "tool_execute")
            correlation_data: Agent-specific correlation data:
                - For "agent_execute": {prompt, response, model_name, tokens, latency, cost}
                - For "llm_call": {prompt, response, model_name, tokens, latency, cost}
                - For "tool_execute": {tool_name, parameters, result, latency}
            user_context: Optional user context
        
        Returns:
            Enhanced correlation context with all agentic correlation data
        """
        import uuid
        from datetime import datetime
        
        # Get workflow_id (generate if not present)
        workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
        agent_execution_id = f"{self.agent_name}_{int(datetime.now().timestamp())}"
        
        # Discover platform correlation services (lazy-load)
        if not hasattr(self, '_security_guard') or self._security_guard is None:
            self._security_guard = await self.get_security_guard_api()
        if not hasattr(self, '_traffic_cop') or self._traffic_cop is None:
            self._traffic_cop = await self.get_traffic_cop_api()
        if not hasattr(self, '_conductor') or self._conductor is None:
            self._conductor = await self.get_conductor_api()
        if not hasattr(self, '_post_office') or self._post_office is None:
            self._post_office = await self.get_post_office_api()
        if not hasattr(self, '_nurse') or self._nurse is None:
            self._nurse = await self.get_nurse_api()
        
        # Build correlation context
        correlation_context = user_context.copy() if user_context else {}
        correlation_context["workflow_id"] = workflow_id
        correlation_context["agent_execution_id"] = agent_execution_id
        correlation_context["agent_name"] = self.agent_name
        correlation_context["agent_id"] = self.agent_id
        
        # 1. Security Guard: Validate auth & tenant (if needed)
        if self._security_guard and correlation_context.get("user_id"):
            try:
                if correlation_context.get("session_id"):
                    auth_result = await self._security_guard.validate_session(
                        session_token=correlation_context.get("session_id"),
                        user_context=correlation_context
                    )
                    if auth_result and auth_result.get("valid"):
                        correlation_context["auth_validated"] = True
                        correlation_context["tenant_id"] = auth_result.get("tenant_id")
            except Exception as e:
                self.logger.warning(f"⚠️ Auth validation failed: {e}")
        
        # 2. Traffic Cop: Manage agent session/state (if stateful)
        if self._traffic_cop and correlation_context.get("session_id") and self.is_stateful():
            try:
                session_state = await self._traffic_cop.get_session_state(
                    session_id=correlation_context.get("session_id"),
                    workflow_id=workflow_id
                )
                if session_state:
                    correlation_context["session_state"] = session_state
            except Exception as e:
                self.logger.warning(f"⚠️ Session management failed: {e}")
        
        # 3. Conductor: Track agent workflow steps
        if self._conductor:
            try:
                workflow_status = await self._conductor.track_workflow_step(
                    workflow_id=workflow_id,
                    step_name=f"agent.{self.agent_name}.{operation}",
                    status="in_progress",
                    user_context=correlation_context
                )
                if workflow_status:
                    correlation_context["workflow_tracked"] = True
            except Exception as e:
                self.logger.warning(f"⚠️ Workflow tracking failed: {e}")
        
        # 4. Post Office: Publish agent operation start event
        if self._post_office:
            try:
                await self._post_office.publish_event(
                    event_type=f"agent.{self.agent_name}.{operation}.start",
                    event_data={
                        "operation": operation,
                        "agent_name": self.agent_name,
                        "agent_id": self.agent_id,
                        "workflow_id": workflow_id,
                        "agent_execution_id": agent_execution_id,
                        **correlation_data
                    },
                    workflow_id=workflow_id,
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Event publishing failed: {e}")
        
        # 5. Nurse: Record agent execution (prompts, LLM calls, tool usage, costs, performance)
        if self._nurse:
            try:
                # Calculate prompt hash
                prompt_hash = self._calculate_prompt_hash(correlation_data.get("prompt", ""))
                
                # Record agent execution
                await self._nurse.record_agent_execution(
                    agent_id=self.agent_id,
                    agent_name=self.agent_name,
                    prompt_hash=prompt_hash,
                    response=correlation_data.get("response", ""),
                    trace_id=workflow_id,
                    execution_metadata={
                        "operation": operation,
                        "model_name": correlation_data.get("model_name"),
                        "tokens": correlation_data.get("tokens"),
                        "latency_ms": correlation_data.get("latency_ms"),
                        "cost": correlation_data.get("cost"),
                        "tool_calls": correlation_data.get("tool_calls", []),
                        "tool_results": correlation_data.get("tool_results", []),
                        "agent_execution_id": agent_execution_id
                    },
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Agent execution tracking failed: {e}")
        
        return correlation_context
    
    async def _record_agentic_correlation_completion(
        self,
        operation: str,
        result: Dict[str, Any],
        correlation_context: Dict[str, Any]
    ):
        """Record agentic correlation completion for operation."""
        workflow_id = correlation_context.get("workflow_id")
        
        # Conductor: Mark workflow step complete
        if hasattr(self, '_conductor') and self._conductor and workflow_id:
            try:
                await self._conductor.track_workflow_step(
                    workflow_id=workflow_id,
                    step_name=f"agent.{self.agent_name}.{operation}",
                    status="completed" if result.get("success") else "failed",
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Workflow completion tracking failed: {e}")
        
        # Post Office: Publish operation complete event
        if hasattr(self, '_post_office') and self._post_office and workflow_id:
            try:
                await self._post_office.publish_event(
                    event_type=f"agent.{self.agent_name}.{operation}.complete",
                    event_data={
                        "operation": operation,
                        "agent_name": self.agent_name,
                        "success": result.get("success", False),
                        "workflow_id": workflow_id,
                        "agent_execution_id": correlation_context.get("agent_execution_id")
                    },
                    workflow_id=workflow_id,
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Event publishing failed: {e}")
        
        # Nurse: Record completion telemetry
        if hasattr(self, '_nurse') and self._nurse and workflow_id:
            try:
                await self._nurse.record_platform_event(
                    event_type="metric",
                    event_data={
                        "metric_name": f"agent.{self.agent_name}.{operation}.duration",
                        "value": result.get("duration_ms", 0),
                        "service_name": self.agent_name
                    },
                    trace_id=workflow_id,
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Telemetry recording failed: {e}")
    
    def _calculate_prompt_hash(self, prompt: str) -> str:
        """Calculate hash of prompt for tracking."""
        import hashlib
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]
    
    def is_stateful(self) -> bool:
        """Check if agent is stateful (has conversation history)."""
        # Check if agent has stateful configuration
        return hasattr(self, 'conversation_history') and self.conversation_history is not None
    
    # ============================================================================
    # AGENTIC CORRELATION WRAPPER METHODS (For Subclasses)
    # ============================================================================
    
    async def _call_llm_with_tracking(
        self,
        prompt: str,
        llm_call_func,
        model_name: str = None,
        user_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call LLM with automatic agentic correlation tracking.
        
        Subclasses should use this method instead of calling LLM directly.
        
        Args:
            prompt: Prompt to send to LLM
            llm_call_func: Function to call LLM (async function that returns LLM response)
            model_name: Optional model name
            user_context: Optional user context
            **kwargs: Additional arguments for LLM call
            
        Returns:
            LLM response with tracking metadata
        """
        from datetime import datetime
        start_time = datetime.now()
        
        try:
            # Orchestrate agentic correlation (LLM call start)
            correlation_context = await self._orchestrate_agentic_correlation(
                operation="llm_call",
                correlation_data={
                    "prompt": prompt,
                    "model_name": model_name or "unknown"
                },
                user_context=user_context
            )
            
            # Call LLM (existing logic via provided function)
            response = await llm_call_func(prompt, **kwargs)
            
            # Calculate LLM metadata
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            # Extract token usage and cost from response
            tokens = response.get("tokens", {}) if isinstance(response, dict) else {}
            cost = response.get("cost", 0) if isinstance(response, dict) else 0
            response_text = response.get("text", "") if isinstance(response, dict) else str(response)
            
            # Record completion with LLM-specific data
            await self._record_agentic_correlation_completion(
                operation="llm_call",
                result={
                    "success": True,
                    "response": response_text,
                    "tokens": tokens,
                    "cost": cost,
                    "duration_ms": duration_ms,
                    "model_name": model_name
                },
                correlation_context=correlation_context
            )
            
            # Add tracking metadata to response
            if isinstance(response, dict):
                response["_agentic_tracking"] = {
                    "agent_execution_id": correlation_context.get("agent_execution_id"),
                    "workflow_id": correlation_context.get("workflow_id"),
                    "duration_ms": duration_ms,
                    "tracked": True
                }
            
            return response
            
        except Exception as e:
            # Record failure
            correlation_context = correlation_context if 'correlation_context' in locals() else {}
            await self._record_agentic_correlation_completion(
                operation="llm_call",
                result={"success": False, "error": str(e)},
                correlation_context=correlation_context
            )
            raise
    
    async def _call_llm_simple(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: Optional[Any] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        user_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Simple LLM call helper for agents.
        
        Wraps LLMRequest/LLMResponse pattern into a simple interface.
        Uses _call_llm_with_tracking for agentic correlation.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            model: Optional model (LLMModel enum or string, defaults to GPT_4O_MINI)
            max_tokens: Optional max tokens
            temperature: Optional temperature
            user_context: Optional user context
            metadata: Optional metadata
        
        Returns:
            Response text (str)
        """
        from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
        
        # Get LLM abstraction
        llm_abstraction = await self.get_business_abstraction("llm")
        if not llm_abstraction:
            raise ValueError("LLM abstraction not available")
        
        # Resolve model
        if model is None:
            llm_model = LLMModel.GPT_4O_MINI
        elif isinstance(model, str):
            # Try to find matching LLMModel enum value
            try:
                llm_model = LLMModel(model)
            except ValueError:
                # Default to GPT_4O_MINI if model string not found
                self.logger.warning(f"⚠️ Unknown model '{model}', defaulting to GPT_4O_MINI")
                llm_model = LLMModel.GPT_4O_MINI
        elif isinstance(model, LLMModel):
            llm_model = model
        else:
            llm_model = LLMModel.GPT_4O_MINI
        
        # Build messages
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        # Create LLM request
        request = LLMRequest(
            messages=messages,
            model=llm_model,
            max_tokens=max_tokens,
            temperature=temperature,
            metadata=metadata or {}
        )
        
        # Call LLM with tracking
        async def _call_llm_func(prompt_text, **kwargs):
            response = await llm_abstraction.generate_response(request)
            
            # Extract usage info
            usage = response.usage if hasattr(response, 'usage') else {}
            tokens = usage.get("total_tokens", 0) if isinstance(usage, dict) else 0
            
            # Estimate cost (rough estimate: $0.00001 per token for GPT-4O-MINI)
            cost = tokens * 0.00001 if tokens > 0 else 0
            
            return {
                "text": response.content,
                "response": response.content,
                "tokens": {
                    "total_tokens": tokens,
                    "prompt_tokens": usage.get("prompt_tokens", 0) if isinstance(usage, dict) else 0,
                    "completion_tokens": usage.get("completion_tokens", 0) if isinstance(usage, dict) else 0
                },
                "cost": cost
            }
        
        result = await self._call_llm_with_tracking(
            prompt=prompt,
            llm_call_func=_call_llm_func,
            model_name=llm_model.value,
            user_context=user_context
        )
        
        # Extract response text
        if isinstance(result, dict):
            return result.get("text", result.get("response", ""))
        elif hasattr(result, 'content'):
            return result.content
        else:
            return str(result)
    
    async def _execute_tool_with_tracking(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        tool_exec_func,
        user_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute tool with automatic agentic correlation tracking.
        
        Subclasses should use this method instead of calling tools directly.
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            tool_exec_func: Function to execute tool (async function that returns tool result)
            user_context: Optional user context
            **kwargs: Additional arguments for tool execution
            
        Returns:
            Tool result with tracking metadata
        """
        from datetime import datetime
        start_time = datetime.now()
        
        try:
            # Orchestrate agentic correlation (tool execution start)
            correlation_context = await self._orchestrate_agentic_correlation(
                operation="tool_execute",
                correlation_data={
                    "tool_name": tool_name,
                    "parameters": parameters
                },
                user_context=user_context
            )
            
            # Execute tool (existing logic via provided function)
            result = await tool_exec_func(tool_name, parameters, **kwargs)
            
            # Calculate tool metadata
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            # Record completion
            await self._record_agentic_correlation_completion(
                operation="tool_execute",
                result={
                    "success": result.get("success", True) if isinstance(result, dict) else True,
                    "tool_name": tool_name,
                    "result": result,
                    "duration_ms": duration_ms
                },
                correlation_context=correlation_context
            )
            
            # Add tracking metadata to result
            if isinstance(result, dict):
                result["_agentic_tracking"] = {
                    "agent_execution_id": correlation_context.get("agent_execution_id"),
                    "workflow_id": correlation_context.get("workflow_id"),
                    "duration_ms": duration_ms,
                    "tracked": True
                }
            
            return result
            
        except Exception as e:
            # Record failure
            correlation_context = correlation_context if 'correlation_context' in locals() else {}
            await self._record_agentic_correlation_completion(
                operation="tool_execute",
                result={"success": False, "error": str(e), "tool_name": tool_name},
                correlation_context=correlation_context
            )
            raise
    
    async def _execute_agent_with_tracking(
        self,
        request: Dict[str, Any],
        agent_exec_func,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute agent with automatic agentic correlation tracking.
        
        Subclasses should use this method for main agent execution.
        
        Args:
            request: Agent request dictionary
            agent_exec_func: Function to execute agent (async function that returns agent result)
            **kwargs: Additional arguments for agent execution
            
        Returns:
            Agent result with tracking metadata
        """
        from datetime import datetime
        start_time = datetime.now()
        
        try:
            # Orchestrate agentic correlation (agent execution start)
            correlation_context = await self._orchestrate_agentic_correlation(
                operation="agent_execute",
                correlation_data={
                    "prompt": request.get("prompt", request.get("message", "")),
                    "model_name": kwargs.get("model_name"),
                    "user_query": request.get("message", "")
                },
                user_context=request.get("user_context")
            )
            
            # Execute agent (existing logic via provided function)
            result = await agent_exec_func(request, **kwargs)
            
            # Calculate execution metadata
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            # Extract response and metadata
            response_text = result.get("response", "") if isinstance(result, dict) else str(result)
            tokens = result.get("tokens", {}) if isinstance(result, dict) else {}
            cost = result.get("cost", 0) if isinstance(result, dict) else 0
            
            # Record completion
            await self._record_agentic_correlation_completion(
                operation="agent_execute",
                result={
                    "success": result.get("success", True) if isinstance(result, dict) else True,
                    "response": response_text,
                    "tokens": tokens,
                    "cost": cost,
                    "duration_ms": duration_ms,
                    **result
                },
                correlation_context=correlation_context
            )
            
            # Add tracking metadata to result
            if isinstance(result, dict):
                result["_agentic_tracking"] = {
                    "agent_execution_id": correlation_context.get("agent_execution_id"),
                    "workflow_id": correlation_context.get("workflow_id"),
                    "duration_ms": duration_ms,
                    "tracked": True
                }
            
            return result
            
        except Exception as e:
            # Record failure
            correlation_context = correlation_context if 'correlation_context' in locals() else {}
            await self._record_agentic_correlation_completion(
                operation="agent_execute",
                result={"success": False, "error": str(e)},
                correlation_context=correlation_context
            )
            raise
    
    # ============================================================================
    # POLICY INTEGRATION
    # ============================================================================
    
    async def check_policy_compliance(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if an action complies with platform policies."""
        return await self.policy_integration.check_policies(self.agent_id, [action], context, self.tenant_context)
    
    async def authorize_action(self, action: str, resource: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Authorize an action on a resource."""
        return await self.policy_integration.validate_security(self.agent_id, [action], self.tenant_context)
    
    # ============================================================================
    # TOOL COMPOSITION
    # ============================================================================
    
    async def compose_tools(self, tool_chain: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compose and execute a chain of tools."""
        return await self.tool_composition.compose_tools(tool_chain, self.tenant_context)
    
    async def register_tool(self, tool_name: str, tool_definition: Dict[str, Any]) -> bool:
        """Register a tool for composition."""
        return await self.tool_composition.register_tool(tool_name, tool_definition)
    
    # ============================================================================
    # AGUI OUTPUT GENERATION
    # ============================================================================
    
    async def generate_agui_output(self, data: Dict[str, Any], component_type: str = None) -> Dict[str, Any]:
        """Generate AGUI-compliant structured output."""
        return await self.agui_formatter.format_output(data, self.agent_id, self.session_id, self.capabilities, self.expertise)
    
    async def create_analysis_card(self, title: str, metrics: Dict[str, Any], visualizations: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create an analysis card component."""
        return await self.agui_formatter.create_analysis_card(title, metrics, visualizations)
    
    # ============================================================================
    # FOUNDATION REGISTRATION
    # ============================================================================
    
    async def register_with_curator(self, user_context: UserContext, tenant_context: Dict[str, Any]):
        """Register agent capabilities with Curator Foundation."""
        try:
            if self.curator_foundation:
                registration_data = {
                    "agent_id": self.agent_id,
                    "agent_name": self.agent_name,
                    "capabilities": self.capabilities,
                    "required_roles": self.required_roles,
                    "specialization": self.specialization_config,
                    "tenant_context": tenant_context
                }
                
                await self.curator_foundation.register_agent_capability(registration_data, user_context)
                self.logger.info(f"Registered agent {self.agent_name} with Curator Foundation")
            else:
                self.logger.warning("Curator Foundation not available for registration")
                
        except Exception as e:
            self.logger.error(f"Failed to register with Curator Foundation: {e}")
    
    async def register_with_metadata_foundation(self, user_context: UserContext, tenant_context: Dict[str, Any]):
        """Register agent with Metadata Foundation for data lineage."""
        try:
            if self.metadata_foundation:
                metadata = {
                    "agent_id": self.agent_id,
                    "agent_name": self.agent_name,
                    "capabilities": self.capabilities,
                    "specialization": self.specialization_config,
                    "tenant_context": tenant_context,
                    "registration_time": datetime.utcnow().isoformat()
                }
                
                await self.metadata_foundation.register_agent_metadata(metadata, user_context)
                self.logger.info(f"Registered agent {self.agent_name} with Metadata Foundation")
            else:
                self.logger.warning("Metadata Foundation not available for registration")
                
        except Exception as e:
            self.logger.error(f"Failed to register with Metadata Foundation: {e}")
    
    # ============================================================================
    # HEALTH AND STATUS
    # ============================================================================
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent."""
        return {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "status": "initialized" if self.is_initialized else "not_initialized",
            "capabilities": self.capabilities,
            "required_roles": self.required_roles,
            "tenant_context": {
                "tenant_id": self.tenant_id,
                "tenant_user_id": self.tenant_user_id,
                "isolation_enabled": self.tenant_isolation_enabled
            },
            "agentic_abstractions_count": len(self.agentic_abstractions),
            "role_connections": {role: "connected" if conn else "disconnected" for role, conn in self.role_connections.items()},
            "specialization": {
                "name": self.specialization_name,
                "pillar": self.specialization_pillar,
                "capabilities": self.specialization_capabilities
            },
            "foundation_services_status": await self.foundation_services.get_container_health(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def run_health_check(self) -> Dict[str, Any]:
        """Run health checks for the agent."""
        self.logger.info(f"Running health check for agent {self.agent_name}...")
        
        overall_status = "healthy"
        checks = {}
        
        # Check foundation services
        fs_status = await self.foundation_services.get_container_health()
        checks["foundation_services"] = fs_status
        if fs_status["status"] != "healthy":
            overall_status = "degraded"
        
        # Check agentic foundation
        if self.agentic_foundation:
            af_status = await self.agentic_foundation.get_health_status()
            checks["agentic_foundation"] = af_status
            if af_status.get("status") != "healthy":
                overall_status = "degraded"
        
        # Check role connections
        role_checks = {}
        for role, connection in self.role_connections.items():
            role_checks[role] = "connected" if connection else "disconnected"
            if not connection:
                overall_status = "degraded"
        checks["role_connections"] = role_checks
        
        # Check agentic abstractions
        checks["agentic_abstractions"] = {
            "count": len(self.agentic_abstractions),
            "status": "loaded" if self.agentic_abstractions else "empty"
        }
        
        self.logger.info(f"✅ Health check completed for agent {self.agent_name}: {overall_status}")
        return {
            "agent_name": self.agent_name,
            "overall_status": overall_status,
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ============================================================================
    # ABSTRACT METHODS (to be implemented by concrete agents)
    # ============================================================================
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request using agent capabilities."""
        pass
    
    async def get_agent_capabilities(self) -> List[str]:
        """
        Get list of agent capabilities.
        
        Default implementation returns self.capabilities attribute.
        Agents can override if they need dynamic capability discovery.
        
        Returns:
            List of capability names
        """
        return self.capabilities if self.capabilities else []
    
    # ============================================================================
    # UTILITY METHODS (Telemetry, Health, Error Handling)
    # ============================================================================
    
    async def log_operation_with_telemetry(self, operation: str, success: bool = True, details: Optional[Dict[str, Any]] = None):
        """
        Log operation with telemetry tracking.
        
        Convenience method for consistent telemetry logging across all agents.
        Uses the telemetry utility from DI container.
        
        Args:
            operation: Name of the operation being logged
            success: Whether the operation succeeded
            details: Optional dictionary with operation details
        """
        try:
            if success:
                self.logger.info(f"✅ {operation} completed successfully")
            else:
                self.logger.warning(f"⚠️ {operation} completed with issues")
            
            # Record telemetry event if telemetry utility is available
            if self.telemetry:
                try:
                    # Convert details to tags for telemetry
                    tags = {k: str(v) for k, v in (details or {}).items() if isinstance(v, (str, int, float, bool))}
                    await self.telemetry.record_metric(
                        f"agent.{self.agent_name}.operation.{operation}",
                        1.0 if success else 0.0,
                        tags
                    )
                except Exception as telemetry_error:
                    self.logger.debug(f"Telemetry recording failed (non-critical): {telemetry_error}")
        except Exception as e:
            self.logger.error(f"Failed to log operation {operation}: {e}")
    
    async def record_health_metric(self, metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None):
        """
        Record health metric.
        
        Convenience method for consistent health metric recording across all agents.
        Uses the health utility from DI container.
        
        Args:
            metric_name: Name of the health metric
            value: Metric value (typically 1.0 for success, 0.0 for failure)
            metadata: Optional dictionary with metric metadata
        """
        try:
            # Record via telemetry (health metrics are tracked as telemetry metrics)
            if self.telemetry:
                try:
                    # Convert metadata to tags for telemetry
                    tags = {k: str(v) for k, v in (metadata or {}).items() if isinstance(v, (str, int, float, bool))}
                    tags["agent_name"] = self.agent_name
                    await self.telemetry.record_metric(
                        f"health.{metric_name}",
                        value,
                        tags
                    )
                except Exception as telemetry_error:
                    self.logger.debug(f"Health metric recording failed (non-critical): {telemetry_error}")
            
            # Also record via health utility if available
            if self.health:
                try:
                    await self.health.record_metric(metric_name, value, metadata or {})
                except Exception as health_error:
                    self.logger.debug(f"Health utility recording failed (non-critical): {health_error}")
        except Exception as e:
            self.logger.error(f"Failed to record health metric {metric_name}: {e}")
    
    async def handle_error_with_audit(self, error: Exception, operation: str, details: Optional[Dict[str, Any]] = None):
        """
        Handle error with audit logging.
        
        Convenience method for consistent error handling and audit logging across all agents.
        Logs the error, records telemetry, and performs audit logging if security utility is available.
        
        Args:
            error: The exception that occurred
            operation: Name of the operation that failed
            details: Optional dictionary with additional error details
        """
        try:
            # Log the error
            self.logger.error(f"❌ Error in {operation}: {error}")
            
            # Record telemetry for error
            if self.telemetry:
                try:
                    error_tags = {
                        "agent_name": self.agent_name,
                        "operation": operation,
                        "error_type": type(error).__name__,
                        "error_message": str(error)[:200]  # Truncate long messages
                    }
                    if details:
                        error_tags.update({k: str(v) for k, v in details.items() if isinstance(v, (str, int, float, bool))})
                    await self.telemetry.record_metric(
                        f"agent.{self.agent_name}.error.{operation}",
                        1.0,
                        error_tags
                    )
                except Exception as telemetry_error:
                    self.logger.debug(f"Error telemetry recording failed (non-critical): {telemetry_error}")
            
            # Audit logging via security utility if available
            if self.security:
                try:
                    await self.security.audit_log({
                        "action": f"agent_error_{operation}",
                        "agent_name": self.agent_name,
                        "operation": operation,
                        "error_type": type(error).__name__,
                        "error_message": str(error),
                        "details": details or {},
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as audit_error:
                    self.logger.debug(f"Audit logging failed (non-critical): {audit_error}")
        except Exception as e:
            # Last resort - just log to logger if everything else fails
            self.logger.error(f"Failed to handle error with audit: {e}")
    
    @abstractmethod
    async def get_agent_description(self) -> str:
        """Get agent description."""
        pass

    # ============================================================================
    # CURATOR FOUNDATION INTEGRATION (The "Finish" Phase)
    # ============================================================================
    # NOTE: Agent registration is handled by Agentic Foundation factory
    # Agents should NOT self-register - factory owns registration lifecycle

    async def validate_with_curator(self, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate this agent with the Curator Foundation."""
        try:
            if not self.curator_foundation:
                return {
                    "success": False,
                    "message": "Curator Foundation not available for validation",
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Get agent capabilities for validation
            agent_capabilities = await self.get_agent_capabilities()
            
            # Validate agent capabilities
            validation_result = await self.curator_foundation.validate_pattern({
                "agent_name": self.agent_name,
                "agent_id": self.agent_id,
                "capabilities": agent_capabilities,
                "required_roles": self.required_roles,
                "specialization": self.specialization_config.get("specialization") if self.specialization_config else None,
                "pillar": self.specialization_config.get("pillar") if self.specialization_config else None
            })

            self.logger.info(f"✅ Agent {self.agent_name} validation with Curator Foundation: {validation_result}")
            return {
                "success": True,
                "message": "Agent validated with Curator Foundation",
                "validation_result": validation_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to validate agent with Curator Foundation: {e}")
            return {
                "success": False,
                "message": f"Agent validation failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def generate_documentation_with_curator(self, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate documentation for this agent with the Curator Foundation."""
        try:
            if not self.curator_foundation:
                return {
                    "success": False,
                    "message": "Curator Foundation not available for documentation generation",
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Generate AGUI documentation
            api_doc_result = await self.curator_foundation.agui_schema_documentation.generate_agent_documentation(
                self.agent_name, "api"
            )
            user_guide_result = await self.curator_foundation.agui_schema_documentation.generate_agent_documentation(
                self.agent_name, "user_guide"
            )
            
            if api_doc_result and user_guide_result:
                self.logger.info(f"✅ Agent {self.agent_name} documentation generated with Curator Foundation")
                return {
                    "success": True,
                    "message": "Agent documentation generated with Curator Foundation",
                    "documentation_results": {
                        "api_documentation": api_doc_result,
                        "user_guide": user_guide_result
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to generate agent documentation",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate agent documentation with Curator Foundation: {e}")
            return {
                "success": False,
                "message": f"Agent documentation generation failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def register_mcp_tools_with_curator(self, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Register MCP tools with the Curator Foundation."""
        try:
            if not self.curator_foundation:
                return {
                    "success": False,
                    "message": "Curator Foundation not available for MCP tool registration",
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Get MCP tool definitions
            tool_definitions = self.mcp_client_manager.get_tool_definitions() if self.mcp_client_manager else []
            
            if not tool_definitions:
                return {
                    "success": True,
                    "message": "No MCP tools to register",
                    "tools_registered": 0,
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Register each tool with Curator Foundation
            tools_registered = 0
            for tool_def in tool_definitions:
                try:
                    capability_result = await self.curator_foundation.register_capability({
                        "name": tool_def.name,
                        "type": "mcp_tool",
                        "description": tool_def.description,
                        "parameters": tool_def.parameters,
                        "agent_id": self.agent_id,
                        "agent_name": self.agent_name,
                        "pillar": self.specialization_config.get("pillar") if self.specialization_config else None,
                        "specialization": self.specialization_config.get("specialization") if self.specialization_config else None
                    })
                    
                    if capability_result:
                        tools_registered += 1
                        
                except Exception as tool_error:
                    self.logger.warning(f"⚠️ Failed to register MCP tool {tool_def.name}: {tool_error}")

            self.logger.info(f"✅ Registered {tools_registered}/{len(tool_definitions)} MCP tools with Curator Foundation")
            return {
                "success": True,
                "message": f"Registered {tools_registered} MCP tools with Curator Foundation",
                "tools_registered": tools_registered,
                "total_tools": len(tool_definitions),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register MCP tools with Curator Foundation: {e}")
            return {
                "success": False,
                "message": f"MCP tool registration failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_curator_report(self, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get comprehensive Curator report for this agent."""
        try:
            if not self.curator_foundation:
                return {
                    "success": False,
                    "message": "Curator Foundation not available for report generation",
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Get comprehensive Curator report
            curator_report = await self.curator_foundation.get_agent_curator_report(self.agent_id)
            
            if curator_report:
                self.logger.info(f"✅ Generated Curator report for agent {self.agent_name}")
                return {
                    "success": True,
                    "message": f"Curator report generated for agent {self.agent_name}",
                    "curator_report": curator_report,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to generate Curator report",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate Curator report: {e}")
            return {
                "success": False,
                "message": f"Curator report generation failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }