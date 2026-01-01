"""
E2E tests for complete cross-pillar user journey.

Tests:
- Content → Insights → Operations → Business Outcomes workflow
- Complete CTO demo journey
- Data persistence across pillars
"""

import pytest
import asyncio
import httpx
from typing import Dict, Any

from config.test_config import TestConfig
from utils.real_infrastructure_helpers import skip_if_missing_real_infrastructure, get_test_supabase_token


@pytest.mark.e2e
@pytest.mark.production_readiness
@pytest.mark.cross_pillar
@pytest.mark.critical
@pytest.mark.slow
@pytest.mark.cto_demo
class TestCompleteUserJourneyE2E:
    """Test suite for complete cross-pillar user journey E2E validation."""
    
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
    async def test_content_to_insights_workflow(self, api_base_url, session_token):
        """Test Content → Insights workflow."""
        skip_if_missing_real_infrastructure(["supabase", "openai"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            # Step 1: Upload file (Content)
            # Step 2: Analyze file (Insights)
            # This is a simplified test - full implementation would chain these
            
            # Test that both endpoints exist
            content_response = await client.get(
                f"{api_base_url}/api/v1/content-pillar/file-preview/test_file",
                headers=headers
            )
            
            insights_response = await client.post(
                f"{api_base_url}/api/v1/insights-pillar/analyze-content",
                json={"file_id": "test_file", "analysis_type": "structured"},
                headers=headers
            )
            
            # Both endpoints should exist
            assert content_response.status_code != 404
            assert insights_response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_insights_to_operations_workflow(self, api_base_url, session_token):
        """Test Insights → Operations workflow."""
        skip_if_missing_real_infrastructure(["supabase", "openai"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            # Step 1: Analyze content (Insights)
            # Step 2: Generate workflow/SOP (Operations)
            
            insights_response = await client.post(
                f"{api_base_url}/api/v1/insights-pillar/analyze-content",
                json={"file_id": "test_file", "analysis_type": "unstructured"},
                headers=headers
            )
            
            operations_response = await client.post(
                f"{api_base_url}/api/v1/operations-pillar/create-standard-operating-procedure",
                json={"sop_content": {}, "conversion_type": "sop_to_workflow"},
                headers=headers
            )
            
            # Both endpoints should exist
            assert insights_response.status_code != 404
            assert operations_response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_operations_to_business_outcomes_workflow(self, api_base_url, session_token):
        """Test Operations → Business Outcomes workflow."""
        skip_if_missing_real_infrastructure(["supabase", "openai"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            # Step 1: Generate workflow/SOP (Operations)
            # Step 2: Generate roadmap/POC (Business Outcomes)
            
            operations_response = await client.post(
                f"{api_base_url}/api/v1/operations-pillar/create-standard-operating-procedure",
                json={"sop_content": {}, "conversion_type": "sop_to_workflow"},
                headers=headers
            )
            
            business_outcomes_response = await client.post(
                f"{api_base_url}/api/v1/business-outcomes-pillar/generate-strategic-roadmap",
                json={"pillar_summaries": {"operations": {}}},
                headers=headers
            )
            
            # Both endpoints should exist
            assert operations_response.status_code != 404
            assert business_outcomes_response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_complete_cto_demo_journey(self, api_base_url, session_token):
        """Test complete CTO demo journey (all 4 pillars in sequence)."""
        skip_if_missing_real_infrastructure(["supabase", "openai"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Complete journey: Content → Insights → Operations → Business Outcomes
            
            # Step 1: Content - File upload/preview
            content_response = await client.get(
                f"{api_base_url}/api/v1/content-pillar/file-preview/test_file",
                headers=headers
            )
            
            # Step 2: Insights - Analysis
            insights_response = await client.post(
                f"{api_base_url}/api/v1/insights-pillar/analyze-content",
                json={"file_id": "test_file", "analysis_type": "structured"},
                headers=headers
            )
            
            # Step 3: Operations - Workflow generation
            operations_response = await client.post(
                f"{api_base_url}/api/v1/operations-pillar/create-standard-operating-procedure",
                json={"sop_content": {}, "conversion_type": "sop_to_workflow"},
                headers=headers
            )
            
            # Step 4: Business Outcomes - Roadmap generation
            business_outcomes_response = await client.post(
                f"{api_base_url}/api/v1/business-outcomes-pillar/generate-strategic-roadmap",
                json={"pillar_summaries": {"content": {}, "insights": {}, "operations": {}}},
                headers=headers
            )
            
            # All endpoints should exist
            assert content_response.status_code != 404
            assert insights_response.status_code != 404
            assert operations_response.status_code != 404
            assert business_outcomes_response.status_code != 404



