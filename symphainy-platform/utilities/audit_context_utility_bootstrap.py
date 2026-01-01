#!/usr/bin/env python3
"""
Audit Context Utility - Bootstrap Pattern

Builds and manages audit and security event contexts using bootstrap pattern to avoid circular references.
This utility gets bootstrapped by foundation service, then works independently.

WHAT (Utility Role): I build and manage audit contexts using bootstrap pattern
HOW (Utility Implementation): I bootstrap from foundation service, then work independently
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class AuditContext:
    audit_id: str
    user_id: str
    tenant_id: Optional[str]
    action: str
    resource: str
    service_name: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    outcome: Optional[str] = None # e.g., "success", "failure", "denied"

    def to_dict(self) -> Dict[str, Any]:
        return {k: str(v) if isinstance(v, datetime) else v for k, v in self.__dict__.items()}

@dataclass(frozen=True)
class SecurityEventContext:
    event_id: str
    event_type: str # e.g., "authentication_success", "authorization_denied", "data_access"
    user_id: str
    tenant_id: Optional[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    severity: str = "info" # info, warning, error, critical
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {k: str(v) if isinstance(v, datetime) else v for k, v in self.__dict__.items()}

class AuditContextUtilityBootstrap:
    """
    Audit Context Utility - Bootstrap Pattern
    
    Builds and manages audit and security event contexts using bootstrap pattern to avoid circular references.
    This utility gets bootstrapped by foundation service, then works independently.
    """
    
    def __init__(self, service_name: str = "default_service"):
        """Initialize Audit Context Utility (not yet bootstrapped)."""
        self.service_name = service_name
        self.logger = logging.getLogger(f"AuditContextUtilityBootstrap-{service_name}")
        
        # Bootstrap state
        self.is_bootstrapped = False
        self.bootstrap_provider = None
        
        self.logger.info(f"Audit Context Utility Bootstrap initialized for {service_name} (not yet bootstrapped)")
    
    def bootstrap(self, bootstrap_provider):
        """
        Bootstrap the audit context utility with infrastructure capabilities.
        
        Args:
            bootstrap_provider: Foundation service that provides bootstrap implementation
        """
        self.bootstrap_provider = bootstrap_provider
        self.is_bootstrapped = True
        
        self.logger.info(f"Audit Context Utility Bootstrap bootstrapped by {bootstrap_provider.__class__.__name__}")

    async def build_audit_context(self, user_id: str, tenant_id: Optional[str], action: str, resource: str,
                                  request_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None,
                                  outcome: Optional[str] = None) -> AuditContext:
        """Build an AuditContext object."""
        if not self.is_bootstrapped:
            raise RuntimeError("Audit Context Utility not bootstrapped. Call bootstrap() first.")
        
        context = AuditContext(
            audit_id=str(uuid.uuid4()),
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            resource=resource,
            service_name=self.service_name,
            request_id=request_id if request_id else str(uuid.uuid4()),
            details=details if details is not None else {},
            outcome=outcome
        )
        self.logger.debug(f"Audit context built for user {user_id}, action {action}")
        return context

    async def build_security_event_context(self, event_type: str, user_id: str, tenant_id: Optional[str],
                                           severity: str = "info", details: Optional[Dict[str, Any]] = None) -> SecurityEventContext:
        """Build a SecurityEventContext object."""
        if not self.is_bootstrapped:
            raise RuntimeError("Audit Context Utility not bootstrapped. Call bootstrap() first.")
        
        context = SecurityEventContext(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            user_id=user_id,
            tenant_id=tenant_id,
            severity=severity,
            details=details if details is not None else {}
        )
        self.logger.debug(f"Security event built: {event_type} for user {user_id}")
        return context
    
    async def build_audit_log_entry(self, audit_context: AuditContext, security_event_context: Optional[SecurityEventContext] = None) -> Dict[str, Any]:
        """
        Combines audit and security event contexts into a single log entry.
        This utility only *builds* the log entry, it does not store it.
        """
        if not self.is_bootstrapped:
            raise RuntimeError("Audit Context Utility not bootstrapped. Call bootstrap() first.")
        
        log_entry = audit_context.to_dict()
        if security_event_context:
            log_entry["security_event"] = security_event_context.to_dict()
        self.logger.debug(f"Audit log built for user {audit_context.user_id}")
        return log_entry

    async def build_security_log_entry(self, security_event_context: SecurityEventContext, audit_context: Optional[AuditContext] = None) -> Dict[str, Any]:
        """
        Combines security event and audit contexts into a single log entry.
        This utility only *builds* the log entry, it does not store it.
        """
        if not self.is_bootstrapped:
            raise RuntimeError("Audit Context Utility not bootstrapped. Call bootstrap() first.")
        
        log_entry = security_event_context.to_dict()
        if audit_context:
            log_entry["audit_context"] = audit_context.to_dict()
        self.logger.debug(f"Security log built for event {security_event_context.event_type}")
        return log_entry

    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the utility."""
        return {
            "utility_name": "AuditContextUtilityBootstrap",
            "service_name": self.service_name,
            "status": "active" if self.is_bootstrapped else "not_bootstrapped",
            "is_bootstrapped": self.is_bootstrapped,
            "bootstrap_provider": self.bootstrap_provider.__class__.__name__ if self.bootstrap_provider else None,
            "timestamp": datetime.utcnow().isoformat()
        }



