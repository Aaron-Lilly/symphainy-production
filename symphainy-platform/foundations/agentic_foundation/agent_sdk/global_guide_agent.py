"""
Global Guide Agent - Global Level Agent

Builds on orchestrator capabilities + user interactivity capabilities.
Guides users across all dimensions with full platform context.

Characteristics:
- Cross-dimensional awareness - can access all platform dimensions
- Full platform context - understands business outcomes, user journeys, platform capabilities
- Strategic coordination - orchestrates complex multi-dimensional workflows
- User interactivity - can interact with users across dimensions
- Global guidance - guides users across all dimensions
"""

import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from foundations.di_container.di_container_service import DIContainerService
from .global_orchestrator_agent import GlobalOrchestratorAgent
from .mcp_client_manager import MCPClientManager
from .policy_integration import PolicyIntegration
from .tool_composition import ToolComposition
from utilities import UserContext


class GlobalGuideAgent(GlobalOrchestratorAgent):
    """
    Global Guide Agent - Global level, guide capabilities + user interactivity
    
    Builds on orchestrator capabilities + user interactivity capabilities.
    Guides users across all dimensions with full platform context.
    """
    
    def __init__(self, agent_name: str, capabilities: List[str], 
                 required_roles: List[str], agui_schema: Dict[str, Any],
                 foundation_services: DIContainerService,
                 agentic_foundation: 'AgenticFoundationService',
                 mcp_client_manager: MCPClientManager,
                 policy_integration: PolicyIntegration,
                 tool_composition: ToolComposition,
                 agui_formatter: Any,
                 **kwargs):
        """
        Initialize Global Guide Agent.
        
        Args:
            agent_name: Name of the agent
            capabilities: List of agent capabilities
            required_roles: List of required roles
            agui_schema: AGUI schema for structured output
            foundation_services: DI container service
            agentic_foundation: Agentic foundation service for agentic capabilities
            mcp_client_manager: MCP client manager
            policy_integration: Policy integration service
            tool_composition: Tool composition service
            agui_formatter: AGUI output formatter
            **kwargs: Additional arguments
        """
        super().__init__(
            agent_name=agent_name,
            capabilities=capabilities,
            required_roles=required_roles,
            agui_schema=agui_schema,
            foundation_services=foundation_services,
            agentic_foundation=agentic_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            **kwargs
        )
        
        # Global agents have cross-dimensional awareness + user interactivity
        self.cross_dimensional_awareness = True
        self.global_context = True
        self.orchestrator_capabilities = True
        self.user_interactivity = True
        self.user_facing = True
        
        # Global guidance capabilities
        self.guide_operations = {
            'guide_user_journey': self._guide_user_journey,
            'provide_global_guidance': self._provide_global_guidance,
            'coordinate_user_across_dimensions': self._coordinate_user_across_dimensions,
            'optimize_user_experience': self._optimize_user_experience
        }
        
        # Initialize global guidance state
        self._initialize_guide_state()
        
        self.logger.info(f"🧭 GlobalGuideAgent '{agent_name}' initialized with global guidance capabilities")
    
    def _initialize_guide_state(self):
        """Initialize global guidance state."""
        self.guide_state = {
            'dimension': "global",
            'active_users': [],
            'user_journeys': {},
            'global_guidance_metrics': {},
            'user_satisfaction_score': 100.0
        }
        
        self.guide_stats = {
            'user_journeys_guided': 0,
            'global_guidance_sessions': 0,
            'cross_dimensional_coordinations': 0,
            'user_experience_optimizations': 0,
            'user_satisfaction_events': 0,
            'average_guidance_time': 0.0
        }
    
    def _guide_user_journey(self, user_journey: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Guide user journey across dimensions.
        
        Args:
            user_journey: User journey to guide
            **kwargs: Additional parameters
            
        Returns:
            Journey guidance results
        """
        self._log_operation('guide_user_journey', {'journey_id': user_journey.get('id', 'unknown'), 'dimensions': len(user_journey.get('dimensions', []))})
        
        try:
            # Use LLM business abstraction for user journey guidance
            result = self.llm_abstraction.guide_user_journey(
                user_journey=user_journey,
                **kwargs
            )
            
            self._update_guide_stats('guided')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ User journey guidance failed: {e}")
            self._update_guide_stats('failed')
            raise
    
    def _provide_global_guidance(self, guidance_request: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Provide global guidance across dimensions.
        
        Args:
            guidance_request: Request for guidance
            **kwargs: Additional parameters
            
        Returns:
            Global guidance results
        """
        self._log_operation('provide_global_guidance', {'request_type': guidance_request.get('type', 'unknown')})
        
        try:
            # Use LLM business abstraction for global guidance
            result = self.llm_abstraction.provide_global_guidance(
                guidance_request=guidance_request,
                **kwargs
            )
            
            self._update_guide_stats('guided')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Global guidance failed: {e}")
            self._update_guide_stats('failed')
            raise
    
    def _coordinate_user_across_dimensions(self, user_id: str, target_dimensions: List[str], **kwargs) -> Dict[str, Any]:
        """
        Coordinate user across dimensions.
        
        Args:
            user_id: ID of the user
            target_dimensions: Dimensions to coordinate across
            **kwargs: Additional parameters
            
        Returns:
            Cross-dimensional coordination results
        """
        self._log_operation('coordinate_user_across_dimensions', {'user_id': user_id, 'dimensions': len(target_dimensions)})
        
        try:
            # Use LLM business abstraction for cross-dimensional coordination
            result = self.llm_abstraction.coordinate_user_across_dimensions(
                user_id=user_id,
                target_dimensions=target_dimensions,
                **kwargs
            )
            
            self._update_guide_stats('coordinated')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Cross-dimensional coordination failed: {e}")
            self._update_guide_stats('failed')
            raise
    
    def _optimize_user_experience(self, user_context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Optimize user experience across dimensions.
        
        Args:
            user_context: Context of the user
            **kwargs: Additional parameters
            
        Returns:
            User experience optimization results
        """
        self._log_operation('optimize_user_experience', {'user_id': user_context.get('user_id', 'unknown')})
        
        try:
            # Use LLM business abstraction for user experience optimization
            result = self.llm_abstraction.optimize_user_experience(
                user_context=user_context,
                **kwargs
            )
            
            self._update_guide_stats('optimized')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ User experience optimization failed: {e}")
            self._update_guide_stats('failed')
            raise
    
    def _update_guide_stats(self, operation: str):
        """Update guide statistics."""
        if operation == 'guided':
            self.guide_stats['user_journeys_guided'] += 1
            self.guide_stats['global_guidance_sessions'] += 1
        elif operation == 'coordinated':
            self.guide_stats['cross_dimensional_coordinations'] += 1
        elif operation == 'optimized':
            self.guide_stats['user_experience_optimizations'] += 1
        elif operation == 'failed':
            # Decrease satisfaction score on failures
            self.guide_state['user_satisfaction_score'] = max(0, self.guide_state['user_satisfaction_score'] - 3)
    
    def add_user_journey(self, user_id: str, journey_data: Dict[str, Any]):
        """Add user journey."""
        self.guide_state['user_journeys'][user_id] = journey_data
        if user_id not in self.guide_state['active_users']:
            self.guide_state['active_users'].append(user_id)
        self.logger.info(f"🧭 User journey added for {user_id}")
    
    def remove_user_journey(self, user_id: str):
        """Remove user journey."""
        if user_id in self.guide_state['user_journeys']:
            del self.guide_state['user_journeys'][user_id]
        if user_id in self.guide_state['active_users']:
            self.guide_state['active_users'].remove(user_id)
        self.logger.info(f"🧭 User journey removed for {user_id}")
    
    def get_user_journey(self, user_id: str) -> Dict[str, Any]:
        """Get user journey."""
        return self.guide_state['user_journeys'].get(user_id, {})
    
    def get_guide_stats(self) -> Dict[str, Any]:
        """Get guide statistics."""
        return self.guide_stats.copy()
    
    def get_guide_state(self) -> Dict[str, Any]:
        """Get guide state."""
        return self.guide_state.copy()
    
    def execute_guide_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute guide operation with governance.
        
        Args:
            operation: Operation to execute
            **kwargs: Operation parameters
            
        Returns:
            Operation results
        """
        if operation not in self.guide_operations:
            raise ValueError(f"❌ Unknown guide operation: {operation}")
        
        # Check rate limiting
        if self.governance_config['rate_limiting']:
            self._check_rate_limiting()
        
        # Execute operation
        result = self.guide_operations[operation](**kwargs)
        
        # Log for audit
        if self.governance_config['audit_logging']:
            self._log_operation(operation, kwargs)
        
        return result
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        base_info = super().get_agent_info()
        base_info.update({
            'agent_type': 'GlobalGuideAgent',
            'user_interactivity': self.user_interactivity,
            'user_facing': self.user_facing,
            'available_guide_operations': list(self.guide_operations.keys()),
            'guide_stats': self.get_guide_stats(),
            'guide_state': self.get_guide_state()
        })
        return base_info
