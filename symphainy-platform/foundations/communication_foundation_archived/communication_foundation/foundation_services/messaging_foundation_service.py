#!/usr/bin/env python3
"""
Messaging Foundation Service

Infrastructure-level foundation service for asynchronous messaging.
Provides stable API for Smart City services while allowing infrastructure swapping.

WHAT (Foundation Service): I provide messaging infrastructure services
HOW (Service Implementation): I use Public Works Messaging abstraction via DI
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


class MessagingFoundationService(FoundationServiceBase):
    """
    Messaging Foundation Service - Infrastructure-level Messaging Services
    
    Provides messaging infrastructure services for all realms using Public Works
    Messaging abstraction. Provides stable API to Smart City services while allowing
    infrastructure swapping without breaking changes.
    
    WHAT (Foundation Service): I provide messaging infrastructure services
    HOW (Service Implementation): I use Public Works Messaging abstraction via DI
    """
    
    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService):
        """Initialize Messaging Foundation Service."""
        super().__init__(
            service_name="messaging_foundation",
            di_container=di_container
        )
        self.public_works_foundation = public_works_foundation
        
        # Get infrastructure from Public Works (via DI)
        self.messaging_abstraction = None
        
        # Message queues for different realms
        self.realm_queues = {
            "smart_city": [],
            "business_enablement": [],
            "experience": [],
            "journey_solution": []
        }
        
        # Message handlers
        self.message_handlers = {}
        
        # Messaging configuration
        self.messaging_config = {
            "default_retention_hours": 168,  # 7 days
            "max_messages_per_recipient": 1000,
            "message_timeout_seconds": 300,
            "retry_attempts": 3,
            "retry_delay_seconds": 5
        }
        
        # Service state
        self.is_running = False
        
        self.logger.info("🏗️ Messaging Foundation Service initialized")
    
    async def initialize(self) -> bool:
        """Initialize foundation service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("initialize_start", success=True)
            
            self.logger.info("🚀 Initializing Messaging Foundation Service...")
            
            # Get infrastructure from Public Works Foundation (via DI - required)
            self.messaging_abstraction = self.public_works_foundation.get_messaging_abstraction()
            
            if not self.messaging_abstraction:
                raise RuntimeError(
                    "Messaging abstraction not available from Public Works Foundation. "
                    "Ensure Public Works Foundation is initialized and provides messaging abstraction."
                )
            
            # NOTE: MessagingAbstraction doesn't have an initialize() method
            # It's initialized in __init__ and is ready to use immediately
            # No async initialization needed
            
            # Setup message handlers
            await self._setup_message_handlers()
            
            self.is_initialized = True
            self.logger.info("✅ Messaging Foundation Service initialized successfully")
            
            # Record success metric
            await self.record_health_metric("initialize_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("initialize_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "initialize")
            self.logger.error(f"❌ Failed to initialize Messaging Foundation Service: {e}")
            self.service_health = "unhealthy"
            return False
    
    async def _setup_message_handlers(self):
        """Setup message handlers for different realms."""
        self.logger.info("🔧 Setting up message handlers...")
        
        # Setup realm-specific message handlers
        for realm in self.realm_queues.keys():
            await self._setup_realm_message_handler(realm)
        
        self.logger.info("✅ Message handlers setup complete")
    
    async def _setup_realm_message_handler(self, realm: str):
        """Setup message handler for specific realm."""
        self.logger.info(f"🔧 Setting up message handler for {realm}...")
        
        # Create realm-specific message handler
        async def realm_message_handler(message_data: Dict[str, Any]):
            """Handle messages for specific realm."""
            try:
                # Start telemetry tracking (using service's utilities)
                await self.log_operation_with_telemetry("realm_message_handler_start", success=True)
                
                # Process message
                await self._process_realm_message(realm, message_data)
                
                # Record success metric
                await self.record_health_metric("realm_message_handler_success", 1.0, {
                    "realm": realm,
                    "message_type": message_data.get("type", "unknown")
                })
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("realm_message_handler_complete", success=True)
                
            except Exception as e:
                # Use enhanced error handling with audit (using service's utilities)
                await self.handle_error_with_audit(e, "realm_message_handler")
                self.logger.error(f"❌ Message handler error for {realm}: {e}")
        
        # Register handler
        self.message_handlers[realm] = realm_message_handler
        
        self.logger.info(f"✅ Message handler setup complete for {realm}")
    
    async def _process_realm_message(self, realm: str, message_data: Dict[str, Any]):
        """Process message for specific realm."""
        message_type = message_data.get("type", "unknown")
        message_content = message_data.get("content", {})
        
        if message_type == "notification":
            await self._handle_notification_message(realm, message_content)
        elif message_type == "command":
            await self._handle_command_message(realm, message_content)
        elif message_type == "response":
            await self._handle_response_message(realm, message_content)
        else:
            self.logger.warning(f"⚠️ Unknown message type: {message_type}")
    
    async def _handle_notification_message(self, realm: str, message_content: Dict[str, Any]):
        """Handle notification message."""
        self.logger.info(f"📨 Handling notification message for {realm}: {message_content}")
        # This would be implemented with actual notification handling
    
    async def _handle_command_message(self, realm: str, message_content: Dict[str, Any]):
        """Handle command message."""
        self.logger.info(f"📨 Handling command message for {realm}: {message_content}")
        # This would be implemented with actual command handling
    
    async def _handle_response_message(self, realm: str, message_content: Dict[str, Any]):
        """Handle response message."""
        self.logger.info(f"📨 Handling response message for {realm}: {message_content}")
        # This would be implemented with actual response handling
    
    async def start(self):
        """Start Messaging Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("start_start", success=True)
            
            if not self.is_initialized:
                await self.initialize()
            
            self.logger.info("🚀 Starting Messaging Foundation Service...")
            
            # Start messaging abstraction
            if self.messaging_abstraction:
                await self.messaging_abstraction.start()
            
            self.is_running = True
            self.logger.info("✅ Messaging Foundation Service started successfully")
            
            # Record success metric
            await self.record_health_metric("start_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("start_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "start")
            self.logger.error(f"❌ Failed to start Messaging Foundation Service: {e}")
            raise
    
    async def stop(self):
        """Stop Messaging Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("stop_start", success=True)
            
            self.logger.info("🛑 Stopping Messaging Foundation Service...")
            
            # Stop messaging abstraction
            if self.messaging_abstraction:
                await self.messaging_abstraction.stop()
            
            self.is_running = False
            self.logger.info("✅ Messaging Foundation Service stopped successfully")
            
            # Record success metric
            await self.record_health_metric("stop_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("stop_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "stop")
            self.logger.error(f"❌ Failed to stop Messaging Foundation Service: {e}")
            raise
    
    async def shutdown(self) -> bool:
        """Shutdown Messaging Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("shutdown_start", success=True)
            
            await self.stop()
            self.logger.info("🔌 Messaging Foundation Service shutdown complete")
            
            # Record success metric
            await self.record_health_metric("shutdown_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("shutdown_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "shutdown")
            self.logger.error(f"❌ Failed to shutdown Messaging Foundation Service: {e}")
            return False
    
    # Public API methods for Smart City services
    
    async def send_message(self, target_realm: str, message_type: str, message_content: Dict[str, Any], 
                         sender: str = "system", priority: str = "normal") -> Optional[str]:
        """Send message to target realm."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("send_message_start", success=True)
            
            message_data = {
                "type": message_type,
                "content": message_content,
                "sender": sender,
                "target_realm": target_realm,
                "priority": priority,
                "timestamp": datetime.now().isoformat()
            }
            
            # Use Public Works messaging abstraction
            if self.messaging_abstraction:
                message_context = await self.messaging_abstraction.send_message(
                    message_type=message_type,
                    sender=sender,
                    recipient=target_realm,
                    message_content=message_content
                )
                
                if message_context:
                    self.logger.info(f"✅ Message sent to {target_realm}: {message_type}")
                    
                    # Record success metric
                    await self.record_health_metric("send_message_success", 1.0, {
                        "target_realm": target_realm,
                        "message_type": message_type
                    })
                    
                    # End telemetry tracking
                    await self.log_operation_with_telemetry("send_message_complete", success=True)
                    
                    return message_context.message_id
                else:
                    self.logger.error(f"❌ Failed to send message to {target_realm}")
                    await self.record_health_metric("send_message_failed", 1.0, {
                        "target_realm": target_realm,
                        "message_type": message_type
                    })
                    await self.log_operation_with_telemetry("send_message_complete", success=False)
                    return None
            else:
                self.logger.error("❌ Messaging abstraction not available")
                await self.record_health_metric("send_message_error", 1.0, {"error": "abstraction_not_available"})
                await self.log_operation_with_telemetry("send_message_complete", success=False)
                return None
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "send_message")
            self.logger.error(f"❌ Failed to send message to {target_realm}: {e}")
            return None
    
    async def receive_message(self, realm: str, message_id: str) -> Optional[Dict[str, Any]]:
        """Receive message for realm."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("receive_message_start", success=True)
            
            # Use Public Works messaging abstraction
            if self.messaging_abstraction:
                message_context = await self.messaging_abstraction.receive_message(
                    recipient=realm,
                    message_id=message_id
                )
                
                if message_context:
                    result = {
                        "message_id": message_context.message_id,
                        "type": message_context.message_type,
                        "content": message_context.message_content,
                        "sender": message_context.sender,
                        "timestamp": message_context.timestamp
                    }
                    
                    # Record success metric
                    await self.record_health_metric("receive_message_success", 1.0, {
                        "realm": realm,
                        "message_id": message_id
                    })
                    
                    # End telemetry tracking
                    await self.log_operation_with_telemetry("receive_message_complete", success=True)
                    
                    return result
                else:
                    await self.record_health_metric("receive_message_not_found", 1.0, {
                        "realm": realm,
                        "message_id": message_id
                    })
                    await self.log_operation_with_telemetry("receive_message_complete", success=False)
                    return None
            else:
                self.logger.error("❌ Messaging abstraction not available")
                await self.record_health_metric("receive_message_error", 1.0, {"error": "abstraction_not_available"})
                await self.log_operation_with_telemetry("receive_message_complete", success=False)
                return None
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "receive_message")
            self.logger.error(f"❌ Failed to receive message for {realm}: {e}")
            return None
    
    async def get_message_queue(self, realm: str, user_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get message queue for realm."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_message_queue_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, f"realm_{realm}", "read"):
                        await self.record_health_metric("get_message_queue_access_denied", 1.0, {"realm": realm})
                        await self.log_operation_with_telemetry("get_message_queue_complete", success=False)
                        return []
            
            result = self.realm_queues.get(realm, [])
            
            # Record success metric
            await self.record_health_metric("get_message_queue_success", 1.0, {"realm": realm, "count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_message_queue_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_message_queue")
            self.logger.error(f"❌ Failed to get message queue for {realm}: {e}")
            return []
    
    async def clear_message_queue(self, realm: str):
        """Clear message queue for realm."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("clear_message_queue_start", success=True)
            
            self.realm_queues[realm] = []
            self.logger.info(f"✅ Message queue cleared for {realm}")
            
            # Record success metric
            await self.record_health_metric("clear_message_queue_success", 1.0, {"realm": realm})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("clear_message_queue_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "clear_message_queue")
            self.logger.error(f"❌ Failed to clear message queue for {realm}: {e}")
            raise
    
    async def get_messaging_stats(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get messaging statistics."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_messaging_stats_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "messaging_stats", "read"):
                        await self.record_health_metric("get_messaging_stats_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_messaging_stats_complete", success=False)
                        return {}
            
            result = {
                "total_queues": len(self.realm_queues),
                "queue_sizes": {realm: len(queue) for realm, queue in self.realm_queues.items()},
                "is_running": self.is_running,
                "is_initialized": self.is_initialized
            }
            
            # Record success metric
            await self.record_health_metric("get_messaging_stats_success", 1.0, {"total_queues": len(self.realm_queues)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_messaging_stats_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_messaging_stats")
            self.logger.error(f"❌ Failed to get messaging stats: {e}")
            return {}



