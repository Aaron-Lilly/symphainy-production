"""
Task LLM Agent - Simple Level Agent

Task-oriented LLM operations with governance.
Builds on LightweightLLMAgent with specific task-oriented capabilities.

Characteristics:
- Task-oriented LLM operations - specific task-focused LLM calls
- MCP Tools integration - access to platform tools
- AGUI integration - structured output formatting
- Centralized governance - all LLM activity goes through governance
- Cost containment - centralized rate limiting and usage tracking
- Audit trail - complete traceability of LLM operations
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


class TaskLLMAgent(LightweightLLMAgent):
    """
    Task LLM Agent - Simple level, task-oriented LLM operations
    
    Specific task-oriented LLM operations with governance.
    Builds on LightweightLLMAgent with task-specific capabilities.
    """
    
    def __init__(self, agent_name: str, capabilities: List[str], 
                 required_roles: List[str], agui_schema: Dict[str, Any],
                 foundation_services: DIContainerService,
                 agentic_foundation: 'AgenticFoundationService',
                 mcp_client_manager: MCPClientManager,
                 policy_integration: PolicyIntegration,
                 tool_composition: ToolComposition,
                 agui_formatter: Any,
                 task_type: str,
                 **kwargs):
        """
        Initialize Task LLM Agent.
        
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
            task_type: Type of task this agent handles
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
        
        # Task agents are task-oriented LLM operations
        self.task_type = task_type
        self.task_oriented = True
        self.mcp_tools_integration = True
        self.agui_integration = True
        self.centralized_governance = True
        self.user_facing = False
        
        # Task-specific capabilities
        self.task_operations = {
            'process_task': self._process_task,
            'validate_task': self._validate_task,
            'optimize_task': self._optimize_task,
            'complete_task': self._complete_task
        }
        
        # Initialize task-specific configuration
        self._initialize_task_config()
        
        self.logger.info(f"🎯 TaskLLMAgent '{agent_name}' initialized for task type: {task_type}")
    
    def _initialize_task_config(self):
        """Initialize task-specific configuration."""
        self.task_config = {
            'task_type': self.task_type,
            'task_validation': True,
            'task_optimization': True,
            'task_completion_tracking': True,
            'task_quality_metrics': True
        }
        
        self.task_stats = {
            'tasks_processed': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'average_processing_time': 0.0,
            'quality_score': 0.0
        }
    
    def _process_task(self, task_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Process a task using LLM abstraction.
        
        Args:
            task_data: Task data to process
            **kwargs: Additional parameters
            
        Returns:
            Task processing results
        """
        self._log_operation('process_task', {'task_type': self.task_type, 'data_keys': len(task_data.keys())})
        
        try:
            # Use LLM business abstraction for task processing
            result = self.llm_abstraction.process_task(
                task_data=task_data,
                task_type=self.task_type,
                **kwargs
            )
            
            self._update_task_stats('processed')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Task processing failed: {e}")
            self._update_task_stats('failed')
            raise
    
    def _validate_task(self, task_data: Dict[str, Any], validation_criteria: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Validate a task using LLM abstraction.
        
        Args:
            task_data: Task data to validate
            validation_criteria: Criteria for validation
            **kwargs: Additional parameters
            
        Returns:
            Task validation results
        """
        self._log_operation('validate_task', {'task_type': self.task_type, 'criteria_keys': len(validation_criteria.keys())})
        
        try:
            # Use LLM business abstraction for task validation
            result = self.llm_abstraction.validate_task(
                task_data=task_data,
                validation_criteria=validation_criteria,
                task_type=self.task_type,
                **kwargs
            )
            
            self._update_task_stats('validated')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Task validation failed: {e}")
            self._update_task_stats('failed')
            raise
    
    def _optimize_task(self, task_data: Dict[str, Any], optimization_goals: List[str], **kwargs) -> Dict[str, Any]:
        """
        Optimize a task using LLM abstraction.
        
        Args:
            task_data: Task data to optimize
            optimization_goals: Goals for optimization
            **kwargs: Additional parameters
            
        Returns:
            Task optimization results
        """
        self._log_operation('optimize_task', {'task_type': self.task_type, 'goals': len(optimization_goals)})
        
        try:
            # Use LLM business abstraction for task optimization
            result = self.llm_abstraction.optimize_task(
                task_data=task_data,
                optimization_goals=optimization_goals,
                task_type=self.task_type,
                **kwargs
            )
            
            self._update_task_stats('optimized')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Task optimization failed: {e}")
            self._update_task_stats('failed')
            raise
    
    def _complete_task(self, task_data: Dict[str, Any], completion_criteria: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Complete a task using LLM abstraction.
        
        Args:
            task_data: Task data to complete
            completion_criteria: Criteria for completion
            **kwargs: Additional parameters
            
        Returns:
            Task completion results
        """
        self._log_operation('complete_task', {'task_type': self.task_type, 'criteria_keys': len(completion_criteria.keys())})
        
        try:
            # Use LLM business abstraction for task completion
            result = self.llm_abstraction.complete_task(
                task_data=task_data,
                completion_criteria=completion_criteria,
                task_type=self.task_type,
                **kwargs
            )
            
            self._update_task_stats('completed')
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Task completion failed: {e}")
            self._update_task_stats('failed')
            raise
    
    def _update_task_stats(self, operation: str):
        """Update task statistics."""
        if operation == 'processed':
            self.task_stats['tasks_processed'] += 1
        elif operation == 'completed':
            self.task_stats['tasks_completed'] += 1
        elif operation == 'failed':
            self.task_stats['tasks_failed'] += 1
        
        # Calculate quality score
        total_tasks = self.task_stats['tasks_processed']
        if total_tasks > 0:
            self.task_stats['quality_score'] = (self.task_stats['tasks_completed'] / total_tasks) * 100
    
    def execute_task_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute task operation with governance.
        
        Args:
            operation: Operation to execute
            **kwargs: Operation parameters
            
        Returns:
            Operation results
        """
        if operation not in self.task_operations:
            raise ValueError(f"❌ Unknown task operation: {operation}")
        
        # Check rate limiting
        if self.governance_config['rate_limiting']:
            self._check_rate_limiting()
        
        # Execute operation
        result = self.task_operations[operation](**kwargs)
        
        # Log for audit
        if self.governance_config['audit_logging']:
            self._log_operation(operation, kwargs)
        
        return result
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get task statistics."""
        return self.task_stats.copy()
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        base_info = super().get_agent_info()
        base_info.update({
            'agent_type': 'TaskLLMAgent',
            'task_type': self.task_type,
            'task_oriented': self.task_oriented,
            'available_task_operations': list(self.task_operations.keys()),
            'task_stats': self.get_task_stats()
        })
        return base_info
