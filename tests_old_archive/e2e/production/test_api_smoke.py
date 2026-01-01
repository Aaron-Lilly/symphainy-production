#!/usr/bin/env python3
"""
HTTP API Endpoint Smoke Tests

Quick smoke tests to verify all critical endpoints exist and respond.
These tests catch missing endpoints before deployment (like the 404 errors we had).

Run: pytest tests/e2e/production/test_api_smoke.py -v
"""

import pytest
import httpx
from typing import Dict, Any

# Test timeout
TIMEOUT = 10.0


@pytest.mark.e2e
@pytest.mark.smoke
class TestAPISmoke:
    """Smoke tests for critical API endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, http_client):
        """Test that health endpoint exists and responds."""
        response = await http_client.get("/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        print(f"✅ GET /health → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_auth_register_endpoint_exists(self, http_client):
        """Test that user registration endpoint exists (was 404 in production)."""
        # Test with minimal data - endpoint should exist even if validation fails
        response = await http_client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
                "name": "Test User"
            }
        )
        
        # CRITICAL: Should NOT be 404 (endpoint missing)
        assert response.status_code != 404, \
            f"❌ FAILED: POST /api/auth/register returned 404 (endpoint missing) - This was a production bug!"
        
        # Should be 200 (success) or 400/422 (validation error), but not 404
        assert response.status_code in [200, 201, 400, 422], \
            f"Unexpected status: {response.status_code} - {response.text}"
        
        print(f"✅ POST /api/auth/register exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_auth_login_endpoint_exists(self, http_client):
        """Test that user login endpoint exists (was 404 in production)."""
        response = await http_client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        # CRITICAL: Should NOT be 404
        assert response.status_code != 404, \
            f"❌ FAILED: POST /api/auth/login returned 404 (endpoint missing) - This was a production bug!"
        
        # Should be 200 (success), 401 (unauthorized), or 400/422 (validation error)
        assert response.status_code in [200, 401, 400, 422], \
            f"Unexpected status: {response.status_code} - {response.text}"
        
        print(f"✅ POST /api/auth/login exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_session_create_endpoint_exists(self, http_client):
        """Test that session creation endpoint exists (matches frontend: SessionAPIManager)."""
        # Frontend uses: /api/v1/session/create-user-session
        response = await http_client.post(
            "/api/v1/session/create-user-session",
            json={"session_type": "mvp"}
        )
        
        # CRITICAL: Should NOT be 404
        assert response.status_code != 404, \
            f"❌ FAILED: POST /api/v1/session/create-user-session returned 404 (endpoint missing) - This was a production bug!"
        
        # Should return 200 or 201 with session data, or 400/422 (validation error)
        assert response.status_code in [200, 201, 400, 422], \
            f"Session creation failed: {response.status_code} - {response.text}"
        
        # If successful, verify response has session data
        if response.status_code in [200, 201]:
            data = response.json()
            assert "session_token" in data or "session_id" in data or "session" in data, \
                "Session response missing session identifier"
        
        print(f"✅ POST /api/v1/session/create-user-session exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_guide_agent_analyze_endpoint_exists(self, http_client):
        """Test that Guide Agent analyze endpoint exists (matches frontend: GuideAgentAPIManager)."""
        # Frontend uses: /api/v1/journey/guide-agent/analyze-user-intent
        response = await http_client.post(
            "/api/v1/journey/guide-agent/analyze-user-intent",
            json={
                "message": "test message",
                "user_id": "test_user"
            }
        )
        
        # CRITICAL: Should NOT be 404
        assert response.status_code != 404, \
            f"❌ FAILED: POST /api/v1/journey/guide-agent/analyze-user-intent returned 404 (endpoint missing) - This was a production bug!"
        
        # Should be 200 (success), 400/422 (validation error), or 503 (service unavailable)
        assert response.status_code in [200, 400, 422, 503], \
            f"Unexpected status: {response.status_code} - {response.text}"
        
        print(f"✅ POST /api/v1/journey/guide-agent/analyze-user-intent exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_content_upload_endpoint_exists(self, http_client):
        """Test that content upload endpoint exists (matches frontend: ContentAPIManager)."""
        # Frontend uses: /api/v1/content-pillar/upload-file
        # Test with minimal file data
        files = {
            "file": ("test.xlsx", b"fake file content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        }
        response = await http_client.post("/api/v1/content-pillar/upload-file", files=files)
        
        # CRITICAL: Should NOT be 404
        assert response.status_code != 404, \
            f"❌ FAILED: POST /api/v1/content-pillar/upload-file returned 404 (endpoint missing)"
        
        # Should be 200 (success), 400 (validation error), or 401 (unauthorized)
        assert response.status_code in [200, 201, 400, 401, 422], \
            f"Unexpected status: {response.status_code} - {response.text}"
        
        print(f"✅ POST /api/v1/content-pillar/upload-file exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_insights_endpoint_exists(self, http_client):
        """Test that insights endpoint exists (matches frontend: InsightsAPIManager)."""
        # Frontend uses: /api/v1/insights-pillar/analyze-content
        response = await http_client.post(
            "/api/v1/insights-pillar/analyze-content",
            json={
                "file_ids": [],
                "analysis_type": "quick"
            }
        )
        
        # CRITICAL: Should NOT be 404
        assert response.status_code != 404, \
            f"❌ FAILED: POST /api/v1/insights-pillar/analyze-content returned 404 (endpoint missing)"
        
        # Should be 200 (success), 400/422 (validation error), or 401 (unauthorized)
        assert response.status_code in [200, 400, 401, 422], \
            f"Unexpected status: {response.status_code} - {response.text}"
        
        print(f"✅ POST /api/v1/insights-pillar/analyze-content exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_operations_endpoint_exists(self, http_client):
        """Test that operations endpoint exists (matches frontend: OperationsAPIManager)."""
        # Frontend uses: /api/v1/operations-pillar/create-standard-operating-procedure
        response = await http_client.post(
            "/api/v1/operations-pillar/create-standard-operating-procedure",
            json={
                "name": "Test SOP",
                "description": "Test description"
            }
        )
        
        # CRITICAL: Should NOT be 404
        assert response.status_code != 404, \
            f"❌ FAILED: POST /api/v1/operations-pillar/create-standard-operating-procedure returned 404 (endpoint missing)"
        
        # Should be 200 (success), 400/422 (validation error), or 401 (unauthorized)
        assert response.status_code in [200, 201, 400, 401, 422], \
            f"Unexpected status: {response.status_code} - {response.text}"
        
        print(f"✅ POST /api/v1/operations-pillar/create-standard-operating-procedure exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_business_outcomes_endpoint_exists(self, http_client):
        """Test that business outcomes endpoint exists (matches frontend: BusinessOutcomesAPIManager)."""
        # Frontend likely uses: /api/v1/business-outcomes-pillar/generate-strategic-roadmap
        # Testing with a POST request as this is typically a generation endpoint
        response = await http_client.post(
            "/api/v1/business-outcomes-pillar/generate-strategic-roadmap",
            json={
                "context": "test",
                "goals": ["test goal"]
            }
        )
        
        # CRITICAL: Should NOT be 404
        assert response.status_code != 404, \
            f"❌ FAILED: POST /api/v1/business-outcomes-pillar/generate-strategic-roadmap returned 404 (endpoint missing)"
        
        # Should be 200 (success), 400/422 (validation error), or 401 (unauthorized)
        assert response.status_code in [200, 201, 400, 401, 422], \
            f"Unexpected status: {response.status_code} - {response.text}"
        
        print(f"✅ POST /api/v1/business-outcomes-pillar/generate-strategic-roadmap exists → {response.status_code}")

