#!/usr/bin/env python3
"""
AGUI Composition Service - Layer 3 of 5-Layer Architecture

Composition service for AGUI capabilities.
Orchestrates AGUI abstractions and Post Office infrastructure for agentic communication.

WHAT (Business Role): I orchestrate AGUI operations for agentic business logic
HOW (Composition Service): I coordinate AGUI abstractions and Post Office infrastructure
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
import uuid

from ..infrastructure_abstractions.agui_communication_abstraction import AGUICommunicationAbstraction
from ..abstraction_contracts.agui_communication_protocol import AGUIMessage, AGUIResponse, AGUIEvent


class AGUICompositionService:
    """
    AGUI Composition Service - Layer 3 of 5-Layer Architecture
    
    Orchestrates AGUI abstractions and Post Office infrastructure for agentic communication.
    Handles business logic for AGUI operations including message routing and delivery.
    """
    
    def __init__(self, agui_communication_abstraction: AGUICommunicationAbstraction,
                 post_office_service=None, di_container=None):
        """
        Initialize AGUI composition service.
        
        Args:
            agui_communication_abstraction: AGUI communication abstraction instance
            post_office_service: Post Office service for message delivery
            di_container: DI Container for utilities
        """
        self.agui_communication = agui_communication_abstraction
        self.post_office_service = post_office_service
        self.di_container = di_container
        self.service_name = "agui_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("AGUICompositionService")
        
        # Service status
        self.is_initialized = False
        
        # Business metrics
        self.business_metrics = {
            "total_messages_sent": 0,
            "total_events_broadcast": 0,
            "successful_deliveries": 0,
            "failed_deliveries": 0,
            "post_office_deliveries": 0,
            "websocket_deliveries": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        # Initialize service
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the composition service."""
        try:
            # Register default handlers
            self._register_default_handlers()
            
            self.logger.info("✅ AGUI composition service initialized")
            self.is_initialized = True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AGUI composition service: {e}")
            self.is_initialized = False
    
    def _register_default_handlers(self):
        """Register default AGUI handlers."""
        # Register agent status handler
        self.agui_communication.register_message_handler(
            "agent_status", self._handle_agent_status
        )
        
        # Register agent action handler
        self.agui_communication.register_message_handler(
            "agent_action", self._handle_agent_action
        )
        
        # Register agent response handler
        self.agui_communication.register_message_handler(
            "agent_response", self._handle_agent_response
        )
        
        # Register system event handler
        self.agui_communication.register_event_handler(
            "system_event", self._handle_system_event
        )
        
        # Register agent event handler
        self.agui_communication.register_event_handler(
            "agent_event",             self._handle_agent_event
        )
    
    # ============================================================================
    # SECURITY AND MULTI-TENANCY VALIDATION HELPERS
    # ============================================================================
    
    async def _validate_security_and_tenant(self, user_context: Dict[str, Any], 
                                           resource: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Validate security context and tenant access.
        
        Args:
            user_context: User context with user_id, tenant_id, security_context
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            # Get utilities from DI container
            security = self.di_container.get_utility("security") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            tenant = self.di_container.get_utility("tenant") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            
            user_id = user_context.get("user_id")
            tenant_id = user_context.get("tenant_id")
            security_context = user_context.get("security_context")
            
            # Security validation (if security utility available and context provided)
            if security and security_context:
                try:
                    # Validate user permission
                    has_permission = await security.validate_user_permission(
                        user_id, resource, action, 
                        security_context.get("permissions", [])
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "error": f"Permission denied: {action} on {resource}",
                            "error_code": "PERMISSION_DENIED"
                        }
                except Exception as e:
                    self.logger.warning(f"Security validation failed: {e}")
                    # Don't fail on security validation errors - log and continue
                    # (security might not be fully bootstrapped)
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        # For cross-tenant access, this would be handled at foundation service level
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            return {
                                "success": False,
                                "error": f"Tenant access denied for tenant: {tenant_id}",
                                "error_code": "TENANT_ACCESS_DENIED"
                            }
                except Exception as e:
                    self.logger.warning(f"Tenant validation failed: {e}")
                    # Don't fail on tenant validation errors - log and continue
            
            return None  # Validation passed
            
        except Exception as e:
            self.logger.error(f"Security/tenant validation error: {e}")
            # Don't fail on validation errors - log and continue
            return None
    
    # ============================================================================
    # AGENTIC AGUI CAPABILITIES
    # ============================================================================
    
    async def send_agent_status(self, connection_id: str, agent_id: str, 
                              status: str, details: Dict[str, Any] = None,
                              user_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send agent status update.
        
        Args:
            connection_id: Connection ID
            agent_id: Agent ID
            status: Agent status
            details: Additional details
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            bool: Success status
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "agui", "send"
                )
                if validation_error:
                    return False
            
            message = AGUIMessage(
                message_id=str(uuid.uuid4()),
                action="agent_status",
                payload={
                    "agent_id": agent_id,
                    "status": status,
                    "details": details or {},
                    "timestamp": datetime.now().isoformat()
                },
                timestamp=datetime.now(),
                connection_id=connection_id
            )
            
            success = await self.agui_communication.send_message(connection_id, message)
            
            if success:
                self.logger.info(f"Agent status sent to {connection_id}: {agent_id} - {status}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("send_agent_status", {
                        "agent_id": agent_id,
                        "status": status,
                        "success": True
                    })
            
            return success
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "send_agent_status",
                    "connection_id": connection_id,
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to send agent status: {e}")
            return False
    
    async def broadcast_agent_status(self, agent_id: str, status: str, 
                                   details: Dict[str, Any] = None,
                                   exclude_connections: List[str] = None,
                                   user_context: Optional[Dict[str, Any]] = None) -> int:
        """
        Broadcast agent status update.
        
        Args:
            agent_id: Agent ID
            status: Agent status
            details: Additional details
            exclude_connections: Connections to exclude
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            int: Number of connections that received the update
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "agui", "broadcast"
                )
                if validation_error:
                    return 0
            
            message = AGUIMessage(
                message_id=str(uuid.uuid4()),
                action="agent_status",
                payload={
                    "agent_id": agent_id,
                    "status": status,
                    "details": details or {},
                    "timestamp": datetime.now().isoformat()
                },
                timestamp=datetime.now(),
                connection_id="broadcast"
            )
            
            sent_count = await self.agui_communication.broadcast_message(
                message, exclude_connections
            )
            
            self.logger.info(f"Agent status broadcasted to {sent_count} connections: {agent_id} - {status}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("broadcast_agent_status", {
                    "agent_id": agent_id,
                    "status": status,
                    "sent_count": sent_count,
                    "success": True
                })
            
            return sent_count
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "broadcast_agent_status",
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to broadcast agent status: {e}")
            return 0
    
    async def send_agent_action(self, connection_id: str, agent_id: str, 
                              action: str, parameters: Dict[str, Any] = None,
                              user_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send agent action request.
        
        Args:
            connection_id: Connection ID
            agent_id: Agent ID
            action: Action to perform
            parameters: Action parameters
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            bool: Success status
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "agui", "send"
                )
                if validation_error:
                    return False
            
            message = AGUIMessage(
                message_id=str(uuid.uuid4()),
                action="agent_action",
                payload={
                    "agent_id": agent_id,
                    "action": action,
                    "parameters": parameters or {},
                    "timestamp": datetime.now().isoformat()
                },
                timestamp=datetime.now(),
                connection_id=connection_id
            )
            
            success = await self.agui_communication.send_message(connection_id, message)
            
            if success:
                self.logger.info(f"Agent action sent to {connection_id}: {agent_id} - {action}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("send_agent_action", {
                        "agent_id": agent_id,
                        "action": action,
                        "success": True
                    })
            
            return success
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "send_agent_action",
                    "connection_id": connection_id,
                    "agent_id": agent_id,
                    "action": action,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to send agent action: {e}")
            return False
    
    async def send_agent_response(self, connection_id: str, agent_id: str, 
                                response_data: Dict[str, Any], 
                                success: bool = True,
                                user_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send agent response.
        
        Args:
            connection_id: Connection ID
            agent_id: Agent ID
            response_data: Response data
            success: Success status
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            bool: Success status
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "agui", "send"
                )
                if validation_error:
                    return False
            
            message = AGUIMessage(
                message_id=str(uuid.uuid4()),
                action="agent_response",
                payload={
                    "agent_id": agent_id,
                    "response_data": response_data,
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                },
                timestamp=datetime.now(),
                connection_id=connection_id
            )
            
            success = await self.agui_communication.send_message(connection_id, message)
            
            if success:
                self.logger.info(f"Agent response sent to {connection_id}: {agent_id}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("send_agent_response", {
                        "agent_id": agent_id,
                        "success": True
                    })
            
            return success
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "send_agent_response",
                    "connection_id": connection_id,
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to send agent response: {e}")
            return False
    
    async def send_system_event(self, event_type: str, event_data: Dict[str, Any],
                              connection_id: str = None,
                              user_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send system event.
        
        Args:
            event_type: Event type
            event_data: Event data
            connection_id: Specific connection (None for broadcast)
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            bool: Success status
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "agui", "send"
                )
                if validation_error:
                    return False
            
            event = AGUIEvent(
                event_id=str(uuid.uuid4()),
                event_type="system_event",
                data={
                    "system_event_type": event_type,
                    "event_data": event_data,
                    "timestamp": datetime.now().isoformat()
                },
                timestamp=datetime.now(),
                connection_id=connection_id or "system"
            )
            
            if connection_id:
                success = await self.agui_communication.send_event(connection_id, event)
            else:
                sent_count = await self.agui_communication.broadcast_event(event)
                success = sent_count > 0
            
            if success:
                self.logger.info(f"System event sent: {event_type}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("send_system_event", {
                        "event_type": event_type,
                        "success": True
                    })
            
            return success
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "send_system_event",
                    "event_type": event_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to send system event: {e}")
            return False
    
    async def send_agent_event(self, agent_id: str, event_type: str, 
                             event_data: Dict[str, Any],
                             connection_id: str = None,
                             user_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send agent event.
        
        Args:
            agent_id: Agent ID
            event_type: Event type
            event_data: Event data
            connection_id: Specific connection (None for broadcast)
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            bool: Success status
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "agui", "send"
                )
                if validation_error:
                    return False
            
            event = AGUIEvent(
                event_id=str(uuid.uuid4()),
                event_type="agent_event",
                data={
                    "agent_id": agent_id,
                    "agent_event_type": event_type,
                    "event_data": event_data,
                    "timestamp": datetime.now().isoformat()
                },
                timestamp=datetime.now(),
                connection_id=connection_id or "agent"
            )
            
            if connection_id:
                success = await self.agui_communication.send_event(connection_id, event)
            else:
                sent_count = await self.agui_communication.broadcast_event(event)
                success = sent_count > 0
            
            if success:
                self.logger.info(f"Agent event sent: {agent_id} - {event_type}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("send_agent_event", {
                        "agent_id": agent_id,
                        "event_type": event_type,
                        "success": True
                    })
            
            return success
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "send_agent_event",
                    "agent_id": agent_id,
                    "event_type": event_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to send agent event: {e}")
            return False
    
    # ============================================================================
    # MESSAGE HANDLERS
    # ============================================================================
    
    async def _handle_agent_status(self, message: AGUIMessage) -> AGUIResponse:
        """Handle agent status message."""
        try:
            agent_id = message.payload.get("agent_id")
            status = message.payload.get("status")
            
            self.logger.info(f"Agent status received: {agent_id} - {status}")
            
            return AGUIResponse(
                response_id=str(uuid.uuid4()),
                message_id=message.message_id,
                success=True,
                data={"acknowledged": True},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle agent status: {e}")
            return AGUIResponse(
                response_id=str(uuid.uuid4()),
                message_id=message.message_id,
                success=False,
                error=str(e),
                timestamp=datetime.now()
            )
    
    async def _handle_agent_action(self, message: AGUIMessage) -> AGUIResponse:
        """Handle agent action message."""
        try:
            agent_id = message.payload.get("agent_id")
            action = message.payload.get("action")
            parameters = message.payload.get("parameters", {})
            
            self.logger.info(f"Agent action received: {agent_id} - {action}")
            
            # Process action (placeholder)
            result = {"action": action, "parameters": parameters, "processed": True}
            
            return AGUIResponse(
                response_id=str(uuid.uuid4()),
                message_id=message.message_id,
                success=True,
                data=result,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle agent action: {e}")
            return AGUIResponse(
                response_id=str(uuid.uuid4()),
                message_id=message.message_id,
                success=False,
                error=str(e),
                timestamp=datetime.now()
            )
    
    async def _handle_agent_response(self, message: AGUIMessage) -> AGUIResponse:
        """Handle agent response message."""
        try:
            agent_id = message.payload.get("agent_id")
            response_data = message.payload.get("response_data", {})
            
            self.logger.info(f"Agent response received: {agent_id}")
            
            return AGUIResponse(
                response_id=str(uuid.uuid4()),
                message_id=message.message_id,
                success=True,
                data={"acknowledged": True},
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle agent response: {e}")
            return AGUIResponse(
                response_id=str(uuid.uuid4()),
                message_id=message.message_id,
                success=False,
                error=str(e),
                timestamp=datetime.now()
            )
    
    async def _handle_system_event(self, event: AGUIEvent):
        """Handle system event."""
        try:
            event_type = event.data.get("system_event_type")
            event_data = event.data.get("event_data", {})
            
            self.logger.info(f"System event received: {event_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to handle system event: {e}")
    
    async def _handle_agent_event(self, event: AGUIEvent):
        """Handle agent event."""
        try:
            agent_id = event.data.get("agent_id")
            event_type = event.data.get("agent_event_type")
            event_data = event.data.get("event_data", {})
            
            self.logger.info(f"Agent event received: {agent_id} - {event_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to handle agent event: {e}")
    
    # ============================================================================
    # SERVICE MANAGEMENT
    # ============================================================================
    
    async def get_service_status(self) -> Dict[str, Any]:
        """
        Get composition service status.
        
        Returns:
            Dict: Service status
        """
        try:
            # Get AGUI communication status
            agui_health = await self.agui_communication.health_check()
            
            result = {
                "service": "AGUICompositionService",
                "initialized": self.is_initialized,
                "agui_communication": agui_health,
                "timestamp": datetime.now().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_service_status", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_service_status",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get service status: {e}")
            return {
                "service": "AGUICompositionService",
                "initialized": self.is_initialized,
                "error": str(e),
                "error_code": "AGUI_SERVICE_STATUS_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all components.
        
        Returns:
            Dict: Health check result
        """
        try:
            health_status = {
                "healthy": True,
                "components": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Check AGUI communication
            try:
                agui_health = await self.agui_communication.health_check()
                health_status["components"]["agui_communication"] = agui_health
                
                if not agui_health.get("healthy", False):
                    health_status["healthy"] = False
                    
            except Exception as e:
                health_status["components"]["agui_communication"] = {
                    "healthy": False,
                    "error": str(e)
                }
                health_status["healthy"] = False
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("health_check", {
                    "healthy": health_status.get("healthy", False),
                    "success": True
                })
            
            return health_status
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "health_check",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "error_code": "AGUI_HEALTH_CHECK_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    # ============================================================================
    # POST OFFICE INTEGRATION
    # ============================================================================
    
    async def deliver_agui_message_via_post_office(self, agui_message: AGUIMessage, 
                                                  recipient_id: str = None,
                                                  tenant_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Deliver AGUI message via Post Office service.
        
        Args:
            agui_message: AGUI message to deliver
            recipient_id: Specific recipient ID (if None, broadcasts)
            tenant_context: Tenant context for multi-tenancy
            
        Returns:
            Dict containing delivery result
        """
        try:
            if not self.post_office_service:
                return {
                    "success": False,
                    "error": "Post Office service not available",
                    "delivery_method": "none"
                }
            
            # Create message data for Post Office
            message_data = {
                "recipient_id": recipient_id or "broadcast",
                "content": agui_message.payload,
                "message_type": "agui_message",
                "sender_id": agui_message.payload.get("agent_id", "system"),
                "priority": "normal",
                "agui_action": agui_message.action,
                "agui_message_id": agui_message.message_id
            }
            
            # Send via Post Office
            result = await self.post_office_service.send_message(message_data, tenant_context)
            
            if result.get("status") == "success":
                self.business_metrics["post_office_deliveries"] += 1
                self.business_metrics["successful_deliveries"] += 1
                self.business_metrics["last_updated"] = datetime.now().isoformat()
                
                return {
                    "success": True,
                    "delivery_method": "post_office",
                    "delivery_id": result.get("message_id"),
                    "recipient_id": recipient_id or "broadcast"
                }
            else:
                self.business_metrics["failed_deliveries"] += 1
                self.business_metrics["last_updated"] = datetime.now().isoformat()
                
                return {
                    "success": False,
                    "error": result.get("message", "Post Office delivery failed"),
                    "delivery_method": "post_office"
                }
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "deliver_agui_message_via_post_office",
                    "recipient_id": recipient_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to deliver AGUI message via Post Office: {e}")
            self.business_metrics["failed_deliveries"] += 1
            self.business_metrics["last_updated"] = datetime.now().isoformat()
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "AGUI_POST_OFFICE_DELIVERY_ERROR",
                "delivery_method": "post_office"
            }
    
    async def deliver_agui_event_via_post_office(self, agui_event: AGUIEvent,
                                               recipient_id: str = None,
                                               tenant_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Deliver AGUI event via Post Office service.
        
        Args:
            agui_event: AGUI event to deliver
            recipient_id: Specific recipient ID (if None, broadcasts)
            tenant_context: Tenant context for multi-tenancy
            
        Returns:
            Dict containing delivery result
        """
        try:
            if not self.post_office_service:
                return {
                    "success": False,
                    "error": "Post Office service not available",
                    "delivery_method": "none"
                }
            
            # Create event data for Post Office
            event_data = {
                "recipient_id": recipient_id or "broadcast",
                "content": agui_event.data,
                "message_type": "agui_event",
                "sender_id": agui_event.data.get("agent_id", "system"),
                "priority": "normal",
                "agui_event_type": agui_event.event_type,
                "agui_event_id": agui_event.event_id
            }
            
            # Send via Post Office
            result = await self.post_office_service.send_message(event_data, tenant_context)
            
            if result.get("status") == "success":
                self.business_metrics["post_office_deliveries"] += 1
                self.business_metrics["successful_deliveries"] += 1
                self.business_metrics["last_updated"] = datetime.now().isoformat()
                
                return {
                    "success": True,
                    "delivery_method": "post_office",
                    "delivery_id": result.get("message_id"),
                    "recipient_id": recipient_id or "broadcast"
                }
            else:
                self.business_metrics["failed_deliveries"] += 1
                self.business_metrics["last_updated"] = datetime.now().isoformat()
                
                return {
                    "success": False,
                    "error": result.get("message", "Post Office delivery failed"),
                    "delivery_method": "post_office"
                }
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "deliver_agui_event_via_post_office",
                    "recipient_id": recipient_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to deliver AGUI event via Post Office: {e}")
            self.business_metrics["failed_deliveries"] += 1
            self.business_metrics["last_updated"] = datetime.now().isoformat()
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "AGUI_POST_OFFICE_EVENT_DELIVERY_ERROR",
                "delivery_method": "post_office"
            }
    
    def get_business_metrics(self) -> Dict[str, Any]:
        """Get business metrics for AGUI operations."""
        return self.business_metrics.copy()
    
    def get_composition_health(self) -> Dict[str, Any]:
        """Get AGUI composition service health status."""
        return {
            "service_name": "AGUICompositionService",
            "post_office_available": self.post_office_service is not None,
            "agui_communication_available": self.agui_communication is not None,
            "business_metrics": self.get_business_metrics(),
            "is_initialized": self.is_initialized,
            "status": "healthy"
        }


