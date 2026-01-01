"""
E2E Test: HTTP API Endpoints - Reality Check
Tests that would have caught yesterday's 404 errors

This test validates that all API endpoints the frontend uses actually exist
and respond correctly when the platform is running.
"""

import pytest
import httpx
import asyncio
from typing import Dict, Any
import os

# Import backend_url fixture from conftest
BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
TIMEOUT = 10.0

@pytest.mark.e2e
@pytest.mark.critical
class TestCriticalAPIEndpoints:
    """Test critical API endpoints that caused yesterday's failures"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, backend_server):
        """Test that basic health endpoint works"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200, f"Health check failed: {response.text}"
            print(f"✅ GET /health → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_auth_register_endpoint_exists(self, backend_server):
        """Test that user registration endpoint exists (404 yesterday)"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Test that endpoint exists (even with invalid data, shouldn't be 404)
            response = await client.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "testpassword123",
                    "name": "Test User"
                }
            )
            
            # Should NOT be 404 (endpoint missing)
            assert response.status_code != 404, \
                f"❌ FAILED: POST /api/auth/register returned 404 (endpoint missing) - This was yesterday's bug!"
            
            # Should be 200 (success) or 400/422 (validation error), but not 404
            assert response.status_code in [200, 201, 400, 422], \
                f"Unexpected status: {response.status_code} - {response.text}"
            
            print(f"✅ POST /api/auth/register exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_auth_login_endpoint_exists(self, backend_server):
        """Test that user login endpoint exists (404 yesterday)"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "testpassword123"
                }
            )
            
            assert response.status_code != 404, \
                f"❌ FAILED: POST /api/auth/login returned 404 (endpoint missing)"
            
            assert response.status_code in [200, 401, 400, 422], \
                f"Unexpected status: {response.status_code}"
            
            print(f"✅ POST /api/auth/login exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_global_session_endpoint_exists(self, backend_server):
        """Test that global session endpoint exists (404 yesterday)"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(f"{BASE_URL}/api/global/session")
            
            assert response.status_code != 404, \
                f"❌ FAILED: POST /api/global/session returned 404 (endpoint missing) - This was yesterday's bug!"
            
            # Should return 200 with session data
            assert response.status_code in [200, 201], \
                f"Session creation failed: {response.status_code} - {response.text}"
            
            # Verify response has session data
            data = response.json()
            assert "session_token" in data or "session_id" in data, \
                "Session response missing session identifier"
            
            print(f"✅ POST /api/global/session exists → {response.status_code}")
            return data
    
    @pytest.mark.asyncio
    async def test_guide_agent_analyze_endpoint_exists(self, backend_server):
        """Test that Guide Agent analyze endpoint exists (404 yesterday)"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/api/global/agent/analyze",
                json={
                    "message": "I want to upload files",
                    "session_token": "test_token"
                }
            )
            
            assert response.status_code != 404, \
                f"❌ FAILED: POST /api/global/agent/analyze returned 404 (endpoint missing) - This was yesterday's bug!"
            
            assert response.status_code in [200, 400, 422], \
                f"Unexpected status: {response.status_code}"
            
            print(f"✅ POST /api/global/agent/analyze exists → {response.status_code}")

@pytest.mark.e2e
class TestMVPPillarEndpoints:
    """Test that all 4 MVP pillar endpoints exist"""
    
    @pytest.mark.asyncio
    async def test_content_upload_endpoint_exists(self, backend_server):
        """Test Content Pillar upload endpoint"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Test endpoint exists (even without actual file)
            response = await client.post(
                f"{BASE_URL}/api/mvp/content/upload",
                data={"session_token": "test_token"}
            )
            
            assert response.status_code != 404, \
                "Content upload endpoint missing"
            
            print(f"✅ POST /api/mvp/content/upload exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_content_files_endpoint_exists(self, backend_server):
        """Test Content Pillar list files endpoint"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{BASE_URL}/api/mvp/content/files",
                params={"session_token": "test_token"}
            )
            
            assert response.status_code != 404, \
                "Content files list endpoint missing"
            
            print(f"✅ GET /api/mvp/content/files exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_insights_analyze_endpoint_exists(self, backend_server):
        """Test Insights Pillar analyze endpoint"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/api/mvp/insights/analyze",
                json={"session_token": "test_token", "data": {}}
            )
            
            assert response.status_code != 404, \
                "Insights analyze endpoint missing"
            
            print(f"✅ POST /api/mvp/insights/analyze exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_operations_sop_endpoint_exists(self, backend_server):
        """Test Operations Pillar SOP generation endpoint"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/api/mvp/operations/sop/create",
                json={"session_token": "test_token", "context": "test"}
            )
            
            assert response.status_code != 404, \
                "Operations SOP endpoint missing"
            
            print(f"✅ POST /api/mvp/operations/sop/create exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_operations_workflow_endpoint_exists(self, backend_server):
        """Test Operations Pillar workflow generation endpoint"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/api/mvp/operations/workflow/create",
                json={"session_token": "test_token", "context": "test"}
            )
            
            assert response.status_code != 404, \
                "Operations workflow endpoint missing"
            
            print(f"✅ POST /api/mvp/operations/workflow/create exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_business_outcomes_roadmap_endpoint_exists(self, backend_server):
        """Test Business Outcomes roadmap generation endpoint"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/api/mvp/business-outcomes/roadmap/create",
                json={"session_token": "test_token", "context": {}}
            )
            
            assert response.status_code != 404, \
                "Business Outcomes roadmap endpoint missing"
            
            print(f"✅ POST /api/mvp/business-outcomes/roadmap/create exists → {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_business_outcomes_poc_endpoint_exists(self, backend_server):
        """Test Business Outcomes POC proposal generation endpoint"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/api/mvp/business-outcomes/poc-proposal/create",
                json={"session_token": "test_token", "context": {}}
            )
            
            assert response.status_code != 404, \
                "Business Outcomes POC proposal endpoint missing"
            
            print(f"✅ POST /api/mvp/business-outcomes/poc-proposal/create exists → {response.status_code}")

@pytest.mark.e2e
class TestCompleteUserJourney:
    """Test complete user journey through API"""
    
    @pytest.mark.asyncio
    async def test_full_registration_and_session_flow(self, backend_server):
        """Test that a user can register and get a session"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Step 1: Register user
            register_response = await client.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "email": f"test_user_{asyncio.current_task().get_name()}@example.com",
                    "password": "SecurePassword123!",
                    "name": "Test User"
                }
            )
            
            assert register_response.status_code in [200, 201], \
                f"Registration failed: {register_response.status_code} - {register_response.text}"
            
            user_data = register_response.json()
            assert "user" in user_data or "token" in user_data, \
                "Registration response missing user data or token"
            
            print(f"✅ User registered successfully")
            
            # Step 2: Create global session
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            
            assert session_response.status_code in [200, 201], \
                f"Session creation failed: {session_response.status_code}"
            
            session_data = session_response.json()
            session_token = session_data.get("session_token") or session_data.get("session_id")
            
            assert session_token, "Session response missing token"
            
            print(f"✅ Session created: {session_token}")
            
            # Step 3: Test that session can be used
            agent_response = await client.post(
                f"{BASE_URL}/api/global/agent/analyze",
                json={
                    "message": "I want to test the system",
                    "session_token": session_token
                }
            )
            
            assert agent_response.status_code in [200, 400, 422], \
                f"Agent analyze failed: {agent_response.status_code}"
            
            print(f"✅ Complete user journey works!")

@pytest.mark.e2e
class TestAPIResponseStructure:
    """Test that API responses have expected structure"""
    
    @pytest.mark.asyncio
    async def test_session_response_structure(self, backend_server):
        """Test that session endpoint returns proper structure"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(f"{BASE_URL}/api/global/session")
            
            if response.status_code == 200:
                data = response.json()
                
                # Should have session identifier
                assert "session_token" in data or "session_id" in data, \
                    "Session response missing identifier"
                
                # Should have pillar states
                assert "pillar_states" in data or "pillars" in data, \
                    "Session response missing pillar states"
                
                print(f"✅ Session response structure correct")
    
    @pytest.mark.asyncio
    async def test_auth_response_structure(self, backend_server):
        """Test that auth endpoints return proper structure"""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Try to register (may fail if user exists, that's OK)
            response = await client.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "email": "structure_test@example.com",
                    "password": "TestPassword123!",
                    "name": "Structure Test"
                }
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                
                # Should have user data
                assert "user" in data or "token" in data, \
                    "Auth response missing user data"
                
                if "user" in data:
                    user = data["user"]
                    assert "email" in user or "id" in user, \
                        "User object missing basic fields"
                
                print(f"✅ Auth response structure correct")

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])

