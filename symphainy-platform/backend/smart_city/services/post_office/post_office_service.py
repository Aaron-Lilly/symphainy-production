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
import json

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
        
        # WebSocket Gateway Service (Phase 2)
        self.websocket_gateway_service = None
        
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
            
            # Initialize WebSocket Gateway Service (Phase 2)
            from .websocket_gateway_service import WebSocketGatewayService
            self.websocket_gateway_service = WebSocketGatewayService(
                di_container=self.di_container,
                post_office_service=self
            )
            await self.websocket_gateway_service.initialize()
            
            # Register WebSocket Gateway with Consul (Phase 2)
            await self._register_websocket_gateway_with_consul()
            
            if self.logger:
                self.logger.info("✅ WebSocket Gateway Service initialized and registered")
            
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
            # Error handling with audit
            await self.handle_error_with_audit(
                e,
                "post_office_initialize",
                {
                    "service": "PostOfficeService",
                    "error_type": type(e).__name__
                }
            )
            
            self.service_health = "unhealthy"
            
            # Log failure
            await self.log_operation_with_telemetry(
                "post_office_initialize_complete",
                success=False,
                details={"error": str(e), "error_type": type(e).__name__}
            )
            
            # Record health metric
            await self.record_health_metric(
                "post_office_initialized",
                0.0,
                metadata={"error_type": type(e).__name__}
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
    
    async def _register_websocket_gateway_with_consul(self):
        """Register WebSocket Gateway Service with Consul (Phase 2)."""
        try:
            if not self.websocket_gateway_service:
                return
            
            # Get Curator Foundation for service registration
            curator = self.di_container.get_foundation_service("CuratorFoundationService")
            if not curator:
                if self.logger:
                    self.logger.warning("⚠️ Curator Foundation not available, skipping Consul registration")
                return
            
            # Prepare service metadata
            service_metadata = {
                "service_type": "websocket_gateway",
                "address": "0.0.0.0",  # Will be discovered via Traefik
                "port": 8000,  # Backend port (Traefik routes /ws to this)
                "tags": ["websocket", "gateway", "post_office", "smart_city", "real-time"],
                "realm": "smart_city",
                "health_check_endpoint": "/health/websocket-gateway",
                "endpoints": ["/ws"],
                "capabilities": ["websocket_connection", "channel_routing", "message_fanout"]
            }
            
            # Register via Curator (which uses Consul via Public Works)
            registration = await curator.register_service(
                service_instance=self.websocket_gateway_service,
                service_metadata=service_metadata
            )
            
            if registration and registration.get("success"):
                if self.logger:
                    self.logger.info(f"✅ WebSocket Gateway registered with Consul: {registration.get('service_id', 'unknown')}")
            else:
                if self.logger:
                    self.logger.warning("⚠️ WebSocket Gateway Consul registration failed, continuing without service discovery")
                    
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to register WebSocket Gateway with Consul: {e}")
    
    # ============================================================================
    # WEBSOCKET GATEWAY SOA APIs (Phase 2)
    # ============================================================================
    
    async def get_websocket_endpoint(
        self,
        session_token: str,
        realm: str
    ) -> Dict[str, Any]:
        """
        Get WebSocket endpoint URL for realm.
        
        Used by Experience Realm to get WebSocket URL for frontend.
        
        Note: Realm access validation happens at Platform Gateway level.
        This service trusts Platform Gateway has already validated.
        
        Args:
            session_token: Session token for authentication
            realm: Realm requesting the endpoint
            
        Returns:
            Dict with websocket_url, channels, and message_format
        """
        try:
            if not self.websocket_gateway_service:
                return {
                    "success": False,
                    "error": "WebSocket Gateway Service not initialized"
                }
            
            # Get gateway URL (will use Consul in Phase 2, for now use instance info)
            # TODO: Phase 2 - Get from Consul service discovery
            gateway_url = f"ws://localhost/ws"  # Placeholder, will be discovered via Consul
            
            return {
                "success": True,
                "websocket_url": f"{gateway_url}?session_token={session_token}",
                "channels": [
                    "guide",
                    "pillar:content",
                    "pillar:insights",
                    "pillar:operations",
                    "pillar:business_outcomes"
                ],
                "message_format": {
                    "channel": "string (guide | pillar:content | pillar:insights | pillar:operations | pillar:business_outcomes)",
                    "intent": "string (chat | query | command)",
                    "payload": {
                        "message": "string",
                        "conversation_id": "string (optional)",
                        "metadata": "object (optional)"
                    }
                }
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to get WebSocket endpoint: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def publish_to_agent_channel(
        self,
        channel: str,
        message: Dict[str, Any],
        realm: str
    ) -> Dict[str, Any]:
        """
        Publish message to agent channel.
        
        Used by Business Enablement agents to send messages via WebSocket.
        
        Note: Realm access validation happens at Platform Gateway level.
        This service trusts Platform Gateway has already validated.
        
        Args:
            channel: Channel name (e.g., "guide", "pillar:content")
            message: Message to publish
            realm: Realm publishing the message
            
        Returns:
            Dict with status and channel info
        """
        try:
            if not self.messaging_abstraction:
                return {
                    "success": False,
                    "error": "Messaging abstraction not available"
                }
            
            # Publish to Redis channel
            redis_channel = f"websocket:{channel}"
            
            # Add metadata
            message_with_metadata = {
                "source": realm,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Publish to Redis
            if hasattr(self.messaging_abstraction, 'publish'):
                await self.messaging_abstraction.publish(
                    redis_channel,
                    json.dumps(message_with_metadata)
                )
            elif hasattr(self.messaging_abstraction, 'send_message'):
                await self.messaging_abstraction.send_message(
                    redis_channel,
                    message_with_metadata
                )
            
            return {
                "success": True,
                "status": "published",
                "channel": redis_channel
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to publish to channel {channel}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def subscribe_to_channel(
        self,
        channel: str,
        callback: Any,
        realm: str
    ) -> Dict[str, Any]:
        """
        Subscribe to channel for realm.
        
        Used by agents to receive messages from WebSocket connections.
        
        Note: Realm access validation happens at Platform Gateway level.
        This service trusts Platform Gateway has already validated.
        
        Future: Agents should access this via MCP Tools (separate refactoring thread).
        
        Args:
            channel: Channel name to subscribe to
            callback: Callback function to handle messages
            realm: Realm subscribing to the channel
            
        Returns:
            Dict with subscription status
        """
        try:
            if not self.messaging_abstraction:
                return {
                    "success": False,
                    "error": "Messaging abstraction not available"
                }
            
            # Subscribe to Redis channel
            redis_channel = f"websocket:{channel}"
            
            # Create pubsub subscription
            if hasattr(self.messaging_abstraction, 'pubsub'):
                pubsub = self.messaging_abstraction.pubsub()
                await pubsub.subscribe(redis_channel)
                
                # Start background task to handle messages
                import asyncio
                asyncio.create_task(self._handle_channel_messages(pubsub, callback))
                
                return {
                    "success": True,
                    "status": "subscribed",
                    "channel": redis_channel
                }
            else:
                return {
                    "success": False,
                    "error": "Pub/Sub not available in messaging abstraction"
                }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to subscribe to channel {channel}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_channel_messages(self, pubsub: Any, callback: Any):
        """Background task to handle channel messages."""
        try:
            async for message in pubsub.listen():
                if message.get('type') == 'message':
                    data = json.loads(message.get('data', '{}'))
                    await callback(data)
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error handling channel messages: {e}")
    
    async def send_to_connection(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send message to specific WebSocket connection.
        
        Used by agents to send responses to WebSocket connections.
        
        Args:
            connection_id: Connection ID to send message to
            message: Message to send
            
        Returns:
            Dict with send status
        """
        try:
            if not self.websocket_gateway_service:
                return {
                    "success": False,
                    "error": "WebSocket Gateway Service not initialized"
                }
            
            # Delegate to WebSocket Gateway Service
            success = await self.websocket_gateway_service.send_to_connection(
                connection_id,
                message
            )
            
            return {
                "success": success,
                "connection_id": connection_id
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to send to connection {connection_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
