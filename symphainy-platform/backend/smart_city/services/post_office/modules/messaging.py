#!/usr/bin/env python3
"""
Messaging Module - Post Office Service

Handles message operations using proper infrastructure abstractions.
"""

from typing import Dict, Any, Optional


class Messaging:
    """Messaging module for Post Office Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def send_message(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send message using Redis messaging infrastructure."""
        recipient = request.get("recipient", "unknown")
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "send_message_start",
            success=True,
            details={"recipient": recipient}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "messaging", "write"):
                        await self.service.record_health_metric("send_message_access_denied", 1.0, {"recipient": recipient})
                        await self.service.log_operation_with_telemetry("send_message_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to send message")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id") or request.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("send_message_tenant_denied", 1.0, {"recipient": recipient, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("send_message_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use Messaging Abstraction (Redis)
            message_context = await self.service.messaging_abstraction.send_message(
                message_type=request.get("message_type", "text"),
                sender=request.get("sender"),
                recipient=request.get("recipient"),
                message_content=request.get("message_content", {}),
                priority=request.get("priority", "normal"),
                correlation_id=request.get("correlation_id"),
                tenant_id=request.get("tenant_id")
            )
            
            if message_context:
                # Record health metric
                await self.service.record_health_metric(
                    "message_sent",
                    1.0,
                    {"message_id": message_context.message_id, "recipient": recipient}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "send_message_complete",
                    success=True,
                    details={"message_id": message_context.message_id, "recipient": recipient}
                )
                
                return {
                    "message_id": message_context.message_id,
                    "status": "sent",
                    "timestamp": message_context.timestamp,
                    "success": True
                }
            else:
                await self.service.record_health_metric("message_send_failed", 1.0, {"recipient": recipient})
                await self.service.log_operation_with_telemetry("send_message_complete", success=False, details={"error": "Failed to send message"})
                return {
                    "message_id": None,
                    "status": "failed",
                    "error": "Failed to send message",
                    "success": False
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "send_message")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "send_message_complete",
                success=False,
                details={"recipient": recipient, "error": str(e)}
            )
            return {
                "message_id": None,
                "status": "failed",
                "error": str(e),
                "success": False
            }
    
    async def get_messages(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get messages using Redis messaging infrastructure."""
        recipient = request.get("recipient", "unknown")
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "get_messages_start",
            success=True,
            details={"recipient": recipient}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "messaging", "read"):
                        await self.service.record_health_metric("get_messages_access_denied", 1.0, {"recipient": recipient})
                        await self.service.log_operation_with_telemetry("get_messages_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to read messages")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id") or request.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("get_messages_tenant_denied", 1.0, {"recipient": recipient, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("get_messages_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use Messaging Abstraction (Redis)
            messages = await self.service.messaging_abstraction.get_messages_for_recipient(
                recipient=request.get("recipient"),
                message_type=request.get("message_type"),
                limit=request.get("limit", 50),
                offset=request.get("offset", 0)
            )
            
            # Record health metric
            await self.service.record_health_metric(
                "messages_retrieved",
                1.0,
                {"recipient": recipient, "count": len(messages)}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "get_messages_complete",
                success=True,
                details={"recipient": recipient, "count": len(messages)}
            )
            
            return {
                "messages": messages,
                "total": len(messages),
                "success": True
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "get_messages")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "get_messages_complete",
                success=False,
                details={"recipient": recipient, "error": str(e)}
            )
            return {
                "messages": [],
                "total": 0,
                "error": str(e),
                "success": False
            }
    
    async def get_message_status(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get message status using Redis messaging infrastructure."""
        message_id = request.get("message_id", "unknown")
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "get_message_status_start",
            success=True,
            details={"message_id": message_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "messaging", "read"):
                        await self.service.record_health_metric("get_message_status_access_denied", 1.0, {"message_id": message_id})
                        await self.service.log_operation_with_telemetry("get_message_status_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to read message status")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("get_message_status_tenant_denied", 1.0, {"message_id": message_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("get_message_status_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Use Messaging Abstraction (Redis)
            message_context = await self.service.messaging_abstraction.get_message(message_id)
            
            if message_context:
                # Record health metric
                await self.service.record_health_metric(
                    "message_status_retrieved",
                    1.0,
                    {"message_id": message_id, "status": message_context.status}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_message_status_complete",
                    success=True,
                    details={"message_id": message_id, "status": message_context.status}
                )
                
                return {
                    "message_id": message_id,
                    "status": message_context.status,
                    "timestamp": message_context.timestamp,
                    "delivery_status": message_context.delivery_status,
                    "success": True
                }
            else:
                await self.service.record_health_metric("message_status_not_found", 1.0, {"message_id": message_id})
                await self.service.log_operation_with_telemetry("get_message_status_complete", success=False, details={"message_id": message_id, "reason": "not_found"})
                return {
                    "message_id": message_id,
                    "status": "not_found",
                    "error": "Message not found",
                    "success": False
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "get_message_status")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "get_message_status_complete",
                success=False,
                details={"message_id": message_id, "error": str(e)}
            )
            return {
                "message_id": message_id,
                "status": "error",
                "error": str(e),
                "success": False
            }








