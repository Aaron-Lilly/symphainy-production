"""
Dimension Specialist Agent - Dimensional Level Agent

Builds on simple agents + basic state awareness and use of tools.
Specialist agents within a dimension with deep expertise.

Characteristics:
- Dimensional awareness - deep expertise within their dimension
- State awareness - can maintain and manage state
- Tool usage - can use MCP tools effectively
- Specialized capabilities - focused on specific dimensional functions
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
from .lightweight_llm_agent import LightweightLLMAgent
from .mcp_client_manager import MCPClientManager
from .policy_integration import PolicyIntegration
from .tool_composition import ToolComposition
from utilities import UserContext


class DimensionSpecialistAgent(LightweightLLMAgent):
    """
    Dimension Specialist Agent - Dimensional level, specialist capabilities
    
    Builds on simple agents + basic state awareness and use of tools.
    Specialist agents within a dimension with deep expertise.
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
        Initialize Dimension Specialist Agent.
        
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
            dimension: Dimension this agent specializes in
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
        
        # Dimension agents have dimensional awareness
        self.dimension = dimension
        self.dimensional_awareness = True
        self.state_awareness = True
        self.tool_usage = True
        self.specialist_capabilities = True
        self.user_facing = False
        
        # Dimension-specific capabilities
        self.dimension_operations = {
            'analyze_dimension': self._analyze_dimension,
            'coordinate_dimension': self._coordinate_dimension,
            'optimize_dimension': self._optimize_dimension,
            'monitor_dimension': self._monitor_dimension
        }
        
        # Initialize dimension-specific state
        self._initialize_dimension_state()
        
        self.logger.info(f"🏗️ DimensionSpecialistAgent '{agent_name}' initialized for dimension: {dimension}")
    
    def _initialize_dimension_state(self):
        """Initialize dimension-specific state."""
        self.dimension_state = {
            'dimension': self.dimension,
            'current_context': None,
            'active_operations': [],
            'dimension_metrics': {},
            'coordination_status': 'idle'
        }
        
        self.dimension_stats = {
            'operations_executed': 0,
            'coordination_events': 0,
            'optimization_cycles': 0,
            'monitoring_checks': 0,
            'dimension_health_score': 100.0
        }
    
    def _analyze_dimension(self, analysis_scope: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze dimension using specialist capabilities.
        
        Args:
            analysis_scope: Scope of analysis
            **kwargs: Additional parameters
            
        Returns:
            Dimension analysis results
        """
        self._log_operation('analyze_dimension', {'dimension': self.dimension, 'scope': analysis_scope})
        
        try:
            # Use LLM business abstraction for dimension analysis
            result = self.llm_abstraction.analyze_dimension(
                dimension=self.dimension,
                analysis_scope=analysis_scope,
                **kwargs
            )
            
            self._update_dimension_stats('analyzed')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Dimension analysis failed: {e}")
            self._update_dimension_stats('failed')
            raise
    
    def _coordinate_dimension(self, coordination_targets: List[str], **kwargs) -> Dict[str, Any]:
        """
        Coordinate within dimension using specialist capabilities.
        
        Args:
            coordination_targets: Targets for coordination
            **kwargs: Additional parameters
            
        Returns:
            Coordination results
        """
        self._log_operation('coordinate_dimension', {'dimension': self.dimension, 'targets': len(coordination_targets)})
        
        try:
            # Use LLM business abstraction for dimension coordination
            result = self.llm_abstraction.coordinate_dimension(
                dimension=self.dimension,
                coordination_targets=coordination_targets,
                **kwargs
            )
            
            self._update_dimension_stats('coordinated')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Dimension coordination failed: {e}")
            self._update_dimension_stats('failed')
            raise
    
    def _optimize_dimension(self, optimization_goals: List[str], **kwargs) -> Dict[str, Any]:
        """
        Optimize dimension using specialist capabilities.
        
        Args:
            optimization_goals: Goals for optimization
            **kwargs: Additional parameters
            
        Returns:
            Optimization results
        """
        self._log_operation('optimize_dimension', {'dimension': self.dimension, 'goals': len(optimization_goals)})
        
        try:
            # Use LLM business abstraction for dimension optimization
            result = self.llm_abstraction.optimize_dimension(
                dimension=self.dimension,
                optimization_goals=optimization_goals,
                **kwargs
            )
            
            self._update_dimension_stats('optimized')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Dimension optimization failed: {e}")
            self._update_dimension_stats('failed')
            raise
    
    def _monitor_dimension(self, monitoring_metrics: List[str], **kwargs) -> Dict[str, Any]:
        """
        Monitor dimension using specialist capabilities.
        
        Args:
            monitoring_metrics: Metrics to monitor
            **kwargs: Additional parameters
            
        Returns:
            Monitoring results
        """
        self._log_operation('monitor_dimension', {'dimension': self.dimension, 'metrics': len(monitoring_metrics)})
        
        try:
            # Use LLM business abstraction for dimension monitoring
            result = self.llm_abstraction.monitor_dimension(
                dimension=self.dimension,
                monitoring_metrics=monitoring_metrics,
                **kwargs
            )
            
            self._update_dimension_stats('monitored')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Dimension monitoring failed: {e}")
            self._update_dimension_stats('failed')
            raise
    
    def _update_dimension_stats(self, operation: str):
        """Update dimension statistics."""
        if operation == 'analyzed':
            self.dimension_stats['operations_executed'] += 1
        elif operation == 'coordinated':
            self.dimension_stats['coordination_events'] += 1
        elif operation == 'optimized':
            self.dimension_stats['optimization_cycles'] += 1
        elif operation == 'monitored':
            self.dimension_stats['monitoring_checks'] += 1
        elif operation == 'failed':
            # Decrease health score on failures
            self.dimension_stats['dimension_health_score'] = max(0, self.dimension_stats['dimension_health_score'] - 5)
    
    def set_dimension_context(self, context: Dict[str, Any]):
        """Set dimension context."""
        self.dimension_state['current_context'] = context
        self.logger.info(f"📝 Dimension context updated for {self.dimension}")
    
    def get_dimension_context(self) -> Dict[str, Any]:
        """Get dimension context."""
        return self.dimension_state['current_context']
    
    def get_dimension_stats(self) -> Dict[str, Any]:
        """Get dimension statistics."""
        return self.dimension_stats.copy()
    
    def get_dimension_state(self) -> Dict[str, Any]:
        """Get dimension state."""
        return self.dimension_state.copy()
    
    def execute_dimension_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute dimension operation with governance.
        
        Args:
            operation: Operation to execute
            **kwargs: Operation parameters
            
        Returns:
            Operation results
        """
        if operation not in self.dimension_operations:
            raise ValueError(f"❌ Unknown dimension operation: {operation}")
        
        # Check rate limiting
        if self.governance_config['rate_limiting']:
            self._check_rate_limiting()
        
        # Execute operation
        result = self.dimension_operations[operation](**kwargs)
        
        # Log for audit
        if self.governance_config['audit_logging']:
            self._log_operation(operation, kwargs)
        
        return result
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        base_info = super().get_agent_info()
        base_info.update({
            'agent_type': 'DimensionSpecialistAgent',
            'dimension': self.dimension,
            'dimensional_awareness': self.dimensional_awareness,
            'state_awareness': self.state_awareness,
            'tool_usage': self.tool_usage,
            'specialist_capabilities': self.specialist_capabilities,
            'available_dimension_operations': list(self.dimension_operations.keys()),
            'dimension_stats': self.get_dimension_stats(),
            'dimension_state': self.get_dimension_state()
        })
        return base_info
