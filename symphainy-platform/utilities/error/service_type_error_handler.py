#!/usr/bin/env python3
"""
Service Type-Specific Error Handler

Service type-specific error handling patterns for Services, Agents, MCP Servers, and Foundation Services.
Provides specialized error handling based on service type with real working implementations.

WHAT (Utility Role): I provide service type-specific error handling patterns
HOW (Utility Implementation): I handle errors based on service type with appropriate recovery strategies
"""

import logging
from typing import Dict, Any, Optional, Type
from datetime import datetime
from enum import Enum

from .realm_error_handler_base import RealmErrorHandlerBase, ErrorContext, ErrorResponse, ErrorSeverity, ErrorAction


class ServiceType(Enum):
    """Service type enumeration."""
    SERVICE = "service"
    AGENT = "agent"
    MCP_SERVER = "mcp_server"
    FOUNDATION_SERVICE = "foundation_service"


class ServiceTypeErrorHandler:
    """
    Service type-specific error handler.
    
    Provides specialized error handling patterns based on service type:
    - Services: Business logic, API operations, data processing
    - Agents: Autonomous operations, reasoning, decision making
    - MCP Servers: Tool execution, AI capabilities, agent communication
    - Foundation Services: Infrastructure, utilities, core platform services
    """
    
    def __init__(self, realm_error_handler: RealmErrorHandlerBase):
        """Initialize service type error handler."""
        self.realm_error_handler = realm_error_handler
        self.logger = logging.getLogger(f"ServiceTypeErrorHandler-{realm_error_handler.realm_name}")
        
        # Service type-specific error patterns
        self.service_type_patterns = self._initialize_service_type_patterns()
        
        self.logger.info(f"✅ Service type error handler initialized for {realm_error_handler.realm_name}")
    
    def _initialize_service_type_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize service type-specific error patterns."""
        return {
            "service": {
                "common_errors": {
                    "BUSINESS_LOGIC_ERROR": {
                        "severity": ErrorSeverity.MEDIUM,
                        "action": ErrorAction.RETRY,
                        "user_message": "Business logic error - retrying operation"
                    },
                    "API_OPERATION_ERROR": {
                        "severity": ErrorSeverity.HIGH,
                        "action": ErrorAction.RETRY_WITH_BACKOFF,
                        "user_message": "API operation failed - retrying with backoff"
                    },
                    "DATA_PROCESSING_ERROR": {
                        "severity": ErrorSeverity.MEDIUM,
                        "action": ErrorAction.RETRY,
                        "user_message": "Data processing error - retrying operation"
                    },
                    "SERVICE_DEPENDENCY_ERROR": {
                        "severity": ErrorSeverity.HIGH,
                        "action": ErrorAction.ESCALATE,
                        "user_message": "Service dependency error - escalating"
                    }
                },
                "recovery_strategies": {
                    "BUSINESS_LOGIC_ERROR": [
                        "Check business rules",
                        "Verify input data",
                        "Retry operation",
                        "Use fallback logic"
                    ],
                    "API_OPERATION_ERROR": [
                        "Check API connectivity",
                        "Verify API credentials",
                        "Retry with exponential backoff",
                        "Use alternative API endpoint"
                    ],
                    "DATA_PROCESSING_ERROR": [
                        "Check data format",
                        "Verify data integrity",
                        "Retry processing",
                        "Use alternative processing method"
                    ],
                    "SERVICE_DEPENDENCY_ERROR": [
                        "Check dependent service health",
                        "Verify service configuration",
                        "Escalate to service administrator",
                        "Use service fallback"
                    ]
                }
            },
            "agent": {
                "common_errors": {
                    "REASONING_ERROR": {
                        "severity": ErrorSeverity.MEDIUM,
                        "action": ErrorAction.RETRY,
                        "user_message": "Agent reasoning error - retrying decision"
                    },
                    "AUTONOMOUS_OPERATION_ERROR": {
                        "severity": ErrorSeverity.HIGH,
                        "action": ErrorAction.ESCALATE,
                        "user_message": "Autonomous operation error - escalating to human"
                    },
                    "DECISION_MAKING_ERROR": {
                        "severity": ErrorSeverity.MEDIUM,
                        "action": ErrorAction.RETRY,
                        "user_message": "Decision making error - retrying decision"
                    },
                    "AGENT_COMMUNICATION_ERROR": {
                        "severity": ErrorSeverity.MEDIUM,
                        "action": ErrorAction.RETRY_WITH_BACKOFF,
                        "user_message": "Agent communication error - retrying with backoff"
                    }
                },
                "recovery_strategies": {
                    "REASONING_ERROR": [
                        "Check reasoning engine",
                        "Verify agent context",
                        "Retry reasoning",
                        "Use simplified reasoning"
                    ],
                    "AUTONOMOUS_OPERATION_ERROR": [
                        "Check autonomy controls",
                        "Verify operation safety",
                        "Escalate to human operator",
                        "Use supervised operation"
                    ],
                    "DECISION_MAKING_ERROR": [
                        "Check decision rules",
                        "Verify decision context",
                        "Retry decision making",
                        "Use conservative decision"
                    ],
                    "AGENT_COMMUNICATION_ERROR": [
                        "Check agent connectivity",
                        "Verify communication protocol",
                        "Retry with backoff",
                        "Use alternative communication"
                    ]
                }
            },
            "mcp_server": {
                "common_errors": {
                    "TOOL_EXECUTION_ERROR": {
                        "severity": ErrorSeverity.MEDIUM,
                        "action": ErrorAction.RETRY,
                        "user_message": "Tool execution error - retrying"
                    },
                    "AI_CAPABILITY_ERROR": {
                        "severity": ErrorSeverity.HIGH,
                        "action": ErrorAction.FALLBACK,
                        "user_message": "AI capability error - using fallback"
                    },
                    "AGENT_COMMUNICATION_ERROR": {
                        "severity": ErrorSeverity.MEDIUM,
                        "action": ErrorAction.RETRY_WITH_BACKOFF,
                        "user_message": "Agent communication error - retrying with backoff"
                    },
                    "MCP_PROTOCOL_ERROR": {
                        "severity": ErrorSeverity.HIGH,
                        "action": ErrorAction.ESCALATE,
                        "user_message": "MCP protocol error - escalating"
                    }
                },
                "recovery_strategies": {
                    "TOOL_EXECUTION_ERROR": [
                        "Check tool configuration",
                        "Verify tool dependencies",
                        "Retry tool execution",
                        "Use alternative tool"
                    ],
                    "AI_CAPABILITY_ERROR": [
                        "Check AI service health",
                        "Verify AI model availability",
                        "Use fallback AI capability",
                        "Use simplified AI processing"
                    ],
                    "AGENT_COMMUNICATION_ERROR": [
                        "Check agent connectivity",
                        "Verify communication protocol",
                        "Retry with backoff",
                        "Use alternative communication"
                    ],
                    "MCP_PROTOCOL_ERROR": [
                        "Check MCP protocol implementation",
                        "Verify MCP server configuration",
                        "Escalate to MCP administrator",
                        "Use alternative MCP server"
                    ]
                }
            },
            "foundation_service": {
                "common_errors": {
                    "INFRASTRUCTURE_ERROR": {
                        "severity": ErrorSeverity.HIGH,
                        "action": ErrorAction.ESCALATE,
                        "user_message": "Infrastructure error - escalating"
                    },
                    "UTILITY_ERROR": {
                        "severity": ErrorSeverity.MEDIUM,
                        "action": ErrorAction.RETRY,
                        "user_message": "Utility error - retrying"
                    },
                    "CORE_PLATFORM_ERROR": {
                        "severity": ErrorSeverity.CRITICAL,
                        "action": ErrorAction.ESCALATE,
                        "user_message": "Core platform error - escalating immediately"
                    },
                    "CONFIGURATION_ERROR": {
                        "severity": ErrorSeverity.HIGH,
                        "action": ErrorAction.ESCALATE,
                        "user_message": "Configuration error - escalating"
                    }
                },
                "recovery_strategies": {
                    "INFRASTRUCTURE_ERROR": [
                        "Check infrastructure health",
                        "Verify infrastructure configuration",
                        "Escalate to infrastructure team",
                        "Use infrastructure fallback"
                    ],
                    "UTILITY_ERROR": [
                        "Check utility configuration",
                        "Verify utility dependencies",
                        "Retry utility operation",
                        "Use utility fallback"
                    ],
                    "CORE_PLATFORM_ERROR": [
                        "Check core platform health",
                        "Verify platform configuration",
                        "Escalate to platform team immediately",
                        "Use emergency platform mode"
                    ],
                    "CONFIGURATION_ERROR": [
                        "Check configuration files",
                        "Verify environment variables",
                        "Escalate to configuration team",
                        "Use default configuration"
                    ]
                }
            }
        }
    
    def handle_service_error(self, error: Exception, context: ErrorContext, service_type: ServiceType) -> ErrorResponse:
        """Handle error based on service type."""
        try:
            # Add service type-specific context
            context.additional_context = context.additional_context or {}
            context.additional_context.update({
                "service_type": service_type.value,
                "error_category": "service_type_specific"
            })
            
            # Get service type-specific patterns
            service_patterns = self.service_type_patterns.get(service_type.value, {})
            
            # Determine error code based on service type
            error_code = self._get_service_type_error_code(error, service_type)
            
            # Get service type-specific error pattern
            error_pattern = service_patterns.get("common_errors", {}).get(
                error_code, 
                self.service_type_patterns["service"]["common_errors"]["BUSINESS_LOGIC_ERROR"]
            )
            
            # Create enhanced error response
            error_response = self.realm_error_handler.handle_error(error, context)
            
            # Override with service type-specific patterns
            error_response.severity = error_pattern["severity"]
            error_response.action = error_pattern["action"]
            error_response.user_message = error_pattern["user_message"]
            error_response.recovery_suggestions = service_patterns.get("recovery_strategies", {}).get(
                error_code, 
                ["Check logs for details", "Contact support if problem persists"]
            )
            
            # Add service type-specific technical details
            error_response.technical_details.update({
                "service_type": service_type.value,
                "service_type_error_code": error_code,
                "service_type_patterns_applied": True
            })
            
            return error_response
            
        except Exception as e:
            # Fallback to realm error handler
            self.logger.error(f"❌ Service type error handler failed: {e}")
            return self.realm_error_handler.handle_error(error, context)
    
    def _get_service_type_error_code(self, error: Exception, service_type: ServiceType) -> str:
        """Get error code based on service type and error."""
        error_message = str(error).lower()
        
        if service_type == ServiceType.SERVICE:
            if "business" in error_message or "logic" in error_message:
                return "BUSINESS_LOGIC_ERROR"
            elif "api" in error_message or "http" in error_message:
                return "API_OPERATION_ERROR"
            elif "data" in error_message or "processing" in error_message:
                return "DATA_PROCESSING_ERROR"
            elif "dependency" in error_message or "service" in error_message:
                return "SERVICE_DEPENDENCY_ERROR"
        
        elif service_type == ServiceType.AGENT:
            if "reasoning" in error_message or "reason" in error_message:
                return "REASONING_ERROR"
            elif "autonomous" in error_message or "autonomy" in error_message:
                return "AUTONOMOUS_OPERATION_ERROR"
            elif "decision" in error_message or "decide" in error_message:
                return "DECISION_MAKING_ERROR"
            elif "communication" in error_message or "communicate" in error_message:
                return "AGENT_COMMUNICATION_ERROR"
        
        elif service_type == ServiceType.MCP_SERVER:
            if "tool" in error_message or "execute" in error_message:
                return "TOOL_EXECUTION_ERROR"
            elif "ai" in error_message or "model" in error_message:
                return "AI_CAPABILITY_ERROR"
            elif "communication" in error_message or "agent" in error_message:
                return "AGENT_COMMUNICATION_ERROR"
            elif "mcp" in error_message or "protocol" in error_message:
                return "MCP_PROTOCOL_ERROR"
        
        elif service_type == ServiceType.FOUNDATION_SERVICE:
            if "infrastructure" in error_message or "infra" in error_message:
                return "INFRASTRUCTURE_ERROR"
            elif "utility" in error_message or "util" in error_message:
                return "UTILITY_ERROR"
            elif "core" in error_message or "platform" in error_message:
                return "CORE_PLATFORM_ERROR"
            elif "config" in error_message or "configuration" in error_message:
                return "CONFIGURATION_ERROR"
        
        # Default fallback
        return "UNKNOWN_ERROR"
    
    def get_service_type_error_summary(self, service_type: ServiceType) -> Dict[str, Any]:
        """Get service type-specific error summary."""
        base_summary = self.realm_error_handler.get_error_statistics()
        
        # Add service type-specific metrics
        service_type_metrics = {
            "service_type": service_type.value,
            "service_type_patterns": self.service_type_patterns.get(service_type.value, {}),
            "total_errors": base_summary["total_errors"],
            "error_counts": base_summary["error_counts"],
            "recent_errors": base_summary["recent_errors"]
        }
        
        return service_type_metrics
    
    def get_all_service_type_patterns(self) -> Dict[str, Any]:
        """Get all service type patterns."""
        return self.service_type_patterns


