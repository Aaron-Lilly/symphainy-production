#!/usr/bin/env python3
"""
Insights Liaison Agent - REFACTORED with DimensionLiaisonAgent

This demonstrates how to refactor the existing InsightsLiaisonAgent to use our new
hierarchical DimensionLiaisonAgent while maintaining all existing functionality
and adding enhanced capabilities.

REFACTORING APPROACH:
- Replace BusinessLiaisonAgentBase inheritance with DimensionLiaisonAgent inheritance
- Maintain all existing interfaces and methods
- Add enhanced hierarchical capabilities
- Preserve backward compatibility
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from utilities import UserContext

# Import NEW hierarchical agent
from agentic.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent

# Import foundation services for proper initialization
from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService


class InsightsLiaisonAgent(DimensionLiaisonAgent):
    """
    Insights Liaison Agent - REFACTORED with DimensionLiaisonAgent
    
    Liaison agent for the Insights Pillar that provides conversational interface
    and user guidance for insights analysis operations.
    
    ENHANCED CAPABILITIES:
    - Dimensional awareness (from DimensionLiaisonAgent)
    - State awareness (from DimensionLiaisonAgent)
    - Tool usage (from DimensionLiaisonAgent)
    - User interactivity (from DimensionLiaisonAgent)
    - Centralized LLM governance (from DimensionLiaisonAgent)
    - Cost containment and audit trail (from DimensionLiaisonAgent)
    
    MAINTAINED FUNCTIONALITY:
    - All existing interfaces and methods
    - Insights-specific capabilities
    - User conversation processing
    - Capability guidance
    """
    
    def __init__(self, utility_foundation=None, di_container=None):
        """Initialize Insights Liaison Agent with DimensionLiaisonAgent capabilities."""
        
        # Create default DI container if none provided
        if di_container is None:
            di_container = DIContainerService("insights_liaison_agent")
        
        # Get public works foundation for LLM abstraction
        public_works_foundation = di_container.get_public_works_foundation()
        
        # Get MCP client manager and other services
        mcp_client_manager = di_container.get_mcp_client_manager()
        policy_integration = di_container.get_policy_integration()
        tool_composition = di_container.get_tool_composition()
        agui_formatter = di_container.get_agui_formatter()
        
        # Define AGUI schema for the Insights Liaison Agent
        agui_schema = {
            "agent_name": "InsightsLiaisonAgent",
            "version": "1.0.0",
            "description": "Liaison agent for the Insights Pillar with enhanced capabilities",
            "components": [
                {
                    "type": "conversation_card",
                    "title": "Insights Analysis Chat",
                    "description": "Conversational interface for insights analysis",
                    "properties": {
                        "message": "Hello! I'm your Insights Analysis assistant. How can I help you today?",
                        "conversation_history": "array",
                        "analysis_type": "string",
                        "visualization_options": "array"
                    }
                },
                {
                    "type": "capability_card",
                    "title": "Insights Capabilities",
                    "description": "Available insights analysis capabilities",
                    "properties": {
                        "capabilities": "array",
                        "use_cases": "array",
                        "analysis_types": "array"
                    }
                }
            ]
        }
        
        # Initialize with DimensionLiaisonAgent (ENHANCED)
        super().__init__(
            agent_name="InsightsLiaisonAgent",
            capabilities=[
                "insights_analysis",
                "data_visualization",
                "pattern_detection",
                "user_guidance",
                "conversation_management"
            ],
            required_roles=[
                "insights_pillar",
                "data_steward",
                "librarian"
            ],
            agui_schema=agui_schema,
            foundation_services=di_container,
            public_works_foundation=public_works_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            dimension="insights"
        )
        
        # Store utility foundation for backward compatibility
        self.utility_foundation = utility_foundation
        
        # Insights-specific capabilities (ENHANCED)
        self.insights_capabilities = [
            "data_analysis",
            "visualization",
            "insights_generation",
            "apg_mode",
            "pattern_detection",
            "trend_analysis",
            "anomaly_detection"
        ]
        
        # User sessions for insights analysis
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        self.analysis_history: Dict[str, List[Dict[str, Any]]] = {}
        
        self.logger.info(f"🤖 {self.agent_name} initialized - Enhanced Insights Liaison Agent with DimensionLiaisonAgent capabilities")
    
    # ============================================================================
    # ENHANCED CAPABILITIES FROM DIMENSIONLIAISONAGENT
    # ============================================================================
    
    async def liaise_with_user_enhanced(self, user_request: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Enhanced user liaison using DimensionLiaisonAgent capabilities.
        
        This method leverages the hierarchical agent's dimensional awareness
        and user interactivity for superior insights analysis guidance.
        """
        try:
            # Use DimensionLiaisonAgent's enhanced user liaison
            result = await self.execute_liaison_operation(
                operation="liaise_with_user",
                user_request=user_request,
                **kwargs
            )
            
            # Add Insights-specific enhancements
            enhanced_result = await self._enhance_insights_liaison(result, user_request)
            
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced insights liaison failed: {e}")
            # Fallback to original method
            return await self._original_process_conversation(user_request)
    
    async def provide_user_guidance_enhanced(self, guidance_context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Enhanced user guidance using DimensionLiaisonAgent capabilities.
        
        This method leverages the hierarchical agent's dimensional awareness
        for superior insights analysis guidance.
        """
        try:
            # Use DimensionLiaisonAgent's enhanced user guidance
            result = await self.execute_liaison_operation(
                operation="provide_user_guidance",
                guidance_context=guidance_context,
                **kwargs
            )
            
            # Add Insights-specific enhancements
            enhanced_result = await self._enhance_insights_guidance(result, guidance_context)
            
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced insights guidance failed: {e}")
            # Fallback to original method
            return await self._original_provide_capability_guidance(guidance_context)
    
    # ============================================================================
    # MAINTAINED EXISTING FUNCTIONALITY
    # ============================================================================
    
    async def process_conversation(self, request) -> Any:
        """Process a conversation request for insights analysis (ENHANCED)."""
        try:
            # Use enhanced liaison capabilities
            user_request = {
                "message": getattr(request, 'message', 'Hello'),
                "context": "insights_analysis",
                "user_id": getattr(request, 'user_id', 'anonymous')
            }
            
            # Use enhanced liaison operation
            result = await self.liaise_with_user_enhanced(user_request)
            
            # Return response in expected format
            class MockResponse:
                def __init__(self, success, message, response_type="TEXT_RESPONSE"):
                    self.success = success
                    self.message = message
                    self.response_type = response_type
            
            return MockResponse(
                success=result.get("success", True),
                message=result.get("message", "Hello! I'm your Insights Analysis assistant. How can I help you today?")
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to process conversation: {e}")
            # Return error response
            class MockResponse:
                def __init__(self, success, message, response_type="TEXT_RESPONSE"):
                    self.success = success
                    self.message = message
                    self.response_type = response_type
            
            return MockResponse(False, f"Sorry, I encountered an error: {str(e)}")
    
    async def provide_capability_guidance(self, request) -> Any:
        """Provide capability guidance for insights analysis (ENHANCED)."""
        try:
            # Use enhanced guidance capabilities
            guidance_context = {
                "capability_type": "insights_analysis",
                "user_level": getattr(request, 'user_level', 'beginner'),
                "context": "capability_guidance"
            }
            
            # Use enhanced guidance operation
            result = await self.provide_user_guidance_enhanced(guidance_context)
            
            # Return enhanced capabilities
            enhanced_capabilities = [
                {
                    "name": "Enhanced Data Analysis",
                    "description": "Advanced data analysis with AI-powered insights and pattern detection",
                    "use_cases": ["Trend analysis", "Pattern recognition", "Predictive modeling", "APG mode"],
                    "enhanced_features": ["AI-powered insights", "Automated pattern detection", "Real-time analysis"]
                },
                {
                    "name": "Intelligent Visualization",
                    "description": "Create interactive charts and dashboards with AI recommendations",
                    "use_cases": ["Chart creation", "Dashboard building", "Report generation", "Interactive analysis"],
                    "enhanced_features": ["AI-recommended visualizations", "Interactive dashboards", "Real-time updates"]
                },
                {
                    "name": "Advanced Insights Generation",
                    "description": "Generate business insights with AI-powered recommendations",
                    "use_cases": ["Business intelligence", "Strategic planning", "Performance optimization", "Risk analysis"],
                    "enhanced_features": ["AI-powered recommendations", "Automated insights", "Predictive analytics"]
                },
                {
                    "name": "APG Mode Enhanced",
                    "description": "Autonomous Pattern Generation with enhanced AI capabilities",
                    "use_cases": ["Automatic pattern detection", "Anomaly identification", "Trend prediction", "Insight generation"],
                    "enhanced_features": ["Enhanced pattern detection", "Automated anomaly detection", "Predictive insights"]
                }
            ]
            
            return enhanced_capabilities
            
        except Exception as e:
            self.logger.error(f"❌ Failed to provide capability guidance: {e}")
            return []
    
    # ============================================================================
    # ENHANCED LLM OPERATIONS WITH GOVERNANCE
    # ============================================================================
    
    async def _enhanced_insights_analysis(self, analysis_request: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Enhanced insights analysis with centralized governance.
        
        This method uses the DimensionLiaisonAgent's centralized governance
        for cost containment, audit trail, and rate limiting.
        """
        try:
            # Use DimensionLiaisonAgent's centralized LLM governance
            result = await self.execute_llm_operation("analyze", **analysis_request)
            
            # Add Insights-specific processing
            enhanced_result = await self._process_insights_analysis_result(result, analysis_request)
            
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced insights analysis failed: {e}")
            raise
    
    # ============================================================================
    # BACKWARD COMPATIBILITY METHODS
    # ============================================================================
    
    async def _original_process_conversation(self, request) -> Any:
        """Original conversation processing method for fallback."""
        # Original implementation
        user_message = getattr(request, 'message', 'Hello')
        
        if "analyze" in user_message.lower():
            response = "I can help you analyze your data! What type of analysis would you like to perform? I support descriptive, predictive, prescriptive, and diagnostic analysis."
        elif "visualize" in user_message.lower():
            response = "I can create various visualizations for your data! What type of chart would you like? I support line charts, bar charts, pie charts, scatter plots, and more."
        elif "insights" in user_message.lower():
            response = "I can generate business insights from your analysis results! I'll identify patterns, trends, and provide actionable recommendations."
        elif "apg" in user_message.lower():
            response = "APG (Autonomous Pattern Generation) mode can automatically detect patterns and generate insights from your data. Would you like me to process your data using APG mode?"
        else:
            response = "Hello! I'm your Insights Analysis assistant. I can help you with data analysis, visualization, insights generation, and APG mode processing. What would you like to do?"
        
        class MockResponse:
            def __init__(self, success, message, response_type="TEXT_RESPONSE"):
                self.success = success
                self.message = message
                self.response_type = response_type
        
        return MockResponse(True, response)
    
    async def _original_provide_capability_guidance(self, request) -> Any:
        """Original capability guidance method for fallback."""
        # Original implementation
        capabilities = [
            {
                "name": "Data Analysis",
                "description": "Analyze data using various statistical and machine learning techniques",
                "use_cases": ["Trend analysis", "Pattern recognition", "Predictive modeling"]
            },
            {
                "name": "Visualization",
                "description": "Create interactive charts and dashboards for data visualization",
                "use_cases": ["Chart creation", "Dashboard building", "Report generation"]
            },
            {
                "name": "Insights Generation",
                "description": "Generate business insights and actionable recommendations",
                "use_cases": ["Business intelligence", "Strategic planning", "Performance optimization"]
            },
            {
                "name": "APG Mode",
                "description": "Autonomous Pattern Generation for automatic pattern detection",
                "use_cases": ["Pattern detection", "Anomaly identification", "Insight generation"]
            }
        ]
        
        return capabilities
    
    # ============================================================================
    # ENHANCEMENT METHODS
    # ============================================================================
    
    async def _enhance_insights_liaison(self, result: Dict[str, Any], user_request: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance insights liaison with Insights-specific processing."""
        # Add Insights-specific enhancements
        enhanced_result = result.copy()
        enhanced_result["insights_context"] = "enhanced_with_ai"
        enhanced_result["dimensional_awareness"] = True
        enhanced_result["state_management"] = True
        return enhanced_result
    
    async def _enhance_insights_guidance(self, result: Dict[str, Any], guidance_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance insights guidance with Insights-specific processing."""
        # Add Insights-specific enhancements
        enhanced_result = result.copy()
        enhanced_result["insights_guidance"] = "enhanced_with_ai"
        enhanced_result["dimensional_awareness"] = True
        enhanced_result["user_interactivity"] = True
        return enhanced_result
    
    async def _process_insights_analysis_result(self, result: Dict[str, Any], analysis_request: Dict[str, Any]) -> Dict[str, Any]:
        """Process insights analysis result with Insights-specific logic."""
        # Add Insights-specific processing
        enhanced_result = result.copy()
        enhanced_result["insights_analysis"] = "enhanced_with_ai"
        enhanced_result["dimensional_awareness"] = True
        enhanced_result["tool_usage"] = True
        return enhanced_result
    
    # ============================================================================
    # ENHANCED CAPABILITIES SUMMARY
    # ============================================================================
    
    def get_enhanced_capabilities(self) -> Dict[str, Any]:
        """Get enhanced capabilities from DimensionLiaisonAgent."""
        return {
            "hierarchical_agent_type": "DimensionLiaisonAgent",
            "dimension": self.dimension,
            "dimensional_awareness": self.dimensional_awareness,
            "state_awareness": self.state_awareness,
            "tool_usage": self.tool_usage,
            "user_interactivity": self.user_interactivity,
            "centralized_governance": self.centralized_governance,
            "cost_containment": self.governance_config.get('cost_tracking', False),
            "audit_trail": self.governance_config.get('audit_logging', False),
            "rate_limiting": self.governance_config.get('rate_limiting', False),
            "enhanced_llm_operations": list(self.llm_operations.keys()),
            "liaison_operations": list(self.liaison_operations.keys()),
            "insights_capabilities": self.insights_capabilities,
            "usage_stats": self.get_usage_stats(),
            "liaison_stats": self.get_liaison_stats()
        }
