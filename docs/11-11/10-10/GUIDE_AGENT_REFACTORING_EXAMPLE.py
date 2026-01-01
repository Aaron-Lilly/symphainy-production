#!/usr/bin/env python3
"""
Guide Agent Refactoring Example - Using GlobalGuideAgent

This demonstrates how to refactor the existing GuideAgentMVP to use our new
hierarchical GlobalGuideAgent while maintaining all existing functionality
and adding enhanced capabilities.

REFACTORING APPROACH:
- Replace AgentBase inheritance with GlobalGuideAgent inheritance
- Maintain all existing interfaces and methods
- Add enhanced hierarchical capabilities
- Preserve backward compatibility
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional, Type
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../'))

from utilities import UserContext
from config.environment_loader import EnvironmentLoader

# Import NEW hierarchical agent
from agentic.agent_sdk.global_guide_agent import GlobalGuideAgent
from agentic.agui_schema_registry import AGUISchema, AGUIComponent

# Import guide agent interface (UNCHANGED)
from ...interfaces.guide_agent_interface import (
    IGuideAgent, GuidanceType, AssistanceLevel, GuidanceContext, IntentType,
    ProvideGuidanceRequest, ProvideGuidanceResponse,
    AssistUserRequest, AssistUserResponse,
    TroubleshootIssueRequest, TroubleshootIssueResponse,
    ExplainFeatureRequest, ExplainFeatureResponse,
    OptimizeWorkflowRequest, OptimizeWorkflowResponse
)

# Import micro-modules (UNCHANGED)
from .micro_modules.intent_analyzer import IntentAnalyzerModule
from .micro_modules.conversation_manager import ConversationManagerModule
from .micro_modules.user_profiler import UserProfilerModule
from .micro_modules.guidance_engine import GuidanceEngineModule
from .micro_modules.pillar_router import PillarRouterModule

# Import MCP server (UNCHANGED)
from .mcp_server.guide_agent_mcp_server import GuideAgentMCPServer


class GuideAgentMVP(GlobalGuideAgent, IGuideAgent):
    """
    Guide Agent Service - REFACTORED with GlobalGuideAgent
    
    Intelligent user guidance and concierge service that works across multiple dimensions.
    Now enhanced with hierarchical agent capabilities while maintaining all existing functionality.
    
    ENHANCED CAPABILITIES:
    - Cross-dimensional awareness (from GlobalGuideAgent)
    - Global user guidance (from GlobalGuideAgent)
    - Enhanced user interactivity (from GlobalGuideAgent)
    - Centralized LLM governance (from GlobalGuideAgent)
    - Cost containment and audit trail (from GlobalGuideAgent)
    
    MAINTAINED FUNCTIONALITY:
    - All existing interfaces and methods
    - Micro-modules integration
    - MCP server integration
    - Pillar liaison coordination
    - User profiling and conversation management
    """
    
    def __init__(self, di_container=None, curator_foundation=None, metadata_foundation=None, logger: Optional[logging.Logger] = None):
        """Initialize Guide Agent Service with GlobalGuideAgent capabilities."""
        
        # Create default DI container if none provided
        if di_container is None:
            from foundations.di_container.di_container_service import DIContainerService
            di_container = DIContainerService("guide_agent")
        
        # Get public works foundation for LLM abstraction
        public_works_foundation = di_container.get_public_works_foundation()
        
        # Get MCP client manager and other services
        mcp_client_manager = di_container.get_mcp_client_manager()
        policy_integration = di_container.get_policy_integration()
        tool_composition = di_container.get_tool_composition()
        agui_formatter = di_container.get_agui_formatter()
        
        # Define AGUI schema for the Guide Agent (UNCHANGED)
        agui_schema = AGUISchema(
            agent_name="GuideAgent",
            version="1.0.0",
            description="Intelligent user guidance and concierge service that works across multiple dimensions",
            components=[
                AGUIComponent(
                    type="message_card",
                    title="Guide Agent Chat",
                    description="Intelligent user guidance and concierge service",
                    properties={
                        "message": "Welcome to the Guide Agent! I'm here to help you navigate the platform.",
                        "conversation_history": "array",
                        "user_intent": "string",
                        "guidance_type": "string",
                        "pillar_routing": "object"
                    }
                ),
                AGUIComponent(
                    type="info_card",
                    title="User Guidance",
                    description="Contextual guidance and recommendations",
                    properties={
                        "content": "I provide intelligent guidance across all business pillars and dimensions.",
                        "guidance_type": "string",
                        "recommendations": "array",
                        "next_steps": "array"
                    }
                )
            ]
        )
        
        # Initialize with GlobalGuideAgent (ENHANCED)
        super().__init__(
            agent_name="GuideAgent",
            capabilities=[
                "user_guidance",
                "intent_analysis", 
                "pillar_routing",
                "conversation_management",
                "cross_dimensional_coordination"
            ],
            required_roles=[
                "business_orchestrator",
                "delivery_manager",
                "content_pillar",
                "insights_pillar", 
                "operations_pillar",
                "business_outcomes_pillar"
            ],
            agui_schema=agui_schema,
            foundation_services=di_container,
            public_works_foundation=public_works_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter
        )
        
        # Store additional services for micro-modules
        self.curator_foundation = curator_foundation
        self.metadata_foundation = metadata_foundation
        self.environment = EnvironmentLoader()
        
        # Initialize micro-modules (UNCHANGED)
        self.intent_analyzer = IntentAnalyzerModule(self.logger, self.environment)
        self.conversation_manager = ConversationManagerModule(self.logger, self.environment)
        self.user_profiler = UserProfilerModule(self.logger, self.environment)
        self.guidance_engine = GuidanceEngineModule(self.logger, self.environment)
        self.pillar_router = PillarRouterModule(self.logger, self.environment)
        
        # Initialize MCP server (UNCHANGED)
        self.mcp_server = GuideAgentMCPServer()
        
        # Guide Agent specific capabilities (UNCHANGED)
        self.guide_capabilities = [
            "user_guidance",
            "intent_analysis",
            "conversation_management",
            "pillar_routing",
            "cross_pillar_coordination",
            "user_profiling",
            "recommendation_engine"
        ]
        
        # Pillar liaison agents registry (UNCHANGED)
        self.pillar_liaison_agents: Dict[str, Any] = {}
        
        # User profiles and conversation history (UNCHANGED)
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.conversation_histories: Dict[str, List[Dict[str, Any]]] = {}
        
        self.logger.info(f"🎭 {self.agent_name} initialized - Enhanced Cross-Dimensional Guide Agent with GlobalGuideAgent capabilities")
    
    # ============================================================================
    # ENHANCED CAPABILITIES FROM GLOBALGUIDEAGENT
    # ============================================================================
    
    async def guide_user_journey_enhanced(self, user_journey: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Enhanced user journey guidance using GlobalGuideAgent capabilities.
        
        This method leverages the hierarchical agent's cross-dimensional awareness
        and global context for superior user journey guidance.
        """
        try:
            # Use GlobalGuideAgent's enhanced journey guidance
            result = await self.execute_guide_operation(
                operation="guide_user_journey",
                user_journey=user_journey,
                **kwargs
            )
            
            # Add Guide Agent specific enhancements
            enhanced_result = await self._enhance_journey_guidance(result, user_journey)
            
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced journey guidance failed: {e}")
            # Fallback to original method
            return await self._original_guide_user_journey(user_journey, **kwargs)
    
    async def provide_global_guidance_enhanced(self, guidance_request: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Enhanced global guidance using GlobalGuideAgent capabilities.
        
        This method leverages the hierarchical agent's cross-dimensional awareness
        for superior global guidance across all platform dimensions.
        """
        try:
            # Use GlobalGuideAgent's enhanced global guidance
            result = await self.execute_guide_operation(
                operation="provide_global_guidance",
                guidance_request=guidance_request,
                **kwargs
            )
            
            # Add Guide Agent specific enhancements
            enhanced_result = await self._enhance_global_guidance(result, guidance_request)
            
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced global guidance failed: {e}")
            # Fallback to original method
            return await self._original_provide_global_guidance(guidance_request, **kwargs)
    
    # ============================================================================
    # MAINTAINED EXISTING FUNCTIONALITY
    # ============================================================================
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the Guide Agent Service (UNCHANGED)."""
        try:
            self.logger.info(f"🚀 Initializing {self.agent_name}...")
            
            # Initialize base class (now GlobalGuideAgent)
            base_result = await super().initialize()
            if not base_result.get("success"):
                return base_result
            
            # Initialize micro-modules (UNCHANGED)
            await self.intent_analyzer.initialize()
            await self.conversation_manager.initialize()
            await self.user_profiler.initialize()
            await self.guidance_engine.initialize()
            await self.pillar_router.initialize()
            
            # Initialize MCP server (UNCHANGED)
            await self.mcp_server.initialize()
            
            # Initialize pillar liaison agents (UNCHANGED)
            await self._initialize_pillar_liaison_agents()
            
            self.logger.info(f"✅ {self.agent_name} initialized successfully with enhanced capabilities")
            
            return {"success": True, "message": f"{self.agent_name} initialized successfully with enhanced capabilities"}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.agent_name}: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # ENHANCED LLM OPERATIONS WITH GOVERNANCE
    # ============================================================================
    
    async def _enhanced_llm_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Enhanced LLM operation with centralized governance.
        
        This method uses the GlobalGuideAgent's centralized governance
        for cost containment, audit trail, and rate limiting.
        """
        try:
            # Use GlobalGuideAgent's centralized LLM governance
            result = await self.execute_llm_operation(operation, **kwargs)
            
            # Add Guide Agent specific processing
            enhanced_result = await self._process_guide_specific_llm_result(result, operation)
            
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced LLM operation failed: {e}")
            raise
    
    # ============================================================================
    # BACKWARD COMPATIBILITY METHODS
    # ============================================================================
    
    async def _original_guide_user_journey(self, user_journey: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Original journey guidance method for fallback."""
        # Implementation of original method
        pass
    
    async def _original_provide_global_guidance(self, guidance_request: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Original global guidance method for fallback."""
        # Implementation of original method
        pass
    
    async def _enhance_journey_guidance(self, result: Dict[str, Any], user_journey: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance journey guidance with Guide Agent specific processing."""
        # Add Guide Agent specific enhancements
        return result
    
    async def _enhance_global_guidance(self, result: Dict[str, Any], guidance_request: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance global guidance with Guide Agent specific processing."""
        # Add Guide Agent specific enhancements
        return result
    
    async def _process_guide_specific_llm_result(self, result: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Process LLM result with Guide Agent specific logic."""
        # Add Guide Agent specific processing
        return result
    
    # ============================================================================
    # EXISTING METHODS (UNCHANGED - MAINTAINED FOR BACKWARD COMPATIBILITY)
    # ============================================================================
    
    # All existing methods from the original GuideAgentMVP are maintained
    # to ensure backward compatibility while adding enhanced capabilities
    
    async def provide_guidance(self, request: ProvideGuidanceRequest, user_context: UserContext) -> ProvideGuidanceResponse:
        """Provide guidance (ENHANCED with GlobalGuideAgent capabilities)."""
        # Original implementation enhanced with hierarchical capabilities
        pass
    
    async def assist_user(self, request: AssistUserRequest, user_context: UserContext) -> AssistUserResponse:
        """Assist user (ENHANCED with GlobalGuideAgent capabilities)."""
        # Original implementation enhanced with hierarchical capabilities
        pass
    
    # ... (all other existing methods maintained with enhanced capabilities)
    
    # ============================================================================
    # ENHANCED CAPABILITIES SUMMARY
    # ============================================================================
    
    def get_enhanced_capabilities(self) -> Dict[str, Any]:
        """Get enhanced capabilities from GlobalGuideAgent."""
        return {
            "hierarchical_agent_type": "GlobalGuideAgent",
            "cross_dimensional_awareness": self.cross_dimensional_awareness,
            "global_context": self.global_context,
            "user_interactivity": self.user_interactivity,
            "centralized_governance": self.centralized_governance,
            "cost_containment": self.governance_config.get('cost_tracking', False),
            "audit_trail": self.governance_config.get('audit_logging', False),
            "rate_limiting": self.governance_config.get('rate_limiting', False),
            "enhanced_llm_operations": list(self.llm_operations.keys()),
            "guide_operations": list(self.guide_operations.keys()),
            "usage_stats": self.get_usage_stats(),
            "guide_stats": self.get_guide_stats()
        }
