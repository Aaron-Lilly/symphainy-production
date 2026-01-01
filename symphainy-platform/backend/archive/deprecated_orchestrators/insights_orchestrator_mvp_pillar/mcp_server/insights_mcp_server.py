#!/usr/bin/env python3
"""
Insights MCP Server

Wraps Insights Orchestrator as MCP Tools for agent consumption.

IMPORTANT: MCP servers are at the ORCHESTRATOR level (not enabling service level).
"""

import os
import sys
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../../'))

from bases.mcp_server.mcp_server_base import MCPServerBase


class InsightsMCPServer(MCPServerBase):
    """
    MCP Server for Insights Orchestrator (MVP Use Case).
    
    Provides use case-level tools for agents:
    - calculate_metrics_tool: High-level metrics calculation (orchestrates DataAnalyzer + MetricsCalculator)
    - generate_insights_tool: Insight generation (orchestrates DataAnalyzer + MetricsCalculator + VisualizationEngine)
    - create_visualization_tool: Visualization creation (orchestrates MetricsCalculator + VisualizationEngine)
    
    These are HIGH-LEVEL tools that orchestrate multiple enabling services internally.
    """
    
    def __init__(self, orchestrator, di_container):
        """Initialize Insights MCP Server."""
        super().__init__(
            service_name="insights_mcp",
            di_container=di_container
        )
        self.orchestrator = orchestrator
    
    def register_server_tools(self) -> None:
        """Register MCP tools (use case-level)."""
        
        self.register_tool(
            name="calculate_metrics_tool",
            description="Calculate business metrics from data. Orchestrates DataAnalyzer + MetricsCalculator.",
            handler=self._calculate_metrics_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "ID of resource to calculate metrics for"
                    },
                    "options": {
                        "type": "object",
                        "description": "Optional parameters (metric_types, etc.)"
                    }
                },
                "required": ["resource_id"]
            }
        )
        
        self.register_tool(
            name="generate_insights_tool",
            description="Generate insights from data. Orchestrates DataAnalyzer + MetricsCalculator + VisualizationEngine.",
            handler=self._generate_insights_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "ID of resource to generate insights for"
                    },
                    "options": {
                        "type": "object",
                        "description": "Optional parameters (include_visualization, etc.)"
                    }
                },
                "required": ["resource_id"]
            }
        )
        
        self.register_tool(
            name="create_visualization_tool",
            description="Create visual dashboards. Orchestrates MetricsCalculator + VisualizationEngine.",
            handler=self._create_visualization_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "ID of resource to create visualization for"
                    },
                    "options": {
                        "type": "object",
                        "description": "Optional parameters (chart_type, etc.)"
                    }
                },
                "required": ["resource_id"]
            }
        )
        
        self.register_tool(
            name="query_data_insights",
            description="Process natural language query about analysis results. Ask questions like 'What are the top 3 revenue drivers?' or 'Show me a chart of profit margins'.",
            handler=self._query_data_insights_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query (e.g., 'What were the top 5 items?', 'Show me a chart', 'What are the key recommendations?')"
                    },
                    "analysis_id": {
                        "type": "string",
                        "description": "ID of the analysis to query against"
                    },
                    "query_type": {
                        "type": "string",
                        "enum": ["table", "chart", "summary", "auto"],
                        "description": "Preferred response type (defaults to 'auto' for automatic detection)"
                    }
                },
                "required": ["query", "analysis_id"]
            }
        )
        
        # Tool 5: Analyze Content for Insights
        self.register_tool(
            name="analyze_content_for_insights_tool",
            description="Analyze content for insights. Orchestrates DataAnalyzerService.",
            handler=self._analyze_content_for_insights_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "ID of resource to analyze"
                    },
                    "options": {
                        "type": "object",
                        "description": "Optional analysis configuration"
                    }
                },
                "required": ["resource_id"]
            }
        )
        
        # Tool 6: Query Analysis Results
        self.register_tool(
            name="query_analysis_results_tool",
            description="Query analysis results for deep exploration. Orchestrates DataAnalyzerService.",
            handler=self._query_analysis_results_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query string for exploration"
                    },
                    "resource_id": {
                        "type": "string",
                        "description": "ID of resource"
                    },
                    "query_intent": {
                        "type": "object",
                        "description": "Optional query intent metadata"
                    },
                    "options": {
                        "type": "object",
                        "description": "Optional query configuration"
                    }
                },
                "required": ["query", "resource_id"]
            }
        )
        
        # Tool 7: Generate Grounded Insights (Agent-Assisted)
        self.register_tool(
            name="generate_grounded_insights_tool",
            description="Agent-assisted grounded insights generation (AI Showcase - No Hallucination). Orchestrates data science tools to generate insights from actual data.",
            handler=self._generate_grounded_insights_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "Data resource identifier"
                    },
                    "analysis_options": {
                        "type": "object",
                        "description": "Optional analysis configuration"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    }
                },
                "required": ["resource_id"]
            }
        )
        
        # Tool 8: Process Double-Click Query (Agent-Assisted)
        self.register_tool(
            name="process_double_click_query_tool",
            description="Agent-assisted double-click query processing for deep exploration. Enables plain English queries on insights.",
            handler=self._process_double_click_query_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "User query for deep exploration"
                    },
                    "resource_id": {
                        "type": "string",
                        "description": "Data resource identifier"
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context data"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    }
                },
                "required": ["query", "resource_id"]
            }
        )
        
        # Tool 9: Generate Insights Summary (Agent-Assisted)
        self.register_tool(
            name="generate_insights_summary_tool",
            description="Agent-assisted comprehensive insights summary generation with recommendations based on data.",
            handler=self._generate_insights_summary_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "Data resource identifier"
                    },
                    "insights_data": {
                        "type": "object",
                        "description": "Optional pre-computed insights"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    }
                },
                "required": ["resource_id"]
            }
        )
        
        # Tool 10: Explain Data Science Results (Agent-Assisted)
        self.register_tool(
            name="explain_data_science_results_tool",
            description="Agent-assisted plain English explanation of data science results. Translates technical findings to business terms.",
            handler=self._explain_data_science_results_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "analysis_result": {
                        "type": "object",
                        "description": "Data analysis results"
                    },
                    "metrics_result": {
                        "type": "object",
                        "description": "Optional metrics results"
                    },
                    "visualization_result": {
                        "type": "object",
                        "description": "Optional visualization results"
                    }
                },
                "required": ["analysis_result"]
            }
        )
    
    async def execute_tool(self, tool_name: str, parameters: dict, user_context: Optional[Dict[str, Any]] = None) -> dict:
        """
        Execute tool by routing to orchestrator.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        try:
            # Start telemetry tracking
            if self.utilities.telemetry:
                try:
                    await self.utilities.telemetry.collect_metric({
                        "name": "execute_tool_start",
                        "value": 1.0,
                        "type": "counter",
                        "labels": {"tool_name": tool_name, "mcp_server": self.service_name}
                    })
                except Exception:
                    pass  # Telemetry is optional
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.utilities.security
                if security:
                    if not await security.check_permissions(user_context, f"mcp_tool.{tool_name}", "execute"):
                        if self.utilities.health:
                            try:
                                await self.utilities.health.record_metric("execute_tool_access_denied", 1.0, {"tool_name": tool_name})
                            except Exception:
                                pass
                        raise PermissionError(f"Access denied: insufficient permissions to execute tool '{tool_name}'")
            
            # Tenant validation (multi-tenancy support)
            if user_context:
                tenant = self.utilities.tenant
                if tenant:
                    # Handle both dict and UserContext dataclass
                    if isinstance(user_context, dict):
                        tenant_id = user_context.get("tenant_id")
                    else:
                        tenant_id = getattr(user_context, "tenant_id", None)
                    
                    if tenant_id:
                        # Handle both sync and async validate_tenant_access
                        if hasattr(tenant, 'validate_tenant_access'):
                            if asyncio.iscoroutinefunction(tenant.validate_tenant_access):
                                has_access = await tenant.validate_tenant_access(tenant_id, tenant_id)
                            else:
                                has_access = tenant.validate_tenant_access(tenant_id, tenant_id)
                            
                            if not has_access:
                                if self.utilities.health:
                                    try:
                                        await self.utilities.health.record_metric("execute_tool_tenant_denied", 1.0, {"tool_name": tool_name, "tenant_id": tenant_id})
                                    except Exception:
                                        pass
                                raise PermissionError(f"Tenant access denied for tool '{tool_name}': {tenant_id}")
            
            tool_handlers = {
                "calculate_metrics_tool": self._calculate_metrics_tool,
                "generate_insights_tool": self._generate_insights_tool,
                "create_visualization_tool": self._create_visualization_tool,
                "query_data_insights": self._query_data_insights_tool,
                "analyze_content_for_insights_tool": self._analyze_content_for_insights_tool,
                "query_analysis_results_tool": self._query_analysis_results_tool,
                "generate_grounded_insights_tool": self._generate_grounded_insights_tool,
                "process_double_click_query_tool": self._process_double_click_query_tool,
                "generate_insights_summary_tool": self._generate_insights_summary_tool,
                "explain_data_science_results_tool": self._explain_data_science_results_tool
            }
            
            handler = tool_handlers.get(tool_name)
            if handler:
                # Add user_context to parameters if not present
                if user_context and "user_context" not in parameters:
                    parameters["user_context"] = user_context
                
                result = await handler(**parameters)
                
                # End telemetry tracking
                if self.utilities.telemetry:
                    try:
                        await self.utilities.telemetry.collect_metric({
                            "name": "execute_tool_complete",
                            "value": 1.0,
                            "type": "counter",
                            "labels": {"tool_name": tool_name, "status": "success" if result.get("success", True) else "failed"}
                        })
                    except Exception:
                        pass
                
                return result
            else:
                # Record health metric (tool not found)
                if self.utilities.health:
                    try:
                        await self.utilities.health.record_metric("execute_tool_not_found", 1.0, {"tool_name": tool_name})
                    except Exception:
                        pass
                
                # End telemetry tracking
                if self.utilities.telemetry:
                    try:
                        await self.utilities.telemetry.collect_metric({
                            "name": "execute_tool_complete",
                            "value": 0.0,
                            "type": "counter",
                            "labels": {"tool_name": tool_name, "status": "not_found"}
                        })
                    except Exception:
                        pass
                
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            # Error handling
            self.utilities.logger.error(f"❌ execute_tool failed for {tool_name}: {e}")
            
            # Audit logging (if security available)
            if self.utilities.security:
                try:
                    await self.utilities.security.audit_log({
                        "action": "execute_tool_failed",
                        "mcp_server": self.service_name,
                        "tool_name": tool_name,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception:
                    pass  # Audit is optional
            
            # Record health metric (failure)
            if self.utilities.health:
                try:
                    await self.utilities.health.record_metric("execute_tool_error", 1.0, {
                        "tool_name": tool_name,
                        "error": type(e).__name__
                    })
                except Exception:
                    pass
            
            # End telemetry tracking
            if self.utilities.telemetry:
                try:
                    await self.utilities.telemetry.collect_metric({
                        "name": "execute_tool_complete",
                        "value": 0.0,
                        "type": "counter",
                        "labels": {"tool_name": tool_name, "status": "error"}
                    })
                except Exception:
                    pass
            
            return {"error": f"Failed to execute tool {tool_name}: {str(e)}"}
    
    async def _calculate_metrics_tool(
        self,
        resource_id: str,
        options: dict = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Calculate business metrics.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        return await self.orchestrator.calculate_metrics(
            resource_id=resource_id,
            options=options,
            user_context=user_context
        )
    
    async def _generate_insights_tool(
        self,
        resource_id: str,
        options: dict = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Generate insights from data.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        return await self.orchestrator.generate_insights(
            resource_id=resource_id,
            options=options,
            user_context=user_context
        )
    
    async def _create_visualization_tool(
        self,
        resource_id: str,
        options: dict = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Create visual dashboards.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        return await self.orchestrator.create_visualization(
            resource_id=resource_id,
            options=options,
            user_context=user_context
        )
    
    async def _query_data_insights_tool(
        self,
        query: str,
        analysis_id: str,
        query_type: str = "auto",
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Process natural language query about analysis results.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        return await self.orchestrator.query_analysis(
            query=query,
            analysis_id=analysis_id,
            query_type=query_type,
            user_context=user_context
        )
    
    async def _analyze_content_for_insights_tool(
        self,
        resource_id: str,
        options: dict = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Analyze content for insights.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        return await self.orchestrator.analyze_content_for_insights(
            resource_id=resource_id,
            options=options,
            user_context=user_context
        )
    
    async def _query_analysis_results_tool(
        self,
        query: str,
        resource_id: str,
        query_intent: dict = None,
        options: dict = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Query analysis results for deep exploration.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        return await self.orchestrator.query_analysis_results(
            query=query,
            resource_id=resource_id,
            query_intent=query_intent,
            options=options,
            user_context=user_context
        )
    
    async def _generate_grounded_insights_tool(
        self,
        resource_id: str,
        analysis_options: dict = None,
        user_id: str = "anonymous",
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Agent-assisted grounded insights generation (AI Showcase).
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        # Get agent from orchestrator
        if hasattr(self.orchestrator, 'specialist_agent') and self.orchestrator.specialist_agent:
            return await self.orchestrator.specialist_agent.generate_grounded_insights(
                resource_id=resource_id,
                analysis_options=analysis_options,
                user_id=user_id,
                user_context=user_context
            )
        else:
            return {
                "success": False,
                "error": "Insights Specialist Agent not available"
            }
    
    async def _process_double_click_query_tool(
        self,
        query: str,
        resource_id: str,
        context: dict = None,
        user_id: str = "anonymous",
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Agent-assisted double-click query processing.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        # Get agent from orchestrator
        if hasattr(self.orchestrator, 'specialist_agent') and self.orchestrator.specialist_agent:
            return await self.orchestrator.specialist_agent.process_double_click_query(
                query=query,
                resource_id=resource_id,
                context=context,
                user_id=user_id,
                user_context=user_context
            )
        else:
            return {
                "success": False,
                "error": "Insights Specialist Agent not available"
            }
    
    async def _generate_insights_summary_tool(
        self,
        resource_id: str,
        insights_data: dict = None,
        user_id: str = "anonymous",
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Agent-assisted insights summary generation.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        # Get agent from orchestrator
        if hasattr(self.orchestrator, 'specialist_agent') and self.orchestrator.specialist_agent:
            return await self.orchestrator.specialist_agent.generate_insights_summary(
                resource_id=resource_id,
                insights_data=insights_data,
                user_id=user_id,
                user_context=user_context
            )
        else:
            return {
                "success": False,
                "error": "Insights Specialist Agent not available"
            }
    
    async def _explain_data_science_results_tool(
        self,
        analysis_result: dict,
        metrics_result: dict = None,
        visualization_result: dict = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        MCP Tool: Agent-assisted plain English explanation of data science results.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        # Get agent from orchestrator
        if hasattr(self.orchestrator, 'specialist_agent') and self.orchestrator.specialist_agent:
            return await self.orchestrator.specialist_agent.explain_data_science_results(
                analysis_result=analysis_result,
                metrics_result=metrics_result,
                visualization_result=visualization_result,
                user_context=user_context
            )
        else:
            return {
                "success": False,
                "error": "Insights Specialist Agent not available"
            }
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return machine + human readable usage guide."""
        return {
            "server_name": self.service_name,
            "description": "Insights MCP Server - Provides insights generation tools",
            "tools": {
                "calculate_metrics_tool": "Calculate business metrics from data",
                "generate_insights_tool": "Generate insights from data",
                "create_visualization_tool": "Create visualization from data",
                "query_data_insights": "Query data insights",
                "analyze_content_for_insights_tool": "Analyze content for insights",
                "query_analysis_results_tool": "Query analysis results",
                "generate_grounded_insights_tool": "Generate grounded insights",
                "process_double_click_query_tool": "Process double-click query",
                "generate_insights_summary_tool": "Generate insights summary",
                "explain_data_science_results_tool": "Explain data science results"
            },
            "usage_pattern": "All tools require user_context for multi-tenancy and security"
        }
    
    def get_tool_list(self) -> list:
        """Return list of available tool names."""
        return [
            "calculate_metrics_tool",
            "generate_insights_tool",
            "create_visualization_tool",
            "query_data_insights",
            "analyze_content_for_insights_tool",
            "query_analysis_results_tool",
            "generate_grounded_insights_tool",
            "process_double_click_query_tool",
            "generate_insights_summary_tool",
            "explain_data_science_results_tool"
        ]
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Return health status with upstream dependency checks."""
        try:
            # Check orchestrator health
            orchestrator_health = "healthy"
            if hasattr(self.orchestrator, 'get_health_status'):
                try:
                    health = await self.orchestrator.get_health_status()
                    orchestrator_health = health.get("status", "unknown")
                except Exception:
                    orchestrator_health = "error"
            
            return {
                "server_name": self.service_name,
                "status": "healthy" if orchestrator_health == "healthy" else "degraded",
                "orchestrator_status": orchestrator_health,
                "tools_registered": len(self.get_tool_list()),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "server_name": self.service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_version_info(self) -> Dict[str, Any]:
        """Return version and compatibility info."""
        return {
            "server_name": self.service_name,
            "version": "1.0.0",
            "api_version": "v1",
            "compatible_with": ["insights_orchestrator"],
            "timestamp": datetime.utcnow().isoformat()
        }




