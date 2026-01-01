#!/usr/bin/env python3
"""
Post Office Service - Micro-Modular Refactored

Clean micro-modular implementation using dynamic module loading via mixin.
Follows proper base class patterns and mixin methods for infrastructure access.

WHAT (Smart City Role): I orchestrate strategic communication with proper infrastructure
HOW (Service Implementation): I use SmartCityRoleBase with micro-modules loaded dynamically
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

# Import ONLY our new base and protocol
from bases.smart_city_role_base import SmartCityRoleBase
from backend.smart_city.protocols.post_office_service_protocol import PostOfficeServiceProtocol


class PostOfficeService(SmartCityRoleBase, PostOfficeServiceProtocol):
    """
    Post Office Service - Micro-Modular Refactored
    
    Clean implementation using micro-modules loaded dynamically via mixin.
    Uses proper infrastructure abstractions via mixin methods.
    
    WHAT (Smart City Role): I orchestrate strategic communication with proper infrastructure
    HOW (Service Implementation): I use SmartCityRoleBase with micro-modules loaded dynamically
    """
    
    def __init__(self, di_container: Any):
        """Initialize Post Office Service with micro-module support."""
        super().__init__(
            service_name="PostOfficeService",
            role_name="post_office",
            di_container=di_container
        )
        
        # Infrastructure Abstractions (will be initialized via mixin methods in modules)
        self.messaging_abstraction = None
        self.event_management_abstraction = None
        self.session_abstraction = None
        
        # Service State
        self.is_infrastructure_connected = False
        
        # Week 3 Enhancement: SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Service-specific state
        self.active_agents: Dict[str, Dict[str, Any]] = {}
        self.message_history: List[Dict[str, Any]] = []
        self.event_routing_rules: Dict[str, List[str]] = {}
        
        # Micro-modules (loaded dynamically via mixin)
        self.initialization_module = None
        self.messaging_module = None
        self.event_routing_module = None
        self.orchestration_module = None
        self.soa_mcp_module = None
        self.utilities_module = None
        
        # Logger is initialized by SmartCityRoleBase
        if self.logger:
            self.logger.info("✅ Post Office Service (Micro-Modular) initialized")
    
    async def initialize(self) -> bool:
        """Initialize Post Office Service with lazy-loaded modules."""
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "post_office_initialize_start",
            success=True
        )
        
        try:
            # Load modules dynamically using mixin
            self.initialization_module = self.get_module("initialization")
            if not self.initialization_module:
                raise Exception("Failed to load initialization module")
            
            # Initialize infrastructure using module
            await self.initialization_module.initialize_infrastructure()
            
            # Load other modules
            self.messaging_module = self.get_module("messaging")
            self.event_routing_module = self.get_module("event_routing")
            self.orchestration_module = self.get_module("orchestration")
            self.soa_mcp_module = self.get_module("soa_mcp")
            self.utilities_module = self.get_module("utilities")
            
            if not all([self.messaging_module, self.event_routing_module, 
                       self.orchestration_module, self.soa_mcp_module, self.utilities_module]):
                raise Exception("Failed to load required modules")
            
            # Initialize SOA/MCP using module
            await self.soa_mcp_module.initialize_soa_api_exposure()
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Register capabilities using module
            # Register capabilities with curator (Phase 2 pattern - simplified for Smart City)
            await self.soa_mcp_module.register_capabilities()
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            # Record health metric
            await self.record_health_metric(
                "post_office_initialized",
                1.0,
                {"service": "PostOfficeService"}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "post_office_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "post_office_initialize")
            self.service_health = "unhealthy"
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "post_office_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            return False
    
    # ============================================================================
    # MESSAGING METHODS - Delegate to messaging module
    # ============================================================================
    
    async def send_message(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send message with routing and delivery."""
        # Service-level method delegates to module (module handles utilities)
        return await self.messaging_module.send_message(request, user_context)
    
    async def get_messages(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get messages for recipient."""
        # Service-level method delegates to module (module handles utilities)
        return await self.messaging_module.get_messages(request, user_context)
    
    async def get_message_status(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get message delivery status."""
        # Service-level method delegates to module (module handles utilities)
        return await self.messaging_module.get_message_status(request, user_context)
    
    # ============================================================================
    # EVENT ROUTING METHODS - Delegate to event_routing module
    # ============================================================================
    
    async def route_event(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Route event to appropriate service."""
        # Service-level method delegates to module (module handles utilities)
        return await self.event_routing_module.route_event(request, user_context)
    
    async def publish_event(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Publish event via Post Office."""
        # Service-level method delegates to module (module handles utilities)
        return await self.event_routing_module.publish_event(request, user_context)
    
    async def subscribe_to_events(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Subscribe to events via Post Office."""
        # Service-level method delegates to module (module handles utilities)
        return await self.event_routing_module.subscribe_to_events(request, user_context)
    
    async def unsubscribe_from_events(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Unsubscribe from events via Post Office."""
        # Service-level method delegates to module (module handles utilities)
        return await self.event_routing_module.unsubscribe_from_events(request, user_context)
    
    async def register_agent(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Register agent for communication."""
        # Service-level method delegates to module (module handles utilities)
        return await self.event_routing_module.register_agent(request, user_context)
    
    # ============================================================================
    # ORCHESTRATION METHODS - Delegate to orchestration module
    # ============================================================================
    
    async def orchestrate_pillar_coordination(self, pattern_name: str, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate communication between pillars."""
        return await self.orchestration_module.orchestrate_pillar_coordination(pattern_name, trigger_data)
    
    async def orchestrate_realm_communication(self, source_realm: str, target_realm: str, 
                                            communication_data: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate communication between realms."""
        return await self.orchestration_module.orchestrate_realm_communication(source_realm, target_realm, communication_data)
    
    async def orchestrate_event_driven_communication(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate event-driven communication patterns."""
        return await self.orchestration_module.orchestrate_event_driven_communication(event_type, event_data)
    
    async def orchestrate_service_discovery(self, service_type: str, realm: Optional[str] = None) -> Dict[str, Any]:
        """Orchestrate service discovery and location."""
        try:
            # Use service discovery from platform capabilities mixin
            service_discovery = self.get_service_discovery()
            if service_discovery:
                services = await service_discovery.discover_services(service_type, realm)
                return {
                    "service_type": service_type,
                    "realm": realm,
                    "services": services,
                    "success": True
                }
            else:
                return {
                    "service_type": service_type,
                    "realm": realm,
                    "services": [],
                    "error": "Service discovery not available",
                    "success": False
                }
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error orchestrating service discovery: {str(e)}")
            return {
                "service_type": service_type,
                "realm": realm,
                "services": [],
                "error": str(e),
                "success": False
            }
    
    # ============================================================================
    # UTILITY METHODS - Delegate to utilities module
    # ============================================================================
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate that proper infrastructure mapping is working correctly."""
        return await self.utilities_module.validate_infrastructure_mapping()
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities with proper infrastructure status."""
        return await self.utilities_module.get_service_capabilities()
