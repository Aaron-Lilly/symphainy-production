#!/usr/bin/env python3
"""
Realm Access Controller

Provides realm-specific access to infrastructure abstractions.
Handles business logic that belongs in the realm rather than infrastructure.

WHAT (Realm Role): I provide realm-specific business logic for infrastructure abstractions
HOW (Realm Implementation): I orchestrate infrastructure abstractions with realm context
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .composition_services.llm_composition_service import LLMCompositionService
from .infrastructure_abstractions.llm_abstraction import LLMAbstraction


class RealmAccessController:
    """Realm access controller for infrastructure abstractions."""
    
    def __init__(self, di_container):
        """
        Initialize realm access controller.
        
        Args:
            di_container: DI container for service resolution
        """
        self.di_container = di_container
        self.logger = logging.getLogger("RealmAccessController")
        
        # Service instances
        self.llm_composition_service = None
        self.llm_abstraction = None
        
        # Initialize services
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize infrastructure services."""
        try:
            # Get LLM abstraction from DI container
            self.llm_abstraction = self.di_container.get_service("llm_abstraction")
            
            # Create composition service
            self.llm_composition_service = LLMCompositionService(self.llm_abstraction)
            
            self.logger.info("✅ Realm access controller initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize realm access controller: {e}")
            raise
    
    # ============================================================================
    # AGENTIC REALM LLM CAPABILITIES
    # ============================================================================
    
    async def interpret_analysis_results(self, results: Dict[str, Any], 
                                       context: str, expertise: str = None) -> Dict[str, Any]:
        """
        Interpret analysis results for agentic realm.
        
        Args:
            results: Analysis results from MCP tools
            context: Context for interpretation
            expertise: Optional expertise domain
            
        Returns:
            Dict: Interpreted insights
        """
        try:
            return await self.llm_composition_service.interpret_results(
                results=results,
                context=context,
                expertise=expertise,
                format="agui"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to interpret analysis results: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def guide_agent_user(self, user_input: str, available_tools: List[str], 
                              context: str, expertise: str = None) -> Dict[str, Any]:
        """
        Guide agent user through available tools.
        
        Args:
            user_input: User's input/question
            available_tools: List of available MCP tools
            context: Context for guidance
            expertise: Optional expertise domain
            
        Returns:
            Dict: Guidance and recommendations
        """
        try:
            return await self.llm_composition_service.guide_user(
                user_input=user_input,
                available_tools=available_tools,
                context=context,
                expertise=expertise
            )
            
        except Exception as e:
            self.logger.error(f"Failed to guide agent user: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_agent_insights(self, prompt: str, agent_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate insights for agentic realm.
        
        Args:
            prompt: Insight generation prompt
            agent_context: Agent context
            
        Returns:
            Dict: Generated insights
        """
        try:
            return await self.llm_composition_service.generate_agent_response(
                prompt=prompt,
                context=agent_context
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate agent insights: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def analyze_agent_performance(self, agent_description: str, 
                                      capabilities: List[str]) -> Dict[str, Any]:
        """
        Analyze agent performance for realm.
        
        Args:
            agent_description: Agent description
            capabilities: List of capabilities
            
        Returns:
            Dict: Performance analysis
        """
        try:
            return await self.llm_composition_service.analyze_agent_capabilities(
                agent_description=agent_description,
                capabilities=capabilities
            )
            
        except Exception as e:
            self.logger.error(f"Failed to analyze agent performance: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # ============================================================================
    # REALM HEALTH AND STATUS
    # ============================================================================
    
    async def get_realm_status(self) -> Dict[str, Any]:
        """
        Get realm status.
        
        Returns:
            Dict: Realm status
        """
        try:
            return {
                "realm": "agentic",
                "services": {
                    "llm_composition_service": await self.llm_composition_service.get_service_status(),
                    "llm_abstraction": await self.llm_abstraction.health_check()
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get realm status: {e}")
            return {
                "realm": "agentic",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform realm health check.
        
        Returns:
            Dict: Health check result
        """
        try:
            return await self.llm_composition_service.health_check()
            
        except Exception as e:
            self.logger.error(f"Realm health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }