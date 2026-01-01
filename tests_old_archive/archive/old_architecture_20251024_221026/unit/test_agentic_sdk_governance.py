#!/usr/bin/env python3
"""
Unit Tests: Agentic SDK Enhanced Governance Features

Tests the enhanced governance features including rate limiting, cost tracking,
audit logging, and usage monitoring across all agent types.

WHAT (Test Role): I validate the enhanced governance capabilities
HOW (Test Implementation): I test governance features across the agent hierarchy
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


class TestAgenticSDKGovernance:
    """Test the enhanced governance features across all agent types."""
    
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
    
    def test_governance_initialization(self, mock_dependencies):
        """Test that governance is properly initialized for all agent types."""
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
            # Test governance configuration
            assert hasattr(agent, 'governance_config')
            assert agent.governance_config['rate_limiting'] is True
            assert agent.governance_config['cost_tracking'] is True
            assert agent.governance_config['audit_logging'] is True
            assert agent.governance_config['usage_monitoring'] is True
            
            # Test audit log initialization
            assert hasattr(agent, 'audit_log')
            assert isinstance(agent.audit_log, list)
            assert len(agent.audit_log) == 0
            
            # Test usage stats initialization
            assert hasattr(agent, 'usage_stats')
            assert agent.usage_stats['total_requests'] == 0
            assert agent.usage_stats['total_tokens'] == 0
            assert agent.usage_stats['total_cost'] == 0.0
            assert agent.usage_stats['last_request'] is None
    
    def test_audit_logging_functionality(self, mock_dependencies):
        """Test audit logging functionality across agent types."""
        agent = LightweightLLMAgent(
            agent_name="test_agent",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Test initial audit log state
        assert len(agent.audit_log) == 0
        
        # Test logging an operation
        agent._log_operation("test_operation", {"param1": "value1", "param2": "value2"})
        
        # Verify audit log entry
        assert len(agent.audit_log) == 1
        log_entry = agent.audit_log[0]
        
        assert 'timestamp' in log_entry
        assert 'agent_name' in log_entry
        assert 'operation' in log_entry
        assert 'parameters' in log_entry
        
        assert log_entry['agent_name'] == "test_agent"
        assert log_entry['operation'] == "test_operation"
        assert log_entry['parameters'] == {"param1": "value1", "param2": "value2"}
        
        # Test multiple operations
        agent._log_operation("operation2", {"param3": "value3"})
        agent._log_operation("operation3", {"param4": "value4"})
        
        assert len(agent.audit_log) == 3
        
        # Test getting audit log
        audit_log = agent.get_audit_log()
        assert isinstance(audit_log, list)
        assert len(audit_log) == 3
        
        # Test audit log is a copy (not reference)
        audit_log.append("test")
        assert len(agent.audit_log) == 3  # Original should be unchanged
    
    def test_usage_statistics_tracking(self, mock_dependencies):
        """Test usage statistics tracking functionality."""
        agent = LightweightLLMAgent(
            agent_name="test_agent",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Test initial usage stats
        usage_stats = agent.get_usage_stats()
        assert usage_stats['total_requests'] == 0
        assert usage_stats['total_tokens'] == 0
        assert usage_stats['total_cost'] == 0.0
        assert usage_stats['last_request'] is None
        
        # Test updating usage stats
        result = {
            'token_usage': {
                'total_tokens': 150,
                'total_cost': 0.003
            }
        }
        agent._update_usage_stats(result)
        
        # Verify usage stats update
        usage_stats = agent.get_usage_stats()
        assert usage_stats['total_requests'] == 1
        assert usage_stats['total_tokens'] == 150
        assert usage_stats['total_cost'] == 0.003
        assert usage_stats['last_request'] is not None
        
        # Test multiple updates
        result2 = {
            'token_usage': {
                'total_tokens': 200,
                'total_cost': 0.004
            }
        }
        agent._update_usage_stats(result2)
        
        usage_stats = agent.get_usage_stats()
        assert usage_stats['total_requests'] == 2
        assert usage_stats['total_tokens'] == 350  # 150 + 200
        assert usage_stats['total_cost'] == 0.007  # 0.003 + 0.004
    
    def test_usage_statistics_reset(self, mock_dependencies):
        """Test usage statistics reset functionality."""
        agent = LightweightLLMAgent(
            agent_name="test_agent",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Add some usage data
        result = {
            'token_usage': {
                'total_tokens': 100,
                'total_cost': 0.002
            }
        }
        agent._update_usage_stats(result)
        agent._log_operation("test_operation", {"param": "value"})
        
        # Verify data exists
        assert agent.get_usage_stats()['total_requests'] == 1
        assert len(agent.get_audit_log()) == 1
        
        # Reset usage statistics
        agent.reset_usage_stats()
        
        # Verify reset
        usage_stats = agent.get_usage_stats()
        assert usage_stats['total_requests'] == 0
        assert usage_stats['total_tokens'] == 0
        assert usage_stats['total_cost'] == 0.0
        assert usage_stats['last_request'] is None
        
        # Verify audit log is also reset
        assert len(agent.get_audit_log()) == 0
    
    def test_rate_limiting_check(self, mock_dependencies):
        """Test rate limiting check functionality."""
        agent = LightweightLLMAgent(
            agent_name="test_agent",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Test rate limiting check (should not raise exception)
        agent._check_rate_limiting()
        
        # Test with rate limiting disabled
        agent.governance_config['rate_limiting'] = False
        agent._check_rate_limiting()  # Should still not raise exception
    
    def test_governance_configuration_consistency(self, mock_dependencies):
        """Test that governance configuration is consistent across all agent types."""
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
            # All agents should have the same governance configuration
            assert agent.governance_config['rate_limiting'] is True
            assert agent.governance_config['cost_tracking'] is True
            assert agent.governance_config['audit_logging'] is True
            assert agent.governance_config['usage_monitoring'] is True
            
            # All agents should have the same governance methods
            assert hasattr(agent, '_initialize_governance')
            assert hasattr(agent, '_log_operation')
            assert hasattr(agent, '_update_usage_stats')
            assert hasattr(agent, '_check_rate_limiting')
            assert hasattr(agent, 'get_usage_stats')
            assert hasattr(agent, 'get_audit_log')
            assert hasattr(agent, 'reset_usage_stats')
    
    def test_governance_during_operation_execution(self, mock_dependencies):
        """Test that governance is properly applied during operation execution."""
        agent = LightweightLLMAgent(
            agent_name="test_agent",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Mock the operation to return a result with token usage
        def mock_operation(**kwargs):
            return {
                'result': 'test_result',
                'token_usage': {
                    'total_tokens': 100,
                    'total_cost': 0.002
                }
            }
        
        # Add the mock operation to the agent
        agent.llm_operations['test_operation'] = mock_operation
        
        # Test operation execution with governance
        result = agent.execute_llm_operation('test_operation', param1='value1')
        
        # Verify result
        assert result['result'] == 'test_result'
        assert result['token_usage']['total_tokens'] == 100
        
        # Verify governance was applied
        usage_stats = agent.get_usage_stats()
        assert usage_stats['total_requests'] == 1
        assert usage_stats['total_tokens'] == 100
        assert usage_stats['total_cost'] == 0.002
        
        # Verify audit logging
        audit_log = agent.get_audit_log()
        assert len(audit_log) == 1
        assert audit_log[0]['operation'] == 'test_operation'
        assert audit_log[0]['parameters']['param1'] == 'value1'
    
    def test_governance_with_disabled_features(self, mock_dependencies):
        """Test governance behavior when features are disabled."""
        agent = LightweightLLMAgent(
            agent_name="test_agent",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Disable audit logging
        agent.governance_config['audit_logging'] = False
        
        # Mock the operation
        def mock_operation(**kwargs):
            return {'result': 'test_result'}
        
        agent.llm_operations['test_operation'] = mock_operation
        
        # Execute operation
        result = agent.execute_llm_operation('test_operation', param1='value1')
        
        # Verify result
        assert result['result'] == 'test_result'
        
        # Verify no audit logging occurred
        assert len(agent.get_audit_log()) == 0
        
        # Disable rate limiting
        agent.governance_config['rate_limiting'] = False
        
        # Should still work without rate limiting
        result = agent.execute_llm_operation('test_operation', param2='value2')
        assert result['result'] == 'test_result'
    
    def test_governance_error_handling(self, mock_dependencies):
        """Test governance error handling."""
        agent = LightweightLLMAgent(
            agent_name="test_agent",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Test with operation that raises exception
        def failing_operation(**kwargs):
            raise ValueError("Test error")
        
        agent.llm_operations['failing_operation'] = failing_operation
        
        # Execute should raise the exception
        with pytest.raises(ValueError, match="Test error"):
            agent.execute_llm_operation('failing_operation', param1='value1')
        
        # Verify no usage stats were updated
        usage_stats = agent.get_usage_stats()
        assert usage_stats['total_requests'] == 0
        assert usage_stats['total_tokens'] == 0
        assert usage_stats['total_cost'] == 0.0
        
        # Verify no audit logging occurred
        assert len(agent.get_audit_log()) == 0
    
    def test_governance_concurrent_operations(self, mock_dependencies):
        """Test governance with concurrent operations."""
        agent = LightweightLLMAgent(
            agent_name="test_agent",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Mock operation
        def mock_operation(**kwargs):
            return {
                'result': f"result_{kwargs.get('param', 'default')}",
                'token_usage': {
                    'total_tokens': 50,
                    'total_cost': 0.001
                }
            }
        
        agent.llm_operations['test_operation'] = mock_operation
        
        # Test concurrent operations
        import threading
        import time
        
        results = []
        
        def worker(worker_id):
            result = agent.execute_llm_operation('test_operation', param=f"worker_{worker_id}")
            results.append(result)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all operations completed
        assert len(results) == 5
        
        # Verify usage stats were updated correctly
        usage_stats = agent.get_usage_stats()
        assert usage_stats['total_requests'] == 5
        assert usage_stats['total_tokens'] == 250  # 5 * 50
        assert usage_stats['total_cost'] == 0.005  # 5 * 0.001
        
        # Verify audit logging
        audit_log = agent.get_audit_log()
        assert len(audit_log) == 5
        
        # Verify all worker parameters were logged
        logged_params = [entry['parameters']['param'] for entry in audit_log]
        for i in range(5):
            assert f"worker_{i}" in logged_params





