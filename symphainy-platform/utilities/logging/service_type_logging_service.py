#!/usr/bin/env python3
"""
Service Type-Specific Logging Service

Service type-specific logging patterns for Services, Agents, MCP Servers, and Foundation Services.
Provides specialized logging based on service type with real working implementations.

WHAT (Utility Role): I provide service type-specific logging patterns
HOW (Utility Implementation): I handle logging based on service type with appropriate patterns
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from .realm_logging_service_base import RealmLoggingServiceBase, LogContext, LogLevel, LogCategory


class ServiceType(Enum):
    """Service type enumeration."""
    SERVICE = "service"
    AGENT = "agent"
    MCP_SERVER = "mcp_server"
    FOUNDATION_SERVICE = "foundation_service"


class ServiceTypeLoggingService:
    """
    Service type-specific logging service.
    
    Provides specialized logging patterns based on service type:
    - Services: Business logic, API operations, data processing
    - Agents: Autonomous operations, reasoning, decision making
    - MCP Servers: Tool execution, AI capabilities, agent communication
    - Foundation Services: Infrastructure, utilities, core platform services
    """
    
    def __init__(self, realm_logging_service: RealmLoggingServiceBase):
        """Initialize service type logging service."""
        self.realm_logging_service = realm_logging_service
        self.logger = logging.getLogger(f"ServiceTypeLogging-{realm_logging_service.realm_name}")
        
        # Service type-specific logging patterns
        self.service_type_patterns = self._initialize_service_type_patterns()
        
        self.logger.info(f"✅ Service type logging service initialized for {realm_logging_service.realm_name}")
    
    def _initialize_service_type_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize service type-specific logging patterns."""
        return {
            "service": {
                "log_categories": {
                    "business_operation": LogCategory.BUSINESS,
                    "api_operation": LogCategory.SYSTEM,
                    "data_processing": LogCategory.SYSTEM,
                    "service_dependency": LogCategory.SYSTEM,
                    "service_lifecycle": LogCategory.SYSTEM
                },
                "structured_fields": [
                    "business_operation", "business_rule", "business_context",
                    "api_endpoint", "http_method", "api_status", "response_code",
                    "data_type", "data_source", "processing_stage", "data_quality",
                    "dependent_service", "dependency_type", "dependency_status",
                    "service_phase", "service_status", "service_metrics"
                ],
                "performance_metrics": [
                    "response_time", "throughput", "error_rate", "success_rate",
                    "business_operation_count", "api_call_count", "data_processed"
                ]
            },
            "agent": {
                "log_categories": {
                    "reasoning_operation": LogCategory.SYSTEM,
                    "autonomous_operation": LogCategory.SYSTEM,
                    "decision_making": LogCategory.BUSINESS,
                    "agent_communication": LogCategory.SYSTEM,
                    "agent_lifecycle": LogCategory.SYSTEM
                },
                "structured_fields": [
                    "reasoning_type", "reasoning_engine", "reasoning_context", "reasoning_result",
                    "autonomous_operation", "autonomy_level", "safety_status", "operation_result",
                    "decision_type", "decision_context", "decision_result", "decision_confidence",
                    "communication_type", "target_agent", "communication_protocol", "communication_result",
                    "agent_phase", "agent_status", "agent_metrics"
                ],
                "performance_metrics": [
                    "reasoning_time", "decision_time", "autonomous_operation_count",
                    "communication_latency", "agent_uptime", "decision_accuracy"
                ]
            },
            "mcp_server": {
                "log_categories": {
                    "tool_execution": LogCategory.SYSTEM,
                    "ai_capability": LogCategory.SYSTEM,
                    "agent_communication": LogCategory.SYSTEM,
                    "mcp_protocol": LogCategory.SYSTEM,
                    "mcp_lifecycle": LogCategory.SYSTEM
                },
                "structured_fields": [
                    "tool_name", "tool_operation", "tool_context", "tool_result",
                    "ai_capability", "ai_model", "ai_operation", "ai_result",
                    "communication_type", "agent_id", "communication_protocol", "communication_result",
                    "mcp_protocol", "mcp_operation", "mcp_status", "mcp_result",
                    "mcp_phase", "mcp_status", "mcp_metrics"
                ],
                "performance_metrics": [
                    "tool_execution_time", "ai_processing_time", "communication_latency",
                    "mcp_protocol_overhead", "tool_success_rate", "ai_accuracy"
                ]
            },
            "foundation_service": {
                "log_categories": {
                    "infrastructure_operation": LogCategory.SYSTEM,
                    "utility_operation": LogCategory.SYSTEM,
                    "core_platform_operation": LogCategory.SYSTEM,
                    "configuration_operation": LogCategory.SYSTEM,
                    "foundation_lifecycle": LogCategory.SYSTEM
                },
                "structured_fields": [
                    "infrastructure_type", "infrastructure_operation", "infrastructure_status", "infrastructure_metrics",
                    "utility_type", "utility_operation", "utility_status", "utility_metrics",
                    "platform_component", "platform_operation", "platform_status", "platform_metrics",
                    "config_type", "config_operation", "config_status", "config_metrics",
                    "foundation_phase", "foundation_status", "foundation_metrics"
                ],
                "performance_metrics": [
                    "infrastructure_uptime", "utility_response_time", "platform_availability",
                    "configuration_load_time", "foundation_health_score", "service_discovery_time"
                ]
            }
        }
    
    def log_service_operation(self, message: str, context: LogContext, service_type: ServiceType, 
                             operation_type: str = None, operation_data: Dict[str, Any] = None):
        """Log service operation with type-specific patterns."""
        try:
            # Add service type-specific context
            context.additional_context = context.additional_context or {}
            context.additional_context.update({
                "service_type": service_type.value,
                "operation_type": operation_type or "unknown"
            })
            
            # Get service type-specific patterns
            service_patterns = self.service_type_patterns.get(service_type.value, {})
            log_categories = service_patterns.get("log_categories", {})
            
            # Determine log category based on operation type
            log_category = self._get_service_type_log_category(operation_type, service_type, log_categories)
            
            # Add service type-specific structured fields
            log_data = operation_data or {}
            log_data.update(self._get_service_type_structured_data(operation_type, service_type, context))
            
            # Log with realm logging service
            return self.realm_logging_service.log(LogLevel.INFO, log_category, message, context, log_data)
            
        except Exception as e:
            # Fallback to realm logging service
            self.logger.error(f"❌ Service type logging failed: {e}")
            return self.realm_logging_service.log_info(message, context, operation_data)
    
    def _get_service_type_log_category(self, operation_type: str, service_type: ServiceType, 
                                     log_categories: Dict[str, LogCategory]) -> LogCategory:
        """Get log category based on service type and operation."""
        if not operation_type:
            return LogCategory.SYSTEM
        
        operation_lower = operation_type.lower()
        
        if service_type == ServiceType.SERVICE:
            if "business" in operation_lower:
                return log_categories.get("business_operation", LogCategory.BUSINESS)
            elif "api" in operation_lower:
                return log_categories.get("api_operation", LogCategory.SYSTEM)
            elif "data" in operation_lower:
                return log_categories.get("data_processing", LogCategory.SYSTEM)
            elif "dependency" in operation_lower:
                return log_categories.get("service_dependency", LogCategory.SYSTEM)
            elif "lifecycle" in operation_lower:
                return log_categories.get("service_lifecycle", LogCategory.SYSTEM)
        
        elif service_type == ServiceType.AGENT:
            if "reasoning" in operation_lower:
                return log_categories.get("reasoning_operation", LogCategory.SYSTEM)
            elif "autonomous" in operation_lower:
                return log_categories.get("autonomous_operation", LogCategory.SYSTEM)
            elif "decision" in operation_lower:
                return log_categories.get("decision_making", LogCategory.BUSINESS)
            elif "communication" in operation_lower:
                return log_categories.get("agent_communication", LogCategory.SYSTEM)
            elif "lifecycle" in operation_lower:
                return log_categories.get("agent_lifecycle", LogCategory.SYSTEM)
        
        elif service_type == ServiceType.MCP_SERVER:
            if "tool" in operation_lower:
                return log_categories.get("tool_execution", LogCategory.SYSTEM)
            elif "ai" in operation_lower:
                return log_categories.get("ai_capability", LogCategory.SYSTEM)
            elif "communication" in operation_lower:
                return log_categories.get("agent_communication", LogCategory.SYSTEM)
            elif "mcp" in operation_lower or "protocol" in operation_lower:
                return log_categories.get("mcp_protocol", LogCategory.SYSTEM)
            elif "lifecycle" in operation_lower:
                return log_categories.get("mcp_lifecycle", LogCategory.SYSTEM)
        
        elif service_type == ServiceType.FOUNDATION_SERVICE:
            if "infrastructure" in operation_lower:
                return log_categories.get("infrastructure_operation", LogCategory.SYSTEM)
            elif "utility" in operation_lower:
                return log_categories.get("utility_operation", LogCategory.SYSTEM)
            elif "platform" in operation_lower or "core" in operation_lower:
                return log_categories.get("core_platform_operation", LogCategory.SYSTEM)
            elif "config" in operation_lower:
                return log_categories.get("configuration_operation", LogCategory.SYSTEM)
            elif "lifecycle" in operation_lower:
                return log_categories.get("foundation_lifecycle", LogCategory.SYSTEM)
        
        # Default fallback
        return LogCategory.SYSTEM
    
    def _get_service_type_structured_data(self, operation_type: str, service_type: ServiceType, 
                                        context: LogContext) -> Dict[str, Any]:
        """Get service type-specific structured data."""
        structured_data = {
            "service_type": service_type.value,
            "operation_type": operation_type or "unknown",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add service type-specific fields
        service_patterns = self.service_type_patterns.get(service_type.value, {})
        structured_fields = service_patterns.get("structured_fields", [])
        
        # Add common structured fields
        for field in structured_fields:
            if field not in structured_data:
                structured_data[field] = None
        
        return structured_data
    
    def log_service_startup(self, context: LogContext, service_type: ServiceType, service_name: str, 
                           startup_data: Dict[str, Any] = None):
        """Log service startup with type-specific patterns."""
        message = f"{service_type.value.title()} {service_name} starting up"
        log_data = startup_data or {}
        log_data.update({
            "service_name": service_name,
            "startup_timestamp": datetime.utcnow().isoformat(),
            "service_type": service_type.value
        })
        
        return self.log_service_operation(message, context, service_type, "lifecycle", log_data)
    
    def log_service_shutdown(self, context: LogContext, service_type: ServiceType, service_name: str, 
                            shutdown_data: Dict[str, Any] = None):
        """Log service shutdown with type-specific patterns."""
        message = f"{service_type.value.title()} {service_name} shutting down"
        log_data = shutdown_data or {}
        log_data.update({
            "service_name": service_name,
            "shutdown_timestamp": datetime.utcnow().isoformat(),
            "service_type": service_type.value
        })
        
        return self.log_service_operation(message, context, service_type, "lifecycle", log_data)
    
    def log_service_error(self, context: LogContext, service_type: ServiceType, service_name: str, 
                         error: Exception, error_data: Dict[str, Any] = None):
        """Log service error with type-specific patterns."""
        message = f"{service_type.value.title()} {service_name} error: {str(error)}"
        log_data = error_data or {}
        log_data.update({
            "service_name": service_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "service_type": service_type.value
        })
        
        error_details = {
            "traceback": str(error),
            "service_name": service_name,
            "service_type": service_type.value
        }
        
        return self.realm_logging_service.log(LogLevel.ERROR, LogCategory.ERROR, message, context, log_data, error_details)
    
    def log_performance_metric(self, context: LogContext, service_type: ServiceType, metric_name: str, 
                              metric_value: Any, metric_unit: str = None, metric_data: Dict[str, Any] = None):
        """Log performance metric with type-specific patterns."""
        message = f"Performance metric: {metric_name} = {metric_value}"
        log_data = metric_data or {}
        log_data.update({
            "metric_name": metric_name,
            "metric_value": metric_value,
            "metric_unit": metric_unit,
            "metric_timestamp": datetime.utcnow().isoformat(),
            "service_type": service_type.value
        })
        
        return self.log_service_operation(message, context, service_type, "performance", log_data)
    
    def get_service_type_logging_summary(self, service_type: ServiceType) -> Dict[str, Any]:
        """Get service type-specific logging summary."""
        base_summary = self.realm_logging_service.get_log_statistics()
        
        # Add service type-specific metrics
        service_type_metrics = {
            "service_type": service_type.value,
            "service_type_patterns": self.service_type_patterns.get(service_type.value, {}),
            "total_logs": base_summary["total_logs"],
            "logs_by_level": base_summary["logs_by_level"],
            "logs_by_category": base_summary["logs_by_category"],
            "recent_logs": base_summary["recent_logs"]
        }
        
        return service_type_metrics
    
    def get_all_service_type_patterns(self) -> Dict[str, Any]:
        """Get all service type patterns."""
        return self.service_type_patterns


