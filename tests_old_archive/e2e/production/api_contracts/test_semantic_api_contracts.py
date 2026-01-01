"""
API Contract Test: Semantic API Endpoints

Validates that all semantic API endpoints exist and respond correctly.
Tests the contract, not the implementation details.
"""

import pytest
import os
BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
import httpx
import logging

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.e2e, pytest.mark.api_contract, pytest.mark.critical]


@pytest.mark.asyncio
async def test_content_pillar_semantic_endpoints(backend_server, http_client):
    """Test that all Content Pillar semantic endpoints exist."""
    logger.info("🔍 Testing Content Pillar semantic endpoints...")
    
    endpoints = [
        ("GET", f"{BASE_URL}/api/v1/content-pillar/health", None),
        ("POST", f"{BASE_URL}/api/v1/content-pillar/upload-file", {"user_id": "test_user"}),
        ("GET", f"{BASE_URL}/api/v1/content-pillar/list-uploaded-files", {"user_id": "test_user"}),
        ("POST", f"{BASE_URL}/api/v1/content-pillar/process-file/test_file_id", {"user_id": "test_user"}),
        ("GET", f"{BASE_URL}/api/v1/content-pillar/get-file-details/test_file_id", {"user_id": "test_user"}),
    ]
    
    for method, path, params in endpoints:
        if method == "GET":
            response = await http_client.get(path, params=params or {})
        else:
            if "upload-file" in path:
                # File upload requires multipart form data
                files = {"file": ("test.csv", b"test,data\n1,2", "text/csv")}
                data = params or {}
                response = await http_client.post(path, files=files, data=data)
            else:
                response = await http_client.post(path, json=params or {})
        
        # Should not be 404 (endpoint missing)
        assert response.status_code != 404, f"Endpoint missing: {method} {path}"
        
        logger.info(f"✅ {method} {path} exists (status: {response.status_code})")


@pytest.mark.asyncio
async def test_insights_pillar_semantic_endpoints(backend_server, http_client):
    """Test that all Insights Pillar semantic endpoints exist."""
    logger.info("🔍 Testing Insights Pillar semantic endpoints...")
    
    endpoints = [
        ("GET", f"{BASE_URL}/api/v1/insights-pillar/health", None),
        ("POST", f"{BASE_URL}/api/v1/insights-pillar/analyze-content", {
            "user_id": "test_user",
            "file_id": "test_file_id",
            "analysis_type": "basic"
        }),
        ("GET", f"{BASE_URL}/api/v1/insights-pillar/get-analysis-results/test_analysis_id", {
            "user_id": "test_user"
        }),
    ]
    
    for method, path, params in endpoints:
        if method == "GET":
            response = await http_client.get(path, params=params or {})
        else:
            response = await http_client.post(path, json=params or {})
        
        # Should not be 404 (endpoint missing)
        assert response.status_code != 404, f"Endpoint missing: {method} {path}"
        
        logger.info(f"✅ {method} {path} exists (status: {response.status_code})")


@pytest.mark.asyncio
async def test_operations_pillar_semantic_endpoints(backend_server, http_client):
    """Test that all Operations Pillar semantic endpoints exist."""
    logger.info("🔍 Testing Operations Pillar semantic endpoints...")
    
    endpoints = [
        ("GET", f"{BASE_URL}/api/v1/operations-pillar/health", None),
        ("POST", f"{BASE_URL}/api/v1/operations-pillar/create-standard-operating-procedure", {
            "user_id": "test_user",
            "title": "Test SOP",
            "description": "Test description"
        }),
        ("GET", f"{BASE_URL}/api/v1/operations-pillar/list-standard-operating-procedures", {
            "user_id": "test_user"
        }),
        ("POST", f"{BASE_URL}/api/v1/operations-pillar/create-workflow", {
            "user_id": "test_user",
            "name": "Test Workflow",
            "description": "Test description"
        }),
        ("GET", f"{BASE_URL}/api/v1/operations-pillar/list-workflows", {
            "user_id": "test_user"
        }),
        ("POST", f"{BASE_URL}/api/v1/operations-pillar/convert-sop-to-workflow", {
            "user_id": "test_user",
            "sop_id": "test_sop_id"
        }),
        ("POST", f"{BASE_URL}/api/v1/operations-pillar/convert-workflow-to-sop", {
            "user_id": "test_user",
            "workflow_id": "test_workflow_id"
        }),
    ]
    
    for method, path, params in endpoints:
        if method == "GET":
            response = await http_client.get(path, params=params or {})
        else:
            response = await http_client.post(path, json=params or {})
        
        # Should not be 404 (endpoint missing)
        assert response.status_code != 404, f"Endpoint missing: {method} {path}"
        
        logger.info(f"✅ {method} {path} exists (status: {response.status_code})")


@pytest.mark.asyncio
async def test_business_outcomes_pillar_semantic_endpoints(backend_server, http_client):
    """Test that all Business Outcomes Pillar semantic endpoints exist."""
    logger.info("🔍 Testing Business Outcomes Pillar semantic endpoints...")
    
    endpoints = [
        ("GET", f"{BASE_URL}/api/v1/business-outcomes-pillar/health", None),
        ("POST", f"{BASE_URL}/api/v1/business-outcomes-pillar/generate-strategic-roadmap", {
            "user_id": "test_user",
            "pillar_outputs": {}
        }),
    ]
    
    for method, path, params in endpoints:
        if method == "GET":
            response = await http_client.get(path, params=params or {})
        else:
            response = await http_client.post(path, json=params or {})
        
        # Should not be 404 (endpoint missing)
        assert response.status_code != 404, f"Endpoint missing: {method} {path}"
        
        logger.info(f"✅ {method} {path} exists (status: {response.status_code})")


@pytest.mark.asyncio
async def test_session_semantic_endpoints(backend_server, http_client):
    """Test that all Session semantic endpoints exist."""
    logger.info("🔍 Testing Session semantic endpoints...")
    
    endpoints = [
        ("POST", f"{BASE_URL}/api/v1/session/create-user-session", {
            "user_id": "test_user",
            "session_type": "mvp"
        }),
        ("GET", f"{BASE_URL}/api/v1/session/get-session-details/test_session_id", {
            "user_id": "test_user"
        }),
        ("GET", f"{BASE_URL}/api/v1/session/get-session-state/test_session_id", {
            "user_id": "test_user"
        }),
    ]
    
    for method, path, params in endpoints:
        if method == "GET":
            response = await http_client.get(path, params=params or {})
        else:
            response = await http_client.post(path, json=params or {})
        
        # Should not be 404 (endpoint missing)
        assert response.status_code != 404, f"Endpoint missing: {method} {path}"
        
        logger.info(f"✅ {method} {path} exists (status: {response.status_code})")


@pytest.mark.asyncio
async def test_guide_agent_semantic_endpoints(backend_server, http_client):
    """Test that all Guide Agent semantic endpoints exist."""
    logger.info("🔍 Testing Guide Agent semantic endpoints...")
    
    endpoints = [
        ("GET", f"{BASE_URL}/api/v1/guide-agent/health", None),
        ("POST", f"{BASE_URL}/api/v1/guide-agent/analyze-user-intent", {
            "user_id": "test_user",
            "message": "I want to upload files",
            "session_token": "test_token"
        }),
        ("POST", f"{BASE_URL}/api/v1/guide-agent/get-journey-guidance", {
            "user_id": "test_user",
            "session_token": "test_token",
            "current_pillar": "content"
        }),
    ]
    
    for method, path, params in endpoints:
        if method == "GET":
            response = await http_client.get(path, params=params or {})
        else:
            response = await http_client.post(path, json=params or {})
        
        # Should not be 404 (endpoint missing)
        assert response.status_code != 404, f"Endpoint missing: {method} {path}"
        
        logger.info(f"✅ {method} {path} exists (status: {response.status_code})")


@pytest.mark.asyncio
async def test_liaison_agents_semantic_endpoints(backend_server, http_client):
    """Test that all Liaison Agents semantic endpoints exist."""
    logger.info("🔍 Testing Liaison Agents semantic endpoints...")
    
    endpoints = [
        ("GET", f"{BASE_URL}/api/v1/liaison-agents/health", None),
        ("POST", f"{BASE_URL}/api/v1/liaison-agents/send-message-to-pillar-agent", {
            "user_id": "test_user",
            "message": "Test message",
            "pillar": "content",
            "session_token": "test_token"
        }),
        ("GET", f"{BASE_URL}/api/v1/liaison-agents/get-pillar-conversation-history/test_session_id/content", {
            "user_id": "test_user"
        }),
    ]
    
    for method, path, params in endpoints:
        if method == "GET":
            response = await http_client.get(path, params=params or {})
        else:
            response = await http_client.post(path, json=params or {})
        
        # Should not be 404 (endpoint missing)
        assert response.status_code != 404, f"Endpoint missing: {method} {path}"
        
        logger.info(f"✅ {method} {path} exists (status: {response.status_code})")


