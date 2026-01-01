#!/usr/bin/env python3
"""
Unit Tests: Agentic SDK Hierarchical Agent Structure

Tests the new hierarchical agent classes and their capabilities.
This test suite ensures the hierarchical agent system works correctly.

WHAT (Test Role): I validate the hierarchical agent structure and capabilities
HOW (Test Implementation): I test each agent level with proper governance integration
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
from agentic.agui_schema_registry import AGUISchema, AGUIComponent


class TestAgenticSDKHierarchy:
    """Test the hierarchical agent structure and capabilities."""
    
    def _create_test_agui_schema(self, agent_name: str) -> AGUISchema:
        """Create a valid AGUISchema for testing."""
        return AGUISchema(
            agent_name=agent_name,
            version="1.0.0",
            description=f"Test {agent_name} for validation",
            components=[
                AGUIComponent(
                    type="message_card",
                    title="Test Component",
                    description="A test component",
                    required=True,
                    properties={
                        "message": "Test message"
                    }
                )
            ]
        )
    
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
        public_works_foundation = Mock()
        public_works_foundation.get_all_business_abstractions.return_value = {}
        public_works_foundation.get_llm_business_abstraction.return_value = Mock()
        
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
    
    def test_lightweight_llm_agent_initialization(self, mock_dependencies):
        """Test LightweightLLMAgent initialization and basic capabilities."""
        test_schema = self._create_test_agui_schema("test_lightweight_agent")
        
        agent = LightweightLLMAgent(
            agent_name="test_lightweight_agent",
            capabilities=["llm_operations", "mcp_tools"],
            required_roles=["data_analyst"],
            agui_schema=test_schema,
            foundation_services=mock_dependencies['di_container'],
            public_works_foundation=mock_dependencies['public_works_foundation'],
            mcp_client_manager=mock_dependencies['mcp_client_manager'],
            policy_integration=mock_dependencies['policy_integration'],
            tool_composition=mock_dependencies['tool_composition'],
            agui_formatter=mock_dependencies['agui_formatter']
        )
        
        # Test basic properties
        assert agent.agent_name == "test_lightweight_agent"
        assert agent.llm_only_operations is True
        assert agent.mcp_tools_integration is True
        assert agent.agui_integration is True
        assert agent.centralized_governance is True
        assert agent.user_facing is False
        
        # Test governance initialization
        assert hasattr(agent, 'governance_config')
        assert agent.governance_config['rate_limiting'] is True
        assert agent.governance_config['cost_tracking'] is True
        assert agent.governance_config['audit_logging'] is True
        assert agent.governance_config['usage_monitoring'] is True
        
        # Test audit and usage tracking
        assert hasattr(agent, 'audit_log')
        assert hasattr(agent, 'usage_stats')
        assert agent.usage_stats['total_requests'] == 0
        assert agent.usage_stats['total_tokens'] == 0
        assert agent.usage_stats['total_cost'] == 0.0
    
    def test_task_llm_agent_initialization(self, mock_dependencies):
        """Test TaskLLMAgent initialization and task-specific capabilities."""
        test_schema = self._create_test_agui_schema("test_task_agent")
        
        agent = TaskLLMAgent(
            agent_name="test_task_agent",
            capabilities=["task_operations", "llm_operations"],
            required_roles=["task_executor"],
            agui_schema=test_schema,
            foundation_services=mock_dependencies['di_container'],
            public_works_foundation=mock_dependencies['public_works_foundation'],
            mcp_client_manager=mock_dependencies['mcp_client_manager'],
            policy_integration=mock_dependencies['policy_integration'],
            tool_composition=mock_dependencies['tool_composition'],
            agui_formatter=mock_dependencies['agui_formatter'],
            task_type="data_analysis"
        )
        
        # Test basic properties
        assert agent.agent_name == "test_task_agent"
        assert agent.task_type == "data_analysis"
        assert agent.task_oriented is True
        assert agent.centralized_governance is True
        assert agent.user_facing is False
        
        # Test task-specific capabilities
        assert hasattr(agent, 'task_operations')
        assert isinstance(agent.task_operations, dict)
    
    def test_dimension_specialist_agent_initialization(self, mock_dependencies):
        """Test DimensionSpecialistAgent initialization and dimensional capabilities."""
        agent = DimensionSpecialistAgent(
            agent_name="test_specialist_agent",
            capabilities=["specialist_operations", "dimensional_awareness"],
            required_roles=["business_analyst"],
            agui_schema=self._create_test_agui_schema("test_specialist_agent"),
            foundation_services=mock_dependencies['di_container'],
            public_works_foundation=mock_dependencies['public_works_foundation'],
            mcp_client_manager=mock_dependencies['mcp_client_manager'],
            policy_integration=mock_dependencies['policy_integration'],
            tool_composition=mock_dependencies['tool_composition'],
            agui_formatter=mock_dependencies['agui_formatter'],
            dimension="business_enablement"
        )
        
        # Test basic properties
        assert agent.agent_name == "test_specialist_agent"
        assert agent.dimension == "business_enablement"
        assert agent.dimensional_awareness is True
        assert agent.state_awareness is True
        assert agent.tool_usage is True
        assert agent.centralized_governance is True
        assert agent.user_facing is False
        
        # Test specialist capabilities
        assert hasattr(agent, 'specialist_operations')
        assert isinstance(agent.specialist_operations, dict)
    
    def test_dimension_liaison_agent_initialization(self, mock_dependencies):
        """Test DimensionLiaisonAgent initialization and liaison capabilities."""
        agent = DimensionLiaisonAgent(
            agent_name="test_liaison_agent",
            capabilities=["liaison_operations", "user_interactivity"],
            required_roles=["business_liaison"],
            agui_schema=self._create_test_agui_schema("test_specialist_agent"),
            foundation_services=mock_dependencies['di_container'],
            public_works_foundation=mock_dependencies['public_works_foundation'],
            mcp_client_manager=mock_dependencies['mcp_client_manager'],
            policy_integration=mock_dependencies['policy_integration'],
            tool_composition=mock_dependencies['tool_composition'],
            agui_formatter=mock_dependencies['agui_formatter'],
            dimension="business_enablement"
        )
        
        # Test basic properties
        assert agent.agent_name == "test_liaison_agent"
        assert agent.dimension == "business_enablement"
        assert agent.liaison_capabilities is True
        assert agent.user_interactivity is True
        assert agent.user_facing is True
        
        # Test liaison capabilities
        assert hasattr(agent, 'liaison_operations')
        assert isinstance(agent.liaison_operations, dict)
    
    def test_global_orchestrator_agent_initialization(self, mock_dependencies):
        """Test GlobalOrchestratorAgent initialization and orchestrator capabilities."""
        agent = GlobalOrchestratorAgent(
            agent_name="test_orchestrator_agent",
            capabilities=["orchestration", "cross_dimensional_awareness"],
            required_roles=["platform_orchestrator"],
            agui_schema=self._create_test_agui_schema("test_specialist_agent"),
            foundation_services=mock_dependencies['di_container'],
            public_works_foundation=mock_dependencies['public_works_foundation'],
            mcp_client_manager=mock_dependencies['mcp_client_manager'],
            policy_integration=mock_dependencies['policy_integration'],
            tool_composition=mock_dependencies['tool_composition'],
            agui_formatter=mock_dependencies['agui_formatter']
        )
        
        # Test basic properties
        assert agent.agent_name == "test_orchestrator_agent"
        assert agent.cross_dimensional_awareness is True
        assert agent.platform_context is True
        assert agent.strategic_coordination is True
        assert agent.centralized_governance is True
        assert agent.user_facing is False
        
        # Test orchestrator capabilities
        assert hasattr(agent, 'orchestrator_operations')
        assert isinstance(agent.orchestrator_operations, dict)
    
    def test_global_guide_agent_initialization(self, mock_dependencies):
        """Test GlobalGuideAgent initialization and guide capabilities."""
        agent = GlobalGuideAgent(
            agent_name="test_guide_agent",
            capabilities=["guidance", "user_interactivity", "cross_dimensional_awareness"],
            required_roles=["platform_guide"],
            agui_schema=self._create_test_agui_schema("test_specialist_agent"),
            foundation_services=mock_dependencies['di_container'],
            public_works_foundation=mock_dependencies['public_works_foundation'],
            mcp_client_manager=mock_dependencies['mcp_client_manager'],
            policy_integration=mock_dependencies['policy_integration'],
            tool_composition=mock_dependencies['tool_composition'],
            agui_formatter=mock_dependencies['agui_formatter']
        )
        
        # Test basic properties
        assert agent.agent_name == "test_guide_agent"
        assert agent.guide_capabilities is True
        assert agent.user_interactivity is True
        assert agent.cross_dimensional_awareness is True
        assert agent.platform_context is True
        assert agent.user_facing is True
        
        # Test guide capabilities
        assert hasattr(agent, 'guide_operations')
        assert isinstance(agent.guide_operations, dict)
    
    def test_agent_hierarchy_inheritance(self, mock_dependencies):
        """Test that agent hierarchy properly inherits capabilities."""
        # Test LightweightLLMAgent (base level)
        lightweight = LightweightLLMAgent(
            agent_name="lightweight",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        assert lightweight.llm_only_operations is True
        assert lightweight.centralized_governance is True
        
        # Test TaskLLMAgent (inherits from LightweightLLMAgent)
        task = TaskLLMAgent(
            agent_name="task",
            capabilities=["task_operations"],
            required_roles=["executor"],
            agui_schema={},
            task_type="analysis",
            **mock_dependencies
        )
        assert task.llm_only_operations is True  # Inherited
        assert task.task_oriented is True  # New capability
        assert task.centralized_governance is True  # Inherited
        
        # Test DimensionSpecialistAgent (inherits from LightweightLLMAgent)
        specialist = DimensionSpecialistAgent(
            agent_name="specialist",
            capabilities=["specialist_operations"],
            required_roles=["specialist"],
            agui_schema={},
            dimension="business",
            **mock_dependencies
        )
        assert specialist.llm_only_operations is True  # Inherited
        assert specialist.dimensional_awareness is True  # New capability
        assert specialist.centralized_governance is True  # Inherited
        
        # Test DimensionLiaisonAgent (inherits from DimensionSpecialistAgent)
        liaison = DimensionLiaisonAgent(
            agent_name="liaison",
            capabilities=["liaison_operations"],
            required_roles=["liaison"],
            agui_schema={},
            dimension="business",
            **mock_dependencies
        )
        assert liaison.llm_only_operations is True  # Inherited
        assert liaison.dimensional_awareness is True  # Inherited
        assert liaison.liaison_capabilities is True  # New capability
        assert liaison.user_facing is True  # New capability
        
        # Test GlobalOrchestratorAgent (inherits from DimensionSpecialistAgent)
        orchestrator = GlobalOrchestratorAgent(
            agent_name="orchestrator",
            capabilities=["orchestration"],
            required_roles=["orchestrator"],
            agui_schema={},
            **mock_dependencies
        )
        assert orchestrator.llm_only_operations is True  # Inherited
        assert orchestrator.dimensional_awareness is True  # Inherited
        assert orchestrator.cross_dimensional_awareness is True  # New capability
        
        # Test GlobalGuideAgent (inherits from GlobalOrchestratorAgent)
        guide = GlobalGuideAgent(
            agent_name="guide",
            capabilities=["guidance"],
            required_roles=["guide"],
            agui_schema={},
            **mock_dependencies
        )
        assert guide.llm_only_operations is True  # Inherited
        assert guide.dimensional_awareness is True  # Inherited
        assert guide.cross_dimensional_awareness is True  # Inherited
        assert guide.guide_capabilities is True  # New capability
        assert guide.user_facing is True  # New capability
    
    def test_agent_capability_progression(self, mock_dependencies):
        """Test that agent capabilities progress correctly through the hierarchy."""
        # Simple Level: LightweightLLMAgent
        lightweight = LightweightLLMAgent(
            agent_name="lightweight",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        assert lightweight.llm_only_operations is True
        assert lightweight.user_facing is False
        
        # Simple Level: TaskLLMAgent
        task = TaskLLMAgent(
            agent_name="task",
            capabilities=["task_operations"],
            required_roles=["executor"],
            agui_schema={},
            task_type="analysis",
            **mock_dependencies
        )
        assert task.llm_only_operations is True
        assert task.task_oriented is True
        assert task.user_facing is False
        
        # Dimensional Level: DimensionSpecialistAgent
        specialist = DimensionSpecialistAgent(
            agent_name="specialist",
            capabilities=["specialist_operations"],
            required_roles=["specialist"],
            agui_schema={},
            dimension="business",
            **mock_dependencies
        )
        assert specialist.llm_only_operations is True
        assert specialist.dimensional_awareness is True
        assert specialist.state_awareness is True
        assert specialist.user_facing is False
        
        # Dimensional Level: DimensionLiaisonAgent
        liaison = DimensionLiaisonAgent(
            agent_name="liaison",
            capabilities=["liaison_operations"],
            required_roles=["liaison"],
            agui_schema={},
            dimension="business",
            **mock_dependencies
        )
        assert liaison.llm_only_operations is True
        assert liaison.dimensional_awareness is True
        assert liaison.liaison_capabilities is True
        assert liaison.user_facing is True
        
        # Global Level: GlobalOrchestratorAgent
        orchestrator = GlobalOrchestratorAgent(
            agent_name="orchestrator",
            capabilities=["orchestration"],
            required_roles=["orchestrator"],
            agui_schema={},
            **mock_dependencies
        )
        assert orchestrator.llm_only_operations is True
        assert orchestrator.dimensional_awareness is True
        assert orchestrator.cross_dimensional_awareness is True
        assert orchestrator.platform_context is True
        assert orchestrator.user_facing is False
        
        # Global Level: GlobalGuideAgent
        guide = GlobalGuideAgent(
            agent_name="guide",
            capabilities=["guidance"],
            required_roles=["guide"],
            agui_schema={},
            **mock_dependencies
        )
        assert guide.llm_only_operations is True
        assert guide.dimensional_awareness is True
        assert guide.cross_dimensional_awareness is True
        assert guide.guide_capabilities is True
        assert guide.user_facing is True
    
    def test_agent_governance_consistency(self, mock_dependencies):
        """Test that all agents have consistent governance capabilities."""
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
        
        for agent in agents:
            # All agents should have centralized governance
            assert agent.centralized_governance is True
            
            # All agents should have governance configuration
            assert hasattr(agent, 'governance_config')
            assert agent.governance_config['rate_limiting'] is True
            assert agent.governance_config['cost_tracking'] is True
            assert agent.governance_config['audit_logging'] is True
            assert agent.governance_config['usage_monitoring'] is True
            
            # All agents should have audit and usage tracking
            assert hasattr(agent, 'audit_log')
            assert hasattr(agent, 'usage_stats')
            assert agent.usage_stats['total_requests'] == 0
            assert agent.usage_stats['total_tokens'] == 0
            assert agent.usage_stats['total_cost'] == 0.0
            
            # All agents should have governance methods
            assert hasattr(agent, 'get_usage_stats')
            assert hasattr(agent, 'get_audit_log')
            assert hasattr(agent, 'reset_usage_stats')
    
    def test_agent_info_consistency(self, mock_dependencies):
        """Test that all agents provide consistent agent information."""
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
        
        for agent in agents:
            agent_info = agent.get_agent_info()
            
            # All agents should provide consistent agent information
            assert 'agent_name' in agent_info
            assert 'capabilities' in agent_info
            assert 'required_roles' in agent_info
            assert 'centralized_governance' in agent_info
            assert 'user_facing' in agent_info
            assert 'available_operations' in agent_info
            assert 'usage_stats' in agent_info
            
            # Agent name should match
            assert agent_info['agent_name'] == agent.agent_name
            
            # Governance should be consistent
            assert agent_info['centralized_governance'] is True
            
            # Usage stats should be available
            assert isinstance(agent_info['usage_stats'], dict)
            assert 'total_requests' in agent_info['usage_stats']
            assert 'total_tokens' in agent_info['usage_stats']
            assert 'total_cost' in agent_info['usage_stats']
