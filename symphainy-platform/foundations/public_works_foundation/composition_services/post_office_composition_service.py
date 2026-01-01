#!/usr/bin/env python3
"""
Post Office Composition Service - Layer 4 of 5-Layer Architecture

Orchestrates event and messaging abstractions for Post Office operations.
This service composes event and messaging infrastructure to provide
business-facing Post Office capabilities.

WHAT (Composition Role): I orchestrate events and messaging for Post Office
HOW (Composition Implementation): I compose event and messaging abstractions into Post Office capabilities
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

from foundations.public_works_foundation.infrastructure_abstractions.event_management_abstraction import EventManagementAbstraction
from foundations.public_works_foundation.infrastructure_abstractions.messaging_abstraction import MessagingAbstraction
from foundations.public_works_foundation.abstraction_contracts.event_management_protocol import EventPriority, EventStatus
from foundations.public_works_foundation.abstraction_contracts.messaging_protocol import MessagePriority, MessageType, MessageStatus

logger = logging.getLogger(__name__)


class PostOfficeCompositionService:
    """
    Post Office Composition Service.
    
    Orchestrates event and messaging abstractions to provide
    comprehensive Post Office capabilities including event routing,
    message delivery, and communication coordination.
    """
    
    def __init__(self, event_management: EventManagementAbstraction,
                 messaging: MessagingAbstraction, di_container=None):
        """Initialize Post Office Composition Service with abstractions."""
        self.event_management = event_management
        self.messaging = messaging
        self.di_container = di_container
        self.service_name = "post_office_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("PostOfficeCompositionService")
        
        # Post Office state
        self.active_agents: Dict[str, Dict[str, Any]] = {}
        self.message_queues: Dict[str, List[str]] = {}
        self.event_subscriptions: Dict[str, List[str]] = {}
        self.post_office_metrics: Dict[str, Any] = {
            "total_events": 0,
            "total_messages": 0,
            "active_agents": 0,
            "successful_deliveries": 0,
            "failed_deliveries": 0,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        self.logger.info("✅ Post Office Composition Service initialized")
    
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
    

    async def route_event(self, event_type: str, source: str, target: str, 
                         event_data: Dict[str, Any], priority: EventPriority = EventPriority.NORMAL,
                         tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Route an event to appropriate handlers.
        
        This is the core event routing functionality - routing events
        to appropriate services based on event type and target.
        """
        try:
            self.logger.info(f"Routing event {event_type} from {source} to {target}")
            
            # Publish event using event management
            event_context = await self.event_management.publish_event(
                event_type=event_type,
                source=source,
                target=target,
                event_data=event_data,
                priority=priority,
                tenant_id=tenant_id
            )
            
            if event_context:
                # Update metrics
                self.post_office_metrics["total_events"] += 1
                self.post_office_metrics["last_updated"] = datetime.utcnow().isoformat()
                
                self.logger.info(f"✅ Event {event_context.event_id} routed from {source} to {target}")
                
                # Record platform operation event
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("route_event", {
                        "event_type": event_type,
                        "source": source,
                        "target": target,
                        "event_id": event_context.event_id,
                        "success": True
                    })
                
                return {
                    "success": True,
                    "event_id": event_context.event_id,
                    "event_type": event_type,
                    "source": source,
                    "target": target,
                    "routed_at": datetime.utcnow().isoformat()
                }
            else:
                self.post_office_metrics["failed_deliveries"] += 1
                self.logger.error(f"❌ Failed to route event {event_type} from {source} to {target}")
                
                return {
                    "success": False,
                    "error": "Failed to route event",
                    "event_type": event_type,
                    "source": source,
                    "target": target
                }
                
        except Exception as e:
            self.post_office_metrics["failed_deliveries"] += 1
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "route_event",
                    "event_type": event_type,
                    "source": source,
                    "target": target,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error routing event {event_type}: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "EVENT_ROUTING_ERROR",
                "event_type": event_type,
                "source": source,
                "target": target
            }
    
    async def send_message(self, message_type: MessageType, sender: str, recipient: str,
                         message_content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL,
                         tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a message to a recipient.
        """
        try:
            self.logger.info(f"Sending {message_type.value} message from {sender} to {recipient}")
            
            # Send message using messaging abstraction
            message_context = await self.messaging.send_message(
                message_type=message_type,
                sender=sender,
                recipient=recipient,
                message_content=message_content,
                priority=priority,
                tenant_id=tenant_id
            )
            
            if message_context:
                # Update metrics
                self.post_office_metrics["total_messages"] += 1
                self.post_office_metrics["successful_deliveries"] += 1
                self.post_office_metrics["last_updated"] = datetime.utcnow().isoformat()
                
                self.logger.info(f"✅ Message {message_context.message_id} sent from {sender} to {recipient}")
                
                # Record platform operation event
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("send_message", {
                        "message_type": message_type.value,
                        "sender": sender,
                        "recipient": recipient,
                        "message_id": message_context.message_id,
                        "success": True
                    })
                
                return {
                    "success": True,
                    "message_id": message_context.message_id,
                    "message_type": message_type.value,
                    "sender": sender,
                    "recipient": recipient,
                    "sent_at": datetime.utcnow().isoformat()
                }
            else:
                self.post_office_metrics["failed_deliveries"] += 1
                self.logger.error(f"❌ Failed to send message from {sender} to {recipient}")
                
                return {
                    "success": False,
                    "error": "Failed to send message",
                    "sender": sender,
                    "recipient": recipient
                }
                
        except Exception as e:
            self.post_office_metrics["failed_deliveries"] += 1
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "send_message",
                    "message_type": message_type.value,
                    "sender": sender,
                    "recipient": recipient,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error sending message: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "MESSAGE_SEND_ERROR",
                "sender": sender,
                "recipient": recipient
            }
    
    async def send_broadcast_message(self, message_type: MessageType, sender: str, recipients: List[str],
                                   message_content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL,
                                   tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a broadcast message to multiple recipients.
        """
        try:
            self.logger.info(f"Broadcasting {message_type.value} message from {sender} to {len(recipients)} recipients")
            
            # Send broadcast message using messaging abstraction
            message_contexts = await self.messaging.send_broadcast_message(
                message_type=message_type,
                sender=sender,
                recipients=recipients,
                message_content=message_content,
                priority=priority,
                tenant_id=tenant_id
            )
            
            # Update metrics
            self.post_office_metrics["total_messages"] += len(message_contexts)
            self.post_office_metrics["successful_deliveries"] += len(message_contexts)
            self.post_office_metrics["last_updated"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"✅ Broadcast message sent to {len(message_contexts)} recipients")
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("send_broadcast_message", {
                    "message_type": message_type.value,
                    "sender": sender,
                    "recipient_count": len(message_contexts),
                    "success": True
                })
            
            return {
                "success": True,
                "message_count": len(message_contexts),
                "message_type": message_type.value,
                "sender": sender,
                "recipients": recipients,
                "sent_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "send_broadcast_message",
                    "message_type": message_type.value,
                    "sender": sender,
                    "recipient_count": len(recipients),
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error sending broadcast message: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "BROADCAST_MESSAGE_ERROR",
                "sender": sender,
                "recipients": recipients
            }
    
    async def register_agent(self, agent_id: str, agent_type: str, capabilities: List[str],
                           tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Register an agent with the Post Office.
        """
        try:
            self.logger.info(f"Registering agent {agent_id} of type {agent_type}")
            
            # Store agent information
            self.active_agents[agent_id] = {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "capabilities": capabilities,
                "tenant_id": tenant_id,
                "registered_at": datetime.utcnow(),
                "status": "active"
            }
            
            # Update metrics
            self.post_office_metrics["active_agents"] = len(self.active_agents)
            self.post_office_metrics["last_updated"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"✅ Agent {agent_id} registered successfully")
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("register_agent", {
                    "agent_id": agent_id,
                    "agent_type": agent_type,
                    "success": True
                })
            
            return {
                "success": True,
                "agent_id": agent_id,
                "agent_type": agent_type,
                "capabilities": capabilities,
                "registered_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "register_agent",
                    "agent_id": agent_id,
                    "agent_type": agent_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error registering agent {agent_id}: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "AGENT_REGISTRATION_ERROR",
                "agent_id": agent_id
            }
    
    async def unregister_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Unregister an agent from the Post Office.
        """
        try:
            self.logger.info(f"Unregistering agent {agent_id}")
            
            if agent_id in self.active_agents:
                del self.active_agents[agent_id]
                
                # Update metrics
                self.post_office_metrics["active_agents"] = len(self.active_agents)
                self.post_office_metrics["last_updated"] = datetime.utcnow().isoformat()
                
                self.logger.info(f"✅ Agent {agent_id} unregistered successfully")
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "unregistered_at": datetime.utcnow().isoformat()
                }
            else:
                self.logger.warning(f"⚠️ Agent {agent_id} not found")
                
                return {
                    "success": False,
                    "error": "Agent not found",
                    "agent_id": agent_id
                }
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "unregister_agent",
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error unregistering agent {agent_id}: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "AGENT_UNREGISTRATION_ERROR",
                "agent_id": agent_id
            }
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent status.
        """
        try:
            if agent_id in self.active_agents:
                agent_info = self.active_agents[agent_id]
                return {
                    "agent_id": agent_info["agent_id"],
                    "agent_type": agent_info["agent_type"],
                    "capabilities": agent_info["capabilities"],
                    "status": agent_info["status"],
                    "registered_at": agent_info["registered_at"].isoformat(),
                    "tenant_id": agent_info.get("tenant_id")
                }
            else:
                return None
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_agent_status",
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error getting agent status {agent_id}: {e}")
            return None
    
    async def get_messages_for_agent(self, agent_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get messages for a specific agent.
        """
        try:
            messages = await self.messaging.get_messages_for_recipient(agent_id, limit)
            
            # Convert to dict format
            message_dicts = []
            for message in messages:
                message_dicts.append({
                    "message_id": message.message_id,
                    "message_type": message.message_type.value,
                    "sender": message.sender,
                    "recipient": message.recipient,
                    "priority": message.priority.value,
                    "status": message.status.value,
                    "created_at": message.created_at.isoformat(),
                    "message_content": message.message_content
                })
            
            self.logger.debug(f"✅ Retrieved {len(message_dicts)} messages for agent {agent_id}")
            return message_dicts
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_messages_for_agent",
                    "agent_id": agent_id,
                    "limit": limit,
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error getting messages for agent {agent_id}: {e}")
            return []
    
    async def acknowledge_message(self, message_id: str) -> bool:
        """
        Acknowledge a message.
        """
        try:
            success = await self.messaging.acknowledge_message(message_id)
            if success:
                self.logger.info(f"✅ Message {message_id} acknowledged")
            return success
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "acknowledge_message",
                    "message_id": message_id,
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error acknowledging message {message_id}: {e}")
            return False
    
    async def get_post_office_metrics(self) -> Dict[str, Any]:
        """
        Get Post Office metrics.
        """
        try:
            # Get metrics from abstractions
            event_metrics = await self.event_management.get_event_metrics()
            messaging_metrics = await self.messaging.get_message_metrics()
            
            # Combine metrics
            combined_metrics = {
                "post_office_metrics": self.post_office_metrics,
                "event_metrics": event_metrics,
                "messaging_metrics": messaging_metrics,
                "composition_service": "PostOfficeCompositionService",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return combined_metrics
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_post_office_metrics",
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error getting Post Office metrics: {e}")
            return {
                "post_office_metrics": self.post_office_metrics,
                "error": str(e),
                "error_code": "POST_OFFICE_METRICS_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def cleanup_old_data(self, older_than_hours: int = 24) -> Dict[str, int]:
        """
        Clean up old events and messages.
        """
        try:
            self.logger.info(f"Cleaning up data older than {older_than_hours} hours")
            
            # Clean up processed events
            events_cleaned = await self.event_management.cleanup_processed_events(older_than_hours)
            
            # Clean up old messages
            messages_cleaned = await self.messaging.cleanup_old_messages(older_than_hours)
            
            self.logger.info(f"✅ Cleaned up {events_cleaned} events and {messages_cleaned} messages")
            
            return {
                "events_cleaned": events_cleaned,
                "messages_cleaned": messages_cleaned,
                "total_cleaned": events_cleaned + messages_cleaned
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "cleanup_old_data",
                    "older_than_hours": older_than_hours,
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error cleaning up old data: {e}")
            return {
                "events_cleaned": 0,
                "messages_cleaned": 0,
                "total_cleaned": 0,
                "error": str(e),
                "error_code": "CLEANUP_ERROR"
            }



