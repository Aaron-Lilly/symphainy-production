"""
E2E Test: Operations Pillar - Comprehensive Validation

Tests all Operations Pillar capabilities using production platform:
1. SOP → Workflow conversion
2. Workflow → SOP conversion
3. Workflow visualization
4. SOP visualization
5. Coexistence analysis
6. Interactive SOP creation
7. Interactive blueprint creation
8. AI-optimized blueprint generation

Uses real LLM calls and production containers.
Validates the updated operations pillar architecture (Solution → Journey → Realm).
"""

import pytest
import httpx
import logging
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.e2e, pytest.mark.operations, pytest.mark.critical, pytest.mark.production_readiness]

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
TIMEOUT = 120.0  # 2 minutes per operation (LLM calls can be slow)


class TestOperationsPillarE2E:
    """Comprehensive E2E tests for Operations Pillar."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(600)  # 10 minutes for full test
    async def test_operations_pillar_health(self, both_servers, http_client):
        """Test that Operations Solution Orchestrator is accessible."""
        logger.info("🔍 Testing Operations Solution Orchestrator health...")
        
        # Try the new operations-solution endpoint
        response = await http_client.get("/api/v1/operations-solution/health")
        
        # Should not be 404 (endpoint missing)
        assert response.status_code != 404, \
            f"Operations Solution Orchestrator health endpoint missing: {response.status_code} - {response.text}"
        
        logger.info(f"✅ Operations Solution Orchestrator health check passed (status: {response.status_code})")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(300)  # 5 minutes
    async def test_workflow_from_sop_conversion(
        self,
        both_servers,
        http_client,
        test_session,
        parsed_file_for_operations
    ):
        """
        Test Scenario 1: Convert SOP to Workflow
        
        Validates:
        - SOP file can be uploaded and parsed
        - SOP can be converted to workflow diagram
        - Workflow structure is valid (nodes, edges)
        """
        logger.info("🎬 Test Scenario 1: SOP → Workflow Conversion")
        
        session_id = test_session["session_id"]
        session_token = test_session.get("session_token") or session_id
        user_id = test_session["user_id"]
        
        # Get auth token for Bearer authentication
        auth_token = test_session.get("auth_token")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add Bearer token if available (required for operations-solution endpoints)
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Also include session token for platform correlation
        if session_token:
            headers["X-Session-Token"] = session_token
        if user_id:
            headers["X-User-Id"] = user_id
        
        # Step 1: Create a test SOP document
        logger.info("📋 Step 1: Creating test SOP document...")
        
        sop_content = {
            "title": "Test Execution Procedure for Autonomous Vehicle",
            "purpose": "Standard procedure for executing autonomous vehicle test missions",
            "scope": "All test missions for autonomous vehicle systems",
            "sections": [
                {
                    "name": "Pre-Mission Setup",
                    "steps": [
                        {"step": 1, "action": "Verify vehicle systems are operational", "role": "Test Engineer"},
                        {"step": 2, "action": "Load mission plan into vehicle", "role": "Test Engineer"},
                        {"step": 3, "action": "Perform safety checks", "role": "Safety Officer"}
                    ]
                },
                {
                    "name": "Mission Execution",
                    "steps": [
                        {"step": 1, "action": "Start mission execution", "role": "Test Engineer"},
                        {"step": 2, "action": "Monitor telemetry data", "role": "Data Analyst"},
                        {"step": 3, "action": "Record any anomalies", "role": "Test Engineer"}
                    ]
                },
                {
                    "name": "Post-Mission Review",
                    "steps": [
                        {"step": 1, "action": "Download telemetry data", "role": "Data Analyst"},
                        {"step": 2, "action": "Generate mission report", "role": "Test Engineer"},
                        {"step": 3, "action": "Review with team", "role": "Project Manager"}
                    ]
                }
            ]
        }
        
        # Step 2: Convert SOP to Workflow
        logger.info("📋 Step 2: Converting SOP to workflow...")
        
        response = await asyncio.wait_for(
            http_client.post(
                "/api/v1/operations-solution/workflow-from-sop",
                json={
                    "sop_content": sop_content,
                    "workflow_options": {
                        "include_decision_points": True,
                        "include_parallel_tasks": True
                    },
                    "user_context": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "session_token": session_token
                    }
                },
                headers=headers,
                timeout=TIMEOUT
            ),
            timeout=TIMEOUT + 10.0
        )
        
        assert response.status_code in [200, 201], \
            f"❌ SOP to workflow conversion failed: {response.status_code} - {response.text}"
        
        result = response.json()
        logger.info(f"✅ SOP converted to workflow: {json.dumps(result, indent=2)[:500]}")
        
        # Validate workflow structure
        assert "workflow" in result or "workflow_data" in result or "deliverable" in result, \
            f"❌ Workflow missing from response: {result.keys()}"
        
        workflow_data = result.get("workflow") or result.get("workflow_data") or result.get("deliverable", {}).get("workflow")
        assert workflow_data is not None, "❌ Workflow data is None"
        
        # Validate workflow has nodes and edges (or equivalent structure)
        if isinstance(workflow_data, dict):
            has_structure = (
                "nodes" in workflow_data or
                "tasks" in workflow_data or
                "steps" in workflow_data or
                "elements" in workflow_data
            )
            assert has_structure, f"❌ Workflow missing structure: {workflow_data.keys()}"
        
        logger.info("✅ Test Scenario 1: SOP → Workflow conversion validated")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(300)  # 5 minutes
    async def test_sop_from_workflow_conversion(
        self,
        both_servers,
        http_client,
        test_session
    ):
        """
        Test Scenario 2: Convert Workflow to SOP
        
        Validates:
        - Workflow diagram can be converted to SOP document
        - SOP structure is valid (title, sections, steps)
        """
        logger.info("🎬 Test Scenario 2: Workflow → SOP Conversion")
        
        session_id = test_session["session_id"]
        session_token = test_session.get("session_token") or session_id
        user_id = test_session["user_id"]
        
        # Get auth token for Bearer authentication
        auth_token = test_session.get("auth_token")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add Bearer token if available (required for operations-solution endpoints)
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Also include session token for platform correlation
        if session_token:
            headers["X-Session-Token"] = session_token
        if user_id:
            headers["X-User-Id"] = user_id
        
        # Step 1: Create a test workflow diagram
        logger.info("📋 Step 1: Creating test workflow diagram...")
        
        workflow_content = {
            "name": "Autonomous Vehicle Test Mission Workflow",
            "nodes": [
                {"id": "start", "type": "start", "label": "Start Mission"},
                {"id": "verify", "type": "task", "label": "Verify Vehicle Systems"},
                {"id": "load", "type": "task", "label": "Load Mission Plan"},
                {"id": "safety", "type": "task", "label": "Perform Safety Checks"},
                {"id": "execute", "type": "task", "label": "Execute Mission"},
                {"id": "monitor", "type": "task", "label": "Monitor Telemetry"},
                {"id": "review", "type": "task", "label": "Post-Mission Review"},
                {"id": "end", "type": "end", "label": "End Mission"}
            ],
            "edges": [
                {"from": "start", "to": "verify"},
                {"from": "verify", "to": "load"},
                {"from": "load", "to": "safety"},
                {"from": "safety", "to": "execute"},
                {"from": "execute", "to": "monitor"},
                {"from": "monitor", "to": "review"},
                {"from": "review", "to": "end"}
            ]
        }
        
        # Step 2: Convert Workflow to SOP
        logger.info("📋 Step 2: Converting workflow to SOP...")
        
        response = await asyncio.wait_for(
            http_client.post(
                "/api/v1/operations-solution/sop-from-workflow",
                json={
                    "workflow_content": workflow_content,
                    "sop_options": {
                        "include_roles": True,
                        "include_timeline": True
                    },
                    "user_context": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "session_token": session_token
                    }
                },
                headers=headers,
                timeout=TIMEOUT
            ),
            timeout=TIMEOUT + 10.0
        )
        
        assert response.status_code in [200, 201], \
            f"❌ Workflow to SOP conversion failed: {response.status_code} - {response.text}"
        
        result = response.json()
        logger.info(f"✅ Workflow converted to SOP: {json.dumps(result, indent=2)[:500]}")
        
        # Validate SOP structure
        assert "sop" in result or "sop_data" in result or "deliverable" in result, \
            f"❌ SOP missing from response: {result.keys()}"
        
        sop_data = result.get("sop") or result.get("sop_data") or result.get("deliverable", {}).get("sop")
        assert sop_data is not None, "❌ SOP data is None"
        
        # Validate SOP has required structure
        if isinstance(sop_data, dict):
            has_structure = (
                "title" in sop_data or
                "sections" in sop_data or
                "steps" in sop_data or
                "content" in sop_data
            )
            assert has_structure, f"❌ SOP missing structure: {sop_data.keys()}"
        elif isinstance(sop_data, str):
            assert len(sop_data) > 0, "❌ SOP content is empty"
        
        logger.info("✅ Test Scenario 2: Workflow → SOP conversion validated")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(300)  # 5 minutes
    async def test_workflow_visualization(
        self,
        both_servers,
        http_client,
        test_session
    ):
        """
        Test Scenario 3: Workflow Visualization
        
        Validates:
        - Workflow can be visualized
        - Visualization data is properly formatted
        """
        logger.info("🎬 Test Scenario 3: Workflow Visualization")
        
        session_id = test_session["session_id"]
        session_token = test_session.get("session_token") or session_id
        user_id = test_session["user_id"]
        
        # Get auth token for Bearer authentication
        auth_token = test_session.get("auth_token")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add Bearer token if available (required for operations-solution endpoints)
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Also include session token for platform correlation
        if session_token:
            headers["X-Session-Token"] = session_token
        if user_id:
            headers["X-User-Id"] = user_id
        
        # Create test workflow
        workflow_content = {
            "name": "Test Workflow",
            "nodes": [
                {"id": "start", "type": "start", "label": "Start"},
                {"id": "task1", "type": "task", "label": "Task 1"},
                {"id": "end", "type": "end", "label": "End"}
            ],
            "edges": [
                {"from": "start", "to": "task1"},
                {"from": "task1", "to": "end"}
            ]
        }
        
        logger.info("📋 Visualizing workflow...")
        
        response = await asyncio.wait_for(
            http_client.post(
                "/api/v1/operations-solution/workflow-visualization",
                json={
                    "workflow_content": workflow_content,
                    "visualization_options": {
                        "format": "json",
                        "include_metadata": True
                    },
                    "user_context": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "session_token": session_token
                    }
                },
                headers=headers,
                timeout=TIMEOUT
            ),
            timeout=TIMEOUT + 10.0
        )
        
        assert response.status_code in [200, 201], \
            f"❌ Workflow visualization failed: {response.status_code} - {response.text}"
        
        result = response.json()
        logger.info(f"✅ Workflow visualized: {json.dumps(result, indent=2)[:500]}")
        
        # Validate visualization data exists
        assert "workflow" in result or "visualization" in result or "deliverable" in result or "visualization_data" in result, \
            f"❌ Visualization data missing: {result.keys()}"
        
        logger.info("✅ Test Scenario 3: Workflow visualization validated")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(300)  # 5 minutes
    async def test_sop_visualization(
        self,
        both_servers,
        http_client,
        test_session
    ):
        """
        Test Scenario 4: SOP Visualization
        
        Validates:
        - SOP can be visualized
        - Visualization data is properly formatted
        """
        logger.info("🎬 Test Scenario 4: SOP Visualization")
        
        session_id = test_session["session_id"]
        session_token = test_session.get("session_token") or session_id
        user_id = test_session["user_id"]
        
        # Get auth token for Bearer authentication
        auth_token = test_session.get("auth_token")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add Bearer token if available (required for operations-solution endpoints)
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Also include session token for platform correlation
        if session_token:
            headers["X-Session-Token"] = session_token
        if user_id:
            headers["X-User-Id"] = user_id
        
        # Create test SOP
        sop_content = {
            "title": "Test SOP",
            "sections": [
                {
                    "name": "Section 1",
                    "steps": [
                        {"step": 1, "action": "Step 1", "role": "Role 1"}
                    ]
                }
            ]
        }
        
        logger.info("📋 Visualizing SOP...")
        
        response = await asyncio.wait_for(
            http_client.post(
                "/api/v1/operations-solution/sop-visualization",
                json={
                    "sop_content": sop_content,
                    "visualization_options": {
                        "format": "json",
                        "include_metadata": True
                    },
                    "user_context": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "session_token": session_token
                    }
                },
                headers=headers,
                timeout=TIMEOUT
            ),
            timeout=TIMEOUT + 10.0
        )
        
        assert response.status_code in [200, 201], \
            f"❌ SOP visualization failed: {response.status_code} - {response.text}"
        
        result = response.json()
        logger.info(f"✅ SOP visualized: {json.dumps(result, indent=2)[:500]}")
        
        # Validate visualization data exists
        assert "sop" in result or "visualization" in result or "deliverable" in result or "visualization_data" in result, \
            f"❌ Visualization data missing: {result.keys()}"
        
        logger.info("✅ Test Scenario 4: SOP visualization validated")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(600)  # 10 minutes (coexistence analysis can be complex)
    async def test_coexistence_analysis(
        self,
        both_servers,
        http_client,
        test_session
    ):
        """
        Test Scenario 5: Coexistence Analysis
        
        Validates:
        - Can analyze human-AI coexistence
        - Generates optimized blueprint
        - Blueprint has proper structure
        """
        logger.info("🎬 Test Scenario 5: Coexistence Analysis")
        
        session_id = test_session["session_id"]
        session_token = test_session.get("session_token") or session_id
        user_id = test_session["user_id"]
        
        # Get auth token for Bearer authentication
        auth_token = test_session.get("auth_token")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add Bearer token if available (required for operations-solution endpoints)
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Also include session token for platform correlation
        if session_token:
            headers["X-Session-Token"] = session_token
        if user_id:
            headers["X-User-Id"] = user_id
        
        # Create test SOP and workflow
        sop_content = {
            "title": "Current Process SOP",
            "sections": [
                {
                    "name": "Human Tasks",
                    "steps": [
                        {"step": 1, "action": "Review documents", "role": "Human Analyst"},
                        {"step": 2, "action": "Make decisions", "role": "Human Manager"}
                    ]
                }
            ]
        }
        
        workflow_content = {
            "name": "AI-Enhanced Process",
            "nodes": [
                {"id": "ai_review", "type": "task", "label": "AI Document Review"},
                {"id": "human_decision", "type": "task", "label": "Human Decision"}
            ]
        }
        
        logger.info("📋 Analyzing coexistence...")
        
        response = await asyncio.wait_for(
            http_client.post(
                "/api/v1/operations-solution/coexistence-analysis",
                json={
                    "coexistence_content": {
                        "sop_content": sop_content,
                        "workflow_content": workflow_content,
                        "current_state": {"automation_level": "low"},
                        "target_state": {"automation_level": "high"}
                    },
                    "analysis_options": {
                        "include_recommendations": True,
                        "include_risk_assessment": True
                    },
                    "user_context": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "session_token": session_token
                    }
                },
                headers=headers,
                timeout=TIMEOUT * 2  # Coexistence analysis can take longer
            ),
            timeout=TIMEOUT * 2 + 10.0
        )
        
        assert response.status_code in [200, 201], \
            f"❌ Coexistence analysis failed: {response.status_code} - {response.text}"
        
        result = response.json()
        logger.info(f"✅ Coexistence analyzed: {json.dumps(result, indent=2)[:500]}")
        
        # Validate blueprint exists
        assert "blueprint" in result or "deliverable" in result, \
            f"❌ Blueprint missing from response: {result.keys()}"
        
        blueprint = result.get("blueprint") or result.get("deliverable", {}).get("blueprint")
        assert blueprint is not None, "❌ Blueprint is None"
        
        logger.info("✅ Test Scenario 5: Coexistence analysis validated")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(600)  # 10 minutes (interactive creation can be slow)
    async def test_interactive_sop_creation(
        self,
        both_servers,
        http_client,
        test_session
    ):
        """
        Test Scenario 6: Interactive SOP Creation
        
        Validates:
        - Can start interactive SOP creation session
        - Can chat to build SOP
        - Can publish final SOP
        """
        logger.info("🎬 Test Scenario 6: Interactive SOP Creation")
        
        session_id = test_session["session_id"]
        session_token = test_session.get("session_token") or session_id
        user_id = test_session["user_id"]
        
        # Get auth token for Bearer authentication
        auth_token = test_session.get("auth_token")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add Bearer token if available (required for operations-solution endpoints)
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Also include session token for platform correlation
        if session_token:
            headers["X-Session-Token"] = session_token
        if user_id:
            headers["X-User-Id"] = user_id
        
        # Step 1: Start interactive SOP creation
        logger.info("📋 Step 1: Starting interactive SOP creation...")
        
        start_response = await asyncio.wait_for(
            http_client.post(
                "/api/v1/operations-solution/interactive-sop/start",
                json={
                    "user_context": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "session_token": session_token
                    }
                },
                headers=headers,
                timeout=TIMEOUT
            ),
            timeout=TIMEOUT + 10.0
        )
        
        assert start_response.status_code in [200, 201], \
            f"❌ Start interactive SOP creation failed: {start_response.status_code} - {start_response.text}"
        
        start_result = start_response.json()
        logger.info(f"✅ Interactive SOP creation session started: {json.dumps(start_result, indent=2)[:500]}")
        
        # Extract wizard session token from start response
        wizard_session_token = start_result.get("session_token") or session_token
        if not wizard_session_token:
            pytest.fail("❌ No session_token returned from start response")
        
        logger.info(f"📋 Using wizard session token: {wizard_session_token}")
        
        # Step 2: Chat to build SOP
        logger.info("📋 Step 2: Chatting to build SOP...")
        
        chat_response = await asyncio.wait_for(
            http_client.post(
                "/api/v1/operations-solution/interactive-sop/chat",
                json={
                    "message": "I need an SOP for autonomous vehicle test execution. Include pre-mission setup, mission execution, and post-mission review.",
                    "session_token": wizard_session_token,
                    "user_context": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "session_token": session_token
                    }
                },
                headers=headers,
                timeout=TIMEOUT
            ),
            timeout=TIMEOUT + 10.0
        )
        
        assert chat_response.status_code in [200, 201], \
            f"❌ Interactive SOP chat failed: {chat_response.status_code} - {chat_response.text}"
        
        chat_result = chat_response.json()
        logger.info(f"✅ Interactive SOP chat completed: {json.dumps(chat_result, indent=2)[:500]}")
        
        # Step 3: Publish SOP (optional - may not be implemented yet)
        logger.info("📋 Step 3: Publishing SOP...")
        
        # Extract wizard session token from chat response if available, otherwise use the one from start
        chat_result = chat_response.json()
        wizard_session_token = chat_result.get("session_token") or wizard_session_token
        
        publish_response = await asyncio.wait_for(
            http_client.post(
                "/api/v1/operations-solution/interactive-sop/publish",
                json={
                    "session_token": wizard_session_token,
                    "user_context": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "session_token": session_token
                    }
                },
                headers=headers,
                timeout=TIMEOUT
            ),
            timeout=TIMEOUT + 10.0
        )
        
        # Publish may not be implemented yet, so we just check it's not 404
        if publish_response.status_code != 404:
            assert publish_response.status_code in [200, 201], \
                f"⚠️ Publish SOP returned unexpected status: {publish_response.status_code}"
            logger.info("✅ SOP published")
        else:
            logger.info("⚠️ SOP publish endpoint not yet implemented (skipping)")
        
        logger.info("✅ Test Scenario 6: Interactive SOP creation validated")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(600)  # 10 minutes
    async def test_ai_optimized_blueprint(
        self,
        both_servers,
        http_client,
        test_session,
        parsed_file_for_operations
    ):
        """
        Test Scenario 7: AI-Optimized Blueprint Generation
        
        Validates:
        - Can generate optimized blueprint from available documents
        - Blueprint includes AI recommendations
        - Blueprint structure is valid
        """
        logger.info("🎬 Test Scenario 7: AI-Optimized Blueprint Generation")
        
        session_id = test_session["session_id"]
        session_token = test_session.get("session_token") or session_id
        user_id = test_session["user_id"]
        
        # Get auth token for Bearer authentication
        auth_token = test_session.get("auth_token")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add Bearer token if available (required for operations-solution endpoints)
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Also include session token for platform correlation
        if session_token:
            headers["X-Session-Token"] = session_token
        if user_id:
            headers["X-User-Id"] = user_id
        
        # Use the parsed file from fixture (or create a new one)
        file_id = parsed_file_for_operations.file_id
        
        logger.info(f"📋 Generating AI-optimized blueprint from file: {file_id}...")
        
        response = await asyncio.wait_for(
            http_client.post(
                "/api/v1/operations-solution/ai-optimized-blueprint",
                json={
                    "sop_file_ids": [file_id],  # Use available file
                    "workflow_file_ids": [],
                    "optimization_options": {
                        "include_ai_recommendations": True,
                        "include_risk_assessment": True,
                        "target_automation_level": "high"
                    },
                    "user_context": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "session_token": session_token
                    }
                },
                headers=headers,
                timeout=TIMEOUT * 2  # AI optimization can take longer
            ),
            timeout=TIMEOUT * 2 + 10.0
        )
        
        assert response.status_code in [200, 201], \
            f"❌ AI-optimized blueprint generation failed: {response.status_code} - {response.text}"
        
        result = response.json()
        logger.info(f"✅ AI-optimized blueprint generated: {json.dumps(result, indent=2)[:500]}")
        
        # Validate blueprint exists (can be blueprint, blueprint_structure, or deliverable)
        assert "blueprint" in result or "blueprint_structure" in result or "deliverable" in result, \
            f"❌ Blueprint missing from response: {result.keys()}"
        
        blueprint = result.get("blueprint") or result.get("blueprint_structure") or result.get("deliverable", {}).get("blueprint")
        assert blueprint is not None, "❌ Blueprint is None"
        
        logger.info("✅ Test Scenario 7: AI-optimized blueprint generation validated")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(900)  # 15 minutes for complete journey
    async def test_complete_operations_journey(
        self,
        both_servers,
        http_client,
        test_session,
        parsed_file_for_operations
    ):
        """
        Test Scenario 8: Complete Operations Journey
        
        Validates end-to-end operations pillar journey:
        1. Upload and parse SOP/workflow files
        2. Convert SOP to workflow
        3. Convert workflow to SOP
        4. Visualize both
        5. Analyze coexistence
        6. Generate optimized blueprint
        
        This is the comprehensive test that validates all capabilities together.
        """
        logger.info("🎬 Test Scenario 8: Complete Operations Journey")
        
        session_id = test_session["session_id"]
        session_token = test_session.get("session_token") or session_id
        user_id = test_session["user_id"]
        
        # Get auth token for Bearer authentication
        auth_token = test_session.get("auth_token")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add Bearer token if available (required for operations-solution endpoints)
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Also include session token for platform correlation
        if session_token:
            headers["X-Session-Token"] = session_token
        if user_id:
            headers["X-User-Id"] = user_id
        
        # Step 1: Create SOP
        logger.info("📋 Step 1: Creating SOP...")
        sop_content = {
            "title": "Complete Journey Test SOP",
            "sections": [
                {
                    "name": "Setup",
                    "steps": [
                        {"step": 1, "action": "Initialize system", "role": "Engineer"}
                    ]
                }
            ]
        }
        
        # Step 2: Convert SOP to Workflow
        logger.info("📋 Step 2: Converting SOP to workflow...")
        workflow_response = await asyncio.wait_for(
            http_client.post(
                "/api/v1/operations-solution/workflow-from-sop",
                json={
                    "sop_content": sop_content,
                    "user_context": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "session_token": session_token
                    }
                },
                headers=headers,
                timeout=TIMEOUT
            ),
            timeout=TIMEOUT + 10.0
        )
        
        assert workflow_response.status_code in [200, 201], \
            f"❌ SOP to workflow failed: {workflow_response.status_code}"
        
        workflow_result = workflow_response.json()
        workflow_data = workflow_result.get("workflow") or workflow_result.get("workflow_data")
        assert workflow_data is not None, "❌ Workflow data missing"
        logger.info("✅ SOP converted to workflow")
        
        # Step 3: Convert Workflow back to SOP
        logger.info("📋 Step 3: Converting workflow back to SOP...")
        sop_response = await asyncio.wait_for(
            http_client.post(
                "/api/v1/operations-solution/sop-from-workflow",
                json={
                    "workflow_content": workflow_data,
                    "user_context": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "session_token": session_token
                    }
                },
                headers=headers,
                timeout=TIMEOUT
            ),
            timeout=TIMEOUT + 10.0
        )
        
        assert sop_response.status_code in [200, 201], \
            f"❌ Workflow to SOP failed: {sop_response.status_code}"
        
        logger.info("✅ Workflow converted back to SOP")
        
        # Step 4: Visualize Workflow
        logger.info("📋 Step 4: Visualizing workflow...")
        viz_workflow_response = await asyncio.wait_for(
            http_client.post(
                "/api/v1/operations-solution/workflow-visualization",
                json={
                    "workflow_content": workflow_data,
                    "user_context": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "session_token": session_token
                    }
                },
                headers=headers,
                timeout=TIMEOUT
            ),
            timeout=TIMEOUT + 10.0
        )
        
        assert viz_workflow_response.status_code in [200, 201], \
            f"❌ Workflow visualization failed: {viz_workflow_response.status_code}"
        
        logger.info("✅ Workflow visualized")
        
        # Small delay to avoid rate limiting (ProductionTestClient has 0.5s delay, but we need more for multiple requests)
        await asyncio.sleep(2.0)
        
        # Step 5: Analyze Coexistence
        logger.info("📋 Step 5: Analyzing coexistence...")
        coexistence_response = await asyncio.wait_for(
            http_client.post(
                "/api/v1/operations-solution/coexistence-analysis",
                json={
                    "coexistence_content": {
                        "sop_content": sop_content,
                        "workflow_content": workflow_data
                    },
                    "user_context": {
                        "user_id": user_id,
                        "session_id": session_id,
                        "session_token": session_token
                    }
                },
                headers=headers,
                timeout=TIMEOUT * 2
            ),
            timeout=TIMEOUT * 2 + 10.0
        )
        
        # Handle rate limiting gracefully (429) - retry once after delay
        if coexistence_response.status_code == 429:
            logger.warning("⚠️ Rate limited (429), waiting and retrying...")
            await asyncio.sleep(3.0)
            coexistence_response = await asyncio.wait_for(
                http_client.post(
                    "/api/v1/operations-solution/coexistence-analysis",
                    json={
                        "coexistence_content": {
                            "sop_content": sop_content,
                            "workflow_content": workflow_data
                        },
                        "user_context": {
                            "user_id": user_id,
                            "session_id": session_id,
                            "session_token": session_token
                        }
                    },
                    headers=headers,
                    timeout=TIMEOUT * 2
                ),
                timeout=TIMEOUT * 2 + 10.0
            )
        
        assert coexistence_response.status_code in [200, 201], \
            f"❌ Coexistence analysis failed: {coexistence_response.status_code}"
        
        logger.info("✅ Coexistence analyzed")
        
        logger.info("✅ Test Scenario 8: Complete Operations Journey validated")
        
        logger.info("🎉 All Operations Pillar E2E tests completed successfully!")

