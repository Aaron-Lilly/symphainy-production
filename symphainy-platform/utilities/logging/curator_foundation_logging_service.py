#!/usr/bin/env python3
"""
Curator Foundation Logging Service

Realm-specific logging service for Curator Foundation services.
Handles logging for service discovery, agent management, and capability registry services.

WHAT (Utility Role): I provide logging for Curator Foundation realm
HOW (Utility Implementation): I handle service discovery and agent management logging with appropriate patterns
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .realm_logging_service_base import RealmLoggingServiceBase, LogContext, LogLevel, LogCategory


class CuratorFoundationLoggingService(RealmLoggingServiceBase):
    """
    Logging service for Curator Foundation realm.
    
    Handles logging for:
    - Service Discovery Service
    - Agent Capability Registry Service
    - Agent Specialization Management Service
    - Service Registration Services
    - Agent Management Services
    """
    
    def __init__(self, service_name: str = "curator_foundation"):
        """Initialize Curator Foundation logging service."""
        super().__init__("curator_foundation", service_name)
        
        # Curator Foundation-specific logging patterns
        self._initialize_curator_foundation_patterns()
        
        self.logger.info(f"✅ Curator Foundation logging service initialized for {service_name}")
    
    def _initialize_curator_foundation_patterns(self):
        """Initialize Curator Foundation-specific logging patterns."""
        # Override log categories with Curator Foundation-specific patterns
        self.realm_logging_patterns["log_categories"].update({
            "service_discovery": LogCategory.SYSTEM,
            "agent_registry": LogCategory.SYSTEM,
            "agent_specialization": LogCategory.SYSTEM,
            "service_registration": LogCategory.SYSTEM,
            "agent_management": LogCategory.SYSTEM,
            "capability_registration": LogCategory.SYSTEM,
            "service_health_check": LogCategory.PERFORMANCE,
            "agent_health_check": LogCategory.PERFORMANCE,
            "service_communication": LogCategory.SYSTEM
        })
        
        # Add Curator Foundation-specific structured fields
        self.realm_logging_patterns["structured_fields"].extend([
            "discovery_operation", "service_name", "registry_type", "discovery_status",
            "registry_operation", "agent_id", "capability_name", "registry_status",
            "specialization_operation", "specialization_id", "agent_id", "specialization_status",
            "registration_operation", "service_name", "service_type", "registration_status",
            "management_operation", "agent_id", "agent_type", "management_status",
            "capability_operation", "capability_name", "agent_id", "capability_status",
            "health_check_type", "service_name", "health_status", "health_check_status",
            "agent_health_check_type", "agent_id", "agent_health_status", "agent_health_check_status",
            "communication_type", "source_service", "target_service", "communication_status"
        ])
    
    def log_service_discovery_operation(self, message: str, context: LogContext, discovery_operation: str = None, 
                                       service_name: str = None, registry_type: str = None, discovery_status: str = None, 
                                       data: Dict[str, Any] = None):
        """Log service discovery operation-related message."""
        log_data = data or {}
        if discovery_operation:
            log_data["discovery_operation"] = discovery_operation
        if service_name:
            log_data["service_name"] = service_name
        if registry_type:
            log_data["registry_type"] = registry_type
        if discovery_status:
            log_data["discovery_status"] = discovery_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_agent_registry_operation(self, message: str, context: LogContext, registry_operation: str = None, 
                                    agent_id: str = None, capability_name: str = None, registry_status: str = None, 
                                    data: Dict[str, Any] = None):
        """Log agent registry operation-related message."""
        log_data = data or {}
        if registry_operation:
            log_data["registry_operation"] = registry_operation
        if agent_id:
            log_data["agent_id"] = agent_id
        if capability_name:
            log_data["capability_name"] = capability_name
        if registry_status:
            log_data["registry_status"] = registry_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_agent_specialization_operation(self, message: str, context: LogContext, specialization_operation: str = None, 
                                          specialization_id: str = None, agent_id: str = None, specialization_status: str = None, 
                                          data: Dict[str, Any] = None):
        """Log agent specialization operation-related message."""
        log_data = data or {}
        if specialization_operation:
            log_data["specialization_operation"] = specialization_operation
        if specialization_id:
            log_data["specialization_id"] = specialization_id
        if agent_id:
            log_data["agent_id"] = agent_id
        if specialization_status:
            log_data["specialization_status"] = specialization_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_service_registration_operation(self, message: str, context: LogContext, registration_operation: str = None, 
                                          service_name: str = None, service_type: str = None, registration_status: str = None, 
                                          data: Dict[str, Any] = None):
        """Log service registration operation-related message."""
        log_data = data or {}
        if registration_operation:
            log_data["registration_operation"] = registration_operation
        if service_name:
            log_data["service_name"] = service_name
        if service_type:
            log_data["service_type"] = service_type
        if registration_status:
            log_data["registration_status"] = registration_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_agent_management_operation(self, message: str, context: LogContext, management_operation: str = None, 
                                      agent_id: str = None, agent_type: str = None, management_status: str = None, 
                                      data: Dict[str, Any] = None):
        """Log agent management operation-related message."""
        log_data = data or {}
        if management_operation:
            log_data["management_operation"] = management_operation
        if agent_id:
            log_data["agent_id"] = agent_id
        if agent_type:
            log_data["agent_type"] = agent_type
        if management_status:
            log_data["management_status"] = management_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_capability_registration_operation(self, message: str, context: LogContext, capability_operation: str = None, 
                                             capability_name: str = None, agent_id: str = None, capability_status: str = None, 
                                             data: Dict[str, Any] = None):
        """Log capability registration operation-related message."""
        log_data = data or {}
        if capability_operation:
            log_data["capability_operation"] = capability_operation
        if capability_name:
            log_data["capability_name"] = capability_name
        if agent_id:
            log_data["agent_id"] = agent_id
        if capability_status:
            log_data["capability_status"] = capability_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_service_health_check_operation(self, message: str, context: LogContext, health_check_type: str = None, 
                                          service_name: str = None, health_status: str = None, health_check_status: str = None, 
                                          data: Dict[str, Any] = None):
        """Log service health check operation-related message."""
        log_data = data or {}
        if health_check_type:
            log_data["health_check_type"] = health_check_type
        if service_name:
            log_data["service_name"] = service_name
        if health_status:
            log_data["health_status"] = health_status
        if health_check_status:
            log_data["health_check_status"] = health_check_status
        
        return self.log(LogLevel.INFO, LogCategory.PERFORMANCE, message, context, log_data)
    
    def log_agent_health_check_operation(self, message: str, context: LogContext, agent_health_check_type: str = None, 
                                         agent_id: str = None, agent_health_status: str = None, agent_health_check_status: str = None, 
                                         data: Dict[str, Any] = None):
        """Log agent health check operation-related message."""
        log_data = data or {}
        if agent_health_check_type:
            log_data["agent_health_check_type"] = agent_health_check_type
        if agent_id:
            log_data["agent_id"] = agent_id
        if agent_health_status:
            log_data["agent_health_status"] = agent_health_status
        if agent_health_check_status:
            log_data["agent_health_check_status"] = agent_health_check_status
        
        return self.log(LogLevel.INFO, LogCategory.PERFORMANCE, message, context, log_data)
    
    def log_service_communication_operation(self, message: str, context: LogContext, communication_type: str = None, 
                                           source_service: str = None, target_service: str = None, communication_status: str = None, 
                                           data: Dict[str, Any] = None):
        """Log service communication operation-related message."""
        log_data = data or {}
        if communication_type:
            log_data["communication_type"] = communication_type
        if source_service:
            log_data["source_service"] = source_service
        if target_service:
            log_data["target_service"] = target_service
        if communication_status:
            log_data["communication_status"] = communication_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_curator_foundation_startup(self, context: LogContext, service_name: str, startup_data: Dict[str, Any] = None):
        """Log Curator Foundation service startup."""
        message = f"Curator Foundation service {service_name} starting up"
        log_data = startup_data or {}
        log_data["service_name"] = service_name
        log_data["startup_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_curator_foundation_shutdown(self, context: LogContext, service_name: str, shutdown_data: Dict[str, Any] = None):
        """Log Curator Foundation service shutdown."""
        message = f"Curator Foundation service {service_name} shutting down"
        log_data = shutdown_data or {}
        log_data["service_name"] = service_name
        log_data["shutdown_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_curator_foundation_error(self, context: LogContext, service_name: str, error: Exception, 
                                    error_data: Dict[str, Any] = None):
        """Log Curator Foundation service error."""
        message = f"Curator Foundation service {service_name} error: {str(error)}"
        log_data = error_data or {}
        log_data["service_name"] = service_name
        log_data["error_type"] = type(error).__name__
        log_data["error_message"] = str(error)
        
        error_details = {
            "traceback": str(error),
            "service_name": service_name
        }
        
        return self.log(LogLevel.ERROR, LogCategory.ERROR, message, context, log_data, error_details)
    
    def get_curator_foundation_logging_summary(self) -> Dict[str, Any]:
        """Get Curator Foundation-specific logging summary."""
        base_summary = self.get_log_statistics()
        
        # Add Curator Foundation-specific metrics
        curator_foundation_metrics = {
            "service_discovery_operation_logs": self._count_logs_by_field("discovery_operation"),
            "agent_registry_operation_logs": self._count_logs_by_field("registry_operation"),
            "agent_specialization_operation_logs": self._count_logs_by_field("specialization_operation"),
            "service_registration_operation_logs": self._count_logs_by_field("registration_operation"),
            "agent_management_operation_logs": self._count_logs_by_field("management_operation"),
            "capability_registration_operation_logs": self._count_logs_by_field("capability_operation"),
            "service_health_check_operation_logs": self._count_logs_by_field("health_check_type"),
            "agent_health_check_operation_logs": self._count_logs_by_field("agent_health_check_type"),
            "service_communication_operation_logs": self._count_logs_by_field("communication_type")
        }
        
        base_summary["curator_foundation_metrics"] = curator_foundation_metrics
        return base_summary
    
    def _count_logs_by_field(self, field_name: str) -> int:
        """Count logs that contain a specific field."""
        count = 0
        for log_entry in self.log_entries:
            if field_name in log_entry.data:
                count += 1
        return count


