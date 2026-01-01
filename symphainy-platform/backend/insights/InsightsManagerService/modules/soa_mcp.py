#!/usr/bin/env python3
"""
Insights Manager Service - SOA/MCP Module

Micro-module for SOA API exposure and MCP tool integration.
"""

import logging
from typing import Any, Dict
from datetime import datetime


class SoaMcp:
    """SOA/MCP module for Insights Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def initialize_soa_api_exposure(self):
        """Initialize SOA API exposure for Insights Manager capabilities."""
        self.service.soa_apis = {
            "analyze_content_for_insights": {
                "endpoint": "/api/insights-manager/analyze",
                "method": "POST",
                "description": "Analyze content for insights using Insights Orchestrator",
                "parameters": ["content_request"]
            },
            "generate_insights": {
                "endpoint": "/api/insights-manager/generate",
                "method": "POST",
                "description": "Generate insights using Insights Orchestrator",
                "parameters": ["insights_request"]
            },
            "get_insights_orchestrator": {
                "endpoint": "/api/insights-manager/orchestrator",
                "method": "GET",
                "description": "Get Insights Orchestrator status",
                "parameters": []
            }
        }
        
        if hasattr(self.service, 'logger') and self.service.logger:
            self.service.logger.info(f"✅ SOA APIs initialized: {list(self.service.soa_apis.keys())}")
    
    async def initialize_mcp_tool_integration(self):
        """Initialize MCP tool integration for Insights Manager."""
        self.service.mcp_tools = {
            "analyze_content_for_insights_tool": {
                "name": "analyze_content_for_insights",
                "description": "Analyze content for insights using Insights Orchestrator",
                "parameters": ["content_request"]
            },
            "generate_insights_tool": {
                "name": "generate_insights",
                "description": "Generate insights using Insights Orchestrator",
                "parameters": ["insights_request"]
            }
        }
        
        if hasattr(self.service, 'logger') and self.service.logger:
            self.service.logger.info(f"✅ MCP tools initialized: {list(self.service.mcp_tools.keys())}")
    
    async def register_insights_manager_capabilities(self):
        """Register Insights Manager capabilities with Curator (Phase 2 pattern)."""
        try:
            curator = self.service.get_curator()
            if not curator:
                if hasattr(self.service, 'logger') and self.service.logger:
                    self.service.logger.warning("⚠️ Curator not available - cannot register capabilities")
                return
            
            # Register with Curator using Phase 2 pattern
            await self.service.register_with_curator(
                capabilities=["data_analysis", "insights_generation", "visualization", "business_analysis"],
                soa_apis=list(self.service.soa_apis.keys()),
                mcp_tools=list(self.service.mcp_tools.keys()),
                metadata={
                    "manager_type": str(self.service.manager_type),
                    "orchestration_scope": str(self.service.orchestration_scope),
                    "governance_level": str(self.service.governance_level)
                }
            )
            
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("✅ Insights Manager capabilities registered with Curator")
            
        except Exception as e:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.error(f"❌ Failed to register capabilities: {str(e)}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")

