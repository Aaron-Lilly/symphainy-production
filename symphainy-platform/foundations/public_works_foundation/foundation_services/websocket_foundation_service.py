#!/usr/bin/env python3
"""
WebSocket Foundation Service

Infrastructure-level foundation service for WebSocket communication.
Provides stable API for Smart City services while allowing infrastructure swapping.

WHAT (Foundation Service): I provide WebSocket infrastructure services
HOW (Service Implementation): I use Public Works WebSocket adapter via DI
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

# Import foundation base
from bases.foundation_service_base import FoundationServiceBase

# Import Public Works Foundation for infrastructure
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService

# Import DI Container
from foundations.di_container.di_container_service import DIContainerService


class WebSocketFoundationService(FoundationServiceBase):
    """
    WebSocket Foundation Service - Infrastructure-level WebSocket Services
    
    Provides WebSocket infrastructure services for all realms using Public Works
    WebSocket adapter. Provides stable API to Smart City services while allowing
    infrastructure swapping without breaking changes.
    
    WHAT (Foundation Service): I provide WebSocket infrastructure services
    HOW (Service Implementation): I use Public Works WebSocket adapter via DI
    """
    
    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService):
        """Initialize WebSocket Foundation Service."""
        super().__init__(
            service_name="websocket_foundation",
            di_container=di_container
        )
        self.public_works_foundation = public_works_foundation
        
        # Get infrastructure from Public Works (via DI)
        self.websocket_adapter = None
        
        # WebSocket connections registry
        self.connections = {}
        
        # Realm-specific WebSocket managers
        self.realm_managers = {
            "smart_city": {},
            "business_enablement": {},
            "experience": {},
            "journey_solution": {}
        }
        
        # WebSocket configuration
        self.websocket_config = {
            "host": "localhost",
            "port": 8765,
            "path": "/websocket",
            "max_connections": 1000,
            "ping_interval": 30,
            "ping_timeout": 10
        }
        
        # Service state
        self.is_running = False
        
        self.logger.info("🏗️ WebSocket Foundation Service initialized")
    
    async def initialize(self) -> bool:
        """Initialize foundation service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("initialize_start", success=True)
            
            self.logger.info("🚀 Initializing WebSocket Foundation Service...")
            
            # Get infrastructure from Public Works Foundation (via DI - required)
            self.websocket_adapter = self.public_works_foundation.get_websocket_adapter()
            
            if not self.websocket_adapter:
                raise RuntimeError(
                    "WebSocket adapter not available from Public Works Foundation. "
                    "Ensure Public Works Foundation is initialized and provides websocket adapter."
                )
            
            # NOTE: WebSocketAdapter doesn't have an initialize() method
            # It's initialized in __init__ and is ready to use immediately
            # No async initialization needed
            
            # Setup WebSocket handlers
            await self._setup_websocket_handlers()
            
            self.is_initialized = True
            self.logger.info("✅ WebSocket Foundation Service initialized successfully")
            
            # Record success metric
            await self.record_health_metric("initialize_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("initialize_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "initialize")
            self.logger.error(f"❌ Failed to initialize WebSocket Foundation Service: {e}")
            self.service_health = "unhealthy"
            return False
    
    async def _setup_websocket_handlers(self):
        """Setup WebSocket handlers for different realms."""
        self.logger.info("🔧 Setting up WebSocket handlers...")
        
        # Setup realm-specific handlers
        for realm in self.realm_managers.keys():
            await self._setup_realm_handler(realm)
        
        self.logger.info("✅ WebSocket handlers setup complete")
    
    async def _setup_realm_handler(self, realm: str):
        """Setup WebSocket handler for specific realm."""
        self.logger.info(f"🔧 Setting up WebSocket handler for {realm}...")
        
        # Create realm-specific handler
        async def realm_websocket_handler(websocket, path):
            """Handle WebSocket connections for specific realm."""
            client_id = f"{realm}_{datetime.now().timestamp()}"
            
            try:
                # Start telemetry tracking (using service's utilities)
                await self.log_operation_with_telemetry("realm_websocket_handler_start", success=True)
                
                # Register connection
                await self._register_connection(client_id, realm, websocket)
                
                # Handle WebSocket messages
                async for message in websocket:
                    await self._handle_websocket_message(client_id, realm, message)
                
                # Record success metric
                await self.record_health_metric("realm_websocket_handler_success", 1.0, {
                    "realm": realm,
                    "client_id": client_id
                })
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("realm_websocket_handler_complete", success=True)
                    
            except Exception as e:
                # Use enhanced error handling with audit (using service's utilities)
                await self.handle_error_with_audit(e, "realm_websocket_handler")
                self.logger.error(f"❌ WebSocket handler error for {realm}: {e}")
            finally:
                # Unregister connection
                await self._unregister_connection(client_id, realm)
        
        # Register handler with Public Works WebSocket adapter
        if self.websocket_adapter:
            await self.websocket_adapter.register_handler(
                path=f"/{realm}",
                handler=realm_websocket_handler
            )
        
        self.logger.info(f"✅ WebSocket handler setup complete for {realm}")
    
    async def _register_connection(self, client_id: str, realm: str, websocket):
        """Register WebSocket connection."""
        self.connections[client_id] = {
            "realm": realm,
            "websocket": websocket,
            "connected_at": datetime.now(),
            "last_ping": datetime.now()
        }
        
        self.realm_managers[realm][client_id] = self.connections[client_id]
        
        self.logger.info(f"✅ WebSocket connection registered: {client_id} for {realm}")
    
    async def _unregister_connection(self, client_id: str, realm: str):
        """Unregister WebSocket connection."""
        if client_id in self.connections:
            del self.connections[client_id]
        
        if client_id in self.realm_managers[realm]:
            del self.realm_managers[realm][client_id]
        
        self.logger.info(f"✅ WebSocket connection unregistered: {client_id} for {realm}")
    
    async def _handle_websocket_message(self, client_id: str, realm: str, message: str):
        """Handle WebSocket message."""
        try:
            # Parse message
            message_data = await self._parse_websocket_message(message)
            
            # Route message to appropriate handler
            await self._route_websocket_message(client_id, realm, message_data)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to handle WebSocket message: {e}")
    
    async def _parse_websocket_message(self, message: str) -> Dict[str, Any]:
        """Parse WebSocket message."""
        try:
            import json
            return json.loads(message)
        except json.JSONDecodeError:
            return {"type": "text", "content": message}
    
    async def _route_websocket_message(self, client_id: str, realm: str, message_data: Dict[str, Any]):
        """Route WebSocket message to appropriate handler."""
        message_type = message_data.get("type", "unknown")
        
        if message_type == "ping":
            await self._handle_ping(client_id, realm)
        elif message_type == "pong":
            await self._handle_pong(client_id, realm)
        elif message_type == "message":
            await self._handle_realm_message(client_id, realm, message_data)
        else:
            self.logger.warning(f"⚠️ Unknown WebSocket message type: {message_type}")
    
    async def _handle_ping(self, client_id: str, realm: str):
        """Handle ping message."""
        await self._send_websocket_message(client_id, {"type": "pong", "timestamp": datetime.now().isoformat()})
    
    async def _handle_pong(self, client_id: str, realm: str):
        """Handle pong message."""
        if client_id in self.connections:
            self.connections[client_id]["last_ping"] = datetime.now()
    
    async def _handle_realm_message(self, client_id: str, realm: str, message_data: Dict[str, Any]):
        """Handle realm-specific message."""
        # This would be implemented with actual realm-specific message handling
        self.logger.info(f"📨 Handling realm message for {realm}: {message_data}")
    
    async def start(self):
        """Start WebSocket Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("start_start", success=True)
            
            if not self.is_initialized:
                await self.initialize()
            
            self.logger.info("🚀 Starting WebSocket Foundation Service...")
            
            # Start Public Works WebSocket adapter
            if self.websocket_adapter:
                await self.websocket_adapter.start()
            
            self.is_running = True
            self.logger.info("✅ WebSocket Foundation Service started successfully")
            
            # Record success metric
            await self.record_health_metric("start_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("start_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "start")
            self.logger.error(f"❌ Failed to start WebSocket Foundation Service: {e}")
            raise
    
    async def stop(self):
        """Stop WebSocket Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("stop_start", success=True)
            
            self.logger.info("🛑 Stopping WebSocket Foundation Service...")
            
            # Stop Public Works WebSocket adapter
            if self.websocket_adapter:
                await self.websocket_adapter.stop()
            
            # Close all connections
            for client_id in list(self.connections.keys()):
                await self._unregister_connection(client_id, self.connections[client_id]["realm"])
            
            self.is_running = False
            self.logger.info("✅ WebSocket Foundation Service stopped successfully")
            
            # Record success metric
            await self.record_health_metric("stop_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("stop_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "stop")
            self.logger.error(f"❌ Failed to stop WebSocket Foundation Service: {e}")
            raise
    
    async def shutdown(self) -> bool:
        """Shutdown WebSocket Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("shutdown_start", success=True)
            
            await self.stop()
            self.logger.info("🔌 WebSocket Foundation Service shutdown complete")
            
            # Record success metric
            await self.record_health_metric("shutdown_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("shutdown_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "shutdown")
            self.logger.error(f"❌ Failed to shutdown WebSocket Foundation Service: {e}")
            return False
    
    # Public API methods for Smart City services
    
    async def send_websocket_message(self, client_id: str, message: Dict[str, Any]):
        """Send WebSocket message to specific client."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("send_websocket_message_start", success=True)
            
            if client_id in self.connections:
                websocket = self.connections[client_id]["websocket"]
                import json
                await websocket.send(json.dumps(message))
                self.logger.info(f"✅ WebSocket message sent to {client_id}")
                
                # Record success metric
                await self.record_health_metric("send_websocket_message_success", 1.0, {"client_id": client_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("send_websocket_message_complete", success=True)
            else:
                self.logger.warning(f"⚠️ Client {client_id} not found in connections")
                await self.record_health_metric("send_websocket_message_warning", 1.0, {
                    "client_id": client_id,
                    "warning": "client_not_found"
                })
                await self.log_operation_with_telemetry("send_websocket_message_complete", success=False)
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "send_websocket_message")
            self.logger.error(f"❌ Failed to send WebSocket message to {client_id}: {e}")
            raise
    
    async def broadcast_to_realm(self, realm: str, message: Dict[str, Any], user_context: Dict[str, Any] = None):
        """Broadcast message to all clients in realm."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("broadcast_to_realm_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, f"realm_{realm}", "write"):
                        await self.record_health_metric("broadcast_to_realm_access_denied", 1.0, {"realm": realm})
                        await self.log_operation_with_telemetry("broadcast_to_realm_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("broadcast_to_realm_tenant_denied", 1.0, {"realm": realm, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("broadcast_to_realm_complete", success=False)
                            return False
            
            if realm in self.realm_managers:
                for client_id in self.realm_managers[realm]:
                    await self.send_websocket_message(client_id, message)
            
            # Record success metric
            await self.record_health_metric("broadcast_to_realm_success", 1.0, {"realm": realm})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("broadcast_to_realm_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "broadcast_to_realm")
            self.logger.error(f"❌ Failed to broadcast to realm {realm}: {e}")
            return False
    
    async def get_connection_info(self, client_id: str, user_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Get connection information for client."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_connection_info_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "websocket_connections", "read"):
                        await self.record_health_metric("get_connection_info_access_denied", 1.0, {"client_id": client_id})
                        await self.log_operation_with_telemetry("get_connection_info_complete", success=False)
                        return None
            
            result = self.connections.get(client_id)
            
            # Record success metric
            await self.record_health_metric("get_connection_info_success", 1.0, {"client_id": client_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_connection_info_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_connection_info")
            self.logger.error(f"❌ Failed to get connection info for {client_id}: {e}")
            return None
    
    async def get_realm_connections(self, realm: str, user_context: Dict[str, Any] = None) -> List[str]:
        """Get all connection IDs for realm."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_realm_connections_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, f"realm_{realm}", "read"):
                        await self.record_health_metric("get_realm_connections_access_denied", 1.0, {"realm": realm})
                        await self.log_operation_with_telemetry("get_realm_connections_complete", success=False)
                        return []
            
            result = list(self.realm_managers.get(realm, {}).keys())
            
            # Record success metric
            await self.record_health_metric("get_realm_connections_success", 1.0, {"realm": realm, "count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_realm_connections_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_realm_connections")
            self.logger.error(f"❌ Failed to get realm connections for {realm}: {e}")
            return []
    
    async def get_total_connections(self, user_context: Dict[str, Any] = None) -> int:
        """Get total number of active connections."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_total_connections_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "websocket_connections", "read"):
                        await self.record_health_metric("get_total_connections_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_total_connections_complete", success=False)
                        return 0
            
            result = len(self.connections)
            
            # Record success metric
            await self.record_health_metric("get_total_connections_success", 1.0, {"count": result})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_total_connections_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_total_connections")
            self.logger.error(f"❌ Failed to get total connections: {e}")
            return 0
    
    async def get_realm_connection_count(self, realm: str, user_context: Dict[str, Any] = None) -> int:
        """Get number of active connections for realm."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_realm_connection_count_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, f"realm_{realm}", "read"):
                        await self.record_health_metric("get_realm_connection_count_access_denied", 1.0, {"realm": realm})
                        await self.log_operation_with_telemetry("get_realm_connection_count_complete", success=False)
                        return 0
            
            result = len(self.realm_managers.get(realm, {}))
            
            # Record success metric
            await self.record_health_metric("get_realm_connection_count_success", 1.0, {"realm": realm, "count": result})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_realm_connection_count_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_realm_connection_count")
            self.logger.error(f"❌ Failed to get realm connection count for {realm}: {e}")
            return 0



