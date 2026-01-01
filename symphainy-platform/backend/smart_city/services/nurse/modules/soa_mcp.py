#!/usr/bin/env python3
"""
Nurse Service - SOA/MCP Module

Micro-module for SOA API exposure and MCP tool integration.
"""

from typing import Any, Dict
from datetime import datetime


class SoaMcp:
    """SOA/MCP module for Nurse service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def initialize_soa_api_exposure(self):
        """Initialize SOA API exposure for Smart City capabilities."""
        self.service.soa_apis = {
            "collect_telemetry": {
                "endpoint": "/api/nurse/telemetry",
                "method": "POST",
                "description": "Collect telemetry data using OpenTelemetry",
                "parameters": ["service_name", "metric_name", "metric_value", "tags"]
            },
            "get_health_metrics": {
                "endpoint": "/api/nurse/health/{service_name}",
                "method": "GET",
                "description": "Get health metrics for a service",
                "parameters": ["service_name"]
            },
            "set_alert_threshold": {
                "endpoint": "/api/nurse/alerts/thresholds",
                "method": "POST",
                "description": "Set alert threshold for a metric",
                "parameters": ["service_name", "metric_name", "threshold"]
            },
            "run_diagnostics": {
                "endpoint": "/api/nurse/diagnostics/{service_name}",
                "method": "POST",
                "description": "Run system diagnostics for a service",
                "parameters": ["service_name"]
            },
            "start_trace": {
                "endpoint": "/api/nurse/traces",
                "method": "POST",
                "description": "Start a distributed trace using Tempo",
                "parameters": ["trace_name", "context"]
            },
            "get_trace": {
                "endpoint": "/api/nurse/traces/{trace_id}",
                "method": "GET",
                "description": "Retrieve trace data from Tempo",
                "parameters": ["trace_id"]
            },
            "orchestrate_health_monitoring": {
                "endpoint": "/api/nurse/orchestration/health",
                "method": "POST",
                "description": "Orchestrate health monitoring across multiple services",
                "parameters": ["services"]
            },
            "monitor_log_aggregation": {
                "endpoint": "/api/nurse/logs/aggregation",
                "method": "GET",
                "description": "Monitor log aggregation health and metrics",
                "parameters": []
            },
            "query_logs": {
                "endpoint": "/api/nurse/logs/query",
                "method": "POST",
                "description": "Query logs from aggregation backend using LogQL",
                "parameters": ["query", "limit", "start", "end"]
            },
            "search_logs": {
                "endpoint": "/api/nurse/logs/search",
                "method": "POST",
                "description": "Search logs with filters (service, level, time range)",
                "parameters": ["filters", "time_range"]
            },
            "get_log_metrics": {
                "endpoint": "/api/nurse/logs/metrics",
                "method": "GET",
                "description": "Get log volume and aggregation metrics",
                "parameters": ["time_range"]
            },
            # NEW: Observability APIs (Phase 2.2)
            "record_platform_event": {
                "endpoint": "/api/nurse/observability/event",
                "method": "POST",
                "description": "Record platform event (log, metric, or trace)",
                "parameters": ["event_type", "event_data", "trace_id", "user_context"],
                "handler": self.service.observability_module.record_platform_event
            },
            "record_agent_execution": {
                "endpoint": "/api/nurse/observability/agent",
                "method": "POST",
                "description": "Record agent execution for observability",
                "parameters": ["agent_id", "agent_name", "prompt_hash", "response", "trace_id", "execution_metadata", "user_context"],
                "handler": self.service.observability_module.record_agent_execution
            },
            "get_observability_data": {
                "endpoint": "/api/nurse/observability/data",
                "method": "POST",
                "description": "Query observability data (logs, metrics, traces, agent_executions)",
                "parameters": ["data_type", "filters", "limit", "user_context"],
                "handler": self.service.observability_module.get_observability_data
            }
        }
        
        if self.service.logger:
            self.service.logger.info(f"✅ SOA APIs exposed: {len(self.service.soa_apis)} endpoints")
    
    async def initialize_mcp_tool_integration(self):
        """Initialize MCP tool integration for health monitoring operations."""
        self.service.mcp_tools = {
            "health_monitor": {
                "name": "health_monitor",
                "description": "Monitor health metrics and system status",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "service_name": {"type": "string", "description": "Service name"},
                        "monitoring_options": {"type": "object", "description": "Monitoring options"}
                    },
                    "required": ["service_name"]
                }
            },
            "telemetry_collector": {
                "name": "telemetry_collector",
                "description": "Collect telemetry data using OpenTelemetry",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "service_name": {"type": "string", "description": "Service name"},
                        "metric_name": {"type": "string", "description": "Metric name"},
                        "metric_value": {"type": "number", "description": "Metric value"},
                        "tags": {"type": "object", "description": "Metric tags"}
                    },
                    "required": ["service_name", "metric_name", "metric_value"]
                }
            },
            "trace_analyzer": {
                "name": "trace_analyzer",
                "description": "Analyze distributed traces using Tempo",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "trace_id": {"type": "string", "description": "Trace ID"},
                        "analysis_options": {"type": "object", "description": "Analysis options"}
                    },
                    "required": ["trace_id"]
                }
            },
            "alert_manager": {
                "name": "alert_manager",
                "description": "Manage alerts and thresholds",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "service_name": {"type": "string", "description": "Service name"},
                        "metric_name": {"type": "string", "description": "Metric name"},
                        "threshold": {"type": "number", "description": "Alert threshold"}
                    },
                    "required": ["service_name", "metric_name", "threshold"]
                }
            },
            "monitor_log_aggregation": {
                "name": "monitor_log_aggregation",
                "description": "Monitor log aggregation health and collect metrics",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "query_logs": {
                "name": "query_logs",
                "description": "Query logs from aggregation backend using LogQL query language",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "LogQL query string (e.g., '{service_name=\"backend\"}')"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of log entries to return",
                            "default": 100
                        },
                        "start": {
                            "type": "string",
                            "description": "Start time (ISO 8601 or Unix timestamp)"
                        },
                        "end": {
                            "type": "string",
                            "description": "End time (ISO 8601 or Unix timestamp)"
                        }
                    },
                    "required": ["query"]
                }
            },
            "search_logs": {
                "name": "search_logs",
                "description": "Search logs with filters (service, level, time range)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "description": "Search filters (service_name, level, text, etc.)"
                        },
                        "time_range": {
                            "type": "object",
                            "description": "Time range for search (hours, start, end)"
                        }
                    },
                    "required": ["filters"]
                }
            },
            "get_log_metrics": {
                "name": "get_log_metrics",
                "description": "Get log volume and aggregation metrics",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "time_range": {
                            "type": "object",
                            "description": "Time range for metrics (hours, days, start, end)"
                        }
                    },
                    "required": []
                }
            }
        }
        
        if self.service.logger:
            self.service.logger.info(f"✅ MCP tools registered: {len(self.service.mcp_tools)} tools")
    
    async def register_capabilities(self) -> Dict[str, Any]:
        """Register Nurse capabilities with Curator using Phase 2 pattern (simplified for Smart City)."""
        try:
            # Build capabilities list with SOA API and MCP Tool contracts
            capabilities = []
            
            # Create health_monitoring capability
            capabilities.append({
                "name": "health_monitoring",
                "protocol": "NurseServiceProtocol",
                "description": "Health metrics monitoring and status tracking",
                "contracts": {
                    "soa_api": {
                        "api_name": "get_health_metrics",
                        "endpoint": self.service.soa_apis.get("get_health_metrics", {}).get("endpoint", "/soa/nurse/get_health_metrics"),
                        "method": self.service.soa_apis.get("get_health_metrics", {}).get("method", "GET"),
                        "handler": getattr(self.service, "get_health_metrics", None),
                        "metadata": {
                            "description": "Get health metrics for a service"
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "nurse_health_monitor",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "nurse_health_monitor",
                            "description": "Monitor health metrics and system status",
                            "input_schema": self.service.mcp_tools.get("health_monitor", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Create telemetry_collection capability
            capabilities.append({
                "name": "telemetry_collection",
                "protocol": "NurseServiceProtocol",
                "description": "Telemetry data collection using OpenTelemetry",
                "contracts": {
                    "soa_api": {
                        "api_name": "collect_telemetry",
                        "endpoint": self.service.soa_apis.get("collect_telemetry", {}).get("endpoint", "/soa/nurse/collect_telemetry"),
                        "method": self.service.soa_apis.get("collect_telemetry", {}).get("method", "POST"),
                        "handler": getattr(self.service, "collect_telemetry", None),
                        "metadata": {
                            "description": "Collect telemetry data using OpenTelemetry"
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "nurse_telemetry_collector",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "nurse_telemetry_collector",
                            "description": "Collect telemetry data using OpenTelemetry",
                            "input_schema": self.service.mcp_tools.get("telemetry_collector", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Create distributed_tracing capability
            capabilities.append({
                "name": "distributed_tracing",
                "protocol": "NurseServiceProtocol",
                "description": "Distributed tracing using Tempo",
                "contracts": {
                    "soa_api": {
                        "api_name": "start_trace",
                        "endpoint": self.service.soa_apis.get("start_trace", {}).get("endpoint", "/soa/nurse/start_trace"),
                        "method": self.service.soa_apis.get("start_trace", {}).get("method", "POST"),
                        "handler": getattr(self.service, "start_trace", None),
                        "metadata": {
                            "description": "Start a distributed trace using Tempo",
                            "apis": ["start_trace", "get_trace"]
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "nurse_trace_analyzer",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "nurse_trace_analyzer",
                            "description": "Analyze distributed traces using Tempo",
                            "input_schema": self.service.mcp_tools.get("trace_analyzer", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Create log_aggregation capability
            capabilities.append({
                "name": "log_aggregation",
                "protocol": "NurseServiceProtocol",
                "description": "Log aggregation and querying using Loki",
                "contracts": {
                    "soa_api": {
                        "api_name": "monitor_log_aggregation",
                        "endpoint": self.service.soa_apis.get("monitor_log_aggregation", {}).get("endpoint", "/api/nurse/logs/aggregation"),
                        "method": self.service.soa_apis.get("monitor_log_aggregation", {}).get("method", "GET"),
                        "handler": getattr(self.service, "monitor_log_aggregation", None),
                        "metadata": {
                            "description": "Monitor log aggregation health and metrics",
                            "apis": ["monitor_log_aggregation", "query_logs", "search_logs", "get_log_metrics"]
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "nurse_monitor_log_aggregation",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "nurse_monitor_log_aggregation",
                            "description": "Monitor log aggregation health and collect metrics",
                            "input_schema": self.service.mcp_tools.get("monitor_log_aggregation", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Create alert_management capability
            capabilities.append({
                "name": "alert_management",
                "protocol": "NurseServiceProtocol",
                "description": "Alert threshold management and monitoring",
                "contracts": {
                    "soa_api": {
                        "api_name": "set_alert_threshold",
                        "endpoint": self.service.soa_apis.get("set_alert_threshold", {}).get("endpoint", "/soa/nurse/set_alert_threshold"),
                        "method": self.service.soa_apis.get("set_alert_threshold", {}).get("method", "POST"),
                        "handler": getattr(self.service, "set_alert_threshold", None),
                        "metadata": {
                            "description": "Set alert threshold for a metric"
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "nurse_alert_manager",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "nurse_alert_manager",
                            "description": "Manage alerts and thresholds",
                            "input_schema": self.service.mcp_tools.get("alert_manager", {}).get("input_schema", {})
                        }
                    }
                }
            })
            
            # Register using register_with_curator (simplified Phase 2 pattern)
            soa_api_names = list(self.service.soa_apis.keys())
            mcp_tool_names = [f"nurse_{tool}" for tool in self.service.mcp_tools.keys()]
            
            success = await self.service.register_with_curator(
                capabilities=capabilities,
                soa_apis=soa_api_names,
                mcp_tools=mcp_tool_names,
                protocols=[{
                    "name": "NurseServiceProtocol",
                    "definition": {
                        "methods": {api: {"input_schema": {}, "output_schema": {}} for api in soa_api_names}
                    }
                }]
            )
            
            if success:
                if self.service.logger:
                    self.service.logger.info(f"✅ Nurse registered with Curator (Phase 2 pattern - Smart City): {len(capabilities)} capabilities")
            else:
                if self.service.logger:
                    self.service.logger.warning("⚠️ Failed to register Nurse with Curator")
                    
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to register Nurse capabilities: {e}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return capabilities metadata
        return await self._get_nurse_capabilities_dict()
    
    async def register_nurse_capabilities(self) -> Dict[str, Any]:
        """Register Nurse Service capabilities (backward compatibility - calls register_capabilities first)."""
        # Call register_capabilities first to ensure Curator registration happens
        return await self.register_capabilities()
    
    async def _get_nurse_capabilities_dict(self) -> Dict[str, Any]:
        """Get Nurse Service capabilities dict."""
        capabilities = {
            "service_name": "NurseService",
            "service_type": "health_monitor",
            "realm": "smart_city",
            "capabilities": [
                "health_monitoring",
                "telemetry_collection",
                "distributed_tracing",
                "alert_management",
                "system_diagnostics",
                "infrastructure_integration"
            ],
            "infrastructure_connections": {
                "telemetry": "OpenTelemetry",
                "tracing": "Tempo",
                "health_monitoring": "Redis",
                "alert_management": "Redis"
            },
            "soa_apis": self.service.soa_apis,
            "mcp_tools": self.service.mcp_tools,
            "status": "active",
            "infrastructure_connected": self.service.is_infrastructure_connected,
            "infrastructure_correct_from_start": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.service.logger:
            self.service.logger.info("✅ Nurse capabilities registered")
        
        return capabilities

