#!/usr/bin/env python3
"""
Business Abstraction Helper for Agent SDK

Provides convenient access to business abstractions for agents.
Simplifies common business abstraction operations and provides type-safe access.

WHAT (Helper): I provide convenient access to business abstractions for agents
HOW (Helper): I wrap Public Works Foundation abstractions with agent-friendly methods
"""

import asyncio
from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    import logging


class BusinessAbstractionHelper:
    """
    Helper class for agents to easily access and use business abstractions.
    
    Provides:
    - Type-safe access to business abstractions
    - Convenient wrapper methods for common operations
    - Error handling and fallback mechanisms
    - Usage tracking and monitoring
    """
    
    def __init__(self, agent_name: str, public_works_foundation, logger: 'logging.Logger'):
        """
        Initialize the business abstraction helper.
        
        Args:
            agent_name: Name of the agent using this helper
            public_works_foundation: Public Works Foundation Service instance
            logger: Logger instance for the agent
        """
        self.agent_name = agent_name
        self.public_works_foundation = public_works_foundation
        self.logger = logger
        self.usage_tracking = []
        
        # Cache for frequently used abstractions
        self._abstraction_cache = {}
        
        self.logger.info(f"Business Abstraction Helper initialized for agent: {agent_name}")
    
    async def get_abstraction(self, abstraction_name: str) -> Optional[Any]:
        """
        Get a specific business abstraction.
        
        Args:
            abstraction_name: Name of the abstraction to retrieve
            
        Returns:
            Business abstraction instance or None if not found
        """
        try:
            # Check cache first
            if abstraction_name in self._abstraction_cache:
                return self._abstraction_cache[abstraction_name]
            
            # Get from public works foundation
            if self.public_works_foundation:
                abstractions = self.public_works_foundation.get_agentic_abstractions()
                abstraction = abstractions.get(abstraction_name)
                
                if abstraction:
                    # Cache for future use
                    self._abstraction_cache[abstraction_name] = abstraction
                    self._track_usage(abstraction_name, "get_abstraction", True)
                    return abstraction
            
            self._track_usage(abstraction_name, "get_abstraction", False)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get abstraction '{abstraction_name}': {e}")
            self._track_usage(abstraction_name, "get_abstraction", False, str(e))
            return None
    
    async def list_available_abstractions(self) -> Dict[str, str]:
        """
        List all available business abstractions with descriptions.
        
        Returns:
            Dict mapping abstraction names to descriptions
        """
        try:
            if not self.public_works_foundation:
                return {}
            
            abstractions = self.public_works_foundation.get_agentic_abstractions()
            
            # Create descriptions for each abstraction
            descriptions = {
                # Core Agentic Abstractions
                "mcp_client": "MCP client functionality for agent communication",
                "mcp_protocol": "MCP protocol handling and management",
                "tool_registry": "Tool registration and discovery",
                "agui": "Agent-to-Agent User Interface communication",
                "llm": "Large Language Model integration and management",
                "event_routing": "Event routing and messaging",
                "session_management": "Session and state management",
                "security": "Security and authentication services",
                
                # MVP Business Abstractions
                "cobol_processing": "COBOL and mainframe data processing",
                "sop_processing": "Standard Operating Procedure creation and management",
                "poc_generation": "Proof of Concept proposal generation",
                "roadmap_generation": "Strategic roadmap creation and planning",
                "coexistence_evaluation": "Human-AI coexistence evaluation and optimization",
                
                # Foundational Capabilities
                "multi_tenancy": "Multi-tenant resource management",
                "authentication": "User authentication services",
                "authorization": "Access control and permissions"
            }
            
            available = {}
            for name in abstractions.keys():
                available[name] = descriptions.get(name, "Business abstraction")
            
            self._track_usage("all", "list_abstractions", True)
            return available
            
        except Exception as e:
            self.logger.error(f"Failed to list abstractions: {e}")
            self._track_usage("all", "list_abstractions", False, str(e))
            return {}
    
    # Convenience methods for MVP abstractions
    async def process_cobol_data(self, copybook_content: str, **kwargs) -> Dict[str, Any]:
        """Convenience method for COBOL data processing."""
        abstraction = await self.get_abstraction("cobol_processing")
        if abstraction:
            return await abstraction.parse_copybook(copybook_content, **kwargs)
        return {"success": False, "error": "COBOL processing abstraction not available"}
    
    async def create_sop(self, sop_content: str, **kwargs) -> Dict[str, Any]:
        """Convenience method for SOP creation."""
        abstraction = await self.get_abstraction("sop_processing")
        if abstraction:
            return await abstraction.parse_sop_from_text(sop_content, **kwargs)
        return {"success": False, "error": "SOP processing abstraction not available"}
    
    async def generate_poc_proposal(self, business_context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Convenience method for POC proposal generation."""
        abstraction = await self.get_abstraction("poc_generation")
        if abstraction:
            return await abstraction.create_poc_proposal(business_context, **kwargs)
        return {"success": False, "error": "POC generation abstraction not available"}
    
    async def create_roadmap(self, project_context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Convenience method for roadmap creation."""
        abstraction = await self.get_abstraction("roadmap_generation")
        if abstraction:
            return await abstraction.create_strategic_roadmap(project_context, **kwargs)
        return {"success": False, "error": "Roadmap generation abstraction not available"}
    
    async def evaluate_coexistence(self, process_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Convenience method for coexistence evaluation."""
        abstraction = await self.get_abstraction("coexistence_evaluation")
        if abstraction:
            return await abstraction.evaluate_process_coexistence(process_data, **kwargs)
        return {"success": False, "error": "Coexistence evaluation abstraction not available"}
    
    # LLM-specific convenience methods
    async def interpret_analysis_results(self, results: Dict[str, Any], context: str, 
                                       expertise: str = None) -> Dict[str, Any]:
        """Convenience method for LLM interpretation of analysis results."""
        llm_composition = await self.get_abstraction("llm_composition_service")
        if llm_composition:
            return await llm_composition.interpret_results(
                results=results,
                context=context,
                expertise=expertise,
                format="agui"
            )
        return {"success": False, "error": "LLM composition service not available"}
    
    async def guide_user_with_llm(self, user_input: str, available_tools: List[str], 
                                 context: str, expertise: str = None) -> Dict[str, Any]:
        """Convenience method for LLM user guidance."""
        llm_composition = await self.get_abstraction("llm_composition_service")
        if llm_composition:
            return await llm_composition.guide_user(
                user_input=user_input,
                available_tools=available_tools,
                context=context,
                expertise=expertise
            )
        return {"success": False, "error": "LLM composition service not available"}
    
    async def generate_agent_response(self, prompt: str, agent_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Convenience method for LLM agent response generation."""
        llm_composition = await self.get_abstraction("llm_composition_service")
        if llm_composition:
            return await llm_composition.generate_agent_response(
                prompt=prompt,
                context=agent_context
            )
        return {"success": False, "error": "LLM composition service not available"}
    
    # Utility methods
    async def health_check_abstractions(self) -> Dict[str, Any]:
        """Check health of all available abstractions."""
        try:
            abstractions = self.public_works_foundation.get_agentic_abstractions()
            health_status = {}
            
            for name, abstraction in abstractions.items():
                try:
                    if hasattr(abstraction, 'health_check'):
                        health_result = await abstraction.health_check()
                        health_status[name] = health_result.get("status", "unknown")
                    else:
                        health_status[name] = "no_health_check"
                except Exception as e:
                    health_status[name] = f"error: {str(e)}"
            
            return {
                "agent": self.agent_name,
                "abstraction_health": health_status,
                "total_abstractions": len(abstractions),
                "healthy_count": len([s for s in health_status.values() if s == "healthy"]),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check abstraction health: {e}")
            return {"error": str(e)}
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for business abstractions."""
        if not self.usage_tracking:
            return {"message": "No usage data available"}
        
        # Calculate statistics
        total_usage = len(self.usage_tracking)
        successful_usage = len([u for u in self.usage_tracking if u["success"]])
        failed_usage = total_usage - successful_usage
        
        # Most used abstractions
        abstraction_usage = {}
        for usage in self.usage_tracking:
            name = usage["abstraction_name"]
            abstraction_usage[name] = abstraction_usage.get(name, 0) + 1
        
        most_used = sorted(abstraction_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_usage": total_usage,
            "successful_usage": successful_usage,
            "failed_usage": failed_usage,
            "success_rate": (successful_usage / total_usage * 100) if total_usage > 0 else 0,
            "most_used_abstractions": most_used,
            "agent": self.agent_name,
            "timestamp": datetime.now().isoformat()
        }
    
    def _track_usage(self, abstraction_name: str, operation: str, success: bool, error: str = None):
        """Track abstraction usage for monitoring."""
        self.usage_tracking.append({
            "timestamp": datetime.now().isoformat(),
            "abstraction_name": abstraction_name,
            "operation": operation,
            "success": success,
            "error": error,
            "agent": self.agent_name
        })
        
        # Keep only last 1000 usage records
        if len(self.usage_tracking) > 1000:
            self.usage_tracking = self.usage_tracking[-1000:]
    
    async def clear_cache(self):
        """Clear the abstraction cache."""
        self._abstraction_cache.clear()
        self.logger.info("Business abstraction cache cleared")
    
    async def preload_abstractions(self, abstraction_names: List[str]):
        """Preload specific abstractions into cache."""
        for name in abstraction_names:
            await self.get_abstraction(name)
        self.logger.info(f"Preloaded {len(abstraction_names)} abstractions into cache")
