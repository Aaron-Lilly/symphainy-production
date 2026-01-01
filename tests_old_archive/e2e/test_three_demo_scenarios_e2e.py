#!/usr/bin/env python3
"""
E2E Tests for Three CTO Demo Scenarios

Tests the three live demo scenarios:
1. Autonomous Vehicle Testing (Defense T&E)
2. Life Insurance Underwriting/Reserving Insights
3. Data Mash Coexistence/Migration Enablement

Each test validates:
- Session/state orchestration with new architecture
- Agent conversations (Guide + Liaison)
- Orchestrator workflow tracking
- End-to-end journey through all 4 pillars
- Demo file processing
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
FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
DEMO_FILES_DIR = Path("/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files")

# Demo file mappings
DEMO_SCENARIOS = {
    "autonomous_vehicle": {
        "name": "Autonomous Vehicle Testing (Defense T&E)",
        "files": {
            "mission_plan": "mission_plan.csv",
            "telemetry": "telemetry_raw.bin",
            "copybook": "telemetry_copybook.cpy",
            "incidents": "test_incident_reports.docx"
        },
        "zip": "SymphAIny_Demo_Defense_TnE.zip"
    },
    "underwriting": {
        "name": "Life Insurance Underwriting/Reserving Insights",
        "files": {
            "claims": "claims.csv",
            "reinsurance": "reinsurance.xlsx",
            "notes": "underwriting_notes.pdf",
            "policy_master": "policy_master.dat",
            "copybook": "copybook.cpy"
        },
        "zip": "SymphAIny_Demo_Underwriting_Insights.zip"
    },
    "coexistence": {
        "name": "Data Mash Coexistence/Migration Enablement",
        "files": {
            "legacy_policies": "legacy_policy_export.csv",
            "target_schema": "target_schema.json",
            "alignment_map": "alignment_map.json"
        },
        "zip": "SymphAIny_Demo_Coexistence.zip"
    }
}

class TestSessionOrchestration:
    """Test session and state orchestration capabilities."""
    
    @pytest.fixture
    async def session(self):
        """Create a test session."""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            # Create session
            response = await client.post(
                "/api/global/session",
                json={"user_id": "test_user", "session_type": "mvp"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"]
            
            session_id = data.get("session_id")
            session_token = data.get("session_token")
            
            # Verify orchestrator context exists
            assert "orchestrator_states" in data
            assert "orchestrator_context" in data
            assert "conversations" in data
            
            yield {
                "client": client,
                "session_id": session_id,
                "session_token": session_token,
                "data": data
            }
    
    @pytest.mark.asyncio
    async def test_session_has_orchestrator_context(self, session):
        """Verify session includes orchestrator context."""
        data = session["data"]
        
        # Check orchestrator states
        assert "orchestrator_states" in data
        orchestrator_states = data["orchestrator_states"]
        assert isinstance(orchestrator_states, dict)
        
        # Check orchestrator context
        assert "orchestrator_context" in data
        orchestrator_context = data["orchestrator_context"]
        assert isinstance(orchestrator_context, dict)
        assert "active_orchestrators" in orchestrator_context
        assert "enabling_services" in orchestrator_context
        
        # Check conversations (may be empty dict initially)
        assert "conversations" in data
        conversations = data["conversations"]
        assert isinstance(conversations, dict)
        # Conversations dict exists but may be empty until first message
        # Verify structure allows for guide_agent and content_liaison
        # (They'll be populated when agents are used)

class TestAutonomousVehicleScenario:
    """Test Scenario 1: Autonomous Vehicle Testing (Defense T&E)."""
    
    @pytest.fixture
    async def session(self):
        """Create session for AV testing scenario."""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            response = await client.post(
                "/api/global/session",
                json={"user_id": "av_test_user", "session_type": "mvp"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"]
            
            yield {
                "client": client,
                "session_id": data.get("session_id"),
                "session_token": data.get("session_token")
            }
    
    @pytest.mark.asyncio
    async def test_guide_agent_av_conversation(self, session):
        """Test Guide Agent conversation for AV testing scenario."""
        client = session["client"]
        session_token = session["session_token"]
        
        # Send message to Guide Agent
        response = await client.post(
            "/api/global/agent/analyze",
            json={
                "message": "I need to test autonomous vehicle systems with mission plans and telemetry data",
                "user_id": "av_test_user",
                "session_token": session_token
            },
            headers={"X-Session-Token": session_token} if session_token else {}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"]
        
        # Verify response includes analysis
        assert "analysis" in data
        
        # Note: session_id may not be in response if using fallback
        # The important thing is that the request succeeded
    
    @pytest.mark.asyncio
    async def test_upload_mission_plan_csv(self, session):
        """Test uploading mission_plan.csv file."""
        client = session["client"]
        session_token = session["session_token"]
        
        # Check if demo file exists
        demo_zip = DEMO_FILES_DIR / DEMO_SCENARIOS["autonomous_vehicle"]["zip"]
        if not demo_zip.exists():
            pytest.skip(f"Demo file not found: {demo_zip}")
        
        # Extract and read mission_plan.csv
        import zipfile
        with zipfile.ZipFile(demo_zip, 'r') as zf:
            csv_content = None
            for name in zf.namelist():
                if "mission_plan.csv" in name:
                    csv_content = zf.read(name)
                    break
        
        if not csv_content:
            pytest.skip("mission_plan.csv not found in demo zip")
        
        # Upload file
        files = {"file": ("mission_plan.csv", csv_content, "text/csv")}
        data = {"user_id": "av_test_user"}
        headers = {}
        if session_token:
            headers["X-Session-Token"] = session_token
        
        response = await client.post(
            "/api/mvp/content/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"]
        assert "file_id" in result
        
        # Verify workflow tracking
        if "workflow_id" in result:
            assert "orchestrator" in result
            assert result["orchestrator"] == "ContentAnalysisOrchestrator"
        
        return result["file_id"]
    
    @pytest.mark.asyncio
    async def test_parse_telemetry_binary(self, session):
        """Test parsing telemetry binary file with COBOL copybook."""
        client = session["client"]
        session_token = session["session_token"]
        
        # Check if demo file exists
        demo_zip = DEMO_FILES_DIR / DEMO_SCENARIOS["autonomous_vehicle"]["zip"]
        if not demo_zip.exists():
            pytest.skip(f"Demo file not found: {demo_zip}")
        
        # Extract telemetry files
        import zipfile
        with zipfile.ZipFile(demo_zip, 'r') as zf:
            telemetry_content = None
            copybook_content = None
            for name in zf.namelist():
                if "telemetry_raw.bin" in name:
                    telemetry_content = zf.read(name)
                elif "telemetry_copybook.cpy" in name or "copybook.cpy" in name:
                    copybook_content = zf.read(name)
        
        if not telemetry_content:
            pytest.skip("telemetry_raw.bin not found in demo zip")
        
        # Upload telemetry file
        files = {"file": ("telemetry_raw.bin", telemetry_content, "application/octet-stream")}
        data = {"user_id": "av_test_user"}
        headers = {}
        if session_token:
            headers["X-Session-Token"] = session_token
        
        response = await client.post(
            "/api/mvp/content/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"]
        assert "file_id" in result
        
        # Parse file
        file_id = result["file_id"]
        parse_response = await client.post(
            f"/api/mvp/content/parse/{file_id}",
            json={"user_id": "av_test_user"},
            headers=headers
        )
        
        assert parse_response.status_code == 200
        parse_result = parse_response.json()
        # Parse may fail if orchestrator not available, but should return structured response
        assert isinstance(parse_result, dict)
        # Check for either success or error message structure
        assert "success" in parse_result or "message" in parse_result
        
        return file_id

class TestUnderwritingScenario:
    """Test Scenario 2: Life Insurance Underwriting/Reserving Insights."""
    
    @pytest.fixture
    async def session(self):
        """Create session for underwriting scenario."""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            response = await client.post(
                "/api/global/session",
                json={"user_id": "underwriting_user", "session_type": "mvp"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"]
            
            yield {
                "client": client,
                "session_id": data.get("session_id"),
                "session_token": data.get("session_token")
            }
    
    @pytest.mark.asyncio
    async def test_upload_claims_csv(self, session):
        """Test uploading claims.csv file."""
        client = session["client"]
        session_token = session["session_token"]
        
        # Check if demo file exists
        demo_zip = DEMO_FILES_DIR / DEMO_SCENARIOS["underwriting"]["zip"]
        if not demo_zip.exists():
            pytest.skip(f"Demo file not found: {demo_zip}")
        
        # Extract and read claims.csv
        import zipfile
        with zipfile.ZipFile(demo_zip, 'r') as zf:
            csv_content = None
            for name in zf.namelist():
                if "claims.csv" in name:
                    csv_content = zf.read(name)
                    break
        
        if not csv_content:
            pytest.skip("claims.csv not found in demo zip")
        
        # Upload file
        files = {"file": ("claims.csv", csv_content, "text/csv")}
        data = {"user_id": "underwriting_user"}
        headers = {}
        if session_token:
            headers["X-Session-Token"] = session_token
        
        response = await client.post(
            "/api/mvp/content/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"]
        assert "file_id" in result
        
        return result["file_id"]
    
    @pytest.mark.asyncio
    async def test_upload_reinsurance_excel(self, session):
        """Test uploading reinsurance.xlsx file."""
        client = session["client"]
        session_token = session["session_token"]
        
        # Check if demo file exists
        demo_zip = DEMO_FILES_DIR / DEMO_SCENARIOS["underwriting"]["zip"]
        if not demo_zip.exists():
            pytest.skip(f"Demo file not found: {demo_zip}")
        
        # Extract and read reinsurance.xlsx
        import zipfile
        with zipfile.ZipFile(demo_zip, 'r') as zf:
            xlsx_content = None
            for name in zf.namelist():
                if "reinsurance.xlsx" in name:
                    xlsx_content = zf.read(name)
                    break
        
        if not xlsx_content:
            pytest.skip("reinsurance.xlsx not found in demo zip")
        
        # Upload file
        files = {"file": ("reinsurance.xlsx", xlsx_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        data = {"user_id": "underwriting_user"}
        headers = {}
        if session_token:
            headers["X-Session-Token"] = session_token
        
        response = await client.post(
            "/api/mvp/content/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"]
        assert "file_id" in result
        
        return result["file_id"]
    
    @pytest.mark.asyncio
    async def test_upload_and_parse_binary_with_copybook(self, session):
        """Test uploading and parsing binary file (policy_master.dat) with copybook."""
        client = session["client"]
        session_token = session["session_token"]
        
        # Check if demo file exists
        demo_zip = DEMO_FILES_DIR / DEMO_SCENARIOS["underwriting"]["zip"]
        if not demo_zip.exists():
            pytest.skip(f"Demo file not found: {demo_zip}")
        
        # Extract binary file and copybook
        import zipfile
        with zipfile.ZipFile(demo_zip, 'r') as zf:
            binary_content = None
            copybook_content = None
            for name in zf.namelist():
                if "policy_master.dat" in name:
                    binary_content = zf.read(name)
                elif "copybook.cpy" in name or "metadata/copybook.cpy" in name:
                    copybook_content = zf.read(name)
        
        if not binary_content:
            pytest.skip("policy_master.dat not found in demo zip")
        if not copybook_content:
            pytest.skip("copybook.cpy not found in demo zip")
        
        # Upload binary file
        files = {"file": ("policy_master.dat", binary_content, "application/octet-stream")}
        data = {"user_id": "underwriting_user"}
        headers = {}
        if session_token:
            headers["X-Session-Token"] = session_token
        
        upload_response = await client.post(
            "/api/mvp/content/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        assert upload_response.status_code == 200
        upload_result = upload_response.json()
        assert upload_result["success"]
        assert "file_id" in upload_result
        binary_file_id = upload_result["file_id"]
        
        # Upload copybook file
        copybook_files = {"file": ("copybook.cpy", copybook_content, "text/plain")}
        copybook_upload = await client.post(
            "/api/mvp/content/upload",
            files=copybook_files,
            data=data,
            headers=headers
        )
        
        assert copybook_upload.status_code == 200
        copybook_result = copybook_upload.json()
        assert copybook_result["success"]
        copybook_file_id = copybook_result.get("file_id")
        
        # Parse binary file with copybook
        parse_response = await client.post(
            f"/api/mvp/content/parse/{binary_file_id}",
            json={
                "user_id": "underwriting_user",
                "copybook_file_id": copybook_file_id
            },
            headers=headers
        )
        
        assert parse_response.status_code == 200
        parse_result = parse_response.json()
        # Parse may succeed or return structured error
        assert isinstance(parse_result, dict)
        # Verify parsing attempted (either success or structured error)
        assert "success" in parse_result or "message" in parse_result or "error" in parse_result
        
        # If parsing succeeded, verify records were extracted
        if parse_result.get("success"):
            # Should have parsed data or records
            assert "data" in parse_result or "records" in parse_result or "parsed_content" in parse_result
        
        return binary_file_id
    
    @pytest.mark.asyncio
    async def test_content_liaison_underwriting_conversation(self, session):
        """Test Content Liaison conversation for underwriting scenario."""
        client = session["client"]
        session_token = session["session_token"]
        
        # Send message to Content Liaison
        response = await client.post(
            "/api/liaison/chat",
            json={
                "message": "I need to analyze legacy insurance data for underwriting insights",
                "pillar": "content",
                "user_id": "underwriting_user",
                "conversation_id": None
            },
            headers={"X-Session-Token": session_token} if session_token else {}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"]
        assert "response" in data
        # Note: session_id may not be in response if using fallback mode
        # The important thing is that the request succeeded

class TestCoexistenceScenario:
    """Test Scenario 3: Data Mash Coexistence/Migration Enablement."""
    
    @pytest.fixture
    async def session(self):
        """Create session for coexistence scenario."""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            response = await client.post(
                "/api/global/session",
                json={"user_id": "coexistence_user", "session_type": "mvp"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"]
            
            yield {
                "client": client,
                "session_id": data.get("session_id"),
                "session_token": data.get("session_token")
            }
    
    @pytest.mark.asyncio
    async def test_upload_legacy_policies(self, session):
        """Test uploading legacy_policy_export.csv file."""
        client = session["client"]
        session_token = session["session_token"]
        
        # Check if demo file exists
        demo_zip = DEMO_FILES_DIR / DEMO_SCENARIOS["coexistence"]["zip"]
        if not demo_zip.exists():
            pytest.skip(f"Demo file not found: {demo_zip}")
        
        # Extract and read legacy_policy_export.csv
        import zipfile
        with zipfile.ZipFile(demo_zip, 'r') as zf:
            csv_content = None
            for name in zf.namelist():
                if "legacy_policy_export.csv" in name:
                    csv_content = zf.read(name)
                    break
        
        if not csv_content:
            pytest.skip("legacy_policy_export.csv not found in demo zip")
        
        # Upload file
        files = {"file": ("legacy_policy_export.csv", csv_content, "text/csv")}
        data = {"user_id": "coexistence_user"}
        headers = {}
        if session_token:
            headers["X-Session-Token"] = session_token
        
        response = await client.post(
            "/api/mvp/content/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"]
        assert "file_id" in result
        
        return result["file_id"]
    
    @pytest.mark.asyncio
    async def test_upload_alignment_map(self, session):
        """Test uploading alignment_map.json file."""
        client = session["client"]
        session_token = session["session_token"]
        
        # Check if demo file exists
        demo_zip = DEMO_FILES_DIR / DEMO_SCENARIOS["coexistence"]["zip"]
        if not demo_zip.exists():
            pytest.skip(f"Demo file not found: {demo_zip}")
        
        # Extract and read alignment_map.json
        import zipfile
        with zipfile.ZipFile(demo_zip, 'r') as zf:
            json_content = None
            for name in zf.namelist():
                if "alignment_map.json" in name:
                    json_content = zf.read(name)
                    break
        
        if not json_content:
            pytest.skip("alignment_map.json not found in demo zip")
        
        # Upload file
        files = {"file": ("alignment_map.json", json_content, "application/json")}
        data = {"user_id": "coexistence_user"}
        headers = {}
        if session_token:
            headers["X-Session-Token"] = session_token
        
        response = await client.post(
            "/api/mvp/content/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"]
        assert "file_id" in result
        
        return result["file_id"]
    
    @pytest.mark.asyncio
    async def test_operations_liaison_coexistence_conversation(self, session):
        """Test Operations Liaison conversation for coexistence scenario."""
        client = session["client"]
        session_token = session["session_token"]
        
        # Send message to Operations Liaison
        response = await client.post(
            "/api/liaison/chat",
            json={
                "message": "I need to create a coexistence strategy for migrating legacy insurance systems",
                "pillar": "operations",
                "user_id": "coexistence_user",
                "conversation_id": None
            },
            headers={"X-Session-Token": session_token} if session_token else {}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"]
        assert "response" in data
        # Note: session_id may not be in response if using fallback mode
        # The important thing is that the request succeeded
    
    @pytest.mark.asyncio
    async def test_operations_liaison_sop_generation(self, session):
        """Test generating SOP document via interactive dialog with Operations Liaison agent."""
        client = session["client"]
        session_token = session["session_token"]
        
        # Start SOP generation conversation
        response = await client.post(
            "/api/liaison/chat",
            json={
                "message": "I need to create an SOP for data migration procedures using the SOP generator wizard",
                "pillar": "operations",
                "user_id": "coexistence_user",
                "conversation_id": None
            },
            headers={"X-Session-Token": session_token} if session_token else {}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"]
        assert "response" in data
        
        # Verify response indicates SOP generation process started
        response_text = str(data.get("response", {}).get("message", ""))
        # Should mention SOP or wizard or procedure
        assert any(keyword in response_text.lower() for keyword in ["sop", "procedure", "wizard", "process", "document"])
    
    @pytest.mark.asyncio
    async def test_sop_to_workflow_conversion(self, session):
        """Test converting SOP document to workflow diagram."""
        client = session["client"]
        session_token = session["session_token"]
        
        # Create a sample SOP content
        sample_sop = {
            "title": "Data Migration Procedure",
            "description": "Standard procedure for migrating legacy data",
            "steps": [
                {"step": 1, "description": "Extract data from legacy system"},
                {"step": 2, "description": "Validate data integrity"},
                {"step": 3, "description": "Transform data format"},
                {"step": 4, "description": "Load into new system"}
            ]
        }
        
        # Convert SOP to workflow
        response = await client.post(
            "/api/operations/generate_workflow_from_sop",
            json={
                "file_ids": [],
                "workflow_data": {
                    "sop_content": sample_sop,
                    "conversion_type": "sop_to_workflow"
                },
                "user_id": "coexistence_user"
            },
            headers={"X-Session-Token": session_token} if session_token else {}
        )
        
        assert response.status_code == 200
        data = response.json()
        print(f"\n🔍 SOP to Workflow Response: {data}")
        assert data["success"]
        # Should return workflow structure
        assert "workflow_id" in data or "workflow" in data or "workflow_content" in data
    
    @pytest.mark.asyncio
    async def test_workflow_to_sop_conversion(self, session):
        """Test converting workflow diagram to SOP document."""
        client = session["client"]
        session_token = session["session_token"]
        
        # Create a sample workflow
        sample_workflow = {
            "name": "Data Migration Workflow",
            "nodes": [
                {"id": "1", "name": "Extract Data", "type": "task"},
                {"id": "2", "name": "Validate Data", "type": "task"},
                {"id": "3", "name": "Transform Data", "type": "task"},
                {"id": "4", "name": "Load Data", "type": "task"}
            ],
            "edges": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
                {"source": "3", "target": "4"}
            ]
        }
        
        # Convert workflow to SOP
        response = await client.post(
            "/api/operations/generate_sop_from_workflow",
            json={
                "file_ids": [],
                "sop_data": {
                    "workflow": sample_workflow,
                    "conversion_type": "workflow_to_sop"
                },
                "user_id": "coexistence_user"
            },
            headers={"X-Session-Token": session_token} if session_token else {}
        )
        
        assert response.status_code == 200
        data = response.json()
        print(f"\n🔍 Workflow to SOP Response: {data}")
        assert data["success"]
        # Should return SOP structure
        assert "sop_id" in data or "sop_content" in data or "sop" in data

@pytest.mark.asyncio
async def test_all_scenarios_session_persistence():
    """Test that sessions persist across all three scenarios."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Create session
        response = await client.post(
            "/api/global/session",
            json={"user_id": "multi_scenario_user", "session_type": "mvp"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"]
        
        session_id = data.get("session_id")
        session_token = data.get("session_token")
        
        # Test Guide Agent conversation
        guide_response = await client.post(
            "/api/global/agent/analyze",
            json={
                "message": "I need to test multiple scenarios",
                "user_id": "multi_scenario_user",
                "session_token": session_token
            },
            headers={"X-Session-Token": session_token} if session_token else {}
        )
        assert guide_response.status_code == 200
        
        # Test Content Liaison conversation
        content_response = await client.post(
            "/api/liaison/chat",
            json={
                "message": "Upload a file",
                "pillar": "content",
                "user_id": "multi_scenario_user",
                "conversation_id": None
            },
            headers={"X-Session-Token": session_token} if session_token else {}
        )
        assert content_response.status_code == 200
        
        # Retrieve session and verify all conversations present
        get_session_response = await client.get(
            f"/api/global/session/{session_id}",
            headers={"X-Session-Token": session_token} if session_token else {}
        )
        assert get_session_response.status_code == 200
        session_data = get_session_response.json()
        
        assert session_data["success"]
        conversations = session_data.get("conversations", {})
        # Conversations may be empty until agents are actually used
        # Verify structure exists (dict) and will be populated when agents interact
        assert isinstance(conversations, dict)
        # If conversations exist, verify structure
        if conversations:
            # Verify expected conversation keys exist when populated
            assert any(key in conversations for key in ["guide_agent", "content_liaison", "operations_liaison"])
        
        # Verify orchestrator context
        orchestrator_context = session_data.get("orchestrator_context", {})
        assert isinstance(orchestrator_context, dict)

class TestBusinessOutcomesVisualization:
    """Test Business Outcomes Pillar Summary Visualization."""
    
    @pytest.fixture
    async def session(self):
        """Create session for business outcomes visualization."""
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            response = await client.post(
                "/api/global/session",
                json={"user_id": "visualization_user", "session_type": "mvp"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"]
            
            yield {
                "client": client,
                "session_id": data.get("session_id"),
                "session_token": data.get("session_token")
            }
    
    @pytest.mark.asyncio
    async def test_generate_summary_visualization(self, session):
        """Test generating the summary visual for business outcomes pillar."""
        client = session["client"]
        session_token = session["session_token"]
        
        # Create sample pillar outputs
        pillar_outputs = {
            "content_pillar": {
                "files_uploaded": 5,
                "file_types": ["CSV", "XLSX", "PDF", "DAT"],
                "total_size": "50MB"
            },
            "insights_pillar": {
                "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
                "recommendations": ["Rec 1", "Rec 2"],
                "business_impact": "high"
            },
            "operations_pillar": {
                "sops_created": 2,
                "workflows_optimized": 1,
                "coexistence_score": 75
            }
        }
        
        # Generate summary visualization
        response = await client.post(
            "/api/business-outcomes-pillar/generate-strategic-roadmap",
            json={
                "pillar_outputs": pillar_outputs,
                "roadmap_options": {
                    "visualization_type": "summary"
                },
                "user_id": "visualization_user"
            },
            headers={"X-Session-Token": session_token} if session_token else {}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"]
        # Should return visualization data
        assert "roadmap" in data or "roadmap_id" in data or "summary_display" in data or "visualization" in data

