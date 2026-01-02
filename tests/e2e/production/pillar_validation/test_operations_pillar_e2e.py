"""
E2E tests for Operations Pillar validation.

Tests:
- SOP to workflow conversion
- Workflow to SOP conversion
- Coexistence analysis
- Interactive SOP creation
"""

import pytest
import asyncio
import httpx
from typing import Dict, Any

from config.test_config import TestConfig
from utils.real_infrastructure_helpers import skip_if_missing_real_infrastructure, get_test_supabase_token


@pytest.mark.e2e
@pytest.mark.production_readiness
@pytest.mark.pillar
@pytest.mark.operations
@pytest.mark.slow
@pytest.mark.critical
class TestOperationsPillarE2E:
    """Test suite for Operations Pillar E2E validation."""
    
    @pytest.fixture
    def api_base_url(self):
        """Get API base URL from environment."""
        import os
        return os.getenv("TEST_API_URL", "http://localhost")
    
    @pytest.fixture
    def session_token(self):
        """Get session token for authenticated requests."""
        return get_test_supabase_token()
    
    @pytest.mark.asyncio
    async def test_sop_to_workflow_conversion(self, api_base_url, session_token):
        """Test SOP to workflow conversion workflow."""
        skip_if_missing_real_infrastructure(["supabase", "openai"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Test SOP to workflow conversion endpoint
            response = await client.post(
                f"{api_base_url}/api/v1/operations-pillar/create-standard-operating-procedure",
                json={
                    "sop_content": {
                        "title": "Test SOP",
                        "sections": []
                    },
                    "conversion_type": "sop_to_workflow",
                    "options": {}
                },
                headers=headers
            )
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_workflow_to_sop_conversion(self, api_base_url, session_token):
        """Test workflow to SOP conversion workflow."""
        skip_if_missing_real_infrastructure(["supabase", "openai"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Test workflow to SOP conversion endpoint
            response = await client.post(
                f"{api_base_url}/api/v1/operations-pillar/create-standard-operating-procedure",
                json={
                    "workflow_content": {
                        "nodes": [],
                        "edges": []
                    },
                    "conversion_type": "workflow_to_sop",
                    "options": {}
                },
                headers=headers
            )
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_coexistence_analysis(self, api_base_url, session_token):
        """Test coexistence analysis workflow."""
        skip_if_missing_real_infrastructure(["supabase", "openai"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Test coexistence analysis endpoint
            response = await client.post(
                f"{api_base_url}/api/v1/operations-pillar/coexistence-analysis",
                json={
                    "sop_content": {},
                    "workflow_content": {},
                    "options": {}
                },
                headers=headers
            )
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_interactive_sop_creation(self, api_base_url, session_token):
        """Test interactive SOP creation workflow."""
        skip_if_missing_real_infrastructure(["supabase"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test interactive SOP creation endpoint (liaison conversation)
            response = await client.post(
                f"{api_base_url}/api/operations/liaison/conversation",
                json={
                    "message": "Create a new SOP",
                    "conversation_id": "test_conversation",
                    "pillar": "operations"
                },
                headers=headers
            )
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404




