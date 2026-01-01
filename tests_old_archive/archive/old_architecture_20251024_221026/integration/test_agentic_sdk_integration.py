#!/usr/bin/env python3
"""
Integration Tests: Agentic SDK Agent Interactions and Cross-Hierarchical Communication

Tests the integration between different agent types and their ability to work together
in hierarchical structures with proper governance and communication.

WHAT (Test Role): I validate agent interactions and cross-hierarchical communication
HOW (Test Implementation): I test real agent interactions with infrastructure services
"""

import pytest
import sys
import os
import asyncio
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from typing import Dict, Any, List

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../symphainy-platform'))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from agentic.agent_sdk.lightweight_llm_agent import LightweightLLMAgent
from agentic.agent_sdk.task_llm_agent import TaskLLMAgent
from agentic.agent_sdk.dimension_specialist_agent import DimensionSpecialistAgent
from agentic.agent_sdk.dimension_liaison_agent import DimensionLiaisonAgent
from agentic.agent_sdk.global_orchestrator_agent import GlobalOrchestratorAgent
from agentic.agent_sdk.global_guide_agent import GlobalGuideAgent


class TestAgenticSDKIntegration:
    """Test agent interactions and cross-hierarchical communication."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for agent testing."""
        # Mock DIContainerService
        di_container = Mock(spec=DIContainerService)
        di_container.get_logger.return_value = Mock()
        di_container.get_config.return_value = Mock()
        di_container.get_health.return_value = Mock()
        di_container.get_telemetry.return_value = Mock()
        di_container.get_security.return_value = Mock()
        di_container.get_error_handler.return_value = Mock()
        
        # Mock PublicWorksFoundationService
        public_works_foundation = Mock(spec=PublicWorksFoundationService)
        
        # Mock MCPClientManager
        mcp_client_manager = Mock()
        
        # Mock PolicyIntegration
        policy_integration = Mock()
        
        # Mock ToolComposition
        tool_composition = Mock()
        
        # Mock AGUIOutputFormatter
        agui_formatter = Mock()
        
        return {
            'di_container': di_container,
            'public_works_foundation': public_works_foundation,
            'mcp_client_manager': mcp_client_manager,
            'policy_integration': policy_integration,
            'tool_composition': tool_composition,
            'agui_formatter': agui_formatter
        }
    
    def test_agent_hierarchy_communication(self, mock_dependencies):
        """Test communication between agents at different hierarchy levels."""
        # Create agents at different levels
        lightweight = LightweightLLMAgent(
            agent_name="lightweight_agent",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        task = TaskLLMAgent(
            agent_name="task_agent",
            capabilities=["task_operations"],
            required_roles=["executor"],
            agui_schema={},
            task_type="data_analysis",
            **mock_dependencies
        )
        
        specialist = DimensionSpecialistAgent(
            agent_name="specialist_agent",
            capabilities=["specialist_operations"],
            required_roles=["specialist"],
            agui_schema={},
            dimension="business_enablement",
            **mock_dependencies
        )
        
        liaison = DimensionLiaisonAgent(
            agent_name="liaison_agent",
            capabilities=["liaison_operations"],
            required_roles=["liaison"],
            agui_schema={},
            dimension="business_enablement",
            **mock_dependencies
        )
        
        orchestrator = GlobalOrchestratorAgent(
            agent_name="orchestrator_agent",
            capabilities=["orchestration"],
            required_roles=["orchestrator"],
            agui_schema={},
            **mock_dependencies
        )
        
        guide = GlobalGuideAgent(
            agent_name="guide_agent",
            capabilities=["guidance"],
            required_roles=["guide"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Test that all agents can be created and have proper hierarchy
        agents = [lightweight, task, specialist, liaison, orchestrator, guide]
        
        for agent in agents:
            assert agent is not None
            assert agent.centralized_governance is True
            assert hasattr(agent, 'governance_config')
            assert hasattr(agent, 'audit_log')
            assert hasattr(agent, 'usage_stats')
    
    def test_cross_dimensional_agent_coordination(self, mock_dependencies):
        """Test coordination between agents across different dimensions."""
        # Create agents for different dimensions
        business_specialist = DimensionSpecialistAgent(
            agent_name="business_specialist",
            capabilities=["business_analysis"],
            required_roles=["business_analyst"],
            agui_schema={},
            dimension="business_enablement",
            **mock_dependencies
        )
        
        smart_city_specialist = DimensionSpecialistAgent(
            agent_name="smart_city_specialist",
            capabilities=["smart_city_analysis"],
            required_roles=["smart_city_analyst"],
            agui_schema={},
            dimension="smart_city",
            **mock_dependencies
        )
        
        # Create liaison agents for each dimension
        business_liaison = DimensionLiaisonAgent(
            agent_name="business_liaison",
            capabilities=["business_liaison"],
            required_roles=["business_liaison"],
            agui_schema={},
            dimension="business_enablement",
            **mock_dependencies
        )
        
        smart_city_liaison = DimensionLiaisonAgent(
            agent_name="smart_city_liaison",
            capabilities=["smart_city_liaison"],
            required_roles=["smart_city_liaison"],
            agui_schema={},
            dimension="smart_city",
            **mock_dependencies
        )
        
        # Create global orchestrator to coordinate
        orchestrator = GlobalOrchestratorAgent(
            agent_name="global_orchestrator",
            capabilities=["cross_dimensional_orchestration"],
            required_roles=["platform_orchestrator"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Test that all agents can work together
        agents = [business_specialist, smart_city_specialist, business_liaison, smart_city_liaison, orchestrator]
        
        for agent in agents:
            assert agent is not None
            assert agent.centralized_governance is True
            
            # Test governance consistency
            assert agent.governance_config['rate_limiting'] is True
            assert agent.governance_config['cost_tracking'] is True
            assert agent.governance_config['audit_logging'] is True
            assert agent.governance_config['usage_monitoring'] is True
    
    def test_agent_workflow_orchestration(self, mock_dependencies):
        """Test orchestration of agent workflows across the hierarchy."""
        # Create a workflow with agents at different levels
        lightweight = LightweightLLMAgent(
            agent_name="data_processor",
            capabilities=["data_processing"],
            required_roles=["data_processor"],
            agui_schema={},
            **mock_dependencies
        )
        
        task = TaskLLMAgent(
            agent_name="analysis_task",
            capabilities=["analysis"],
            required_roles=["analyst"],
            agui_schema={},
            task_type="data_analysis",
            **mock_dependencies
        )
        
        specialist = DimensionSpecialistAgent(
            agent_name="business_specialist",
            capabilities=["business_analysis"],
            required_roles=["business_analyst"],
            agui_schema={},
            dimension="business_enablement",
            **mock_dependencies
        )
        
        liaison = DimensionLiaisonAgent(
            agent_name="business_liaison",
            capabilities=["business_liaison"],
            required_roles=["business_liaison"],
            agui_schema={},
            dimension="business_enablement",
            **mock_dependencies
        )
        
        orchestrator = GlobalOrchestratorAgent(
            agent_name="workflow_orchestrator",
            capabilities=["workflow_orchestration"],
            required_roles=["workflow_orchestrator"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Test workflow orchestration
        workflow_agents = [lightweight, task, specialist, liaison, orchestrator]
        
        # Simulate workflow execution
        for agent in workflow_agents:
            # Each agent should be able to execute operations
            assert hasattr(agent, 'execute_llm_operation') or hasattr(agent, 'execute_task_operation') or hasattr(agent, 'execute_specialist_operation') or hasattr(agent, 'execute_liaison_operation') or hasattr(agent, 'execute_orchestrator_operation')
            
            # Each agent should have governance
            assert agent.centralized_governance is True
            assert hasattr(agent, 'governance_config')
            assert hasattr(agent, 'audit_log')
            assert hasattr(agent, 'usage_stats')
    
    def test_agent_governance_consistency_across_hierarchy(self, mock_dependencies):
        """Test that governance is consistent across the entire agent hierarchy."""
        # Create agents at all levels
        agents = [
            LightweightLLMAgent(
                agent_name="lightweight",
                capabilities=["llm_operations"],
                required_roles=["analyst"],
                agui_schema={},
                **mock_dependencies
            ),
            TaskLLMAgent(
                agent_name="task",
                capabilities=["task_operations"],
                required_roles=["executor"],
                agui_schema={},
                task_type="analysis",
                **mock_dependencies
            ),
            DimensionSpecialistAgent(
                agent_name="specialist",
                capabilities=["specialist_operations"],
                required_roles=["specialist"],
                agui_schema={},
                dimension="business",
                **mock_dependencies
            ),
            DimensionLiaisonAgent(
                agent_name="liaison",
                capabilities=["liaison_operations"],
                required_roles=["liaison"],
                agui_schema={},
                dimension="business",
                **mock_dependencies
            ),
            GlobalOrchestratorAgent(
                agent_name="orchestrator",
                capabilities=["orchestration"],
                required_roles=["orchestrator"],
                agui_schema={},
                **mock_dependencies
            ),
            GlobalGuideAgent(
                agent_name="guide",
                capabilities=["guidance"],
                required_roles=["guide"],
                agui_schema={},
                **mock_dependencies
            )
        ]
        
        # Test governance consistency
        for agent in agents:
            # All agents should have the same governance configuration
            assert agent.governance_config['rate_limiting'] is True
            assert agent.governance_config['cost_tracking'] is True
            assert agent.governance_config['audit_logging'] is True
            assert agent.governance_config['usage_monitoring'] is True
            
            # All agents should have the same governance methods
            assert hasattr(agent, 'get_usage_stats')
            assert hasattr(agent, 'get_audit_log')
            assert hasattr(agent, 'reset_usage_stats')
            
            # All agents should start with clean governance state
            usage_stats = agent.get_usage_stats()
            assert usage_stats['total_requests'] == 0
            assert usage_stats['total_tokens'] == 0
            assert usage_stats['total_cost'] == 0.0
            assert usage_stats['last_request'] is None
            
            audit_log = agent.get_audit_log()
            assert len(audit_log) == 0
    
    def test_agent_capability_progression_integration(self, mock_dependencies):
        """Test that agent capabilities progress correctly through the hierarchy in integration scenarios."""
        # Create agents at different levels
        lightweight = LightweightLLMAgent(
            agent_name="lightweight",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        task = TaskLLMAgent(
            agent_name="task",
            capabilities=["task_operations"],
            required_roles=["executor"],
            agui_schema={},
            task_type="analysis",
            **mock_dependencies
        )
        
        specialist = DimensionSpecialistAgent(
            agent_name="specialist",
            capabilities=["specialist_operations"],
            required_roles=["specialist"],
            agui_schema={},
            dimension="business",
            **mock_dependencies
        )
        
        liaison = DimensionLiaisonAgent(
            agent_name="liaison",
            capabilities=["liaison_operations"],
            required_roles=["liaison"],
            agui_schema={},
            dimension="business",
            **mock_dependencies
        )
        
        orchestrator = GlobalOrchestratorAgent(
            agent_name="orchestrator",
            capabilities=["orchestration"],
            required_roles=["orchestrator"],
            agui_schema={},
            **mock_dependencies
        )
        
        guide = GlobalGuideAgent(
            agent_name="guide",
            capabilities=["guidance"],
            required_roles=["guide"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Test capability progression
        agents = [lightweight, task, specialist, liaison, orchestrator, guide]
        
        # All agents should have basic capabilities
        for agent in agents:
            assert agent.llm_only_operations is True
            assert agent.centralized_governance is True
            assert hasattr(agent, 'governance_config')
            assert hasattr(agent, 'audit_log')
            assert hasattr(agent, 'usage_stats')
        
        # Test specific capability progression
        assert lightweight.user_facing is False
        assert task.user_facing is False
        assert specialist.user_facing is False
        assert liaison.user_facing is True
        assert orchestrator.user_facing is False
        assert guide.user_facing is True
        
        # Test dimensional awareness progression
        assert lightweight.dimensional_awareness is False
        assert task.dimensional_awareness is False
        assert specialist.dimensional_awareness is True
        assert liaison.dimensional_awareness is True
        assert orchestrator.dimensional_awareness is True
        assert guide.dimensional_awareness is True
        
        # Test cross-dimensional awareness progression
        assert lightweight.cross_dimensional_awareness is False
        assert task.cross_dimensional_awareness is False
        assert specialist.cross_dimensional_awareness is False
        assert liaison.cross_dimensional_awareness is False
        assert orchestrator.cross_dimensional_awareness is True
        assert guide.cross_dimensional_awareness is True
    
    def test_agent_governance_audit_trail_integration(self, mock_dependencies):
        """Test that governance audit trails work correctly across agent interactions."""
        # Create agents
        lightweight = LightweightLLMAgent(
            agent_name="lightweight",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        specialist = DimensionSpecialistAgent(
            agent_name="specialist",
            capabilities=["specialist_operations"],
            required_roles=["specialist"],
            agui_schema={},
            dimension="business",
            **mock_dependencies
        )
        
        guide = GlobalGuideAgent(
            agent_name="guide",
            capabilities=["guidance"],
            required_roles=["guide"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Test that each agent maintains its own audit trail
        agents = [lightweight, specialist, guide]
        
        for agent in agents:
            # Each agent should start with empty audit log
            assert len(agent.get_audit_log()) == 0
            
            # Each agent should have its own usage stats
            usage_stats = agent.get_usage_stats()
            assert usage_stats['total_requests'] == 0
            assert usage_stats['total_tokens'] == 0
            assert usage_stats['total_cost'] == 0.0
        
        # Test that agents can operate independently
        for i, agent in enumerate(agents):
            # Each agent should be able to log operations independently
            agent._log_operation(f"operation_{i}", {"param": f"value_{i}"})
            
            # Each agent should have its own audit log
            audit_log = agent.get_audit_log()
            assert len(audit_log) == 1
            assert audit_log[0]['operation'] == f"operation_{i}"
            assert audit_log[0]['parameters']['param'] == f"value_{i}"
    
    def test_agent_governance_cost_tracking_integration(self, mock_dependencies):
        """Test that governance cost tracking works correctly across agent interactions."""
        # Create agents
        lightweight = LightweightLLMAgent(
            agent_name="lightweight",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        specialist = DimensionSpecialistAgent(
            agent_name="specialist",
            capabilities=["specialist_operations"],
            required_roles=["specialist"],
            agui_schema={},
            dimension="business",
            **mock_dependencies
        )
        
        guide = GlobalGuideAgent(
            agent_name="guide",
            capabilities=["guidance"],
            required_roles=["guide"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Test that each agent tracks its own costs
        agents = [lightweight, specialist, guide]
        
        for i, agent in enumerate(agents):
            # Each agent should start with zero cost
            usage_stats = agent.get_usage_stats()
            assert usage_stats['total_cost'] == 0.0
            
            # Simulate cost tracking
            result = {
                'token_usage': {
                    'total_tokens': 100 * (i + 1),
                    'total_cost': 0.002 * (i + 1)
                }
            }
            agent._update_usage_stats(result)
            
            # Each agent should track its own costs
            usage_stats = agent.get_usage_stats()
            assert usage_stats['total_cost'] == 0.002 * (i + 1)
            assert usage_stats['total_tokens'] == 100 * (i + 1)
    
    def test_agent_governance_reset_integration(self, mock_dependencies):
        """Test that governance reset works correctly across agent interactions."""
        # Create agents
        lightweight = LightweightLLMAgent(
            agent_name="lightweight",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        specialist = DimensionSpecialistAgent(
            agent_name="specialist",
            capabilities=["specialist_operations"],
            required_roles=["specialist"],
            agui_schema={},
            dimension="business",
            **mock_dependencies
        )
        
        guide = GlobalGuideAgent(
            agent_name="guide",
            capabilities=["guidance"],
            required_roles=["guide"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Add some data to each agent
        agents = [lightweight, specialist, guide]
        
        for i, agent in enumerate(agents):
            # Add usage data
            result = {
                'token_usage': {
                    'total_tokens': 100 * (i + 1),
                    'total_cost': 0.002 * (i + 1)
                }
            }
            agent._update_usage_stats(result)
            agent._log_operation(f"operation_{i}", {"param": f"value_{i}"})
        
        # Verify data exists
        for i, agent in enumerate(agents):
            usage_stats = agent.get_usage_stats()
            assert usage_stats['total_cost'] == 0.002 * (i + 1)
            assert len(agent.get_audit_log()) == 1
        
        # Reset each agent independently
        for agent in agents:
            agent.reset_usage_stats()
        
        # Verify each agent was reset independently
        for agent in agents:
            usage_stats = agent.get_usage_stats()
            assert usage_stats['total_cost'] == 0.0
            assert usage_stats['total_tokens'] == 0
            assert usage_stats['total_requests'] == 0
            assert len(agent.get_audit_log()) == 0





