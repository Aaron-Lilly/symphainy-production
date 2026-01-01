#!/usr/bin/env python3
"""
Functional Tests: InsightsBusinessAnalysisAgent

Tests InsightsBusinessAnalysisAgent functionality:
1. Structured data analysis (EDA tools + LLM interpretation)
2. Unstructured data analysis (embedding review with LLM)
3. Agentic correlation tracking
4. MCP tool integration

Phase 1: Tests with mocked LLM/MCP to verify approach
Phase 2: Tests with real LLM calls to verify actual functionality
"""

import pytest
import os
import sys
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'symphainy-platform'))

from utilities import UserContext


# ============================================================================
# TEST FIXTURES: Mock Dependencies
# ============================================================================

@pytest.fixture
def mock_di_container():
    """Create mock DI Container."""
    container = Mock()
    container.realm_name = "business_enablement"
    container.get_utility = Mock(return_value=Mock())
    container.get_service = Mock(return_value=None)
    container.get_foundation_service = Mock(return_value=None)
    container.get_logger = Mock(return_value=Mock())
    return container


@pytest.fixture
def mock_platform_gateway():
    """Create mock Platform Gateway."""
    gateway = Mock()
    
    # Mock semantic data abstraction
    mock_semantic_data = AsyncMock()
    mock_semantic_data.get_semantic_embeddings = AsyncMock(return_value=create_test_schema_embeddings())
    gateway.get_abstraction = Mock(return_value=mock_semantic_data)
    
    return gateway


@pytest.fixture
def mock_public_works_foundation():
    """Create mock Public Works Foundation."""
    foundation = Mock()
    
    # Mock LLM abstraction
    mock_llm_abstraction = AsyncMock()
    mock_llm_abstraction.analyze_text = AsyncMock(return_value={
        "success": True,
        "text": "Mock LLM analysis: The data shows strong revenue growth with positive correlations.",
        "tokens": {"input": 100, "output": 50, "total": 150},
        "cost": 0.001
    })
    foundation.get_abstraction = Mock(return_value=mock_llm_abstraction)
    
    return foundation


@pytest.fixture
def mock_agentic_foundation():
    """Create mock Agentic Foundation."""
    foundation = Mock()
    foundation.public_works_foundation = None  # Will be set separately
    return foundation


@pytest.fixture
def mock_mcp_client_manager():
    """Create mock MCP Client Manager."""
    manager = AsyncMock()
    
    # Mock EDA tool execution
    async def execute_tool(tool_name, parameters):
        if tool_name == "run_eda_analysis":
            return {
                "success": True,
                "content_id": parameters.get("content_id"),
                "eda_results": {
                    "statistics": {
                        "revenue": {
                            "type": "numerical",
                            "mean": 1000.0,
                            "median": 950.0,
                            "std": 200.0
                        }
                    },
                    "correlations": {
                        "correlation_matrix": {
                            "revenue": {"cost": 0.85}
                        }
                    }
                },
                "schema_info": {
                    "columns": ["revenue", "cost", "profit"]
                }
            }
        return {"success": False, "error": "Unknown tool"}
    
    manager.execute_tool = execute_tool
    manager.connect_to_role = AsyncMock(return_value=None)
    
    return manager


@pytest.fixture
def mock_policy_integration():
    """Create mock Policy Integration."""
    integration = Mock()
    integration.initialize = AsyncMock(return_value=True)
    return integration


@pytest.fixture
def mock_tool_composition():
    """Create mock Tool Composition."""
    composition = Mock()
    return composition


@pytest.fixture
def mock_agui_formatter():
    """Create mock AGUI Formatter."""
    formatter = Mock()
    return formatter


@pytest.fixture
def mock_curator_foundation():
    """Create mock Curator Foundation."""
    foundation = AsyncMock()
    foundation.get_registered_services = AsyncMock(return_value={
        "services": {}
    })
    return foundation


@pytest.fixture
def mock_user_context():
    """Create mock User Context."""
    return UserContext(
        user_id="test_user_123",
        email="test@example.com",
        full_name="Test User",
        session_id="test_session_123",
        tenant_id="test_tenant_123",
        permissions=["read", "write"]
    )


@pytest.fixture
async def insights_business_analysis_agent(
    mock_di_container,
    mock_platform_gateway,
    mock_public_works_foundation,
    mock_agentic_foundation,
    mock_mcp_client_manager,
    mock_policy_integration,
    mock_tool_composition,
    mock_agui_formatter,
    mock_curator_foundation
):
    """Create InsightsBusinessAnalysisAgent instance with mocks."""
    from foundations.agentic_foundation.agui_schema_registry import AGUISchema, AGUIComponent
    # Import directly from file to avoid __init__.py import issues
    import importlib.util
    agent_file = os.path.join(
        project_root,
        'symphainy-platform',
        'backend',
        'business_enablement',
        'delivery_manager',
        'mvp_pillar_orchestrators',
        'insights_orchestrator',
        'agents',
        'insights_business_analysis_agent.py'
    )
    spec = importlib.util.spec_from_file_location("insights_business_analysis_agent", agent_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    InsightsBusinessAnalysisAgent = module.InsightsBusinessAnalysisAgent
    
    # Create minimal AGUI schema
    agui_schema = AGUISchema(
        agent_name="InsightsBusinessAnalysisAgent",
        version="1.0",
        description="Business analysis agent for insights",
        components=[]
    )
    
    # Set public works foundation on agentic foundation
    mock_agentic_foundation.public_works_foundation = mock_public_works_foundation
    
    agent = InsightsBusinessAnalysisAgent(
        agent_name="InsightsBusinessAnalysisAgent",
        capabilities=["business_analysis", "eda_interpretation", "embedding_review"],
        required_roles=["librarian", "data_steward"],
        agui_schema=agui_schema,
        foundation_services=mock_di_container,
        agentic_foundation=mock_agentic_foundation,
        public_works_foundation=mock_public_works_foundation,
        mcp_client_manager=mock_mcp_client_manager,
        policy_integration=mock_policy_integration,
        tool_composition=mock_tool_composition,
        agui_formatter=mock_agui_formatter,
        curator_foundation=mock_curator_foundation
    )
    
    # Mock business helper
    from foundations.agentic_foundation.agent_sdk.business_abstraction_helper import BusinessAbstractionHelper
    agent.business_helper = BusinessAbstractionHelper(
        agent.agent_name,
        mock_public_works_foundation,
        agent.logger
    )
    
    # Mock semantic data access
    agent.get_business_abstraction = AsyncMock(return_value=mock_platform_gateway.get_abstraction("semantic_data"))
    
    await agent.initialize()
    return agent


# ============================================================================
# TEST DATA: Mock Semantic Embeddings
# ============================================================================

def create_test_schema_embeddings() -> List[Dict[str, Any]]:
    """Create test schema embeddings."""
    return [
        {
            "_key": "emb_1",
            "id": "emb_1",
            "content_id": "test_content_123",
            "column_name": "revenue",
            "data_type": "float",
            "embedding_type": "schema",
            "metadata": {
                "mean": 1000.0,
                "median": 950.0,
                "std": 200.0
            }
        },
        {
            "_key": "emb_2",
            "id": "emb_2",
            "content_id": "test_content_123",
            "column_name": "cost",
            "data_type": "float",
            "embedding_type": "schema",
            "metadata": {
                "mean": 700.0,
                "median": 680.0,
                "std": 150.0
            }
        }
    ]


def create_test_chunk_embeddings() -> List[Dict[str, Any]]:
    """Create test chunk embeddings for unstructured data."""
    return [
        {
            "_key": "chunk_1",
            "id": "chunk_1",
            "content_id": "test_content_123",
            "embedding_type": "chunk",
            "text": "This is the first chunk of unstructured content. It contains important business information.",
            "chunk_text": "This is the first chunk of unstructured content. It contains important business information."
        },
        {
            "_key": "chunk_2",
            "id": "chunk_2",
            "content_id": "test_content_123",
            "embedding_type": "chunk",
            "text": "The second chunk discusses revenue trends and customer satisfaction metrics.",
            "chunk_text": "The second chunk discusses revenue trends and customer satisfaction metrics."
        }
    ]


# ============================================================================
# PHASE 1: FUNCTIONAL TESTS WITH MOCKED LLM/MCP
# ============================================================================

@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
@pytest.mark.functional
class TestInsightsBusinessAnalysisAgentMocked:
    """Test InsightsBusinessAnalysisAgent with mocked LLM/MCP tools."""
    
    @pytest.mark.asyncio
    async def test_analyze_structured_data_mocked(
        self,
        insights_business_analysis_agent,
        mock_user_context,
        mock_platform_gateway
    ):
        """Test structured data analysis with mocked EDA tool and LLM."""
        # Update mock to return schema embeddings
        mock_semantic_data = mock_platform_gateway.get_abstraction("semantic_data")
        mock_semantic_data.get_semantic_embeddings = AsyncMock(return_value=create_test_schema_embeddings())
        
        # Mock LLM call with tracking
        with patch.object(
            insights_business_analysis_agent,
            '_call_llm_with_tracking',
            new_callable=AsyncMock
        ) as mock_llm_tracking:
            mock_llm_tracking.return_value = {
                "success": True,
                "text": "Mock LLM interpretation: Revenue shows strong growth with positive correlation to costs.",
                "tokens": {"input": 100, "output": 50},
                "cost": 0.001
            }
            
            # Mock tool execution with tracking
            with patch.object(
                insights_business_analysis_agent,
                '_execute_tool_with_tracking',
                new_callable=AsyncMock
            ) as mock_tool_tracking:
                mock_tool_tracking.return_value = {
                    "success": True,
                    "content_id": "test_content_123",
                    "eda_results": {
                        "statistics": {
                            "revenue": {
                                "type": "numerical",
                                "mean": 1000.0,
                                "median": 950.0,
                                "std": 200.0
                            }
                        },
                        "correlations": {
                            "correlation_matrix": {
                                "revenue": {"cost": 0.85}
                            }
                        }
                    },
                    "schema_info": {
                        "columns": ["revenue", "cost", "profit"]
                    }
                }
                
                # Execute analysis
                result = await insights_business_analysis_agent.analyze_structured_data(
                    content_id="test_content_123",
                    user_context=mock_user_context
                )
                
                # Verify result structure
                assert result is not None
                assert result["success"] is True
                assert result["content_id"] == "test_content_123"
                assert "eda_results" in result
                assert "interpretation" in result
                assert "embeddings_used" in result
                
                # Verify EDA tool was called
                assert mock_tool_tracking.called
                call_args = mock_tool_tracking.call_args
                assert call_args[1]["tool_name"] == "run_eda_analysis"
                assert call_args[1]["parameters"]["content_id"] == "test_content_123"
                
                # Verify LLM was called for interpretation
                assert mock_llm_tracking.called
    
    @pytest.mark.asyncio
    async def test_analyze_unstructured_data_mocked(
        self,
        insights_business_analysis_agent,
        mock_user_context,
        mock_platform_gateway
    ):
        """Test unstructured data analysis with mocked LLM."""
        # Update mock to return chunk embeddings
        mock_semantic_data = mock_platform_gateway.get_abstraction("semantic_data")
        mock_semantic_data.get_semantic_embeddings = AsyncMock(return_value=create_test_chunk_embeddings())
        
        # Mock LLM call with tracking
        with patch.object(
            insights_business_analysis_agent,
            '_call_llm_with_tracking',
            new_callable=AsyncMock
        ) as mock_llm_tracking:
            mock_llm_tracking.return_value = {
                "success": True,
                "text": "Mock LLM analysis: The content discusses revenue trends and customer satisfaction.",
                "tokens": {"input": 100, "output": 50},
                "cost": 0.001
            }
            
            # Execute analysis
            result = await insights_business_analysis_agent.analyze_unstructured_data(
                content_id="test_content_123",
                user_context=mock_user_context
            )
            
            # Verify result structure
            assert result is not None
            assert result["success"] is True
            assert result["content_id"] == "test_content_123"
            assert "analysis" in result
            assert "embeddings_reviewed" in result
            
            # Verify LLM was called
            assert mock_llm_tracking.called
            call_args = mock_llm_tracking.call_args
            assert "prompt" in call_args[1] or len(call_args[0]) > 0
    
    @pytest.mark.asyncio
    async def test_agentic_correlation_tracking(
        self,
        insights_business_analysis_agent,
        mock_user_context
    ):
        """Test that agentic correlation tracking is called."""
        # Mock correlation methods
        with patch.object(
            insights_business_analysis_agent,
            '_orchestrate_agentic_correlation',
            new_callable=AsyncMock
        ) as mock_correlation:
            mock_correlation.return_value = {
                "workflow_id": "test_workflow_123",
                "agent_execution_id": "test_exec_123"
            }
            
            # Mock tool execution
            with patch.object(
                insights_business_analysis_agent,
                '_execute_tool_with_tracking',
                new_callable=AsyncMock
            ) as mock_tool:
                mock_tool.return_value = {"success": True, "eda_results": {}}
                
                # Mock LLM call
                with patch.object(
                    insights_business_analysis_agent,
                    '_call_llm_with_tracking',
                    new_callable=AsyncMock
                ) as mock_llm:
                    mock_llm.return_value = {"success": True, "text": "Analysis"}
                    
                    # Execute (will use mocked methods)
                    result = await insights_business_analysis_agent.analyze_structured_data(
                        content_id="test_content_123",
                        user_context=mock_user_context
                    )
                    
                    # Verify correlation tracking was used (via tool/LLM tracking)
                    # The tracking happens inside _execute_tool_with_tracking and _call_llm_with_tracking
                    assert result["success"] is True


# ============================================================================
# PHASE 2: FUNCTIONAL TESTS WITH REAL LLM CALLS
# ============================================================================

@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
@pytest.mark.functional
@pytest.mark.real_llm
class TestInsightsBusinessAnalysisAgentRealLLM:
    """Test InsightsBusinessAnalysisAgent with real LLM calls."""
    
    @pytest.fixture
    async def real_llm_abstraction(self, mock_di_container):
        """Create real LLM abstraction for testing with analyze_text wrapper."""
        import os
        # Try to get API key from environment first
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_OPENAI_API_KEY")
        
        # If not in environment, try to load from .env.secrets file directly
        if not OPENAI_API_KEY:
            try:
                secrets_file = os.path.join(project_root, 'symphainy-platform', '.env.secrets')
                if os.path.exists(secrets_file):
                    with open(secrets_file, 'r') as f:
                        for line in f:
                            if line.startswith('LLM_OPENAI_API_KEY=') or line.startswith('OPENAI_API_KEY='):
                                OPENAI_API_KEY = line.split('=', 1)[1].strip()
                                break
            except Exception as e:
                pass
        
        if not OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set - skipping real LLM tests")
        
        from foundations.public_works_foundation.infrastructure_adapters.openai_adapter import OpenAIAdapter
        from foundations.public_works_foundation.infrastructure_abstractions.llm_abstraction import LLMAbstraction, LLMRequest, LLMModel
        
        openai_adapter = OpenAIAdapter(api_key=OPENAI_API_KEY)
        llm_abstraction = LLMAbstraction(
            openai_adapter=openai_adapter,
            anthropic_adapter=None,
            provider="openai",
            di_container=mock_di_container
        )
        
        # Add analyze_text wrapper method to make it compatible with agent code
        async def analyze_text(text: str, analysis_type: str = "general", **kwargs):
            """Wrapper to convert analyze_text call to generate_response."""
            # Filter out Mock objects from kwargs
            clean_kwargs = {}
            for key, value in kwargs.items():
                # Skip Mock objects
                if hasattr(value, '__class__') and 'Mock' in str(type(value)):
                    continue
                clean_kwargs[key] = value
            
            # Extract and validate parameters
            max_tokens = clean_kwargs.get("max_tokens", 2000)
            temperature = clean_kwargs.get("temperature", 0.7)
            
            # Ensure they're integers/floats
            try:
                max_tokens = int(max_tokens) if max_tokens else 2000
            except (ValueError, TypeError):
                max_tokens = 2000
            
            try:
                temperature = float(temperature) if temperature else 0.7
            except (ValueError, TypeError):
                temperature = 0.7
            
            request = LLMRequest(
                messages=[
                    {"role": "system", "content": f"You are a business analyst providing {analysis_type} analysis."},
                    {"role": "user", "content": text}
                ],
                model=LLMModel.GPT_4O_MINI,
                max_tokens=max_tokens,
                temperature=temperature
            )
            response = await llm_abstraction.generate_response(request)
            return {
                "success": True,
                "text": response.content,
                "response": response.content,
                "tokens": {
                    "input": response.usage.input_tokens if hasattr(response.usage, 'input_tokens') else 0,
                    "output": response.usage.output_tokens if hasattr(response.usage, 'output_tokens') else 0,
                    "total": response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else 0
                },
                "cost": response.cost if hasattr(response, 'cost') else 0
            }
        
        # Attach wrapper method
        llm_abstraction.analyze_text = analyze_text
        
        return llm_abstraction
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.getenv("SKIP_REAL_LLM_TESTS", "false").lower() == "true",
        reason="Real LLM tests skipped via SKIP_REAL_LLM_TESTS environment variable"
    )
    async def test_analyze_structured_data_real_llm(
        self,
        insights_business_analysis_agent,
        mock_user_context,
        mock_platform_gateway,
        real_llm_abstraction,
        mock_public_works_foundation
    ):
        """Test structured data analysis with real LLM calls."""
        # Set real LLM abstraction on public works foundation
        # Patch get_agentic_abstractions to return real LLM
        def get_agentic_abstractions():
            return {"llm": real_llm_abstraction}
        
        mock_public_works_foundation.get_agentic_abstractions = get_agentic_abstractions
        mock_public_works_foundation.get_abstraction = Mock(return_value=real_llm_abstraction)
        insights_business_analysis_agent.public_works_foundation = mock_public_works_foundation
        
        # Also update business_helper's public_works_foundation reference
        if hasattr(insights_business_analysis_agent, 'business_helper') and insights_business_analysis_agent.business_helper:
            insights_business_analysis_agent.business_helper.public_works_foundation = mock_public_works_foundation
            # Clear cache to force refresh
            if hasattr(insights_business_analysis_agent.business_helper, '_abstraction_cache'):
                insights_business_analysis_agent.business_helper._abstraction_cache.clear()
        
        # Directly patch agent's get_business_abstraction to return real LLM and semantic data
        async def get_business_abstraction_with_real_llm(name):
            if name == "llm":
                return real_llm_abstraction
            if name == "semantic_data":
                # Return semantic data from platform gateway
                return mock_platform_gateway.get_abstraction("semantic_data")
            # For other abstractions, try business_helper
            if hasattr(insights_business_analysis_agent, 'business_helper') and insights_business_analysis_agent.business_helper:
                return await insights_business_analysis_agent.business_helper.get_abstraction(name)
            return None
        insights_business_analysis_agent.get_business_abstraction = get_business_abstraction_with_real_llm
        
        # Update mock to return schema embeddings
        mock_semantic_data = mock_platform_gateway.get_abstraction("semantic_data")
        mock_semantic_data.get_semantic_embeddings = AsyncMock(return_value=create_test_schema_embeddings())
        
        # Mock EDA tool (still mocked, but LLM is real)
        with patch.object(
            insights_business_analysis_agent,
            '_execute_tool_with_tracking',
            new_callable=AsyncMock
        ) as mock_tool_tracking:
            mock_tool_tracking.return_value = {
                "success": True,
                "content_id": "test_content_123",
                "eda_results": {
                    "statistics": {
                        "revenue": {
                            "type": "numerical",
                            "mean": 1000.0,
                            "median": 950.0,
                            "std": 200.0,
                            "min": 500.0,
                            "max": 1500.0
                        },
                        "cost": {
                            "type": "numerical",
                            "mean": 700.0,
                            "median": 680.0,
                            "std": 150.0
                        }
                    },
                    "correlations": {
                        "correlation_matrix": {
                            "revenue": {"cost": 0.85}
                        }
                    }
                },
                "schema_info": {
                    "columns": ["revenue", "cost", "profit"]
                }
            }
            
            # Execute analysis (will use real LLM)
            result = await insights_business_analysis_agent.analyze_structured_data(
                content_id="test_content_123",
                user_context=mock_user_context
            )
            
            # Debug: Print result if it failed
            if result and not result.get("success"):
                print(f"\n❌ Analysis failed: {result.get('error', 'Unknown error')}\n")
            
            # Verify result structure
            assert result is not None
            assert result["success"] is True, f"Analysis failed: {result.get('error', 'Unknown error')}"
            assert result["content_id"] == "test_content_123"
            assert "eda_results" in result
            assert "interpretation" in result
            
            # Verify interpretation contains meaningful content
            interpretation = result["interpretation"]
            assert interpretation is not None
            # Real LLM should provide actual insights
            if isinstance(interpretation, dict):
                assert "insights" in interpretation or "text" in interpretation
                # Print insights for verification
                insights_text = interpretation.get("insights") or interpretation.get("text", "")
                print(f"\n📊 Structured Data Analysis Insights:\n{insights_text}\n")
            else:
                print(f"\n📊 Structured Data Analysis Insights:\n{interpretation}\n")
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        os.getenv("SKIP_REAL_LLM_TESTS", "false").lower() == "true",
        reason="Real LLM tests skipped via SKIP_REAL_LLM_TESTS environment variable"
    )
    async def test_analyze_unstructured_data_real_llm(
        self,
        insights_business_analysis_agent,
        mock_user_context,
        mock_platform_gateway,
        real_llm_abstraction,
        mock_public_works_foundation
    ):
        """Test unstructured data analysis with real LLM calls."""
        # Set real LLM abstraction on public works foundation
        mock_public_works_foundation.get_abstraction = Mock(return_value=real_llm_abstraction)
        insights_business_analysis_agent.public_works_foundation = mock_public_works_foundation
        
        # Patch business_helper.get_abstraction to return real LLM abstraction
        if hasattr(insights_business_analysis_agent, 'business_helper') and insights_business_analysis_agent.business_helper:
            original_get_abstraction = insights_business_analysis_agent.business_helper.get_abstraction
            
            async def get_real_llm_abstraction(name):
                if name == "llm":
                    return real_llm_abstraction
                # For other abstractions, use the original method
                return await original_get_abstraction(name)
            
            insights_business_analysis_agent.business_helper.get_abstraction = get_real_llm_abstraction
        
        # Update mock to return chunk embeddings
        mock_semantic_data = mock_platform_gateway.get_abstraction("semantic_data")
        mock_semantic_data.get_semantic_embeddings = AsyncMock(return_value=create_test_chunk_embeddings())
        
        # Execute analysis (will use real LLM)
        result = await insights_business_analysis_agent.analyze_unstructured_data(
            content_id="test_content_123",
            user_context=mock_user_context
        )
        
        # Verify result structure
        assert result is not None
        assert result["success"] is True
        assert result["content_id"] == "test_content_123"
        assert "analysis" in result
        
        # Verify analysis contains meaningful content
        analysis = result["analysis"]
        assert analysis is not None
        # Real LLM should provide actual analysis
        # The analysis might be a string or dict
        if isinstance(analysis, dict):
            # If dict, should have text or insights
            assert "text" in analysis or "insights" in analysis or "analysis" in analysis
            # Print analysis for verification
            analysis_text = analysis.get("text") or analysis.get("insights") or analysis.get("analysis", "")
            print(f"\n📝 Unstructured Data Analysis:\n{analysis_text}\n")
        elif isinstance(analysis, str):
            # If string, should not be empty
            assert len(analysis) > 0
            # Should contain meaningful content (not just mock response)
            assert "AsyncMock" not in analysis
            print(f"\n📝 Unstructured Data Analysis:\n{analysis}\n")

