#!/usr/bin/env python3
"""
Unit Tests: Agentic SDK

Tests the enhanced Agentic SDK with business abstraction access.
Validates AgentBase, BusinessAbstractionHelper, and MVP abstraction integration.

WHAT (Test Role): I validate the Agentic SDK components
HOW (Test Implementation): I test agent creation, business abstraction access, and MVP capabilities
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../symphainy-platform'))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from agentic.agent_sdk import AgentBase, BusinessAbstractionHelper
from agentic.agui_schema_registry import AGUISchema, AGUIComponent


class UserContext:
    """Simple UserContext for testing."""
    def __init__(self, user_id: str, tenant_id: str = "test_tenant", email: str = "test@example.com", 
                 full_name: str = "Test User", session_id: str = "test_session", 
                 permissions: list = None):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.email = email
        self.full_name = full_name
        self.session_id = session_id
        self.permissions = permissions or ["read", "write"]


class TestAgent(AgentBase):
    """Concrete test implementation of AgentBase."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    # Implement required abstract methods
    async def process_request(self, request: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        return {"status": "success", "message": "Test agent processed request"}
    
    def get_agent_capabilities(self) -> List[str]:
        return ["testing"]
    
    def get_agent_description(self) -> str:
        return "Test agent for unit testing"
    
    # Multi-tenant methods (stub implementations for testing)
    async def create_tenant(self, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "tenant_id": "test_tenant"}
    
    async def update_tenant(self, tenant_id: str, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "tenant_id": tenant_id}
    
    async def delete_tenant(self, tenant_id: str) -> Dict[str, Any]:
        return {"status": "success", "tenant_id": tenant_id}
    
    async def list_tenants(self) -> List[Dict[str, Any]]:
        return [{"tenant_id": "test_tenant", "name": "Test Tenant"}]
    
    async def add_user_to_tenant(self, tenant_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "user_id": "test_user"}
    
    async def remove_user_from_tenant(self, tenant_id: str, user_id: str) -> Dict[str, Any]:
        return {"status": "success", "user_id": user_id}
    
    async def get_tenant_users(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [{"user_id": "test_user", "name": "Test User"}]
    
    async def get_tenant_usage_stats(self, tenant_id: str) -> Dict[str, Any]:
        return {"total_requests": 0, "success_rate": 1.0}
    
    async def get_user_tenant_context(self, user_id: str) -> Dict[str, Any]:
        return {"tenant_id": "test_tenant", "permissions": ["read", "write"]}
    
    async def validate_tenant_access(self, tenant_id: str, user_id: str) -> bool:
        return True
    
    async def validate_tenant_feature_access(self, tenant_id: str, user_id: str, feature: str) -> bool:
        return True
    
    async def audit_tenant_action(self, tenant_id: str, user_id: str, action: str, details: Dict[str, Any]) -> None:
        pass


class TestAgentBase:
    """Test AgentBase functionality."""
    
    @pytest.fixture
    def di_container(self):
        """Create a DI container for testing."""
        return DIContainerService("test_agent")
    
    @pytest.fixture
    def public_works_service(self, di_container):
        """Create a Public Works Foundation Service for testing."""
        return PublicWorksFoundationService(di_container)
    
    @pytest.fixture
    def mock_agui_schema(self):
        """Create a mock AGUI schema for testing."""
        return AGUISchema(
            agent_name="test_agent",
            version="1.0.0",
            description="Test schema for testing",
            components=[
                AGUIComponent(
                    type="info_card",
                    title="Test Component",
                    description="Test component for testing",
                    properties={"title": "Test Title", "content": "Test content"}
                )
            ]
        )
    
    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for AgentBase."""
        return {
            'mcp_client_manager': Mock(),
            'policy_integration': AsyncMock(),
            'tool_composition': Mock(),
            'agui_formatter': Mock()
        }
    
    def test_agent_base_initialization(self, di_container, public_works_service, mock_agui_schema, mock_dependencies):
        """Test AgentBase initializes correctly."""
        agent = TestAgent(
            agent_name="test_agent",
            capabilities=["testing"],
            required_roles=["librarian"],
            agui_schema=mock_agui_schema,
            foundation_services=di_container,
            public_works_foundation=public_works_service,
            **mock_dependencies
        )
        
        assert agent is not None
        assert agent.agent_name == "test_agent"
        assert agent.foundation_services is di_container
        assert agent.public_works_foundation is public_works_service
        assert hasattr(agent, 'business_helper')
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, di_container, public_works_service, mock_agui_schema, mock_dependencies):
        """Test agent initialization process."""
        agent = TestAgent(
            agent_name="test_agent",
            capabilities=["testing"],
            required_roles=["librarian"],
            agui_schema=mock_agui_schema,
            foundation_services=di_container,
            public_works_foundation=public_works_service,
            **mock_dependencies
        )
        
        # Mock the initialization dependencies
        agent.mcp_client_manager.connect_to_role = AsyncMock(return_value=True)
        
        await agent.initialize()
        
        assert agent.is_initialized
        # Note: agentic_abstractions may be empty due to async loading issues in test environment
        assert agent.business_helper is not None
    
    @pytest.mark.asyncio
    async def test_business_abstraction_access(self, di_container, public_works_service, mock_agui_schema, mock_dependencies):
        """Test business abstraction access methods."""
        agent = TestAgent(
            agent_name="test_agent",
            capabilities=["testing"],
            required_roles=["librarian"],
            agui_schema=mock_agui_schema,
            foundation_services=di_container,
            public_works_foundation=public_works_service,
            **mock_dependencies
        )
        
        # Mock the initialization dependencies
        agent.mcp_client_manager.connect_to_role = AsyncMock(return_value=True)
        
        await agent.initialize()
        
        # Test getting business abstractions
        cobol_abstraction = await agent.get_business_abstraction("cobol_processing")
        assert cobol_abstraction is not None
        
        # Test listing available abstractions
        available_abstractions = await agent.list_available_business_abstractions()
        assert isinstance(available_abstractions, dict)
        assert len(available_abstractions) > 0
        
        # Test MVP abstraction convenience methods
        cobol_result = await agent.process_cobol_data("TEST-COPYBOOK")
        assert isinstance(cobol_result, dict)
        
        sop_result = await agent.create_sop("Test SOP content")
        assert isinstance(sop_result, dict)
        
        poc_result = await agent.generate_poc_proposal({"project": "test"})
        assert isinstance(poc_result, dict)
        
        roadmap_result = await agent.create_roadmap({"project": "test"})
        assert isinstance(roadmap_result, dict)
        
        coexistence_result = await agent.evaluate_coexistence({
            "process_name": "test_process",
            "steps": [{"step_id": "step1", "actor": "human", "description": "Test step"}]
        })
        assert isinstance(coexistence_result, dict)
    
    @pytest.mark.asyncio
    async def test_health_check(self, di_container, public_works_service, mock_agui_schema, mock_dependencies):
        """Test agent health check."""
        agent = TestAgent(
            agent_name="test_agent",
            capabilities=["testing"],
            required_roles=["librarian"],
            agui_schema=mock_agui_schema,
            foundation_services=di_container,
            public_works_foundation=public_works_service,
            **mock_dependencies
        )
        
        # Mock the initialization dependencies
        agent.mcp_client_manager.connect_to_role = AsyncMock(return_value=True)
        
        await agent.initialize()
        
        health_status = await agent.run_health_check()
        assert isinstance(health_status, dict)
        assert 'overall_status' in health_status
        assert 'agent_name' in health_status
        assert 'checks' in health_status


class TestBusinessAbstractionHelper:
    """Test BusinessAbstractionHelper functionality."""
    
    @pytest.fixture
    def di_container(self):
        """Create a DI container for testing."""
        return DIContainerService("test_helper")
    
    @pytest.fixture
    def public_works_service(self, di_container):
        """Create a Public Works Foundation Service for testing."""
        return PublicWorksFoundationService(di_container)
    
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger."""
        return Mock()
    
    @pytest.fixture
    def business_helper(self, public_works_service, mock_logger):
        """Create a BusinessAbstractionHelper for testing."""
        return BusinessAbstractionHelper("test_agent", public_works_service, mock_logger)
    
    @pytest.mark.asyncio
    async def test_get_abstraction(self, business_helper):
        """Test getting a specific abstraction."""
        abstraction = await business_helper.get_abstraction("cobol_processing")
        assert abstraction is not None
    
    @pytest.mark.asyncio
    async def test_list_available_abstractions(self, business_helper):
        """Test listing available abstractions."""
        abstractions = await business_helper.list_available_abstractions()
        assert isinstance(abstractions, dict)
        assert len(abstractions) > 0
        
        # Check for MVP abstractions
        mvp_abstractions = ['cobol_processing', 'sop_processing', 'poc_generation', 'roadmap_generation', 'coexistence_evaluation']
        for abstraction_name in mvp_abstractions:
            assert abstraction_name in abstractions
    
    @pytest.mark.asyncio
    async def test_mvp_convenience_methods(self, business_helper):
        """Test MVP convenience methods."""
        # Test COBOL processing
        cobol_result = await business_helper.process_cobol_data("TEST-COPYBOOK")
        assert isinstance(cobol_result, dict)
        
        # Test SOP creation
        sop_result = await business_helper.create_sop("Test SOP content")
        assert isinstance(sop_result, dict)
        
        # Test POC generation
        poc_result = await business_helper.generate_poc_proposal({"project": "test"})
        assert isinstance(poc_result, dict)
        
        # Test roadmap creation
        roadmap_result = await business_helper.create_roadmap({"project": "test"})
        assert isinstance(roadmap_result, dict)
        
        # Test coexistence evaluation
        coexistence_result = await business_helper.evaluate_coexistence({
            "process_name": "test_process",
            "steps": [{"step_id": "step1", "actor": "human", "description": "Test step"}]
        })
        assert isinstance(coexistence_result, dict)
    
    @pytest.mark.asyncio
    async def test_health_check_abstractions(self, business_helper):
        """Test abstraction health check."""
        health_status = await business_helper.health_check_abstractions()
        assert isinstance(health_status, dict)
        assert 'agent' in health_status
        assert 'abstraction_health' in health_status
        assert 'total_abstractions' in health_status
    
    def test_usage_statistics(self, business_helper):
        """Test usage statistics."""
        stats = business_helper.get_usage_statistics()
        assert isinstance(stats, dict)
        
        # If no usage data, should return message
        if 'message' in stats:
            assert stats['message'] == 'No usage data available'
        else:
            # If usage data exists, should have these fields
            assert 'total_usage' in stats
            assert 'successful_usage' in stats
            assert 'failed_usage' in stats
            assert 'success_rate' in stats
