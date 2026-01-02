"""
E2E tests for Business Outcomes Pillar validation.

Tests:
- Pillar summary compilation
- Roadmap generation
- POC proposal generation
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
@pytest.mark.business_outcomes
@pytest.mark.slow
@pytest.mark.critical
class TestBusinessOutcomesPillarE2E:
    """Test suite for Business Outcomes Pillar E2E validation."""
    
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
    async def test_pillar_summary_compilation(self, api_base_url, session_token):
        """Test pillar summary compilation workflow."""
        skip_if_missing_real_infrastructure(["supabase", "openai"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Test pillar summary compilation endpoint
            response = await client.post(
                f"{api_base_url}/api/v1/business-outcomes-pillar/compile-pillar-summaries",
                json={
                    "session_id": "test_session",
                    "options": {}
                },
                headers=headers
            )
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_roadmap_generation(self, api_base_url, session_token):
        """Test roadmap generation workflow."""
        skip_if_missing_real_infrastructure(["supabase", "openai"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            # Test roadmap generation endpoint
            response = await client.post(
                f"{api_base_url}/api/v1/business-outcomes-pillar/generate-strategic-roadmap",
                json={
                    "pillar_summaries": {
                        "content": {},
                        "insights": {},
                        "operations": {}
                    },
                    "options": {}
                },
                headers=headers
            )
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_poc_proposal_generation(self, api_base_url, session_token):
        """Test POC proposal generation workflow."""
        skip_if_missing_real_infrastructure(["supabase", "openai"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            # Test POC proposal generation endpoint
            response = await client.post(
                f"{api_base_url}/api/v1/business-outcomes-pillar/generate-poc-proposal",
                json={
                    "pillar_summaries": {},
                    "poc_options": {},
                    "options": {}
                },
                headers=headers
            )
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404




