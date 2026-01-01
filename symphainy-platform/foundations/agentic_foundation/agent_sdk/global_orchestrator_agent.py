"""
Global Orchestrator Agent - Global Level Agent

Builds on dimensional agents + cross-dimensional awareness.
Orchestrates cross-dimensional operations with full platform context.

Characteristics:
- Cross-dimensional awareness - can access all platform dimensions
- Full platform context - understands business outcomes, user journeys, platform capabilities
- Strategic coordination - orchestrates complex multi-dimensional workflows
- Global orchestration - coordinates across all dimensions
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


class GlobalOrchestratorAgent(DimensionSpecialistAgent):
    """
    Global Orchestrator Agent - Global level, orchestrator capabilities
    
    Builds on dimensional agents + cross-dimensional awareness.
    Orchestrates cross-dimensional operations with full platform context.
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
        Initialize Global Orchestrator Agent.
        
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
            dimension="global",
            **kwargs
        )
        
        # Global agents have cross-dimensional awareness
        self.cross_dimensional_awareness = True
        self.global_context = True
        self.orchestrator_capabilities = True
        self.user_facing = False
        
        # Global orchestration capabilities
        self.global_operations = {
            'orchestrate_cross_dimension': self._orchestrate_cross_dimension,
            'coordinate_global_workflow': self._coordinate_global_workflow,
            'manage_platform_resources': self._manage_platform_resources,
            'optimize_global_operations': self._optimize_global_operations
        }
        
        # Initialize global orchestration state
        self._initialize_global_state()
        
        self.logger.info(f"🌐 GlobalOrchestratorAgent '{agent_name}' initialized with cross-dimensional awareness")
    
    def _initialize_global_state(self):
        """Initialize global orchestration state."""
        self.global_state = {
            'dimension': "global",
            'active_dimensions': [],
            'cross_dimensional_operations': [],
            'global_metrics': {},
            'orchestration_status': 'idle'
        }
        
        self.global_stats = {
            'cross_dimensional_operations': 0,
            'global_workflows_coordinated': 0,
            'platform_resources_managed': 0,
            'global_optimizations': 0,
            'orchestration_success_rate': 100.0
        }
    
    def _orchestrate_cross_dimension(self, target_dimensions: List[str], operation_type: str, **kwargs) -> Dict[str, Any]:
        """
        Orchestrate cross-dimensional operations.
        
        Args:
            target_dimensions: Dimensions to orchestrate
            operation_type: Type of operation to orchestrate
            **kwargs: Additional parameters
            
        Returns:
            Orchestration results
        """
        self._log_operation('orchestrate_cross_dimension', {'dimensions': len(target_dimensions), 'operation_type': operation_type})
        
        try:
            # Use LLM business abstraction for cross-dimensional orchestration
            result = self.llm_abstraction.orchestrate_cross_dimension(
                target_dimensions=target_dimensions,
                operation_type=operation_type,
                **kwargs
            )
            
            self._update_global_stats('orchestrated')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Cross-dimensional orchestration failed: {e}")
            self._update_global_stats('failed')
            raise
    
    def _coordinate_global_workflow(self, workflow_definition: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Coordinate global workflow across dimensions.
        
        Args:
            workflow_definition: Definition of the workflow
            **kwargs: Additional parameters
            
        Returns:
            Workflow coordination results
        """
        self._log_operation('coordinate_global_workflow', {'workflow_steps': len(workflow_definition.get('steps', []))})
        
        try:
            # Use LLM business abstraction for global workflow coordination
            result = self.llm_abstraction.coordinate_global_workflow(
                workflow_definition=workflow_definition,
                **kwargs
            )
            
            self._update_global_stats('coordinated')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Global workflow coordination failed: {e}")
            self._update_global_stats('failed')
            raise
    
    def _manage_platform_resources(self, resource_requirements: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Manage platform resources across dimensions.
        
        Args:
            resource_requirements: Requirements for resources
            **kwargs: Additional parameters
            
        Returns:
            Resource management results
        """
        self._log_operation('manage_platform_resources', {'requirements': len(resource_requirements.keys())})
        
        try:
            # Use LLM business abstraction for platform resource management
            result = self.llm_abstraction.manage_platform_resources(
                resource_requirements=resource_requirements,
                **kwargs
            )
            
            self._update_global_stats('managed')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Platform resource management failed: {e}")
            self._update_global_stats('failed')
            raise
    
    def _optimize_global_operations(self, optimization_scope: str, **kwargs) -> Dict[str, Any]:
        """
        Optimize global operations across dimensions.
        
        Args:
            optimization_scope: Scope of optimization
            **kwargs: Additional parameters
            
        Returns:
            Optimization results
        """
        self._log_operation('optimize_global_operations', {'scope': optimization_scope})
        
        try:
            # Use LLM business abstraction for global optimization
            result = self.llm_abstraction.optimize_global_operations(
                optimization_scope=optimization_scope,
                **kwargs
            )
            
            self._update_global_stats('optimized')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Global optimization failed: {e}")
            self._update_global_stats('failed')
            raise
    
    def _update_global_stats(self, operation: str):
        """Update global statistics."""
        if operation == 'orchestrated':
            self.global_stats['cross_dimensional_operations'] += 1
        elif operation == 'coordinated':
            self.global_stats['global_workflows_coordinated'] += 1
        elif operation == 'managed':
            self.global_stats['platform_resources_managed'] += 1
        elif operation == 'optimized':
            self.global_stats['global_optimizations'] += 1
        elif operation == 'failed':
            # Decrease success rate on failures
            self.global_stats['orchestration_success_rate'] = max(0, self.global_stats['orchestration_success_rate'] - 5)
    
    def add_active_dimension(self, dimension: str):
        """Add active dimension."""
        if dimension not in self.global_state['active_dimensions']:
            self.global_state['active_dimensions'].append(dimension)
        self.logger.info(f"🏗️ Active dimension added: {dimension}")
    
    def remove_active_dimension(self, dimension: str):
        """Remove active dimension."""
        if dimension in self.global_state['active_dimensions']:
            self.global_state['active_dimensions'].remove(dimension)
        self.logger.info(f"🏗️ Active dimension removed: {dimension}")
    
    def get_active_dimensions(self) -> List[str]:
        """Get active dimensions."""
        return self.global_state['active_dimensions'].copy()
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global statistics."""
        return self.global_stats.copy()
    
    def get_global_state(self) -> Dict[str, Any]:
        """Get global state."""
        return self.global_state.copy()
    
    def execute_global_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute global operation with governance.
        
        Args:
            operation: Operation to execute
            **kwargs: Operation parameters
            
        Returns:
            Operation results
        """
        if operation not in self.global_operations:
            raise ValueError(f"❌ Unknown global operation: {operation}")
        
        # Check rate limiting
        if self.governance_config['rate_limiting']:
            self._check_rate_limiting()
        
        # Execute operation
        result = self.global_operations[operation](**kwargs)
        
        # Log for audit
        if self.governance_config['audit_logging']:
            self._log_operation(operation, kwargs)
        
        return result
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        base_info = super().get_agent_info()
        base_info.update({
            'agent_type': 'GlobalOrchestratorAgent',
            'cross_dimensional_awareness': self.cross_dimensional_awareness,
            'global_context': self.global_context,
            'orchestrator_capabilities': self.orchestrator_capabilities,
            'available_global_operations': list(self.global_operations.keys()),
            'global_stats': self.get_global_stats(),
            'global_state': self.get_global_state()
        })
        return base_info
