#!/usr/bin/env python3
"""
Business Outcomes MCP Server

Wraps Business Outcomes Orchestrator as MCP Tools for agent consumption.

IMPORTANT: MCP servers are at the ORCHESTRATOR level (not enabling service level).
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../../'))

from bases.mcp_server.mcp_server_base import MCPServerBase


class BusinessOutcomesMCPServer(MCPServerBase):
    """
    MCP Server for Business Outcomes Orchestrator (MVP Use Case).
    
    Provides use case-level tools for agents:
    - track_outcomes_tool: Track business outcomes and KPIs
    - generate_roadmap_tool: Generate strategic roadmaps
    - calculate_kpis_tool: Calculate key performance indicators
    - analyze_outcomes_tool: Analyze business outcome trends
    - generate_strategic_roadmap_tool: Generate strategic roadmap from pillar outputs
    - generate_poc_proposal_tool: Generate POC proposal from pillar outputs
    
    These are HIGH-LEVEL tools that orchestrate multiple enabling services internally.
    """
    
    def __init__(self, orchestrator, di_container):
        """Initialize Business Outcomes MCP Server."""
        super().__init__(
            service_name="business_outcomes_mcp",
            di_container=di_container
        )
        self.orchestrator = orchestrator
    
    def register_server_tools(self) -> None:
        """Register MCP tools (use case-level)."""
        
        self.register_tool(
            name="track_outcomes_tool",
            description="Track business outcomes and KPIs. Orchestrates MetricsCalculator + ReportGenerator.",
            handler=self._track_outcomes_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "ID of resource to track outcomes for"
                    },
                    "options": {
                        "type": "object",
                        "description": "Optional tracking options"
                    }
                },
                "required": ["resource_id"]
            }
        )
        
        self.register_tool(
            name="generate_roadmap_tool",
            description="Generate business roadmap. Orchestrates RoadmapGenerationService.",
            handler=self._generate_roadmap_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "ID of resource to generate roadmap for"
                    },
                    "options": {
                        "type": "object",
                        "description": "Optional roadmap generation options"
                    }
                },
                "required": ["resource_id"]
            }
        )
        
        self.register_tool(
            name="calculate_kpis_tool",
            description="Calculate key performance indicators. Orchestrates MetricsCalculator.",
            handler=self._calculate_kpis_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "ID of resource to calculate KPIs for"
                    },
                    "options": {
                        "type": "object",
                        "description": "Optional KPI calculation options"
                    }
                },
                "required": ["resource_id"]
            }
        )
        
        self.register_tool(
            name="analyze_outcomes_tool",
            description="Analyze business outcome trends. Orchestrates MetricsCalculator + DataAnalyzer.",
            handler=self._analyze_outcomes_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "ID of resource to analyze outcomes for"
                    },
                    "options": {
                        "type": "object",
                        "description": "Optional analysis options"
                    }
                },
                "required": ["resource_id"]
            }
        )
        
        self.register_tool(
            name="generate_strategic_roadmap_tool",
            description="Generate strategic roadmap from pillar outputs. Orchestrates RoadmapGenerationService.",
            handler=self._generate_strategic_roadmap_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "business_context": {
                        "type": "object",
                        "description": "Context with pillar_outputs and roadmap_options"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    }
                },
                "required": ["business_context"]
            }
        )
        
        self.register_tool(
            name="generate_poc_proposal_tool",
            description="Generate comprehensive POC proposal from pillar outputs with agent refinement. Orchestrates POCGenerationService + SpecialistAgent.",
            handler=self._generate_poc_proposal_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "business_context": {
                        "type": "object",
                        "description": "Context with pillar_outputs and proposal_options"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    }
                },
                "required": ["business_context"]
            }
        )
        
        self.register_tool(
            name="generate_comprehensive_poc_tool",
            description="Generate comprehensive POC proposal with full roadmap, financials, and metrics. Orchestrates POCGenerationService.",
            handler=self._generate_comprehensive_poc_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "pillar_outputs": {
                        "type": "object",
                        "description": "Outputs from Content, Insights, and Operations pillars"
                    },
                    "poc_type": {
                        "type": "string",
                        "enum": ["technical", "business", "hybrid"],
                        "description": "Type of POC to generate"
                    },
                    "options": {
                        "type": "object",
                        "description": "Optional generation options"
                    }
                },
                "required": ["pillar_outputs"]
            }
        )
        
        self.register_tool(
            name="create_comprehensive_strategic_plan_tool",
            description="Create comprehensive strategic plan including roadmap, goals, and performance metrics. Orchestrates RoadmapGenerationService.",
            handler=self._create_comprehensive_strategic_plan_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "business_context": {
                        "type": "object",
                        "description": "Business context with objectives, business_name, budget, timeline"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    }
                },
                "required": ["business_context"]
            }
        )
        
        self.register_tool(
            name="track_strategic_progress_tool",
            description="Track strategic progress with business analysis and recommendations. Orchestrates RoadmapGenerationService.",
            handler=self._track_strategic_progress_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "goals": {
                        "type": "array",
                        "description": "List of strategic goals to track",
                        "items": {"type": "object"}
                    },
                    "performance_data": {
                        "type": "object",
                        "description": "Optional performance data for analysis"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    }
                },
                "required": ["goals"]
            }
        )
        
        self.register_tool(
            name="analyze_strategic_trends_tool",
            description="Analyze strategic trends with business implications and recommendations. Orchestrates RoadmapGenerationService.",
            handler=self._analyze_strategic_trends_tool,
            input_schema={
                "type": "object",
                "properties": {
                    "market_data": {
                        "type": "object",
                        "description": "Market and industry data for trend analysis"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    }
                },
                "required": ["market_data"]
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
        # Start telemetry tracking
        self.telemetry_emission.emit_tool_execution_start_telemetry(tool_name, parameters)
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.utilities.security
                if security:
                    if not await security.check_permissions(user_context, f"mcp_tool.{tool_name}", "execute"):
                        self.telemetry_emission.emit_tool_execution_complete_telemetry(tool_name, success=False)
                        raise PermissionError(f"Access denied: insufficient permissions to execute tool '{tool_name}'")
            
            # Tenant validation (multi-tenancy support)
            if user_context:
                tenant = self.utilities.tenant
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        # For MCP tools, user accesses their own tenant resources
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            self.telemetry_emission.emit_tool_execution_complete_telemetry(tool_name, success=False)
                            raise PermissionError(f"Tenant access denied for tool '{tool_name}': {tenant_id}")
            
            tool_handlers = {
                "track_outcomes_tool": self._track_outcomes_tool,
                "generate_roadmap_tool": self._generate_roadmap_tool,
                "calculate_kpis_tool": self._calculate_kpis_tool,
                "analyze_outcomes_tool": self._analyze_outcomes_tool,
                "generate_strategic_roadmap_tool": self._generate_strategic_roadmap_tool,
                "generate_poc_proposal_tool": self._generate_poc_proposal_tool,
                "generate_comprehensive_poc_tool": self._generate_comprehensive_poc_tool,
                "create_comprehensive_strategic_plan_tool": self._create_comprehensive_strategic_plan_tool,
                "track_strategic_progress_tool": self._track_strategic_progress_tool,
                "analyze_strategic_trends_tool": self._analyze_strategic_trends_tool
            }
            
            handler = tool_handlers.get(tool_name)
            if handler:
                result = await handler(**parameters, user_context=user_context)
                self.telemetry_emission.emit_tool_execution_complete_telemetry(tool_name, success=True)
                return result
            else:
                self.telemetry_emission.emit_tool_execution_complete_telemetry(tool_name, success=False)
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
            
            self.telemetry_emission.emit_tool_execution_complete_telemetry(tool_name, success=False, details={"error": str(e)})
            return {"error": f"Failed to execute tool {tool_name}: {str(e)}"}
    
    async def _track_outcomes_tool(self, resource_id: str, options: dict = None, user_context: Optional[Dict[str, Any]] = None) -> dict:
        """MCP Tool: Track business outcomes and KPIs. Includes full utility usage."""
        return await self.orchestrator.track_outcomes(resource_id, options, user_context=user_context)
    
    async def _generate_roadmap_tool(self, resource_id: str, options: dict = None, user_context: Optional[Dict[str, Any]] = None) -> dict:
        """MCP Tool: Generate business roadmap. Includes full utility usage."""
        return await self.orchestrator.generate_roadmap(resource_id, options, user_context=user_context)
    
    async def _calculate_kpis_tool(self, resource_id: str, options: dict = None, user_context: Optional[Dict[str, Any]] = None) -> dict:
        """MCP Tool: Calculate key performance indicators. Includes full utility usage."""
        return await self.orchestrator.calculate_kpis(resource_id, options, user_context=user_context)
    
    async def _analyze_outcomes_tool(self, resource_id: str, options: dict = None, user_context: Optional[Dict[str, Any]] = None) -> dict:
        """MCP Tool: Analyze business outcome trends. Includes full utility usage."""
        return await self.orchestrator.analyze_outcomes(resource_id, options, user_context=user_context)
    
    async def _generate_strategic_roadmap_tool(self, business_context: dict, user_id: str = "anonymous", user_context: Optional[Dict[str, Any]] = None) -> dict:
        """MCP Tool: Generate strategic roadmap from pillar outputs. Includes full utility usage."""
        return await self.orchestrator.generate_strategic_roadmap(business_context, user_id, user_context=user_context)
    
    async def _generate_poc_proposal_tool(self, business_context: dict, user_id: str = "anonymous", user_context: Optional[Dict[str, Any]] = None) -> dict:
        """MCP Tool: Generate POC proposal from pillar outputs with agent refinement. Includes full utility usage."""
        return await self.orchestrator.generate_poc_proposal(business_context, user_id, user_context=user_context)
    
    async def _generate_comprehensive_poc_tool(self, pillar_outputs: dict, poc_type: str = "hybrid", options: dict = None, user_context: Optional[Dict[str, Any]] = None) -> dict:
        """MCP Tool: Generate comprehensive POC proposal with full roadmap, financials, and metrics. Includes full utility usage."""
        # Access POC Generation Service directly via orchestrator
        poc_service = await self.orchestrator._get_poc_generation_service()
        if not poc_service:
            return {
                "success": False,
                "error": "POC Generation Service not available"
            }
        return await poc_service.generate_poc_proposal(
            pillar_outputs=pillar_outputs,
            poc_type=poc_type,
            options=options or {},
            user_context=user_context
        )
    
    async def _create_comprehensive_strategic_plan_tool(self, business_context: dict, user_id: str = "anonymous", user_context: Optional[Dict[str, Any]] = None) -> dict:
        """MCP Tool: Create comprehensive strategic plan. Includes full utility usage."""
        return await self.orchestrator.create_comprehensive_strategic_plan(business_context, user_id, user_context=user_context)
    
    async def _track_strategic_progress_tool(self, goals: list, performance_data: dict = None, user_id: str = "anonymous", user_context: Optional[Dict[str, Any]] = None) -> dict:
        """MCP Tool: Track strategic progress. Includes full utility usage."""
        return await self.orchestrator.track_strategic_progress(goals, performance_data, user_id, user_context=user_context)
    
    async def _analyze_strategic_trends_tool(self, market_data: dict, user_id: str = "anonymous", user_context: Optional[Dict[str, Any]] = None) -> dict:
        """MCP Tool: Analyze strategic trends. Includes full utility usage."""
        return await self.orchestrator.analyze_strategic_trends(market_data, user_id, user_context=user_context)
    
    async def initialize(self):
        """Initialize the MCP server."""
        self.is_initialized = True
        self.logger.info(f"✅ {self.service_name} initialized")
    
    async def shutdown(self):
        """Shutdown the MCP server."""
        self.is_initialized = False
        self.logger.info(f"🛑 {self.service_name} shutdown")
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return machine + human readable usage guide."""
        return {
            "server_name": self.service_name,
            "description": "Business Outcomes MCP Server - Provides business outcomes tracking tools",
            "tools": {
                "track_outcomes_tool": "Track business outcomes and KPIs",
                "generate_roadmap_tool": "Generate strategic roadmaps",
                "calculate_kpis_tool": "Calculate key performance indicators",
                "analyze_outcomes_tool": "Analyze business outcome trends",
                "generate_strategic_roadmap_tool": "Generate strategic roadmap from pillar outputs",
                "generate_poc_proposal_tool": "Generate POC proposal from pillar outputs",
                "generate_comprehensive_poc_tool": "Generate comprehensive POC",
                "create_comprehensive_strategic_plan_tool": "Create comprehensive strategic plan",
                "track_strategic_progress_tool": "Track strategic progress",
                "analyze_strategic_trends_tool": "Analyze strategic trends"
            },
            "usage_pattern": "All tools require user_context for multi-tenancy and security"
        }
    
    def get_tool_list(self) -> list:
        """Return list of available tool names."""
        return [
            "track_outcomes_tool",
            "generate_roadmap_tool",
            "calculate_kpis_tool",
            "analyze_outcomes_tool",
            "generate_strategic_roadmap_tool",
            "generate_poc_proposal_tool",
            "generate_comprehensive_poc_tool",
            "create_comprehensive_strategic_plan_tool",
            "track_strategic_progress_tool",
            "analyze_strategic_trends_tool"
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
            "compatible_with": ["business_outcomes_orchestrator"],
            "timestamp": datetime.utcnow().isoformat()
        }



