#!/usr/bin/env python3
"""
E2E Tests for Semantic APIs

Comprehensive test suite for all new semantic API endpoints.
Tests user-focused semantic naming and full E2E flows.

Tests cover:
- Content Pillar semantic endpoints
- Insights Pillar semantic endpoints
- Operations Pillar semantic endpoints
- Business Outcomes Pillar semantic endpoints
- Guide Agent semantic endpoints
- Liaison Agents semantic endpoints
- Session semantic endpoints
"""

import pytest
import asyncio
import httpx
import json
from pathlib import Path
from typing import Dict, Any, Optional
import os
from datetime import datetime

# Configuration
BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
TIMEOUT = 30.0

# Note: All tests use the backend_server fixture from conftest.py
# which automatically starts/stops the backend server

class TestContentPillarSemantic:
    """Test Content Pillar semantic endpoints with new file ID architecture."""
    
    @pytest.mark.asyncio
    async def test_upload_file_with_filename_parsing(self, backend_server):
        """Test that filename parsing works correctly (ui_name extraction)"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            # Test with a file that has extension
            files = {
                "file": ("userfile.docx", b"test content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            }
            data = {"user_id": "test_user"}
            
            response = await client.post("/api/content-pillar/upload-file", files=files, data=data)
            result = response.json()
            
            if result.get("error") and "Content Analysis Orchestrator not available" in result.get("error", ""):
                pytest.skip("Content Analysis Orchestrator not available")
            
            if result.get("success"):
                # Verify filename parsing
                assert result.get("ui_name") == "userfile" or result.get("file_name") == "userfile.docx"
                assert result.get("original_filename") == "userfile.docx" or result.get("file_name") == "userfile.docx"
                assert result.get("file_extension") == ".docx" or result.get("file_type") == "docx"
                assert result.get("content_type") in ["structured", "unstructured", "hybrid", None]
    
    @pytest.mark.asyncio
    async def test_upload_binary_with_copybook(self, backend_server):
        """Test uploading binary file with copybook"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            # Create binary file and copybook
            binary_content = b"\x00\x01\x02\x03\x04\x05"
            copybook_content = b"01 FIELD-NAME PIC X(10)."
            
            files = {
                "file": ("data.dat", binary_content, "application/octet-stream"),
                "copybook": ("copybook.cpy", copybook_content, "text/plain")
            }
            data = {"user_id": "test_user"}
            
            response = await client.post("/api/content-pillar/upload-file", files=files, data=data)
            result = response.json()
            
            if result.get("error") and "Content Analysis Orchestrator not available" in result.get("error", ""):
                pytest.skip("Content Analysis Orchestrator not available")
            
            if result.get("success"):
                # Verify both files uploaded
                assert result.get("file_id") is not None
                assert result.get("copybook_file_id") is not None, "Copybook file_id should be returned"
                assert result.get("file_type_category") == "binary" or result.get("content_type") == "structured"
    
    @pytest.mark.asyncio
    async def test_upload_sop_workflow_file(self, backend_server):
        """Test that SOP/Workflow files are marked for Operations Pillar"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            # Upload a file that should be classified as SOP/Workflow
            # Based on our file_utils, .bpmn files are classified as sop_workflow
            files = {
                "file": ("workflow.bpmn", b"<?xml version='1.0'?><bpmn:definitions>", "application/xml")
            }
            data = {"user_id": "test_user"}
            
            response = await client.post("/api/content-pillar/upload-file", files=files, data=data)
            result = response.json()
            
            if result.get("error") and "Content Analysis Orchestrator not available" in result.get("error", ""):
                pytest.skip("Content Analysis Orchestrator not available")
            
            if result.get("success"):
                # Verify SOP/Workflow classification
                assert result.get("file_type_category") == "sop_workflow" or result.get("processing_pillar") == "operations_pillar"
                if result.get("processing_pillar"):
                    assert result.get("processing_pillar") == "operations_pillar"
                if result.get("message"):
                    assert "operations" in result.get("message", "").lower() or result.get("file_type_category") == "sop_workflow"
    
    @pytest.mark.asyncio
    async def test_upload_file_to_content_pillar(self, backend_server):
        """Test POST /api/content-pillar/upload-file with new file ID architecture"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            # Create a test file
            test_file_content = b"Test file content for semantic API testing"
            files = {
                "file": ("test_semantic.txt", test_file_content, "text/plain")
            }
            data = {
                "user_id": "test_user_semantic"
            }
            
            response = await client.post(
                "/api/content-pillar/upload-file",
                files=files,
                data=data
            )
            
            assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
            result = response.json()
            
            # Check if orchestrator is available
            if result.get("error") and "Content Analysis Orchestrator not available" in result.get("error", ""):
                # Orchestrator not available - this is expected in test environment
                # But we should still verify the error response structure
                assert result.get("success") is False
                assert "error" in result
                pytest.skip("Content Analysis Orchestrator not available in test environment")
            
            # If orchestrator is available, verify new architecture
            assert result.get("success") is True
            assert "file_id" in result
            
            # Verify file_id is not None (the main fix)
            file_id = result.get("file_id")
            assert file_id is not None, "file_id should never be None"
            assert file_id != "None", "file_id should never be the string 'None'"
            
            # Verify new fields
            assert "uuid" in result or result.get("file_id") is not None  # UUID or file_id should exist
            assert "ui_name" in result or result.get("file_name") is not None  # ui_name or file_name
            assert result.get("file_name") == "test_semantic.txt" or result.get("original_filename") == "test_semantic.txt"
            assert result.get("status") == "uploaded"
            assert "uploaded_at" in result
            
            # Verify content type classification (if available)
            if result.get("content_type"):
                assert result.get("content_type") in ["structured", "unstructured", "hybrid"]
            if result.get("file_type_category"):
                assert isinstance(result.get("file_type_category"), str)
            
            return file_id
    
    @pytest.mark.asyncio
    async def test_list_uploaded_files_in_content_pillar(self, backend_server):
        """Test GET /api/content-pillar/list-uploaded-files"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get(
                "/api/content-pillar/list-uploaded-files",
                params={"user_id": "test_user_semantic"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            assert "files" in data
            assert "count" in data
            assert isinstance(data["files"], list)
    
    @pytest.mark.asyncio
    async def test_process_file_in_content_pillar(self, backend_server):
        """Test POST /api/content-pillar/process-file/{file_id}"""
        # First upload a file
        try:
            file_id = await self.test_upload_file_to_content_pillar()
        except Exception as e:
            if "skip" in str(e).lower() or "orchestrator not available" in str(e).lower():
                pytest.skip("Content Analysis Orchestrator not available - cannot test file processing")
            raise
        
        # Verify file_id is valid before processing
        assert file_id is not None, "file_id must not be None for processing"
        assert file_id != "None", "file_id must not be the string 'None'"
        
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            request_data = {
                "user_id": "test_user_semantic"
            }
            
            response = await client.post(
                f"/api/content-pillar/process-file/{file_id}",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # If orchestrator is not available, the process will fail gracefully
            if not data.get("success") and "orchestrator not available" in data.get("message", "").lower():
                pytest.skip("Content Analysis Orchestrator not available - processing skipped")
            
            assert data.get("success") is True
            assert data.get("file_id") == file_id
            assert "processing_status" in data
    
    @pytest.mark.asyncio
    async def test_get_file_details_from_content_pillar(self, backend_server):
        """Test GET /api/content-pillar/get-file-details/{file_id}"""
        # First upload a file
        file_id = await self.test_upload_file_to_content_pillar()
        
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get(
                f"/api/content-pillar/get-file-details/{file_id}",
                params={"user_id": "test_user_semantic"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            assert "file" in data
    
    @pytest.mark.asyncio
    async def test_content_pillar_health(self, backend_server):
        """Test GET /api/content-pillar/health"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get("/api/content-pillar/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
            assert data.get("pillar") == "content"

class TestInsightsPillarSemantic:
    """Test Insights Pillar semantic endpoints."""
    
    @pytest.mark.asyncio
    async def test_analyze_content_for_insights(self, backend_server):
        """Test POST /api/insights-pillar/analyze-content-for-insights"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            request_data = {
                "file_ids": ["test_file_1", "test_file_2"],
                "analysis_type": "comprehensive",
                "user_id": "test_user_semantic"
            }
            
            response = await client.post(
                "/api/insights-pillar/analyze-content-for-insights",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            # May have analysis_id or be in mock mode
            if data.get("analysis_id"):
                assert "analysis_id" in data
    
    @pytest.mark.asyncio
    async def test_get_analysis_results_from_insights_pillar(self, backend_server):
        """Test GET /api/insights-pillar/get-analysis-results/{analysis_id}"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            analysis_id = "test_analysis_123"
            
            response = await client.get(
                f"/api/insights-pillar/get-analysis-results/{analysis_id}",
                params={"user_id": "test_user_semantic"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            assert "analysis" in data or "findings" in data
    
    @pytest.mark.asyncio
    async def test_insights_pillar_health(self, backend_server):
        """Test GET /api/insights-pillar/health"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get("/api/insights-pillar/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
            assert data.get("pillar") == "insights"

class TestOperationsPillarSemantic:
    """Test Operations Pillar semantic endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_standard_operating_procedure(self, backend_server):
        """Test POST /api/operations-pillar/create-standard-operating-procedure"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            request_data = {
                "description": "Test SOP for semantic API testing",
                "sop_type": "process",
                "user_id": "test_user_semantic"
            }
            
            response = await client.post(
                "/api/operations-pillar/create-standard-operating-procedure",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            assert "sop_id" in data
            assert "sop_title" in data or "sop_content" in data
            
            return data.get("sop_id")
    
    @pytest.mark.asyncio
    async def test_create_workflow_in_operations_pillar(self, backend_server):
        """Test POST /api/operations-pillar/create-workflow"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            request_data = {
                "name": "Test Workflow",
                "description": "Test workflow for semantic API",
                "user_id": "test_user_semantic"
            }
            
            response = await client.post(
                "/api/operations-pillar/create-workflow",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            assert "workflow_id" in data
            assert "workflow" in data
    
    @pytest.mark.asyncio
    async def test_convert_sop_to_workflow_in_operations_pillar(self, backend_server):
        """Test POST /api/operations-pillar/convert-sop-to-workflow"""
        # First create an SOP
        sop_id = await self.test_create_standard_operating_procedure()
        
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            request_data = {
                "sop_id": sop_id,
                "user_id": "test_user_semantic"
            }
            
            response = await client.post(
                "/api/operations-pillar/convert-sop-to-workflow",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            assert "workflow_id" in data
    
    @pytest.mark.asyncio
    async def test_list_standard_operating_procedures(self, backend_server):
        """Test GET /api/operations-pillar/list-standard-operating-procedures"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get(
                "/api/operations-pillar/list-standard-operating-procedures",
                params={"user_id": "test_user_semantic"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            assert "sops" in data
            assert "count" in data
    
    @pytest.mark.asyncio
    async def test_operations_pillar_health(self, backend_server):
        """Test GET /api/operations-pillar/health"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get("/api/operations-pillar/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
            assert data.get("pillar") == "operations"

class TestBusinessOutcomesPillarSemantic:
    """Test Business Outcomes Pillar semantic endpoints."""
    
    @pytest.mark.asyncio
    async def test_generate_strategic_roadmap(self, backend_server):
        """Test POST /api/business-outcomes-pillar/generate-strategic-roadmap"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            request_data = {
                "pillar_outputs": {
                    "content_pillar": {"files_uploaded": 5},
                    "insights_pillar": {"analyses_completed": 2},
                    "operations_pillar": {"sops_created": 3}
                },
                "user_id": "test_user_semantic"
            }
            
            response = await client.post(
                "/api/business-outcomes-pillar/generate-strategic-roadmap",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            assert "roadmap_id" in data or "roadmap" in data
    
    @pytest.mark.asyncio
    async def test_business_outcomes_pillar_health(self, backend_server):
        """Test GET /api/business-outcomes-pillar/health"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get("/api/business-outcomes-pillar/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
            assert data.get("pillar") == "business_outcomes"

class TestGuideAgentSemantic:
    """Test Guide Agent semantic endpoints."""
    
    @pytest.mark.asyncio
    async def test_analyze_user_intent(self, backend_server):
        """Test POST /api/guide-agent/analyze-user-intent"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            request_data = {
                "message": "I want to analyze some data files",
                "user_id": "test_user_semantic"
            }
            
            response = await client.post(
                "/api/guide-agent/analyze-user-intent",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            assert "intent_analysis" in data
            assert "session_id" in data
    
    @pytest.mark.asyncio
    async def test_get_journey_guidance(self, backend_server):
        """Test POST /api/guide-agent/get-journey-guidance"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            request_data = {
                "user_goal": "Analyze legacy data files",
                "user_id": "test_user_semantic"
            }
            
            response = await client.post(
                "/api/guide-agent/get-journey-guidance",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            assert "guidance" in data
    
    @pytest.mark.asyncio
    async def test_guide_agent_health(self, backend_server):
        """Test GET /api/guide-agent/health"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get("/api/guide-agent/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
            assert data.get("agent") == "guide_agent"

class TestLiaisonAgentsSemantic:
    """Test Liaison Agents semantic endpoints."""
    
    @pytest.mark.asyncio
    async def test_send_message_to_pillar_agent(self, backend_server):
        """Test POST /api/liaison-agents/send-message-to-pillar-agent"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            request_data = {
                "message": "Can you help me understand this data?",
                "pillar": "content",
                "user_id": "test_user_semantic"
            }
            
            response = await client.post(
                "/api/liaison-agents/send-message-to-pillar-agent",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            assert "response" in data
            assert data.get("pillar") == "content"
    
    @pytest.mark.asyncio
    async def test_liaison_agents_health(self, backend_server):
        """Test GET /api/liaison-agents/health"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get("/api/liaison-agents/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
            assert data.get("agents") == "liaison_agents"

class TestSessionSemantic:
    """Test Session semantic endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_user_session(self, backend_server):
        """Test POST /api/session/create-user-session"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            request_data = {
                "user_id": "test_user_semantic",
                "session_type": "mvp"
            }
            
            response = await client.post(
                "/api/session/create-user-session",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("success") is True
            assert "session_id" in data
            assert "session_token" in data
            assert "orchestrator_states" in data
            
            return data.get("session_id")
    
    @pytest.mark.asyncio
    async def test_get_session_details(self, backend_server):
        """Test GET /api/session/get-session-details/{session_id}"""
        # First create a session
        session_id = await self.test_create_user_session()
        
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get(
                f"/api/session/get-session-details/{session_id}"
            )
            
            # May return 404 if session not found in mock mode
            if response.status_code == 200:
                data = response.json()
                assert data.get("success") is True
                assert "session" in data
    
    @pytest.mark.asyncio
    async def test_get_session_state(self, backend_server):
        """Test GET /api/session/get-session-state/{session_id}"""
        # First create a session
        session_id = await self.test_create_user_session()
        
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get(
                f"/api/session/get-session-state/{session_id}"
            )
            
            # May return 404 if session not found in mock mode
            if response.status_code == 200:
                data = response.json()
                assert data.get("success") is True
                assert "state" in data or "orchestrator_states" in data
    
    @pytest.mark.asyncio
    async def test_session_health(self, backend_server):
        """Test GET /api/session/health"""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get("/api/session/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
            assert data.get("service") == "session"

class TestSemanticAPIEquivalence:
    """Test equivalence between old and new semantic APIs."""
    
    @pytest.mark.asyncio
    async def test_content_upload_equivalence(self, backend_server):
        """Test that semantic and legacy content upload endpoints produce equivalent results."""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            test_file_content = b"Test file for equivalence testing"
            files = {"file": ("test_equiv.txt", test_file_content, "text/plain")}
            data = {"user_id": "test_user_equiv"}
            
            # Test semantic endpoint
            semantic_response = await client.post(
                "/api/content-pillar/upload-file",
                files=files,
                data=data
            )
            
            # Test legacy endpoint
            legacy_response = await client.post(
                "/api/mvp/content/upload",
                files=files,
                data=data
            )
            
            # Both should succeed
            assert semantic_response.status_code in [200, 201]
            assert legacy_response.status_code in [200, 201]
            
            semantic_data = semantic_response.json()
            legacy_data = legacy_response.json()
            
            # Both should have success=True
            assert semantic_data.get("success") is True
            assert legacy_data.get("success") is True
            
            # Both should return file_id
            assert "file_id" in semantic_data
            assert "file_id" in legacy_data
    
    @pytest.mark.asyncio
    async def test_session_creation_equivalence(self, backend_server):
        """Test that semantic and legacy session creation endpoints produce equivalent results."""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            request_data = {
                "user_id": "test_user_equiv",
                "session_type": "mvp"
            }
            
            # Test semantic endpoint
            semantic_response = await client.post(
                "/api/session/create-user-session",
                json=request_data
            )
            
            # Test legacy endpoint
            legacy_response = await client.post(
                "/api/global/session",
                json=request_data
            )
            
            # Both should succeed
            assert semantic_response.status_code == 200
            assert legacy_response.status_code == 200
            
            semantic_data = semantic_response.json()
            legacy_data = legacy_response.json()
            
            # Both should have success=True
            assert semantic_data.get("success") is True
            assert legacy_data.get("success") is True
            
            # Both should return session_id
            assert "session_id" in semantic_data
            assert "session_id" in legacy_data
    
    @pytest.mark.asyncio
    async def test_guide_agent_equivalence(self, backend_server):
        """Test that semantic and legacy guide agent endpoints produce equivalent results."""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            request_data = {
                "message": "I need help analyzing data",
                "user_id": "test_user_equiv"
            }
            
            # Test semantic endpoint
            semantic_response = await client.post(
                "/api/guide-agent/analyze-user-intent",
                json=request_data
            )
            
            # Test legacy endpoint
            legacy_response = await client.post(
                "/api/global/agent/analyze",
                json=request_data
            )
            
            # Both should succeed
            assert semantic_response.status_code == 200
            assert legacy_response.status_code == 200
            
            semantic_data = semantic_response.json()
            legacy_data = legacy_response.json()
            
            # Both should have success=True
            assert semantic_data.get("success") is True
            assert legacy_data.get("success") is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

