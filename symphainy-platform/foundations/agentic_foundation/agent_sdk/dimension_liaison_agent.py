"""
Dimension Liaison Agent - Dimensional Level Agent

Builds on specialist capabilities + user interactivity capabilities.
User-facing agents within a dimension with liaison capabilities.

Characteristics:
- Dimensional awareness - deep expertise within their dimension
- State awareness - can maintain and manage state
- Tool usage - can use MCP tools effectively
- Specialist capabilities - focused on specific dimensional functions
- User interactivity - can interact with users within their dimension
- Coordinated operations - work within their dimension's context
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
from .dimension_specialist_agent import DimensionSpecialistAgent
from .mcp_client_manager import MCPClientManager
from .policy_integration import PolicyIntegration
from .tool_composition import ToolComposition
from utilities import UserContext


class DimensionLiaisonAgent(DimensionSpecialistAgent):
    """
    Dimension Liaison Agent - Dimensional level, liaison capabilities + user interactivity
    
    Builds on specialist capabilities + user interactivity capabilities.
    User-facing agents within a dimension with liaison capabilities.
    """
    
    def __init__(self, agent_name: str, capabilities: List[str], 
                 required_roles: List[str], agui_schema: Dict[str, Any],
                 foundation_services: DIContainerService,
                 agentic_foundation: 'AgenticFoundationService',
                 mcp_client_manager: MCPClientManager,
                 policy_integration: PolicyIntegration,
                 tool_composition: ToolComposition,
                 agui_formatter: Any,
                 dimension: str,
                 **kwargs):
        """
        Initialize Dimension Liaison Agent.
        
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
            dimension: Dimension this agent liaises for
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
            dimension=dimension,
            **kwargs
        )
        
        # Dimension agents have dimensional awareness + user interactivity
        self.dimension = dimension
        self.dimensional_awareness = True
        self.state_awareness = True
        self.tool_usage = True
        self.specialist_capabilities = True
        self.user_interactivity = True
        self.user_facing = True
        
        # Liaison-specific capabilities
        self.liaison_operations = {
            'liaise_with_user': self._liaise_with_user,
            'translate_user_request': self._translate_user_request,
            'coordinate_user_workflow': self._coordinate_user_workflow,
            'provide_user_guidance': self._provide_user_guidance
        }
        
        # Initialize liaison-specific state
        self._initialize_liaison_state()
        
        self.logger.info(f"🤝 DimensionLiaisonAgent '{agent_name}' initialized for dimension: {dimension}")
    
    def _initialize_liaison_state(self):
        """Initialize liaison-specific state."""
        self.liaison_state = {
            'dimension': self.dimension,
            'active_users': [],
            'user_sessions': {},
            'liaison_metrics': {},
            'user_satisfaction_score': 100.0
        }
        
        self.liaison_stats = {
            'user_interactions': 0,
            'successful_liaisons': 0,
            'failed_liaisons': 0,
            'user_satisfaction_events': 0,
            'average_response_time': 0.0
        }
    
    def _liaise_with_user(self, user_request: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Liaise with user within dimension.
        
        Args:
            user_request: User request to process
            **kwargs: Additional parameters
            
        Returns:
            Liaison results
        """
        self._log_operation('liaise_with_user', {'dimension': self.dimension, 'request_type': user_request.get('type', 'unknown')})
        
        try:
            # Use LLM business abstraction for user liaison
            result = self.llm_abstraction.liaise_with_user(
                dimension=self.dimension,
                user_request=user_request,
                **kwargs
            )
            
            self._update_liaison_stats('liaised')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ User liaison failed: {e}")
            self._update_liaison_stats('failed')
            raise
    
    def _translate_user_request(self, user_request: Dict[str, Any], target_format: str, **kwargs) -> Dict[str, Any]:
        """
        Translate user request to dimension-specific format.
        
        Args:
            user_request: User request to translate
            target_format: Target format for translation
            **kwargs: Additional parameters
            
        Returns:
            Translation results
        """
        self._log_operation('translate_user_request', {'dimension': self.dimension, 'target_format': target_format})
        
        try:
            # Use LLM business abstraction for request translation
            result = self.llm_abstraction.translate_user_request(
                dimension=self.dimension,
                user_request=user_request,
                target_format=target_format,
                **kwargs
            )
            
            self._update_liaison_stats('translated')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Request translation failed: {e}")
            self._update_liaison_stats('failed')
            raise
    
    def _coordinate_user_workflow(self, workflow_steps: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Coordinate user workflow within dimension.
        
        Args:
            workflow_steps: Steps in the workflow
            **kwargs: Additional parameters
            
        Returns:
            Workflow coordination results
        """
        self._log_operation('coordinate_user_workflow', {'dimension': self.dimension, 'steps': len(workflow_steps)})
        
        try:
            # Use LLM business abstraction for workflow coordination
            result = self.llm_abstraction.coordinate_user_workflow(
                dimension=self.dimension,
                workflow_steps=workflow_steps,
                **kwargs
            )
            
            self._update_liaison_stats('coordinated')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Workflow coordination failed: {e}")
            self._update_liaison_stats('failed')
            raise
    
    def _provide_user_guidance(self, guidance_context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Provide user guidance within dimension.
        
        Args:
            guidance_context: Context for guidance
            **kwargs: Additional parameters
            
        Returns:
            Guidance results
        """
        self._log_operation('provide_user_guidance', {'dimension': self.dimension, 'context_keys': len(guidance_context.keys())})
        
        try:
            # Use LLM business abstraction for user guidance
            result = self.llm_abstraction.provide_user_guidance(
                dimension=self.dimension,
                guidance_context=guidance_context,
                **kwargs
            )
            
            self._update_liaison_stats('guided')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ User guidance failed: {e}")
            self._update_liaison_stats('failed')
            raise
    
    def _update_liaison_stats(self, operation: str):
        """Update liaison statistics."""
        if operation == 'liaised':
            self.liaison_stats['user_interactions'] += 1
            self.liaison_stats['successful_liaisons'] += 1
        elif operation == 'translated':
            self.liaison_stats['user_interactions'] += 1
        elif operation == 'coordinated':
            self.liaison_stats['user_interactions'] += 1
        elif operation == 'guided':
            self.liaison_stats['user_interactions'] += 1
        elif operation == 'failed':
            self.liaison_stats['failed_liaisons'] += 1
            # Decrease satisfaction score on failures
            self.liaison_state['user_satisfaction_score'] = max(0, self.liaison_state['user_satisfaction_score'] - 2)
    
    def add_user_session(self, user_id: str, session_data: Dict[str, Any]):
        """Add user session."""
        self.liaison_state['user_sessions'][user_id] = session_data
        self.liaison_state['active_users'].append(user_id)
        self.logger.info(f"👤 User session added for {user_id} in {self.dimension}")
    
    def remove_user_session(self, user_id: str):
        """Remove user session."""
        if user_id in self.liaison_state['user_sessions']:
            del self.liaison_state['user_sessions'][user_id]
        if user_id in self.liaison_state['active_users']:
            self.liaison_state['active_users'].remove(user_id)
        self.logger.info(f"👤 User session removed for {user_id} in {self.dimension}")
    
    def get_user_session(self, user_id: str) -> Dict[str, Any]:
        """Get user session."""
        return self.liaison_state['user_sessions'].get(user_id, {})
    
    def get_liaison_stats(self) -> Dict[str, Any]:
        """Get liaison statistics."""
        return self.liaison_stats.copy()
    
    def get_liaison_state(self) -> Dict[str, Any]:
        """Get liaison state."""
        return self.liaison_state.copy()
    
    def execute_liaison_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute liaison operation with governance.
        
        Args:
            operation: Operation to execute
            **kwargs: Operation parameters
            
        Returns:
            Operation results
        """
        if operation not in self.liaison_operations:
            raise ValueError(f"❌ Unknown liaison operation: {operation}")
        
        # Check rate limiting
        if self.governance_config['rate_limiting']:
            self._check_rate_limiting()
        
        # Execute operation
        result = self.liaison_operations[operation](**kwargs)
        
        # Log for audit
        if self.governance_config['audit_logging']:
            self._log_operation(operation, kwargs)
        
        return result
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        base_info = super().get_agent_info()
        base_info.update({
            'agent_type': 'DimensionLiaisonAgent',
            'user_interactivity': self.user_interactivity,
            'user_facing': self.user_facing,
            'available_liaison_operations': list(self.liaison_operations.keys()),
            'liaison_stats': self.get_liaison_stats(),
            'liaison_state': self.get_liaison_state()
        })
        return base_info
