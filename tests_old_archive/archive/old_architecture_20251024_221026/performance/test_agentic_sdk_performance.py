#!/usr/bin/env python3
"""
Performance Tests: Agentic SDK Governance Overhead and Agent Scalability

Tests the performance characteristics of the hierarchical agent system,
including governance overhead, scalability, and resource usage.

WHAT (Test Role): I validate agent performance and scalability characteristics
HOW (Test Implementation): I test performance metrics and resource usage patterns
"""

import pytest
import sys
import os
import time
import threading
import asyncio
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from typing import Dict, Any, List
import psutil
import gc

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


class TestAgenticSDKPerformance:
    """Test the performance characteristics of the Agentic SDK."""
    
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
    
    def test_agent_initialization_performance(self, mock_dependencies):
        """Test agent initialization performance."""
        # Test initialization time for each agent type
        agent_types = [
            (LightweightLLMAgent, {"agent_name": "lightweight", "capabilities": ["llm_operations"], "required_roles": ["analyst"], "agui_schema": {}}),
            (TaskLLMAgent, {"agent_name": "task", "capabilities": ["task_operations"], "required_roles": ["executor"], "agui_schema": {}, "task_type": "analysis"}),
            (DimensionSpecialistAgent, {"agent_name": "specialist", "capabilities": ["specialist_operations"], "required_roles": ["specialist"], "agui_schema": {}, "dimension": "business"}),
            (DimensionLiaisonAgent, {"agent_name": "liaison", "capabilities": ["liaison_operations"], "required_roles": ["liaison"], "agui_schema": {}, "dimension": "business"}),
            (GlobalOrchestratorAgent, {"agent_name": "orchestrator", "capabilities": ["orchestration"], "required_roles": ["orchestrator"], "agui_schema": {}}),
            (GlobalGuideAgent, {"agent_name": "guide", "capabilities": ["guidance"], "required_roles": ["guide"], "agui_schema": {}})
        ]
        
        for agent_class, kwargs in agent_types:
            start_time = time.time()
            agent = agent_class(**kwargs, **mock_dependencies)
            end_time = time.time()
            
            initialization_time = end_time - start_time
            
            # Initialization should be fast (less than 0.1 seconds)
            assert initialization_time < 0.1, f"{agent_class.__name__} initialization took {initialization_time:.3f}s"
            assert agent is not None
    
    def test_agent_memory_usage(self, mock_dependencies):
        """Test agent memory usage characteristics."""
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create multiple agents
        agents = []
        for i in range(10):
            agent = LightweightLLMAgent(
                agent_name=f"agent_{i}",
                capabilities=["llm_operations"],
                required_roles=["analyst"],
                agui_schema={},
                **mock_dependencies
            )
            agents.append(agent)
        
        # Get memory usage after creating agents
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 10MB for 10 agents)
        assert memory_increase < 10 * 1024 * 1024, f"Memory usage increased by {memory_increase / 1024 / 1024:.2f}MB"
        
        # Each agent should use reasonable memory
        memory_per_agent = memory_increase / len(agents)
        assert memory_per_agent < 1024 * 1024, f"Each agent uses {memory_per_agent / 1024:.2f}KB"
    
    def test_governance_overhead_performance(self, mock_dependencies):
        """Test governance overhead performance."""
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
                'result': 'test_result',
                'token_usage': {
                    'total_tokens': 100,
                    'total_cost': 0.002
                }
            }
        
        agent.llm_operations['test_operation'] = mock_operation
        
        # Test operation execution time with governance
        start_time = time.time()
        for _ in range(100):
            agent.execute_llm_operation('test_operation', param='value')
        end_time = time.time()
        
        execution_time = end_time - start_time
        avg_time_per_operation = execution_time / 100
        
        # Average operation time should be reasonable (less than 0.01 seconds)
        assert avg_time_per_operation < 0.01, f"Average operation time: {avg_time_per_operation:.4f}s"
        
        # Verify governance was applied
        usage_stats = agent.get_usage_stats()
        assert usage_stats['total_requests'] == 100
        assert usage_stats['total_tokens'] == 10000  # 100 * 100
        assert usage_stats['total_cost'] == 0.2  # 100 * 0.002
        
        # Verify audit logging
        audit_log = agent.get_audit_log()
        assert len(audit_log) == 100
    
    def test_concurrent_agent_performance(self, mock_dependencies):
        """Test performance with concurrent agent operations."""
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
                'result': 'test_result',
                'token_usage': {
                    'total_tokens': 50,
                    'total_cost': 0.001
                }
            }
        
        agent.llm_operations['test_operation'] = mock_operation
        
        # Test concurrent operations
        results = []
        start_time = time.time()
        
        def worker(worker_id):
            result = agent.execute_llm_operation('test_operation', param=f'worker_{worker_id}')
            results.append(result)
        
        # Create multiple threads
        threads = []
        for i in range(20):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # All operations should complete
        assert len(results) == 20
        
        # Execution time should be reasonable (less than 1 second for 20 concurrent operations)
        assert execution_time < 1.0, f"Concurrent execution took {execution_time:.3f}s"
        
        # Verify governance was applied correctly
        usage_stats = agent.get_usage_stats()
        assert usage_stats['total_requests'] == 20
        assert usage_stats['total_tokens'] == 1000  # 20 * 50
        assert usage_stats['total_cost'] == 0.02  # 20 * 0.001
    
    def test_agent_scalability(self, mock_dependencies):
        """Test agent scalability with increasing numbers of agents."""
        # Test with different numbers of agents
        agent_counts = [1, 5, 10, 20]
        
        for count in agent_counts:
            start_time = time.time()
            
            # Create agents
            agents = []
            for i in range(count):
                agent = LightweightLLMAgent(
                    agent_name=f"agent_{i}",
                    capabilities=["llm_operations"],
                    required_roles=["analyst"],
                    agui_schema={},
                    **mock_dependencies
                )
                agents.append(agent)
            
            # Test agent operations
            for agent in agents:
                agent._log_operation(f"operation_{count}", {"param": "value"})
                agent._update_usage_stats({
                    'token_usage': {
                        'total_tokens': 100,
                        'total_cost': 0.002
                    }
                })
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Execution time should scale reasonably
            assert execution_time < count * 0.1, f"Execution time for {count} agents: {execution_time:.3f}s"
            
            # Verify all agents work correctly
            for agent in agents:
                assert len(agent.get_audit_log()) == 1
                usage_stats = agent.get_usage_stats()
                assert usage_stats['total_requests'] == 1
                assert usage_stats['total_tokens'] == 100
                assert usage_stats['total_cost'] == 0.002
    
    def test_governance_memory_usage(self, mock_dependencies):
        """Test governance memory usage characteristics."""
        agent = LightweightLLMAgent(
            agent_name="test_agent",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Add many operations to test memory usage
        for i in range(1000):
            agent._log_operation(f"operation_{i}", {"param": f"value_{i}"})
            agent._update_usage_stats({
                'token_usage': {
                    'total_tokens': 100,
                    'total_cost': 0.002
                }
            })
        
        # Get memory usage after operations
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 5MB for 1000 operations)
        assert memory_increase < 5 * 1024 * 1024, f"Memory usage increased by {memory_increase / 1024 / 1024:.2f}MB"
        
        # Verify data integrity
        audit_log = agent.get_audit_log()
        assert len(audit_log) == 1000
        
        usage_stats = agent.get_usage_stats()
        assert usage_stats['total_requests'] == 1000
        assert usage_stats['total_tokens'] == 100000  # 1000 * 100
        assert usage_stats['total_cost'] == 2.0  # 1000 * 0.002
    
    def test_governance_reset_performance(self, mock_dependencies):
        """Test governance reset performance."""
        agent = LightweightLLMAgent(
            agent_name="test_agent",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Add data
        for i in range(1000):
            agent._log_operation(f"operation_{i}", {"param": f"value_{i}"})
            agent._update_usage_stats({
                'token_usage': {
                    'total_tokens': 100,
                    'total_cost': 0.002
                }
            })
        
        # Test reset performance
        start_time = time.time()
        agent.reset_usage_stats()
        end_time = time.time()
        
        reset_time = end_time - start_time
        
        # Reset should be fast (less than 0.1 seconds)
        assert reset_time < 0.1, f"Reset took {reset_time:.4f}s"
        
        # Verify reset worked
        usage_stats = agent.get_usage_stats()
        assert usage_stats['total_requests'] == 0
        assert usage_stats['total_tokens'] == 0
        assert usage_stats['total_cost'] == 0.0
        
        audit_log = agent.get_audit_log()
        assert len(audit_log) == 0
    
    def test_agent_hierarchy_performance(self, mock_dependencies):
        """Test performance across the agent hierarchy."""
        # Test each agent type
        agent_types = [
            (LightweightLLMAgent, {"agent_name": "lightweight", "capabilities": ["llm_operations"], "required_roles": ["analyst"], "agui_schema": {}}),
            (TaskLLMAgent, {"agent_name": "task", "capabilities": ["task_operations"], "required_roles": ["executor"], "agui_schema": {}, "task_type": "analysis"}),
            (DimensionSpecialistAgent, {"agent_name": "specialist", "capabilities": ["specialist_operations"], "required_roles": ["specialist"], "agui_schema": {}, "dimension": "business"}),
            (DimensionLiaisonAgent, {"agent_name": "liaison", "capabilities": ["liaison_operations"], "required_roles": ["liaison"], "agui_schema": {}, "dimension": "business"}),
            (GlobalOrchestratorAgent, {"agent_name": "orchestrator", "capabilities": ["orchestration"], "required_roles": ["orchestrator"], "agui_schema": {}}),
            (GlobalGuideAgent, {"agent_name": "guide", "capabilities": ["guidance"], "required_roles": ["guide"], "agui_schema": {}})
        ]
        
        for agent_class, kwargs in agent_types:
            # Test initialization performance
            start_time = time.time()
            agent = agent_class(**kwargs, **mock_dependencies)
            init_time = time.time() - start_time
            
            # Initialization should be fast
            assert init_time < 0.1, f"{agent_class.__name__} initialization: {init_time:.4f}s"
            
            # Test operation performance
            start_time = time.time()
            for _ in range(100):
                agent._log_operation("test_operation", {"param": "value"})
                agent._update_usage_stats({
                    'token_usage': {
                        'total_tokens': 50,
                        'total_cost': 0.001
                    }
                })
            operation_time = time.time() - start_time
            
            # Operations should be fast
            assert operation_time < 0.5, f"{agent_class.__name__} operations: {operation_time:.4f}s"
            
            # Test reset performance
            start_time = time.time()
            agent.reset_usage_stats()
            reset_time = time.time() - start_time
            
            # Reset should be fast
            assert reset_time < 0.1, f"{agent_class.__name__} reset: {reset_time:.4f}s"
    
    def test_governance_configuration_performance(self, mock_dependencies):
        """Test governance configuration performance."""
        agent = LightweightLLMAgent(
            agent_name="test_agent",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Test governance configuration access performance
        start_time = time.time()
        for _ in range(1000):
            config = agent.governance_config
            assert config['rate_limiting'] is True
            assert config['cost_tracking'] is True
            assert config['audit_logging'] is True
            assert config['usage_monitoring'] is True
        end_time = time.time()
        
        access_time = end_time - start_time
        avg_access_time = access_time / 1000
        
        # Configuration access should be very fast
        assert avg_access_time < 0.001, f"Average config access time: {avg_access_time:.6f}s"
    
    def test_agent_info_performance(self, mock_dependencies):
        """Test agent info retrieval performance."""
        agent = LightweightLLMAgent(
            agent_name="test_agent",
            capabilities=["llm_operations"],
            required_roles=["analyst"],
            agui_schema={},
            **mock_dependencies
        )
        
        # Add some data
        for i in range(100):
            agent._log_operation(f"operation_{i}", {"param": f"value_{i}"})
            agent._update_usage_stats({
                'token_usage': {
                    'total_tokens': 100,
                    'total_cost': 0.002
                }
            })
        
        # Test agent info retrieval performance
        start_time = time.time()
        for _ in range(100):
            agent_info = agent.get_agent_info()
            assert 'agent_name' in agent_info
            assert 'capabilities' in agent_info
            assert 'usage_stats' in agent_info
        end_time = time.time()
        
        retrieval_time = end_time - start_time
        avg_retrieval_time = retrieval_time / 100
        
        # Agent info retrieval should be fast
        assert avg_retrieval_time < 0.01, f"Average info retrieval time: {avg_retrieval_time:.4f}s"





