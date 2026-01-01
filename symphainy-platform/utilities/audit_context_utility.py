#!/usr/bin/env python3
"""
Audit Context Utility - Clean Audit Context Building

Builds and injects audit context with no enforcement decisions.
This is the refactored security capability with clean separation of concerns.

WHAT (Utility Role): I build and inject audit context
HOW (Utility Implementation): I use clean interfaces with no enforcement logic
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class AuditContext:
    """Audit context data structure - no enforcement logic."""
    user_id: str
    tenant_id: str
    action: str
    resource: str
    trace_id: str
    request_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_roles: list[str] = field(default_factory=list)
    user_permissions: list[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class SecurityEvent:
    """Security event data structure - no enforcement logic."""
    event_type: str
    severity: str
    user_id: str
    tenant_id: str
    action: str
    resource: str
    trace_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)

class AuditContextUtility:
    """
    Audit Context Utility - Clean Audit Context Building
    
    Builds and injects audit context with no enforcement decisions.
    This utility only builds context - it does not make authorization decisions.
    """
    
    def __init__(self):
        """Initialize Audit Context Utility."""
        self.logger = logging.getLogger("AuditContextUtility")
        self.logger.info("✅ Audit Context Utility initialized")
    
    # ============================================================================
    # AUDIT CONTEXT BUILDING (No Enforcement)
    # ============================================================================
    
    async def build_audit_context(self, 
                                user_context: 'SecurityContext',
                                action: str, 
                                resource: str,
                                trace_context: 'TraceContext',
                                details: Dict[str, Any] = None) -> AuditContext:
        """Build audit context for logging - no enforcement decisions."""
        try:
            # Build audit context
            context = AuditContext(
                user_id=user_context.user_id or "unknown",
                tenant_id=user_context.tenant_id or "unknown",
                action=action,
                resource=resource,
                trace_id=trace_context.trace_id,
                request_id=trace_context.request_id,
                user_roles=user_context.roles,
                user_permissions=user_context.permissions,
                details=details or {}
            )
            
            self.logger.info(f"✅ Audit context built for user {context.user_id}, action {action}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to build audit context: {str(e)}")
            # Return default context on error
            return AuditContext(
                user_id="unknown",
                tenant_id="unknown",
                action=action,
                resource=resource,
                trace_id=trace_context.trace_id,
                request_id=trace_context.request_id
            )
    
    async def build_security_event(self, 
                                 event_type: str,
                                 severity: str,
                                 user_context: 'SecurityContext',
                                 action: str,
                                 resource: str,
                                 trace_context: 'TraceContext',
                                 details: Dict[str, Any] = None) -> SecurityEvent:
        """Build security event for monitoring - no enforcement decisions."""
        try:
            # Build security event
            event = SecurityEvent(
                event_type=event_type,
                severity=severity,
                user_id=user_context.user_id or "unknown",
                tenant_id=user_context.tenant_id or "unknown",
                action=action,
                resource=resource,
                trace_id=trace_context.trace_id,
                details=details or {}
            )
            
            self.logger.info(f"✅ Security event built: {event_type} for user {event.user_id}")
            return event
            
        except Exception as e:
            self.logger.error(f"Failed to build security event: {str(e)}")
            # Return default event on error
            return SecurityEvent(
                event_type=event_type,
                severity=severity,
                user_id="unknown",
                tenant_id="unknown",
                action=action,
                resource=resource,
                trace_id=trace_context.trace_id
            )
    
    # ============================================================================
    # AUDIT LOG BUILDING (No Enforcement)
    # ============================================================================
    
    async def build_audit_log(self, 
                            audit_context: AuditContext,
                            service_name: str = "audit_context_utility") -> Dict[str, Any]:
        """Build audit log entry - no enforcement decisions."""
        try:
            # Build audit log entry
            log_entry = {
                "audit_id": str(uuid.uuid4()),
                "user_id": audit_context.user_id,
                "tenant_id": audit_context.tenant_id,
                "action": audit_context.action,
                "resource": audit_context.resource,
                "trace_id": audit_context.trace_id,
                "request_id": audit_context.request_id,
                "timestamp": audit_context.timestamp.isoformat(),
                "user_roles": audit_context.user_roles,
                "user_permissions": audit_context.user_permissions,
                "service_name": service_name,
                "details": audit_context.details
            }
            
            self.logger.info(f"✅ Audit log built for user {audit_context.user_id}")
            return log_entry
            
        except Exception as e:
            self.logger.error(f"Failed to build audit log: {str(e)}")
            return {}
    
    async def build_security_log(self, 
                               security_event: SecurityEvent,
                               service_name: str = "audit_context_utility") -> Dict[str, Any]:
        """Build security log entry - no enforcement decisions."""
        try:
            # Build security log entry
            log_entry = {
                "security_id": str(uuid.uuid4()),
                "event_type": security_event.event_type,
                "severity": security_event.severity,
                "user_id": security_event.user_id,
                "tenant_id": security_event.tenant_id,
                "action": security_event.action,
                "resource": security_event.resource,
                "trace_id": security_event.trace_id,
                "timestamp": security_event.timestamp.isoformat(),
                "service_name": service_name,
                "details": security_event.details
            }
            
            self.logger.info(f"✅ Security log built for event {security_event.event_type}")
            return log_entry
            
        except Exception as e:
            self.logger.error(f"Failed to build security log: {str(e)}")
            return {}
    
    # ============================================================================
    # AUDIT CONTEXT VALIDATION (No Enforcement)
    # ============================================================================
    
    def is_audit_context_valid(self, context: AuditContext) -> bool:
        """Check if audit context is valid - no enforcement decisions."""
        try:
            # Basic validation - context must have required fields
            if not context.user_id or not context.action or not context.resource:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate audit context: {str(e)}")
            return False
    
    def is_security_event_valid(self, event: SecurityEvent) -> bool:
        """Check if security event is valid - no enforcement decisions."""
        try:
            # Basic validation - event must have required fields
            if not event.event_type or not event.severity or not event.user_id:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate security event: {str(e)}")
            return False
    
    # ============================================================================
    # AUDIT CONTEXT ENRICHMENT (No Enforcement)
    # ============================================================================
    
    async def enrich_audit_context(self, 
                                 audit_context: AuditContext,
                                 additional_details: Dict[str, Any]) -> AuditContext:
        """Enrich audit context with additional details - no enforcement decisions."""
        try:
            # Create enriched context with additional details
            enriched_details = {**audit_context.details, **additional_details}
            
            # Build enriched audit context
            enriched_context = AuditContext(
                user_id=audit_context.user_id,
                tenant_id=audit_context.tenant_id,
                action=audit_context.action,
                resource=audit_context.resource,
                trace_id=audit_context.trace_id,
                request_id=audit_context.request_id,
                timestamp=audit_context.timestamp,
                user_roles=audit_context.user_roles,
                user_permissions=audit_context.user_permissions,
                details=enriched_details
            )
            
            self.logger.info(f"✅ Audit context enriched for user {audit_context.user_id}")
            return enriched_context
            
        except Exception as e:
            self.logger.error(f"Failed to enrich audit context: {str(e)}")
            return audit_context
    
    async def enrich_security_event(self, 
                                  security_event: SecurityEvent,
                                  additional_details: Dict[str, Any]) -> SecurityEvent:
        """Enrich security event with additional details - no enforcement decisions."""
        try:
            # Create enriched event with additional details
            enriched_details = {**security_event.details, **additional_details}
            
            # Build enriched security event
            enriched_event = SecurityEvent(
                event_type=security_event.event_type,
                severity=security_event.severity,
                user_id=security_event.user_id,
                tenant_id=security_event.tenant_id,
                action=security_event.action,
                resource=security_event.resource,
                trace_id=security_event.trace_id,
                timestamp=security_event.timestamp,
                details=enriched_details
            )
            
            self.logger.info(f"✅ Security event enriched for event {security_event.event_type}")
            return enriched_event
            
        except Exception as e:
            self.logger.error(f"Failed to enrich security event: {str(e)}")
            return security_event
    
    # ============================================================================
    # UTILITY STATUS
    # ============================================================================
    
    def get_utility_status(self) -> Dict[str, Any]:
        """Get utility status information."""
        return {
            "utility_name": "AuditContextUtility",
            "status": "active",
            "capabilities": [
                "build_audit_context",
                "build_security_event",
                "build_audit_log",
                "build_security_log",
                "enrich_audit_context",
                "enrich_security_event"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }



