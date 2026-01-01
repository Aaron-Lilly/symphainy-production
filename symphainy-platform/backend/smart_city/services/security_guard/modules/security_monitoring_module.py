#!/usr/bin/env python3
"""
Security Monitoring Module - Security Guard Micro-Module

Handles security monitoring, metrics collection, and security event tracking.
Part of the Security Guard Service micro-modular architecture.

WHAT (Monitoring Role): I handle security monitoring and metrics collection
HOW (Monitoring Implementation): I collect and analyze security metrics and events
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import security protocols
from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import SecurityContext

# Import audit and security event contexts
from utilities.audit_context_utility_integrated import AuditContext, SecurityEventContext


class SecurityMonitoringModule:
    """
    Security Monitoring Module - Security Guard Micro-Module
    
    Handles security monitoring, metrics collection, and security event tracking.
    Part of the Security Guard Service micro-modular architecture.
    
    WHAT (Monitoring Role): I handle security monitoring and metrics collection
    HOW (Monitoring Implementation): I collect and analyze security metrics and events
    """
    
    def __init__(self, service_name: str = "security_monitoring_module"):
        """Initialize Security Monitoring Module."""
        self.service_name = service_name
        self.logger = self.service.di_container.get_logger(f"SecurityMonitoringModule-{service_name}")
        
        # Security monitoring statistics
        self.monitoring_stats = {
            "security_events": 0,
            "authentication_events": 0,
            "authorization_events": 0,
            "session_events": 0,
            "tenant_isolation_events": 0,
            "feature_access_events": 0
        }
        
        # Security event history
        self.security_events = []
        
        self.logger.info(f"✅ Security Monitoring Module '{service_name}' initialized")
    
    async def initialize(self):
        """Initialize Security Monitoring Module."""
        try:
            self.logger.info(f"🚀 Initializing Security Monitoring Module '{self.service_name}'...")
            self.logger.info(f"✅ Security Monitoring Module '{self.service_name}' initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Security Monitoring Module '{self.service_name}': {e}")
            raise
    
    async def track_security_event(self, event_type: str, security_context: SecurityContext, 
                                  details: Dict[str, Any] = None) -> SecurityEventContext:
        """Track security event."""
        try:
            # Create security event context
            sec_event_ctx = SecurityEventContext(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                user_id=security_context.user_id,
                tenant_id=security_context.tenant_id,
                severity="info",
                details=details or {}
            )
            
            # Update statistics
            self.monitoring_stats["security_events"] += 1
            self.monitoring_stats[f"{event_type}_events"] += 1
            
            # Store event
            self.security_events.append(sec_event_ctx)
            
            # Keep only last 1000 events
            if len(self.security_events) > 1000:
                self.security_events = self.security_events[-1000:]
            
            self.logger.info(f"Security event tracked: {event_type} for user {security_context.user_id}")
            return sec_event_ctx
            
        except Exception as e:
            self.logger.error(f"❌ Failed to track security event: {e}")
            return SecurityEventContext(
                event_id=str(uuid.uuid4()),
                event_type="error",
                user_id=security_context.user_id if security_context else None,
                tenant_id=security_context.tenant_id if security_context else None,
                severity="error",
                details={"error": str(e)}
            )
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get comprehensive security metrics."""
        try:
            total_events = self.monitoring_stats["security_events"]
            
            return {
                "total_security_events": total_events,
                "authentication_events": self.monitoring_stats["authentication_events"],
                "authorization_events": self.monitoring_stats["authorization_events"],
                "session_events": self.monitoring_stats["session_events"],
                "tenant_isolation_events": self.monitoring_stats["tenant_isolation_events"],
                "feature_access_events": self.monitoring_stats["feature_access_events"],
                "event_distribution": {
                    "authentication": (self.monitoring_stats["authentication_events"] / total_events * 100) if total_events > 0 else 0,
                    "authorization": (self.monitoring_stats["authorization_events"] / total_events * 100) if total_events > 0 else 0,
                    "session": (self.monitoring_stats["session_events"] / total_events * 100) if total_events > 0 else 0,
                    "tenant_isolation": (self.monitoring_stats["tenant_isolation_events"] / total_events * 100) if total_events > 0 else 0,
                    "feature_access": (self.monitoring_stats["feature_access_events"] / total_events * 100) if total_events > 0 else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get security metrics: {e}")
            return {}
    
    async def get_recent_events(self, limit: int = 10) -> List[SecurityEventContext]:
        """Get recent security events."""
        try:
            return self.security_events[-limit:] if self.security_events else []
        except Exception as e:
            self.logger.error(f"❌ Failed to get recent events: {e}")
            return []
    
    async def get_events_by_type(self, event_type: str) -> List[SecurityEventContext]:
        """Get events by type."""
        try:
            return [event for event in self.security_events if event.event_type == event_type]
        except Exception as e:
            self.logger.error(f"❌ Failed to get events by type: {e}")
            return []
    
    async def get_events_by_user(self, user_id: str) -> List[SecurityEventContext]:
        """Get events by user."""
        try:
            return [event for event in self.security_events if event.user_id == user_id]
        except Exception as e:
            self.logger.error(f"❌ Failed to get events by user: {e}")
            return []
    
    async def get_events_by_tenant(self, tenant_id: str) -> List[SecurityEventContext]:
        """Get events by tenant."""
        try:
            return [event for event in self.security_events if event.tenant_id == tenant_id]
        except Exception as e:
            self.logger.error(f"❌ Failed to get events by tenant: {e}")
            return []
    
    async def clear_old_events(self, days: int = 30):
        """Clear events older than specified days."""
        try:
            cutoff_date = datetime.utcnow().timestamp() - (days * 24 * 60 * 60)
            self.security_events = [
                event for event in self.security_events 
                if event.timestamp.timestamp() > cutoff_date
            ]
            self.logger.info(f"Cleared events older than {days} days")
        except Exception as e:
            self.logger.error(f"❌ Failed to clear old events: {e}")
    
    def get_capabilities(self) -> list:
        """Get module capabilities."""
        return [
            "security_event_tracking",
            "security_metrics_collection",
            "event_history_management",
            "event_filtering",
            "event_cleanup"
        ]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get module status."""
        return {
            "module": "SecurityMonitoringModule",
            "service_name": self.service_name,
            "status": "active",
            "capabilities": self.get_capabilities(),
            "total_events": len(self.security_events),
            "metrics": await self.get_security_metrics()
        }



