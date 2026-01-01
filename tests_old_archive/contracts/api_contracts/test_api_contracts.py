#!/usr/bin/env python3
"""
API Contract Testing Framework

This test suite validates API contracts between all services to ensure
proper communication and integration. This prevents integration issues
and ensures service compatibility.

CRITICAL REQUIREMENT: These tests validate REAL API contracts, not mocks.
We need to prove the APIs actually work as designed.
"""

import pytest
import asyncio

import os
import json
from pathlib import Path
from typing import Dict, Any, List
import httpx

# Add the platform directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../symphainy-platform'))

class TestAPIContracts:
    """Test API contracts between all services."""

    @pytest.fixture
    def base_url(self):
        """Base URL for API testing."""
        return "http://localhost:8000"

    @pytest.fixture
    def test_headers(self):
        """Test headers for API requests."""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @pytest.fixture
    def test_tenant_context(self):
        """Test tenant context for multi-tenant testing."""
        return {
            "tenant_id": "test_tenant_123",
            "user_id": "test_user_123",
            "session_id": "test_session_123"
        }

    # =============================================================================
    # HEALTH CHECK API CONTRACTS
    # =============================================================================

    async def test_health_check_api_contract(self, base_url, test_headers):
        """Test health check API contract compliance."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health", headers=test_headers)
            
            # Test status code compliance
            assert response.status_code == 200, f"Health check should return 200, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Health check response should be a dictionary"
            
            # Test required fields
            assert "status" in response_data, "Health check response should have 'status' field"
            assert "timestamp" in response_data, "Health check response should have 'timestamp' field"
            
            # Test status value
            assert response_data["status"] in ["healthy", "unhealthy"], "Status should be 'healthy' or 'unhealthy'"

    async def test_services_health_api_contract(self, base_url, test_headers):
        """Test services health API contract compliance."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/services", headers=test_headers)
            
            # Test status code compliance
            assert response.status_code == 200, f"Services health should return 200, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Services health response should be a dictionary"
            
            # Test required fields
            assert "services" in response_data, "Services health response should have 'services' field"
            assert isinstance(response_data["services"], dict), "Services should be a dictionary"

    # =============================================================================
    # CONTENT PILLAR API CONTRACTS
    # =============================================================================

    async def test_content_pillar_health_api_contract(self, base_url, test_headers):
        """Test content pillar health API contract compliance."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/content/health", headers=test_headers)
            
            # Test status code compliance
            assert response.status_code == 200, f"Content pillar health should return 200, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Content pillar health response should be a dictionary"
            
            # Test required fields
            assert "status" in response_data, "Content pillar health response should have 'status' field"
            assert "pillar" in response_data, "Content pillar health response should have 'pillar' field"
            assert response_data["pillar"] == "content", "Pillar should be 'content'"

    async def test_content_pillar_upload_api_contract(self, base_url, test_headers, test_tenant_context):
        """Test content pillar upload API contract compliance."""
        # Test request schema validation
        upload_data = {
            "filename": "test_document.pdf",
            "content_type": "application/pdf",
            "size": 1024,
            "tenant_id": test_tenant_context["tenant_id"],
            "user_id": test_tenant_context["user_id"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/content/upload",
                json=upload_data,
                headers=test_headers
            )
            
            # Test status code compliance (may be 200, 201, or 400 depending on implementation)
            assert response.status_code in [200, 201, 400], f"Upload should return 200/201/400, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Upload response should be a dictionary"
            
            # Test required fields based on status code
            if response.status_code in [200, 201]:
                assert "file_id" in response_data, "Upload response should have 'file_id' field"
                assert "status" in response_data, "Upload response should have 'status' field"
            else:
                assert "error" in response_data, "Error response should have 'error' field"

    async def test_content_pillar_files_api_contract(self, base_url, test_headers, test_tenant_context):
        """Test content pillar files API contract compliance."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/api/content/files",
                headers=test_headers,
                params={"tenant_id": test_tenant_context["tenant_id"]}
            )
            
            # Test status code compliance
            assert response.status_code == 200, f"Files list should return 200, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Files list response should be a dictionary"
            
            # Test required fields
            assert "files" in response_data, "Files list response should have 'files' field"
            assert isinstance(response_data["files"], list), "Files should be a list"

    async def test_content_pillar_parse_api_contract(self, base_url, test_headers, test_tenant_context):
        """Test content pillar parse API contract compliance."""
        parse_data = {
            "file_id": "test_file_123",
            "tenant_id": test_tenant_context["tenant_id"],
            "user_id": test_tenant_context["user_id"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/content/parse",
                json=parse_data,
                headers=test_headers
            )
            
            # Test status code compliance
            assert response.status_code in [200, 400, 404], f"Parse should return 200/400/404, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Parse response should be a dictionary"

    # =============================================================================
    # INSIGHTS PILLAR API CONTRACTS
    # =============================================================================

    async def test_insights_pillar_health_api_contract(self, base_url, test_headers):
        """Test insights pillar health API contract compliance."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/insights/health", headers=test_headers)
            
            # Test status code compliance
            assert response.status_code == 200, f"Insights pillar health should return 200, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Insights pillar health response should be a dictionary"
            
            # Test required fields
            assert "status" in response_data, "Insights pillar health response should have 'status' field"
            assert "pillar" in response_data, "Insights pillar health response should have 'pillar' field"
            assert response_data["pillar"] == "insights", "Pillar should be 'insights'"

    async def test_insights_pillar_analyze_api_contract(self, base_url, test_headers, test_tenant_context):
        """Test insights pillar analyze API contract compliance."""
        analyze_data = {
            "file_id": "test_file_123",
            "analysis_type": "basic",
            "tenant_id": test_tenant_context["tenant_id"],
            "user_id": test_tenant_context["user_id"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/insights/analyze",
                json=analyze_data,
                headers=test_headers
            )
            
            # Test status code compliance
            assert response.status_code in [200, 400, 404], f"Analyze should return 200/400/404, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Analyze response should be a dictionary"

    async def test_insights_pillar_chat_api_contract(self, base_url, test_headers, test_tenant_context):
        """Test insights pillar chat API contract compliance."""
        chat_data = {
            "message": "What insights can you provide about my data?",
            "context": {"file_id": "test_file_123"},
            "tenant_id": test_tenant_context["tenant_id"],
            "user_id": test_tenant_context["user_id"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/insights/chat",
                json=chat_data,
                headers=test_headers
            )
            
            # Test status code compliance
            assert response.status_code in [200, 400], f"Chat should return 200/400, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Chat response should be a dictionary"

    # =============================================================================
    # OPERATIONS PILLAR API CONTRACTS
    # =============================================================================

    async def test_operations_pillar_health_api_contract(self, base_url, test_headers):
        """Test operations pillar health API contract compliance."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/operations/health", headers=test_headers)
            
            # Test status code compliance
            assert response.status_code == 200, f"Operations pillar health should return 200, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Operations pillar health response should be a dictionary"
            
            # Test required fields
            assert "status" in response_data, "Operations pillar health response should have 'status' field"
            assert "pillar" in response_data, "Operations pillar health response should have 'pillar' field"
            assert response_data["pillar"] == "operations", "Pillar should be 'operations'"

    async def test_operations_pillar_sop_builder_api_contract(self, base_url, test_headers, test_tenant_context):
        """Test operations pillar SOP builder API contract compliance."""
        sop_data = {
            "process_name": "Test Process",
            "description": "Test process description",
            "tenant_id": test_tenant_context["tenant_id"],
            "user_id": test_tenant_context["user_id"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/operations/sop-builder",
                json=sop_data,
                headers=test_headers
            )
            
            # Test status code compliance
            assert response.status_code in [200, 400], f"SOP builder should return 200/400, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "SOP builder response should be a dictionary"

    async def test_operations_pillar_workflow_builder_api_contract(self, base_url, test_headers, test_tenant_context):
        """Test operations pillar workflow builder API contract compliance."""
        workflow_data = {
            "workflow_name": "Test Workflow",
            "description": "Test workflow description",
            "tenant_id": test_tenant_context["tenant_id"],
            "user_id": test_tenant_context["user_id"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/operations/workflow-builder",
                json=workflow_data,
                headers=test_headers
            )
            
            # Test status code compliance
            assert response.status_code in [200, 400], f"Workflow builder should return 200/400, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Workflow builder response should be a dictionary"

    # =============================================================================
    # BUSINESS OUTCOMES PILLAR API CONTRACTS
    # =============================================================================

    async def test_business_outcomes_pillar_health_api_contract(self, base_url, test_headers):
        """Test business outcomes pillar health API contract compliance."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/business-outcomes/health", headers=test_headers)
            
            # Test status code compliance
            assert response.status_code == 200, f"Business outcomes pillar health should return 200, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Business outcomes pillar health response should be a dictionary"
            
            # Test required fields
            assert "status" in response_data, "Business outcomes pillar health response should have 'status' field"
            assert "pillar" in response_data, "Business outcomes pillar health response should have 'pillar' field"
            assert response_data["pillar"] == "business-outcomes", "Pillar should be 'business-outcomes'"

    async def test_business_outcomes_pillar_strategic_planning_api_contract(self, base_url, test_headers, test_tenant_context):
        """Test business outcomes pillar strategic planning API contract compliance."""
        planning_data = {
            "objective": "Test strategic objective",
            "timeframe": "6 months",
            "tenant_id": test_tenant_context["tenant_id"],
            "user_id": test_tenant_context["user_id"]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/business-outcomes/strategic-planning",
                json=planning_data,
                headers=test_headers
            )
            
            # Test status code compliance
            assert response.status_code in [200, 400], f"Strategic planning should return 200/400, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Strategic planning response should be a dictionary"

    async def test_business_outcomes_pillar_metrics_api_contract(self, base_url, test_headers, test_tenant_context):
        """Test business outcomes pillar metrics API contract compliance."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/api/business-outcomes/metrics",
                headers=test_headers,
                params={"tenant_id": test_tenant_context["tenant_id"]}
            )
            
            # Test status code compliance
            assert response.status_code == 200, f"Metrics should return 200, got {response.status_code}"
            
            # Test response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Metrics response should be a dictionary"
            
            # Test required fields
            assert "metrics" in response_data, "Metrics response should have 'metrics' field"
            assert isinstance(response_data["metrics"], dict), "Metrics should be a dictionary"

    # =============================================================================
    # ERROR RESPONSE CONTRACT VALIDATION
    # =============================================================================

    async def test_error_response_contracts(self, base_url, test_headers):
        """Test error response contract compliance."""
        # Test 404 error contract
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/nonexistent", headers=test_headers)
            
            # Test status code compliance
            assert response.status_code == 404, f"Nonexistent endpoint should return 404, got {response.status_code}"
            
            # Test error response format
            response_data = response.json()
            assert isinstance(response_data, dict), "Error response should be a dictionary"
            assert "error" in response_data, "Error response should have 'error' field"

    # =============================================================================
    # MULTI-TENANT API CONTRACT VALIDATION
    # =============================================================================

    async def test_multi_tenant_api_contracts(self, base_url, test_headers):
        """Test multi-tenant API contract compliance."""
        # Test that APIs require tenant context
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/content/files", headers=test_headers)
            
            # Should either require tenant_id or return appropriate error
            assert response.status_code in [200, 400, 401], f"Files API should handle tenant context, got {response.status_code}"
            
            if response.status_code in [400, 401]:
                response_data = response.json()
                assert "error" in response_data, "Error response should have 'error' field"

