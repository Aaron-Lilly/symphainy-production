#!/usr/bin/env python3
"""
Event Routing Module - Post Office Service

Handles event routing operations using proper infrastructure abstractions.
"""

from typing import Dict, Any, Optional


class EventRouting:
    """Event routing module for Post Office Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def route_event(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Route event using Redis event management infrastructure."""
        event_type = request.get("event_type", "unknown")
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "route_event_start",
            success=True,
            details={"event_type": event_type}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "event_routing", "write"):
                        await self.service.record_health_metric("route_event_access_denied", 1.0, {"event_type": event_type})
                        await self.service.log_operation_with_telemetry("route_event_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to route event")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id") or request.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("route_event_tenant_denied", 1.0, {"event_type": event_type, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("route_event_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use Event Management Abstraction (Redis)
            event_context = await self.service.event_management_abstraction.publish_event(
                event_type=event_type,
                source=request.get("source"),
                target=request.get("target"),
                event_data=request.get("event_data", {}),
                priority=request.get("priority", "normal"),
                correlation_id=request.get("correlation_id"),
                tenant_id=request.get("tenant_id")
            )
            
            if event_context:
                # Record health metric
                await self.service.record_health_metric(
                    "event_routed",
                    1.0,
                    {"event_id": event_context.event_id, "event_type": event_type}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "route_event_complete",
                    success=True,
                    details={"event_id": event_context.event_id, "event_type": event_type}
                )
                
                return {
                    "event_id": event_context.event_id,
                    "status": "routed",
                    "timestamp": event_context.timestamp,
                    "success": True
                }
            else:
                await self.service.record_health_metric("event_route_failed", 1.0, {"event_type": event_type})
                await self.service.log_operation_with_telemetry("route_event_complete", success=False, details={"error": "Failed to route event"})
                return {
                    "event_id": None,
                    "status": "failed",
                    "error": "Failed to route event",
                    "success": False
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "route_event")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "route_event_complete",
                success=False,
                details={"event_type": event_type, "error": str(e)}
            )
            return {
                "event_id": None,
                "status": "failed",
                "error": str(e),
                "success": False
            }
    
    async def register_agent(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Register agent using Redis session management infrastructure."""
        from datetime import datetime
        agent_id = request.get("agent_id", "unknown")
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "register_agent_start",
            success=True,
            details={"agent_id": agent_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_management", "write"):
                        await self.service.record_health_metric("register_agent_access_denied", 1.0, {"agent_id": agent_id})
                        await self.service.log_operation_with_telemetry("register_agent_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to register agent")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id") or request.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("register_agent_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("register_agent_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            agent_config = request.get("agent_config", {})
            
            # Store agent registration in session management
            self.service.active_agents[agent_id] = {
                "agent_id": agent_id,
                "agent_config": agent_config,
                "registered_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Record health metric
            await self.service.record_health_metric(
                "agent_registered",
                1.0,
                {"agent_id": agent_id}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "register_agent_complete",
                success=True,
                details={"agent_id": agent_id}
            )
            
            return {
                "agent_id": agent_id,
                "status": "registered",
                "registered_at": self.service.active_agents[agent_id]["registered_at"],
                "success": True
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "register_agent")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "register_agent_complete",
                success=False,
                details={"agent_id": agent_id, "error": str(e)}
            )
            return {
                "agent_id": agent_id,
                "status": "failed",
                "error": str(e),
                "success": False
            }
    
    async def publish_event(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Publish event via Post Office.
        
        Uses event_management_abstraction internally (Redis → Kafka swap only affects Post Office).
        """
        from datetime import datetime
        
        event_type = request.get("event_type", "generic")
        event_data = request.get("event_data", {})
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "publish_event_start",
            success=True,
            details={"event_type": event_type}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "event_publishing", "write"):
                        await self.service.record_health_metric("publish_event_access_denied", 1.0, {"event_type": event_type})
                        await self.service.log_operation_with_telemetry("publish_event_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to publish event")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id") or request.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("publish_event_tenant_denied", 1.0, {"event_type": event_type, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("publish_event_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use event_management_abstraction internally
            if not self.service.event_management_abstraction:
                return {
                    "success": False,
                    "error": "Event management abstraction not available"
                }
            
            # Publish event via abstraction
            event_context = await self.service.event_management_abstraction.publish_event(
                event_type=event_type,
                source=request.get("source"),
                target=request.get("target"),
                event_data=event_data,
                priority=request.get("priority", "normal"),
                correlation_id=request.get("correlation_id"),
                tenant_id=request.get("tenant_id") or (user_context.get("tenant_id") if user_context else None)
            )
            
            if event_context:
                # Record health metric
                await self.service.record_health_metric(
                    "event_published",
                    1.0,
                    {"event_id": event_context.event_id if hasattr(event_context, 'event_id') else None, "event_type": event_type}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "publish_event_complete",
                    success=True,
                    details={"event_id": event_context.event_id if hasattr(event_context, 'event_id') else None, "event_type": event_type}
                )
                
                return {
                    "success": True,
                    "event_id": event_context.event_id if hasattr(event_context, 'event_id') else None,
                    "event_type": event_type,
                    "published_at": datetime.utcnow().isoformat()
                }
            else:
                await self.service.record_health_metric("event_publish_failed", 1.0, {"event_type": event_type})
                await self.service.log_operation_with_telemetry("publish_event_complete", success=False, details={"error": "Failed to publish event"})
                return {
                    "success": False,
                    "error": "Failed to publish event"
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "publish_event")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "publish_event_complete",
                success=False,
                details={"event_type": event_type, "error": str(e)}
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def subscribe_to_events(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Subscribe to events via Post Office.
        
        Uses event_management_abstraction internally.
        """
        from datetime import datetime
        
        event_type = request.get("event_type")
        handler_id = request.get("handler_id")
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "subscribe_to_events_start",
            success=True,
            details={"event_type": event_type, "handler_id": handler_id}
        )
        
        try:
            if not event_type or not handler_id:
                return {
                    "success": False,
                    "error": "event_type and handler_id required"
                }
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "event_subscription", "write"):
                        await self.service.record_health_metric("subscribe_to_events_access_denied", 1.0, {"event_type": event_type})
                        await self.service.log_operation_with_telemetry("subscribe_to_events_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to subscribe to events")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id") or request.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("subscribe_to_events_tenant_denied", 1.0, {"event_type": event_type, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("subscribe_to_events_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use event_management_abstraction internally
            if not self.service.event_management_abstraction:
                return {
                    "success": False,
                    "error": "Event management abstraction not available"
                }
            
            # Subscribe via abstraction
            # Note: handler_id is used to identify the handler, actual handler function should be stored separately
            success = await self.service.event_management_abstraction.subscribe(event_type, handler_id)
            
            if success:
                # Record health metric
                await self.service.record_health_metric(
                    "event_subscribed",
                    1.0,
                    {"event_type": event_type, "handler_id": handler_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "subscribe_to_events_complete",
                    success=True,
                    details={"event_type": event_type, "handler_id": handler_id}
                )
                
                return {
                    "success": True,
                    "event_type": event_type,
                    "handler_id": handler_id,
                    "subscribed_at": datetime.utcnow().isoformat()
                }
            else:
                await self.service.record_health_metric("event_subscribe_failed", 1.0, {"event_type": event_type})
                await self.service.log_operation_with_telemetry("subscribe_to_events_complete", success=False, details={"error": "Failed to subscribe to events"})
                return {
                    "success": False,
                    "error": "Failed to subscribe to events"
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "subscribe_to_events")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "subscribe_to_events_complete",
                success=False,
                details={"event_type": event_type, "handler_id": handler_id, "error": str(e)}
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def unsubscribe_from_events(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Unsubscribe from events via Post Office.
        
        Uses event_management_abstraction internally.
        """
        from datetime import datetime
        
        event_type = request.get("event_type")
        handler_id = request.get("handler_id")
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "unsubscribe_from_events_start",
            success=True,
            details={"event_type": event_type, "handler_id": handler_id}
        )
        
        try:
            if not event_type or not handler_id:
                return {
                    "success": False,
                    "error": "event_type and handler_id required"
                }
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "event_subscription", "write"):
                        await self.service.record_health_metric("unsubscribe_from_events_access_denied", 1.0, {"event_type": event_type})
                        await self.service.log_operation_with_telemetry("unsubscribe_from_events_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to unsubscribe from events")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id") or request.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("unsubscribe_from_events_tenant_denied", 1.0, {"event_type": event_type, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("unsubscribe_from_events_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use event_management_abstraction internally
            if not self.service.event_management_abstraction:
                return {
                    "success": False,
                    "error": "Event management abstraction not available"
                }
            
            # Unsubscribe via abstraction
            success = await self.service.event_management_abstraction.unsubscribe(event_type, handler_id)
            
            if success:
                # Record health metric
                await self.service.record_health_metric(
                    "event_unsubscribed",
                    1.0,
                    {"event_type": event_type, "handler_id": handler_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "unsubscribe_from_events_complete",
                    success=True,
                    details={"event_type": event_type, "handler_id": handler_id}
                )
                
                return {
                    "success": True,
                    "event_type": event_type,
                    "handler_id": handler_id,
                    "unsubscribed_at": datetime.utcnow().isoformat()
                }
            else:
                await self.service.record_health_metric("event_unsubscribe_failed", 1.0, {"event_type": event_type})
                await self.service.log_operation_with_telemetry("unsubscribe_from_events_complete", success=False, details={"error": "Failed to unsubscribe from events"})
                return {
                    "success": False,
                    "error": "Failed to unsubscribe from events"
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "unsubscribe_from_events")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "unsubscribe_from_events_complete",
                success=False,
                details={"event_type": event_type, "handler_id": handler_id, "error": str(e)}
            )
            return {
                "success": False,
                "error": str(e)
            }








