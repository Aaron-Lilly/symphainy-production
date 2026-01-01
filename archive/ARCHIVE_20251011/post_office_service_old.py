#!/usr/bin/env python3
"""
Post Office Service - Multi-Tenant

Production-ready Smart City service for comprehensive event routing, messaging,
AGUI agent communication, and cross-dimensional coordination with multi-tenant
awareness and proper tenant isolation.

WHAT (Smart City Role): I manage all event routing, messaging, and agent communication with tenant awareness
HOW (Service Implementation): I use Public Works abstractions and advanced event management with tenant isolation
"""

import os
import sys
import uuid
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../'))

from bases.soa_service_base import SOAServiceBase
from backend.smart_city.protocols.soa_service_protocol import SOAServiceProtocol, SOAEndpoint, SOAServiceInfo
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation import CuratorFoundationService
from utilities import UserContext
from config.environment_loader import EnvironmentLoader
from config import Environment
from foundations.infrastructure_foundation.abstractions.redis_streams_abstraction import RedisStreamsAbstraction

# Import micro-modules
from .micro_modules.event_routing_redis import EventRoutingModule
from .micro_modules.messaging_redis import MessagingModule
from .micro_modules.agui_communication import AGUICommunicationModule
from .micro_modules.notification import NotificationModule

# Import interfaces (for consumers, not implementers)
from backend.smart_city.interfaces import (
    IEventRouting, IAGUICommunication, EventType, MessagePriority, DeliveryGuarantee,
    EventScope, Event, Message, EventPublishRequest, EventPublishResponse,
    EventSubscribeRequest, EventSubscribeResponse, MessageSendRequest, MessageSendResponse,
    EventCorrelationRequest, EventCorrelationResponse, AGUIMessageRequest, AGUIMessageResponse,
    EventReplayRequest, EventReplayResponse
)
from bases.soa_service_base import SOAServiceBase, SOAServiceProtocol, SOAEndpoint, SOAServiceInfo


class PostOfficeService(SOAServiceBase):
    """
    Post Office Service - Multi-Tenant

    Production-ready Smart City service that manages comprehensive event routing,
    messaging, AGUI agent communication, and cross-dimensional coordination
    with multi-tenant awareness and proper tenant isolation.
    
    WHAT (Smart City Role): I manage all event routing, messaging, and agent communication with tenant awareness
    HOW (Service Implementation): I use Public Works abstractions and advanced event management with tenant isolation
    """

    def __init__(self, utility_foundation=None, public_works_foundation=None, curator_foundation=None, environment=Environment.DEVELOPMENT):
        """Initialize Post Office Service with multi-tenant capabilities."""
        super().__init__("PostOfficeService", utility_foundation, curator_foundation)
        
        self.public_works_foundation = public_works_foundation
        self.env_loader = EnvironmentLoader(environment)
        
        # Multi-tenant coordination service
        self.multi_tenant_coordinator = None
        if self.public_works_foundation:
            self.multi_tenant_coordinator = self.public_works_foundation.multi_tenant_coordination_service
        
        # Smart city abstractions from public works
        self.smart_city_abstractions = {}
        
        # Initialize SOA protocol
        self.soa_protocol = PostOfficeSOAProtocol("PostOfficeService", self, curator_foundation), public_works_foundation
        
        # Environment-specific configuration
        self.config = self.env_loader.get_all_config()
        self.api_config = self.env_loader.get_api_config()
        self.feature_flags = self.env_loader.get_feature_flags()
        
        # Initialize Redis Streams abstraction
        self.redis_streams_abstraction = RedisStreamsAbstraction(
            host="localhost",
            port=6379,
            password=None,
            graph_name="post_office"
        )

        # Initialize micro-modules after parent initialization
        self.event_routing_module = EventRoutingModule(self.logger, self.env_loader, self.redis_streams_abstraction)
        self.messaging_module = MessagingModule(self.logger, self.env_loader, self.redis_streams_abstraction)
        self.agui_communication_module = AGUICommunicationModule(self.logger, self.env_loader)
        self.notification_module = NotificationModule(self.logger, self.env_loader)

        # Service capabilities
        self.capabilities = [
            "event_routing",
            "messaging",
            "agui_communication",
            "notification_management",
            "multi_tenant_event_routing"
        ]

        self.logger.info("📮 Post Office Service initialized - Multi-Tenant Event Routing Hub")

    async def initialize(self):
        """Initialize the Post Office Service with multi-tenant capabilities."""
        try:
            await super().initialize()
            
            self.logger.info("🚀 Initializing Post Office Service with multi-tenant capabilities...")

            # Initialize SOA protocol
            await self.soa_protocol.initialize()
            self.logger.info("✅ SOA Protocol initialized")

            # Initialize multi-tenant coordination
            if self.multi_tenant_coordinator:
                await self.multi_tenant_coordinator.initialize()
                self.logger.info("✅ Multi-tenant coordination initialized")
            
            # Load smart city abstractions from public works
            if self.public_works_foundation:
                await self.soa_protocol.load_smart_city_abstractions()
            self.smart_city_abstractions = self.soa_protocol.get_all_abstractions()
                self.logger.info(f"✅ Loaded {len(self.smart_city_abstractions)} smart city abstractions")
            
            # Initialize micro-modules
            await self.event_routing_module.initialize()
            await self.messaging_module.initialize()
            await self.agui_communication_module.initialize()
            await self.notification_module.initialize()

            self.logger.info("✅ Post Office Service initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Post Office Service: {e}")
            raise

    # ============================================================================
    # EVENT ROUTING INTERFACE IMPLEMENTATION
    # ============================================================================

    async def publish_event(self, event_data: Dict[str, Any], user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Publish an event to the routing system with tenant awareness."""
        try:
            # Validate tenant access
            if user_context and self.multi_tenant_coordinator:
                tenant_validation = await self.multi_tenant_coordinator.validate_tenant_feature_access(
                    user_context.tenant_id, "event_publishing"
                )
                if not tenant_validation.get("allowed", False):
                    return {
                        "success": False,
                        "error": "Insufficient tenant permissions for event publishing"
                    }
            
            # Add tenant context to event data
            if user_context and user_context.tenant_id:
                event_data["tenant_id"] = user_context.tenant_id
                event_data["published_by"] = user_context.user_id
            
            # Publish the event
            result = await self.event_routing_module.publish_event(event_data, user_context)
            
            if result.get("success"):
                # Record telemetry with tenant context
                await self.telemetry_service.record_metric(
                    "event_published", 1,
                    {
                        "event_type": event_data.get("event_type", "unknown"),
                        "tenant_id": user_context.tenant_id if user_context else "system"
                    }
                )
                
                # Audit the action
                if user_context:
                    await self.security_service.audit_user_action(
                        user_context, "publish_event", "post_office",
                        {
                            "event_type": event_data.get("event_type", "unknown"),
                            "event_id": result.get("event_id")
                        }
                    )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="post_office_publish_event")
            return {"success": False, "error": f"Event publishing failed: {str(e)}"}

    async def subscribe_to_events(self, subscription_data: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Subscribe to events matching the given criteria."""
        return await self.event_routing_module.subscribe_to_events(subscription_data, user_context)

    async def unsubscribe_from_events(self, subscription_id: str, user_context: Optional[Dict] = None) -> bool:
        """Unsubscribe from events."""
        return await self.event_routing_module.unsubscribe_from_events(subscription_id, user_context)

    async def get_events(self, filters: Optional[Dict[str, Any]] = None, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get events matching the given filters."""
        return await self.event_routing_module.get_events(filters, user_context)

    async def correlate_events(self, correlation_data: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Correlate events based on correlation criteria."""
        return await self.event_routing_module.correlate_events(correlation_data, user_context)

    async def replay_events(self, replay_data: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Replay events for a given time range or correlation ID."""
        return await self.event_routing_module.replay_events(replay_data, user_context)

    # ============================================================================
    # MESSAGING INTERFACE IMPLEMENTATION
    # ============================================================================

    async def send_message(self, message_data: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Send a message to recipients."""
        return await self.messaging_module.send_message(message_data, user_context)

    async def get_message_status(self, message_id: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get the status of a message."""
        return await self.messaging_module.get_message_status(message_id, user_context)

    async def cancel_message(self, message_id: str, user_context: Optional[Dict] = None) -> bool:
        """Cancel a pending message."""
        return await self.messaging_module.cancel_message(message_id, user_context)

    async def retry_message(self, message_id: str, user_context: Optional[Dict] = None) -> bool:
        """Retry a failed message."""
        return await self.messaging_module.retry_message(message_id, user_context)

    async def create_message_template(self, template_data: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a message template."""
        return await self.messaging_module.create_message_template(template_data, user_context)

    async def send_templated_message(self, template_id: str, template_data: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Send a message using a template."""
        return await self.messaging_module.send_templated_message(template_id, template_data, user_context)

    async def get_messages(self, filters: Optional[Dict[str, Any]] = None, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get messages matching the given filters."""
        return await self.messaging_module.get_messages(filters, user_context)

    # ============================================================================
    # AGUI COMMUNICATION INTERFACE IMPLEMENTATION
    # ============================================================================

    async def register_agent(self, agent_data: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Register an AGUI agent."""
        return await self.agui_communication_module.register_agent(agent_data, user_context)

    async def unregister_agent(self, agent_id: str, user_context: Optional[Dict] = None) -> bool:
        """Unregister an AGUI agent."""
        return await self.agui_communication_module.unregister_agent(agent_id, user_context)

    async def send_agent_message(self, message_data: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Send a message to an AGUI agent."""
        return await self.agui_communication_module.send_agent_message(message_data, user_context)

    async def broadcast_to_agents(self, broadcast_data: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Broadcast a message to multiple agents."""
        return await self.agui_communication_module.broadcast_to_agents(broadcast_data, user_context)

    async def get_agent_messages(self, agent_id: str, filters: Optional[Dict[str, Any]] = None, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get messages for a specific agent."""
        return await self.agui_communication_module.get_agent_messages(agent_id, filters, user_context)

    async def get_agent_status(self, agent_id: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get the status of a specific agent."""
        return await self.agui_communication_module.get_agent_status(agent_id, user_context)

    async def update_agent_heartbeat(self, agent_id: str, user_context: Optional[Dict] = None) -> bool:
        """Update agent heartbeat."""
        return await self.agui_communication_module.update_agent_heartbeat(agent_id, user_context)

    async def find_agents_by_capability(self, capability: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Find agents with a specific capability."""
        return await self.agui_communication_module.find_agents_by_capability(capability, user_context)

    # ============================================================================
    # NOTIFICATION MANAGEMENT
    # ============================================================================

    async def create_notification(self, notification_data: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a notification."""
        return await self.notification_module.create_notification(notification_data, user_context)

    async def get_notification(self, notification_id: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get a specific notification."""
        return await self.notification_module.get_notification(notification_id, user_context)

    async def mark_notification_read(self, notification_id: str, user_context: Optional[Dict] = None) -> bool:
        """Mark a notification as read."""
        return await self.notification_module.mark_notification_read(notification_id, user_context)

    async def get_user_notifications(self, user_id: str, filters: Optional[Dict[str, Any]] = None, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get notifications for a specific user."""
        return await self.notification_module.get_user_notifications(user_id, filters, user_context)

    async def create_notification_template(self, template_data: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a notification template."""
        return await self.notification_module.create_notification_template(template_data, user_context)

    async def send_templated_notification(self, template_id: str, template_data: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Send a notification using a template."""
        return await self.notification_module.send_templated_notification(template_id, template_data, user_context)

    async def set_user_preferences(self, user_id: str, preferences: Dict[str, Any], user_context: Optional[Dict] = None) -> bool:
        """Set notification preferences for a user."""
        return await self.notification_module.set_user_preferences(user_id, preferences, user_context)

    async def get_user_preferences(self, user_id: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get notification preferences for a user."""
        return await self.notification_module.get_user_preferences(user_id, user_context)

    # ============================================================================
    # SERVICE MANAGEMENT
    # ============================================================================

    async def get_service_info(self) -> Dict[str, Any]:
        """Get service information."""
        return {
            "service_name": self.service_name,
            "service_version": self.service_version,
            "capabilities": self.capabilities,
            "status": "healthy",
            "environment": self.env_loader.get_environment().value,
            "micro_modules": [
                "event_routing",
                "messaging", 
                "agui_communication",
                "notification"
            ]
        }

    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        try:
            # Get status from all micro-modules
            event_routing_status = await self.event_routing_module.get_status()
            messaging_status = await self.messaging_module.get_status()
            agui_communication_status = await self.agui_communication_module.get_status()
            notification_status = await self.notification_module.get_status()

            return {
                "service_name": self.service_name,
                "overall_status": "healthy",
                "environment": self.env_loader.get_environment().value,
                "micro_modules": {
                    "event_routing": event_routing_status,
                    "messaging": messaging_status,
                    "agui_communication": agui_communication_status,
                    "notification": notification_status
                },
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to get health status: {e}")
            return {
                "service_name": self.service_name,
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        try:
            # Get metrics from all micro-modules
            event_routing_status = await self.event_routing_module.get_status()
            messaging_status = await self.messaging_module.get_status()
            agui_communication_status = await self.agui_communication_module.get_status()
            notification_status = await self.notification_module.get_status()

            return {
                "service_name": self.service_name,
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {
                    "event_routing": {
                        "total_events": event_routing_status.get("total_events", 0),
                        "active_subscriptions": event_routing_status.get("active_subscriptions", 0),
                        "total_correlations": event_routing_status.get("total_correlations", 0)
                    },
                    "messaging": {
                        "total_messages": messaging_status.get("total_messages", 0),
                        "pending_messages": messaging_status.get("pending_messages", 0),
                        "delivered_messages": messaging_status.get("delivered_messages", 0),
                        "failed_messages": messaging_status.get("failed_messages", 0),
                        "total_templates": messaging_status.get("total_templates", 0)
                    },
                    "agui_communication": {
                        "total_agents": agui_communication_status.get("total_agents", 0),
                        "active_agents": agui_communication_status.get("active_agents", 0),
                        "online_agents": agui_communication_status.get("online_agents", 0),
                        "total_messages": agui_communication_status.get("total_messages", 0),
                        "total_capabilities": agui_communication_status.get("total_capabilities", 0)
                    },
                    "notification": {
                        "total_notifications": notification_status.get("total_notifications", 0),
                        "pending_notifications": notification_status.get("pending_notifications", 0),
                        "delivered_notifications": notification_status.get("delivered_notifications", 0),
                        "read_notifications": notification_status.get("read_notifications", 0),
                        "failed_notifications": notification_status.get("failed_notifications", 0),
                        "total_templates": notification_status.get("total_templates", 0),
                        "total_user_preferences": notification_status.get("total_user_preferences", 0)
                    }
                }
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to get metrics: {e}")
            return {
                "service_name": self.service_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def cleanup(self):
        """Cleanup service resources."""
        try:
            self.logger.info("🧹 Cleaning up Post Office Service...")
            # Cleanup micro-modules if needed
            self.logger.info("✅ Post Office Service cleanup completed")
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup Post Office Service: {e}")
    
    # ============================================================================
    # MULTI-TENANT SPECIFIC METHODS
    # ============================================================================
    
    async def get_tenant_events(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get all events for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's events"}
            
            # Get tenant-specific events
            filters = {"tenant_id": tenant_id}
            result = await self.get_events(filters, user_context)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_events", "post_office",
                    {"tenant_id": tenant_id, "event_count": len(result.get("events", []))}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_events")
            return {"success": False, "error": str(e)}
    
    async def get_tenant_event_metrics(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get event metrics for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's event metrics"}
            
            # Get tenant events
            tenant_events = await self.get_tenant_events(tenant_id, user_context)
            if not tenant_events.get("success"):
                return tenant_events
            
            events = tenant_events.get("events", [])
            
            # Calculate event metrics
            event_metrics = {
                "tenant_id": tenant_id,
                "total_events": len(events),
                "events_by_type": self._calculate_events_by_type(events),
                "events_by_status": self._calculate_events_by_status(events),
                "average_processing_time": self._calculate_average_processing_time(events),
                "event_volume_trend": self._calculate_event_volume_trend(events)
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_event_metrics", "post_office",
                    {"tenant_id": tenant_id, "total_events": event_metrics["total_events"]}
                )
            
            return {"success": True, "event_metrics": event_metrics}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_event_metrics")
            return {"success": False, "error": str(e)}
    
    async def get_tenant_messaging_summary(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get messaging summary for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's messaging summary"}
            
            # Get tenant-specific messages
            filters = {"tenant_id": tenant_id}
            result = await self.get_messages(filters, user_context)
            
            if not result.get("success"):
                return result
            
            messages = result.get("messages", [])
            
            # Calculate messaging summary
            messaging_summary = {
                "tenant_id": tenant_id,
                "total_messages": len(messages),
                "messages_by_status": self._calculate_messages_by_status(messages),
                "messages_by_priority": self._calculate_messages_by_priority(messages),
                "delivery_success_rate": self._calculate_delivery_success_rate(messages),
                "average_delivery_time": self._calculate_average_delivery_time(messages)
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_messaging_summary", "post_office",
                    {"tenant_id": tenant_id, "total_messages": messaging_summary["total_messages"]}
                )
            
            return {"success": True, "messaging_summary": messaging_summary}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_messaging_summary")
            return {"success": False, "error": str(e)}
    
    def _calculate_events_by_type(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of events by type."""
        type_counts = {}
        for event in events:
            event_type = event.get("event_type", "unknown")
            type_counts[event_type] = type_counts.get(event_type, 0) + 1
        return type_counts
    
    def _calculate_events_by_status(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of events by status."""
        status_counts = {}
        for event in events:
            status = event.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
    
    def _calculate_average_processing_time(self, events: List[Dict[str, Any]]) -> float:
        """Calculate average event processing time in milliseconds."""
        if not events:
            return 0.0
        
        processing_times = []
        for event in events:
            if event.get("processing_time"):
                processing_times.append(event["processing_time"])
        
        return round(sum(processing_times) / len(processing_times), 2) if processing_times else 0.0
    
    def _calculate_event_volume_trend(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate event volume trend over time."""
        # Simplified trend calculation - in a real implementation, you'd group by time periods
        return {
            "last_hour": len([e for e in events if self._is_recent_event(e, 1)]),
            "last_24_hours": len([e for e in events if self._is_recent_event(e, 24)]),
            "last_week": len([e for e in events if self._is_recent_event(e, 168)])
        }
    
    def _is_recent_event(self, event: Dict[str, Any], hours: int) -> bool:
        """Check if an event is within the specified hours."""
        if not event.get("timestamp"):
            return False
        
        try:
            event_time = datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00'))
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            return event_time >= cutoff_time
        except:
            return False
    
    def _calculate_messages_by_status(self, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of messages by status."""
        status_counts = {}
        for message in messages:
            status = message.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
    
    def _calculate_messages_by_priority(self, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of messages by priority."""
        priority_counts = {}
        for message in messages:
            priority = message.get("priority", "normal")
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        return priority_counts
    
    def _calculate_delivery_success_rate(self, messages: List[Dict[str, Any]]) -> float:
        """Calculate message delivery success rate."""
        if not messages:
            return 100.0
        
        successful_deliveries = len([m for m in messages if m.get("status") == "delivered"])
        return round((successful_deliveries / len(messages)) * 100, 2)
    
    def _calculate_average_delivery_time(self, messages: List[Dict[str, Any]]) -> float:
        """Calculate average message delivery time in seconds."""
        if not messages:
            return 0.0
        
        delivery_times = []
        for message in messages:
            if message.get("delivery_time"):
                delivery_times.append(message["delivery_time"])
        
        return round(sum(delivery_times) / len(delivery_times), 2) if delivery_times else 0.0


class PostOfficeSOAProtocol(SOAServiceProtocol):
    """SOA Protocol implementation for Post Office Service."""
    
    def __init__(self, service_name: str, service_instance, curator_foundation=None, public_works_foundation=None):
        """Initialize Post Office SOA Protocol."""
        super().__init__(service_name, None, curator_foundation, public_works_foundation)
        self.service_instance = service_instance
        self.service_info = None
        
    async def initialize(self, user_context: UserContext = None):
        """Initialize the SOA service."""
        # Create service info with multi-tenant metadata
        self.service_info = SOAServiceInfo(
            service_name="PostOfficeService",
            version="1.0.0",
            description="Post Office Service - Multi-tenant event routing and messaging",
            interface_name="IPostOffice",
            endpoints=self._create_all_endpoints(),
            tags=["event-routing", "messaging", "multi-tenant", "agent-communication"],
            contact={"email": "postoffice@smartcity.com"},
            multi_tenant_enabled=True,
            tenant_isolation_level="strict"
        )
    
    def get_service_info(self) -> SOAServiceInfo:
        """Get service information for OpenAPI generation."""
        return self.service_info
    
    def get_openapi_spec(self) -> Dict[str, Any]:
        """Get OpenAPI 3.0 specification for this service."""
        if not self.service_info:
            return {"error": "Service not initialized"}
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.service_info.service_name,
                "version": self.service_info.version,
                "description": self.service_info.description,
                "contact": self.service_info.contact
            },
            "servers": [
                {"url": "https://api.smartcity.com/post-office", "description": "Post Office Service"}
            ],
            "paths": self._create_openapi_paths(),
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        }
    
    def get_docs(self) -> Dict[str, Any]:
        """Get service documentation."""
        return {
            "service": self.service_info.service_name,
            "description": self.service_info.description,
            "version": self.service_info.version,
            "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
            "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
            "tenant_isolation_level": self.service_info.tenant_isolation_level
        }
    
    async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Register this service with Curator Foundation Service."""
        if self.curator_foundation:
            capability = {
                "interface": self.service_info.interface_name,
                "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
                "tools": [],  # MCP tools handled separately
                "description": self.service_info.description,
                "realm": "smart_city",
                "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
                "tenant_isolation_level": self.service_info.tenant_isolation_level
            }
            
            return await self.curator_foundation.register_capability(
                self.service_name, 
                capability, 
                user_context
            )
        else:
            return {"error": "Curator Foundation Service not available"}
    
    def _create_all_endpoints(self) -> List[SOAEndpoint]:
        """Create all endpoints for Post Office Service."""
        endpoints = []
        
        # Standard endpoints
        endpoints.extend(self._create_standard_endpoints())
        endpoints.extend(self._create_health_endpoints())
        endpoints.extend(self._create_tenant_aware_endpoints())
        
        # Post Office specific endpoints
        endpoints.extend([
            SOAEndpoint(
                path="/messages",
                method="POST",
                summary="Send Message",
                description="Send a message with tenant awareness",
                request_schema={
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string"},
                        "subject": {"type": "string"},
                        "content": {"type": "string"},
                        "priority": {"type": "string"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["recipient", "subject", "content"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Messages", "Sending"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/messages/{message_id}",
                method="GET",
                summary="Get Message",
                description="Get a specific message",
                parameters=[
                    {
                        "name": "message_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Message ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string"},
                        "recipient": {"type": "string"},
                        "subject": {"type": "string"},
                        "content": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Messages", "Retrieval"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/messages",
                method="GET",
                summary="List Messages",
                description="List messages for the current tenant",
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "messages": {"type": "array", "items": {"type": "object"}},
                        "total_count": {"type": "integer"}
                    }
                }),
                tags=["Messages", "Management"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/events",
                method="POST",
                summary="Publish Event",
                description="Publish an event with tenant awareness",
                request_schema={
                    "type": "object",
                    "properties": {
                        "event_type": {"type": "string"},
                        "event_data": {"type": "object"},
                        "target_services": {"type": "array", "items": {"type": "string"}},
                        "priority": {"type": "string"}
                    },
                    "required": ["event_type", "event_data"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "event_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Events", "Publishing"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/events/{event_id}",
                method="GET",
                summary="Get Event",
                description="Get a specific event",
                parameters=[
                    {
                        "name": "event_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Event ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "event_id": {"type": "string"},
                        "event_type": {"type": "string"},
                        "event_data": {"type": "object"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Events", "Retrieval"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/events",
                method="GET",
                summary="List Events",
                description="List events for the current tenant",
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "events": {"type": "array", "items": {"type": "object"}},
                        "total_count": {"type": "integer"}
                    }
                }),
                tags=["Events", "Management"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/tenant/{tenant_id}/message-summary",
                method="GET",
                summary="Get Tenant Message Summary",
                description="Get message summary for a specific tenant",
                parameters=[
                    {
                        "name": "tenant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Tenant ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "total_messages": {"type": "integer"},
                        "messages_by_status": {"type": "object"},
                        "delivery_success_rate": {"type": "number"}
                    }
                }),
                tags=["Tenant", "Messages"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/tenant/{tenant_id}/event-summary",
                method="GET",
                summary="Get Tenant Event Summary",
                description="Get event summary for a specific tenant",
                parameters=[
                    {
                        "name": "tenant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Tenant ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "total_events": {"type": "integer"},
                        "events_by_type": {"type": "object"},
                        "average_processing_time": {"type": "number"}
                    }
                }),
                tags=["Tenant", "Events"],
                requires_tenant=True,
                tenant_scope="tenant"
            )
        ])
        
        return endpoints
    
    def _create_openapi_paths(self) -> Dict[str, Any]:
        """Create OpenAPI paths for all endpoints."""
        paths = {}
        
        for endpoint in self.service_info.endpoints:
            path_item = {
                endpoint.method.lower(): {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags,
                    "security": [{"BearerAuth": []}] if endpoint.requires_tenant else []
                }
            }
            
            if endpoint.parameters:
                path_item[endpoint.method.lower()]["parameters"] = endpoint.parameters
            
            if endpoint.request_schema:
                path_item[endpoint.method.lower()]["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint.request_schema
                        }
                    }
                }
            
            if endpoint.response_schema:
                path_item[endpoint.method.lower()]["responses"] = {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": endpoint.response_schema
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "content": {
                            "application/json": {
                                "schema": self._create_error_response_schema()
                            }
                        }
                    }
                }
            
            paths[endpoint.path] = path_item
        
        return paths