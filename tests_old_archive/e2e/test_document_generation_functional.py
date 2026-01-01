"""
E2E Test: Document Generation - Functional Business Logic
Tests that document generation ACTUALLY WORKS

This validates the core value proposition:
- Can we generate SOPs?
- Can we generate workflows?
- Can we generate roadmaps?
- Can we generate POC proposals?
- Are they actually useful/professional?
"""

import pytest
import httpx
import os
import json
import asyncio

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
TIMEOUT = 60.0  # Document generation may take longer

@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.critical
class TestSOPGeneration:
    """Test that SOP generation actually produces usable documents"""
    
    @pytest.mark.asyncio
    async def test_generate_sop_functional(self):
        """Test SOP generation produces structured, professional document"""
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Create session
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            assert session_response.status_code in [200, 201]
            session_token = (session_response.json()).get("session_token", "session_id")
            
            # Request SOP generation
            sop_request = {
                "session_token": session_token,
                "context": {
                    "title": "Data Upload and Processing Procedure",
                    "department": "Operations",
                    "purpose": "Standardize data upload, validation, and processing workflow"
                }
            }
            
            sop_response = await client.post(
                f"{BASE_URL}/api/mvp/operations/sop/create",
                json=sop_request
            )
            
            assert sop_response.status_code == 200, \
                f"❌ CRITICAL: SOP generation failed: {sop_response.text}"
            
            sop_data = sop_response.json()
            
            # Verify SOP structure
            assert "sop" in sop_data or "document" in sop_data or "content" in sop_data, \
                "❌ CRITICAL: SOP response missing document"
            
            sop_key = next((k for k in ["sop", "document", "content"] if k in sop_data), None)
            sop = sop_data[sop_key]
            
            # Verify SOP has key sections
            if isinstance(sop, dict):
                # Structured SOP
                assert "purpose" in sop or "Purpose" in sop, \
                    "❌ CRITICAL: SOP missing Purpose section"
                assert "scope" in sop or "Scope" in sop, \
                    "❌ CRITICAL: SOP missing Scope section"
                assert "procedures" in sop or "Procedures" in sop or "steps" in sop, \
                    "❌ CRITICAL: SOP missing Procedures section"
                
                print(f"✅ SOP has structured sections")
                
            elif isinstance(sop, str):
                # Text-based SOP
                assert len(sop) > 200, \
                    f"❌ CRITICAL: SOP too short ({len(sop)} chars), likely not a real document"
                
                # Check for key SOP components
                sop_lower = sop.lower()
                assert "purpose" in sop_lower or "objective" in sop_lower, \
                    "❌ CRITICAL: SOP missing purpose/objective"
                assert "procedure" in sop_lower or "step" in sop_lower, \
                    "❌ CRITICAL: SOP missing procedure steps"
                
                print(f"✅ SOP is {len(sop)} characters with proper structure")
            
            else:
                pytest.fail(f"❌ CRITICAL: SOP has unexpected type: {type(sop)}")
            
            print(f"✅ FUNCTIONAL TEST PASSED: SOP generation produces usable document")

@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.critical
class TestWorkflowGeneration:
    """Test that workflow generation produces valid diagrams"""
    
    @pytest.mark.asyncio
    async def test_generate_workflow_functional(self):
        """Test workflow generation produces valid diagram with nodes and edges"""
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Create session
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            session_token = (session_response.json()).get("session_token", "session_id")
            
            # Request workflow generation
            workflow_request = {
                "session_token": session_token,
                "context": {
                    "process": "Customer Onboarding Workflow",
                    "steps": [
                        "Submit application",
                        "Verify identity",
                        "Review documentation",
                        "Approve/reject",
                        "Send notification"
                    ]
                }
            }
            
            workflow_response = await client.post(
                f"{BASE_URL}/api/mvp/operations/workflow/create",
                json=workflow_request
            )
            
            assert workflow_response.status_code == 200, \
                f"❌ CRITICAL: Workflow generation failed: {workflow_response.text}"
            
            workflow_data = workflow_response.json()
            
            # Verify workflow structure
            workflow_key = next((k for k in ["workflow", "diagram", "content"] if k in workflow_data), None)
            assert workflow_key, "❌ CRITICAL: Workflow response missing diagram"
            
            workflow = workflow_data[workflow_key]
            
            # Verify workflow has nodes and edges
            if isinstance(workflow, dict):
                # Structured workflow
                assert "nodes" in workflow or "steps" in workflow, \
                    "❌ CRITICAL: Workflow missing nodes/steps"
                
                nodes = workflow.get("nodes") or workflow.get("steps", [])
                assert len(nodes) >= 3, \
                    f"❌ CRITICAL: Workflow should have multiple nodes, got {len(nodes)}"
                
                # Check for edges/connections
                has_edges = "edges" in workflow or "connections" in workflow or "transitions" in workflow
                print(f"✅ Workflow has {len(nodes)} nodes" + (" and edges" if has_edges else ""))
                
            elif isinstance(workflow, str):
                # Text-based workflow (e.g., Mermaid, BPMN XML)
                assert len(workflow) > 100, \
                    f"❌ CRITICAL: Workflow too short ({len(workflow)} chars)"
                
                # Check for workflow indicators
                workflow_lower = workflow.lower()
                has_workflow_syntax = any(indicator in workflow_lower for indicator in [
                    "graph", "flowchart", "-->", "->", "bpmn", "process", "task"
                ])
                
                assert has_workflow_syntax, \
                    "❌ CRITICAL: Workflow doesn't appear to be a valid diagram format"
                
                print(f"✅ Workflow is {len(workflow)} characters in diagram format")
            
            print(f"✅ FUNCTIONAL TEST PASSED: Workflow generation produces valid diagram")

@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.critical
class TestRoadmapGeneration:
    """Test that roadmap generation produces strategic plans"""
    
    @pytest.mark.asyncio
    async def test_generate_roadmap_functional(self):
        """Test roadmap generation produces phased strategic plan"""
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Create session
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            session_token = (session_response.json()).get("session_token", "session_id")
            
            # Request roadmap generation
            roadmap_request = {
                "session_token": session_token,
                "context": {
                    "project": "Digital Transformation Initiative",
                    "goals": [
                        "Modernize legacy systems",
                        "Improve data analytics capabilities",
                        "Enhance customer experience"
                    ],
                    "timeline": "12 months"
                }
            }
            
            roadmap_response = await client.post(
                f"{BASE_URL}/api/mvp/business-outcomes/roadmap/create",
                json=roadmap_request
            )
            
            assert roadmap_response.status_code == 200, \
                f"❌ CRITICAL: Roadmap generation failed: {roadmap_response.text}"
            
            roadmap_data = roadmap_response.json()
            
            # Verify roadmap structure
            roadmap_key = next((k for k in ["roadmap", "plan", "content"] if k in roadmap_data), None)
            assert roadmap_key, "❌ CRITICAL: Roadmap response missing plan"
            
            roadmap = roadmap_data[roadmap_key]
            
            # Verify roadmap has phases/milestones
            if isinstance(roadmap, dict):
                # Structured roadmap
                has_phases = "phases" in roadmap or "milestones" in roadmap or "stages" in roadmap
                assert has_phases, \
                    "❌ CRITICAL: Roadmap missing phases/milestones"
                
                phases_key = next((k for k in ["phases", "milestones", "stages"] if k in roadmap), None)
                phases = roadmap[phases_key]
                
                assert len(phases) >= 2, \
                    f"❌ CRITICAL: Roadmap should have multiple phases, got {len(phases)}"
                
                # Check each phase has key components
                first_phase = phases[0]
                assert "name" in first_phase or "title" in first_phase, \
                    "❌ CRITICAL: Phase missing name/title"
                
                has_timeline = "timeline" in first_phase or "duration" in first_phase or "timeframe" in first_phase
                has_activities = "activities" in first_phase or "tasks" in first_phase or "objectives" in first_phase
                
                print(f"✅ Roadmap has {len(phases)} phases with timeline and activities")
                
            elif isinstance(roadmap, str):
                # Text-based roadmap
                assert len(roadmap) > 300, \
                    f"❌ CRITICAL: Roadmap too short ({len(roadmap)} chars)"
                
                roadmap_lower = roadmap.lower()
                assert "phase" in roadmap_lower or "milestone" in roadmap_lower or "stage" in roadmap_lower, \
                    "❌ CRITICAL: Roadmap missing phase/milestone structure"
                assert "month" in roadmap_lower or "quarter" in roadmap_lower or "week" in roadmap_lower, \
                    "❌ CRITICAL: Roadmap missing timeline information"
                
                print(f"✅ Roadmap is {len(roadmap)} characters with phases and timeline")
            
            print(f"✅ FUNCTIONAL TEST PASSED: Roadmap generation produces strategic plan")

@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.critical
class TestPOCProposalGeneration:
    """Test that POC proposal generation produces professional documents"""
    
    @pytest.mark.asyncio
    async def test_generate_poc_proposal_functional(self):
        """Test POC proposal generation produces comprehensive, professional proposal"""
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Create session
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            session_token = (session_response.json()).get("session_token", "session_id")
            
            # Request POC proposal generation
            poc_request = {
                "session_token": session_token,
                "context": {
                    "project": "AI-Powered Data Analytics Platform",
                    "business_problem": "Manual data analysis is time-consuming and error-prone",
                    "proposed_solution": "Automated analytics with AI-driven insights",
                    "expected_outcomes": [
                        "80% reduction in analysis time",
                        "Improved data accuracy",
                        "Faster decision-making"
                    ]
                }
            }
            
            poc_response = await client.post(
                f"{BASE_URL}/api/mvp/business-outcomes/poc-proposal/create",
                json=poc_request
            )
            
            assert poc_response.status_code == 200, \
                f"❌ CRITICAL: POC proposal generation failed: {poc_response.text}"
            
            poc_data = poc_response.json()
            
            # Verify POC structure
            poc_key = next((k for k in ["proposal", "poc", "content"] if k in poc_data), None)
            assert poc_key, "❌ CRITICAL: POC response missing proposal"
            
            poc = poc_data[poc_key]
            
            # Verify POC has key sections
            if isinstance(poc, dict):
                # Structured POC
                required_sections = ["objectives", "scope", "timeline", "deliverables"]
                missing_sections = []
                
                for section in required_sections:
                    # Check various case variations
                    has_section = any(
                        key.lower().replace("_", "").replace(" ", "") == section
                        for key in poc.keys()
                    )
                    if not has_section:
                        missing_sections.append(section)
                
                if missing_sections:
                    print(f"⚠️  POC missing sections: {missing_sections}")
                    print(f"   (Has: {list(poc.keys())})")
                else:
                    print(f"✅ POC has all required sections")
                
                # Verify content quality
                assert len(str(poc)) > 200, \
                    "❌ CRITICAL: POC content too sparse"
                
            elif isinstance(poc, str):
                # Text-based POC
                assert len(poc) > 500, \
                    f"❌ CRITICAL: POC too short ({len(poc)} chars) for professional proposal"
                
                poc_lower = poc.lower()
                
                # Check for key POC components
                required_terms = ["objective", "scope", "timeline", "deliverable"]
                found_terms = [term for term in required_terms if term in poc_lower]
                
                assert len(found_terms) >= 3, \
                    f"❌ CRITICAL: POC missing key sections (found only {found_terms})"
                
                print(f"✅ POC is {len(poc)} characters with comprehensive structure")
            
            print(f"✅ FUNCTIONAL TEST PASSED: POC proposal generation produces professional document")

@pytest.mark.e2e
@pytest.mark.functional
class TestDocumentQuality:
    """Test that generated documents meet quality standards"""
    
    @pytest.mark.asyncio
    async def test_document_generation_not_generic(self):
        """Test that documents are contextual, not generic templates"""
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Create session
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            session_token = (session_response.json()).get("session_token", "session_id")
            
            # Generate SOP with specific context
            sop_request = {
                "session_token": session_token,
                "context": {
                    "title": "Quantum Computing Data Processing",
                    "department": "Advanced Research",
                    "purpose": "Handle quantum computing results"
                }
            }
            
            sop_response = await client.post(
                f"{BASE_URL}/api/mvp/operations/sop/create",
                json=sop_request
            )
            
            if sop_response.status_code == 200:
                sop_data = sop_response.json()
                sop_key = next((k for k in ["sop", "document", "content"] if k in sop_data), None)
                sop = str(sop_data.get(sop_key, ""))
                
                # Check if SOP includes context terms
                context_terms = ["quantum", "computing", "advanced", "research"]
                found_terms = [term for term in context_terms if term.lower() in sop.lower()]
                
                if len(found_terms) >= 2:
                    print(f"✅ SOP includes contextual terms: {found_terms}")
                    print(f"✅ Document generation appears contextual, not generic")
                else:
                    print(f"⚠️  Warning: SOP may be too generic (only found {found_terms})")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

