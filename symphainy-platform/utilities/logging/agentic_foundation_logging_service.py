#!/usr/bin/env python3
"""
Agentic Foundation Logging Service

Realm-specific logging service for Agentic Foundation services.
Handles logging for AI capabilities, agent reasoning, and autonomous operations.

WHAT (Utility Role): I provide logging for Agentic Foundation realm
HOW (Utility Implementation): I handle AI and agent-specific logging with appropriate patterns
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .realm_logging_service_base import RealmLoggingServiceBase, LogContext, LogLevel, LogCategory


class AgenticFoundationLoggingService(RealmLoggingServiceBase):
    """
    Logging service for Agentic Foundation realm.
    
    Handles logging for:
    - AI Capability Services
    - Agent Reasoning Services
    - Autonomous Operation Services
    - MCP Tool Services
    - Agent Communication Services
    """
    
    def __init__(self, service_name: str = "agentic_foundation"):
        """Initialize Agentic Foundation logging service."""
        super().__init__("agentic_foundation", service_name)
        
        # Agentic Foundation-specific logging patterns
        self._initialize_agentic_foundation_patterns()
        
        self.logger.info(f"✅ Agentic Foundation logging service initialized for {service_name}")
    
    def _initialize_agentic_foundation_patterns(self):
        """Initialize Agentic Foundation-specific logging patterns."""
        # Override log categories with Agentic Foundation-specific patterns
        self.realm_logging_patterns["log_categories"].update({
            "ai_capability": LogCategory.SYSTEM,
            "agent_reasoning": LogCategory.SYSTEM,
            "autonomous_operation": LogCategory.SYSTEM,
            "mcp_tool": LogCategory.SYSTEM,
            "agent_communication": LogCategory.SYSTEM,
            "ai_model": LogCategory.SYSTEM,
            "reasoning_engine": LogCategory.SYSTEM,
            "autonomy_control": LogCategory.SYSTEM,
            "agent_coordination": LogCategory.SYSTEM
        })
        
        # Add Agentic Foundation-specific structured fields
        self.realm_logging_patterns["structured_fields"].extend([
            "capability_type", "ai_model", "capability_operation", "capability_status",
            "reasoning_type", "reasoning_engine", "reasoning_context", "reasoning_status",
            "operation_type", "autonomy_level", "safety_status", "operation_status",
            "tool_name", "tool_operation", "tool_context", "tool_status",
            "communication_type", "source_agent", "target_agent", "communication_status",
            "model_name", "model_type", "model_operation", "model_status",
            "engine_type", "reasoning_rule", "reasoning_context", "engine_status",
            "control_type", "control_parameter", "safety_level", "control_status",
            "coordination_type", "involved_agents", "coordination_rule", "coordination_status"
        ])
    
    def log_ai_capability_operation(self, message: str, context: LogContext, capability_type: str = None, 
                                   ai_model: str = None, capability_operation: str = None, capability_status: str = None, 
                                   data: Dict[str, Any] = None):
        """Log AI capability operation-related message."""
        log_data = data or {}
        if capability_type:
            log_data["capability_type"] = capability_type
        if ai_model:
            log_data["ai_model"] = ai_model
        if capability_operation:
            log_data["capability_operation"] = capability_operation
        if capability_status:
            log_data["capability_status"] = capability_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_agent_reasoning_operation(self, message: str, context: LogContext, reasoning_type: str = None, 
                                     reasoning_engine: str = None, reasoning_context: str = None, reasoning_status: str = None, 
                                     data: Dict[str, Any] = None):
        """Log agent reasoning operation-related message."""
        log_data = data or {}
        if reasoning_type:
            log_data["reasoning_type"] = reasoning_type
        if reasoning_engine:
            log_data["reasoning_engine"] = reasoning_engine
        if reasoning_context:
            log_data["reasoning_context"] = reasoning_context
        if reasoning_status:
            log_data["reasoning_status"] = reasoning_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_autonomous_operation(self, message: str, context: LogContext, operation_type: str = None, 
                                autonomy_level: str = None, safety_status: str = None, operation_status: str = None, 
                                data: Dict[str, Any] = None):
        """Log autonomous operation-related message."""
        log_data = data or {}
        if operation_type:
            log_data["operation_type"] = operation_type
        if autonomy_level:
            log_data["autonomy_level"] = autonomy_level
        if safety_status:
            log_data["safety_status"] = safety_status
        if operation_status:
            log_data["operation_status"] = operation_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_mcp_tool_operation(self, message: str, context: LogContext, tool_name: str = None, 
                              tool_operation: str = None, tool_context: str = None, tool_status: str = None, 
                              data: Dict[str, Any] = None):
        """Log MCP tool operation-related message."""
        log_data = data or {}
        if tool_name:
            log_data["tool_name"] = tool_name
        if tool_operation:
            log_data["tool_operation"] = tool_operation
        if tool_context:
            log_data["tool_context"] = tool_context
        if tool_status:
            log_data["tool_status"] = tool_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_agent_communication_operation(self, message: str, context: LogContext, communication_type: str = None, 
                                          source_agent: str = None, target_agent: str = None, communication_status: str = None, 
                                          data: Dict[str, Any] = None):
        """Log agent communication operation-related message."""
        log_data = data or {}
        if communication_type:
            log_data["communication_type"] = communication_type
        if source_agent:
            log_data["source_agent"] = source_agent
        if target_agent:
            log_data["target_agent"] = target_agent
        if communication_status:
            log_data["communication_status"] = communication_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_ai_model_operation(self, message: str, context: LogContext, model_name: str = None, 
                              model_type: str = None, model_operation: str = None, model_status: str = None, 
                              data: Dict[str, Any] = None):
        """Log AI model operation-related message."""
        log_data = data or {}
        if model_name:
            log_data["model_name"] = model_name
        if model_type:
            log_data["model_type"] = model_type
        if model_operation:
            log_data["model_operation"] = model_operation
        if model_status:
            log_data["model_status"] = model_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_reasoning_engine_operation(self, message: str, context: LogContext, engine_type: str = None, 
                                      reasoning_rule: str = None, reasoning_context: str = None, engine_status: str = None, 
                                      data: Dict[str, Any] = None):
        """Log reasoning engine operation-related message."""
        log_data = data or {}
        if engine_type:
            log_data["engine_type"] = engine_type
        if reasoning_rule:
            log_data["reasoning_rule"] = reasoning_rule
        if reasoning_context:
            log_data["reasoning_context"] = reasoning_context
        if engine_status:
            log_data["engine_status"] = engine_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_autonomy_control_operation(self, message: str, context: LogContext, control_type: str = None, 
                                      control_parameter: str = None, safety_level: str = None, control_status: str = None, 
                                      data: Dict[str, Any] = None):
        """Log autonomy control operation-related message."""
        log_data = data or {}
        if control_type:
            log_data["control_type"] = control_type
        if control_parameter:
            log_data["control_parameter"] = control_parameter
        if safety_level:
            log_data["safety_level"] = safety_level
        if control_status:
            log_data["control_status"] = control_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_agent_coordination_operation(self, message: str, context: LogContext, coordination_type: str = None, 
                                        involved_agents: list = None, coordination_rule: str = None, coordination_status: str = None, 
                                        data: Dict[str, Any] = None):
        """Log agent coordination operation-related message."""
        log_data = data or {}
        if coordination_type:
            log_data["coordination_type"] = coordination_type
        if involved_agents:
            log_data["involved_agents"] = involved_agents
        if coordination_rule:
            log_data["coordination_rule"] = coordination_rule
        if coordination_status:
            log_data["coordination_status"] = coordination_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_agentic_foundation_startup(self, context: LogContext, service_name: str, startup_data: Dict[str, Any] = None):
        """Log Agentic Foundation service startup."""
        message = f"Agentic Foundation service {service_name} starting up"
        log_data = startup_data or {}
        log_data["service_name"] = service_name
        log_data["startup_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_agentic_foundation_shutdown(self, context: LogContext, service_name: str, shutdown_data: Dict[str, Any] = None):
        """Log Agentic Foundation service shutdown."""
        message = f"Agentic Foundation service {service_name} shutting down"
        log_data = shutdown_data or {}
        log_data["service_name"] = service_name
        log_data["shutdown_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_agentic_foundation_error(self, context: LogContext, service_name: str, error: Exception, 
                                    error_data: Dict[str, Any] = None):
        """Log Agentic Foundation service error."""
        message = f"Agentic Foundation service {service_name} error: {str(error)}"
        log_data = error_data or {}
        log_data["service_name"] = service_name
        log_data["error_type"] = type(error).__name__
        log_data["error_message"] = str(error)
        
        error_details = {
            "traceback": str(error),
            "service_name": service_name
        }
        
        return self.log(LogLevel.ERROR, LogCategory.ERROR, message, context, log_data, error_details)
    
    def get_agentic_foundation_logging_summary(self) -> Dict[str, Any]:
        """Get Agentic Foundation-specific logging summary."""
        base_summary = self.get_log_statistics()
        
        # Add Agentic Foundation-specific metrics
        agentic_foundation_metrics = {
            "ai_capability_operation_logs": self._count_logs_by_field("capability_type"),
            "agent_reasoning_operation_logs": self._count_logs_by_field("reasoning_type"),
            "autonomous_operation_logs": self._count_logs_by_field("operation_type"),
            "mcp_tool_operation_logs": self._count_logs_by_field("tool_name"),
            "agent_communication_operation_logs": self._count_logs_by_field("communication_type"),
            "ai_model_operation_logs": self._count_logs_by_field("model_name"),
            "reasoning_engine_operation_logs": self._count_logs_by_field("engine_type"),
            "autonomy_control_operation_logs": self._count_logs_by_field("control_type"),
            "agent_coordination_operation_logs": self._count_logs_by_field("coordination_type")
        }
        
        base_summary["agentic_foundation_metrics"] = agentic_foundation_metrics
        return base_summary
    
    def _count_logs_by_field(self, field_name: str) -> int:
        """Count logs that contain a specific field."""
        count = 0
        for log_entry in self.log_entries:
            if field_name in log_entry.data:
                count += 1
        return count


