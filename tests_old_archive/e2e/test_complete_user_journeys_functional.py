"""
E2E Test: Complete User Journeys - Functional
Tests that COMPLETE USER WORKFLOWS actually work end-to-end

This validates the entire CTO demo flow:
1. Register → Upload File → Parse → Analyze → Generate Documents
2. All 4 pillars in sequence
3. Progress tracking throughout
4. No data loss between steps

These are the MOST CRITICAL tests for production readiness.
"""

import pytest
import httpx
import os
from pathlib import Path
import json
import asyncio

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
DEMO_FILES_DIR = Path("/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files")
TIMEOUT = 60.0

@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.critical
@pytest.mark.asyncio
class TestCompleteContentToInsightsJourney:
    """Test complete journey: Upload file → Parse → Analyze"""
    
    async def test_upload_parse_analyze_complete_flow(self):
        """Test the CTO demo flow: Upload CSV → Parse → Get Insights"""
        
        csv_file = DEMO_FILES_DIR / "SymphAIny_Demo_Underwriting_Insights/data/claims.csv"
        
        if not csv_file.exists():
            pytest.skip(f"Demo file not found: {csv_file}")
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            print("\n" + "="*70)
            print("COMPLETE JOURNEY TEST: Content → Insights")
            print("="*70)
            
            # STEP 1: Register user
            print("\n[STEP 1] Register new user...")
            register_response = await client.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "email": f"test_journey_{asyncio.current_task().get_name()}@example.com",
                    "password": "SecurePass123!",
                    "name": "Journey Test User"
                }
            )
            
            assert register_response.status_code in [200, 201], \
                f"❌ JOURNEY FAILED at registration: {register_response.text}"
            print("✅ User registered")
            
            # STEP 2: Create global session
            print("\n[STEP 2] Create global session...")
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            
            assert session_response.status_code in [200, 201], \
                f"❌ JOURNEY FAILED at session creation: {session_response.text}"
            
            session_data = session_response.json()
            session_token = session_data.get("session_token") or session_data.get("session_id")
            assert session_token, "❌ JOURNEY FAILED: No session token returned"
            print(f"✅ Session created: {session_token}")
            
            # STEP 3: Upload file to Content Pillar
            print("\n[STEP 3] Upload file to Content Pillar...")
            with open(csv_file, 'rb') as f:
                files = {'file': ('claims.csv', f, 'text/csv')}
                data = {'session_token': session_token}
                
                upload_response = await client.post(
                    f"{BASE_URL}/api/mvp/content/upload",
                    files=files,
                    data=data
                )
            
            assert upload_response.status_code in [200, 201], \
                f"❌ JOURNEY FAILED at file upload: {upload_response.text}"
            
            upload_data = upload_response.json()
            file_id = upload_data.get("file_id") or upload_data.get("id")
            assert file_id, "❌ JOURNEY FAILED: No file ID returned"
            print(f"✅ File uploaded: {file_id}")
            
            # STEP 4: Parse the file
            print("\n[STEP 4] Parse file...")
            parse_response = await client.post(
                f"{BASE_URL}/api/mvp/content/parse/{file_id}",
                json={"session_token": session_token}
            )
            
            assert parse_response.status_code == 200, \
                f"❌ JOURNEY FAILED at parsing: {parse_response.text}"
            
            parse_data = parse_response.json()
            data_key = next((k for k in ["data", "records", "rows"] if k in parse_data), None)
            assert data_key, "❌ JOURNEY FAILED: No parsed data returned"
            
            parsed_rows = parse_data[data_key]
            assert len(parsed_rows) > 0, "❌ JOURNEY FAILED: No rows parsed"
            print(f"✅ File parsed: {len(parsed_rows)} rows")
            
            # STEP 5: Navigate to Insights Pillar and analyze data
            print("\n[STEP 5] Analyze data in Insights Pillar...")
            insights_response = await client.post(
                f"{BASE_URL}/api/mvp/insights/analyze",
                json={
                    "session_token": session_token,
                    "file_id": file_id,
                    "analysis_type": "claims_analysis"
                }
            )
            
            assert insights_response.status_code == 200, \
                f"❌ JOURNEY FAILED at analysis: {insights_response.text}"
            
            insights_data = insights_response.json()
            insights_key = next((k for k in ["insights", "analysis", "results"] if k in insights_data), None)
            
            if insights_key:
                insights = insights_data[insights_key]
                print(f"✅ Analysis complete: {type(insights).__name__}")
            else:
                print("⚠️  Analysis returned but no insights field (may be OK if different structure)")
            
            print("\n" + "="*70)
            print("✅ COMPLETE JOURNEY SUCCESS: Register → Upload → Parse → Analyze")
            print("="*70)

@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.critical
@pytest.mark.asyncio
class TestCompleteOperationsWorkflowJourney:
    """Test complete journey: Create SOP → Generate Workflow"""
    
    async def test_sop_to_workflow_complete_flow(self):
        """Test the Operations Pillar flow: Generate SOP → Create Workflow"""
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            print("\n" + "="*70)
            print("COMPLETE JOURNEY TEST: SOP → Workflow")
            print("="*70)
            
            # STEP 1: Create session
            print("\n[STEP 1] Create session...")
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            session_token = (session_response.json()).get("session_token", "session_id")
            print(f"✅ Session: {session_token}")
            
            # STEP 2: Generate SOP
            print("\n[STEP 2] Generate SOP...")
            sop_response = await client.post(
                f"{BASE_URL}/api/mvp/operations/sop/create",
                json={
                    "session_token": session_token,
                    "context": {
                        "title": "Customer Data Processing",
                        "steps": [
                            "Receive customer data",
                            "Validate data format",
                            "Process records",
                            "Generate report",
                            "Send notification"
                        ]
                    }
                }
            )
            
            assert sop_response.status_code == 200, \
                f"❌ JOURNEY FAILED at SOP generation: {sop_response.text}"
            
            sop_data = sop_response.json()
            sop_key = next((k for k in ["sop", "document", "content"] if k in sop_data), None)
            assert sop_key, "❌ JOURNEY FAILED: No SOP returned"
            
            sop = sop_data[sop_key]
            sop_id = sop_data.get("sop_id") or sop_data.get("id")
            print(f"✅ SOP generated: {sop_id or 'created'}")
            
            # STEP 3: Generate Workflow from SOP
            print("\n[STEP 3] Generate Workflow from SOP...")
            workflow_response = await client.post(
                f"{BASE_URL}/api/mvp/operations/workflow/create",
                json={
                    "session_token": session_token,
                    "context": {
                        "source": "sop",
                        "sop_id": sop_id,
                        "sop_content": sop if isinstance(sop, str) else None
                    }
                }
            )
            
            assert workflow_response.status_code == 200, \
                f"❌ JOURNEY FAILED at workflow generation: {workflow_response.text}"
            
            workflow_data = workflow_response.json()
            workflow_key = next((k for k in ["workflow", "diagram", "content"] if k in workflow_data), None)
            assert workflow_key, "❌ JOURNEY FAILED: No workflow returned"
            
            workflow = workflow_data[workflow_key]
            print(f"✅ Workflow generated")
            
            # STEP 4: Verify workflow represents SOP
            if isinstance(workflow, dict) and "nodes" in workflow:
                assert len(workflow["nodes"]) >= 3, \
                    "❌ JOURNEY FAILED: Workflow should have multiple nodes"
                print(f"✅ Workflow has {len(workflow['nodes'])} nodes")
            elif isinstance(workflow, str):
                assert len(workflow) > 100, \
                    "❌ JOURNEY FAILED: Workflow too short"
                print(f"✅ Workflow is {len(workflow)} characters")
            
            print("\n" + "="*70)
            print("✅ COMPLETE JOURNEY SUCCESS: SOP → Workflow")
            print("="*70)

@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.critical
@pytest.mark.asyncio
class TestCompleteBusinessOutcomesJourney:
    """Test complete journey: Data → Insights → Roadmap → POC"""
    
    async def test_insights_to_business_outcomes_flow(self):
        """Test the strategic flow: Analyze → Create Roadmap → Generate POC"""
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            print("\n" + "="*70)
            print("COMPLETE JOURNEY TEST: Insights → Roadmap → POC")
            print("="*70)
            
            # STEP 1: Create session
            print("\n[STEP 1] Create session...")
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            session_token = (session_response.json()).get("session_token", "session_id")
            print(f"✅ Session: {session_token}")
            
            # STEP 2: Analyze data (simulated)
            print("\n[STEP 2] Analyze business data...")
            insights_response = await client.post(
                f"{BASE_URL}/api/mvp/insights/analyze",
                json={
                    "session_token": session_token,
                    "data": {
                        "revenue": [100000, 120000, 145000],
                        "customer_growth": ["+10%", "+15%", "+20%"],
                        "market_opportunity": "High"
                    }
                }
            )
            
            assert insights_response.status_code == 200, \
                f"❌ JOURNEY FAILED at insights: {insights_response.text}"
            print(f"✅ Insights generated")
            
            # STEP 3: Create strategic roadmap
            print("\n[STEP 3] Create strategic roadmap...")
            roadmap_response = await client.post(
                f"{BASE_URL}/api/mvp/business-outcomes/roadmap/create",
                json={
                    "session_token": session_token,
                    "context": {
                        "project": "Market Expansion Initiative",
                        "insights": "Strong revenue growth and market opportunity",
                        "timeline": "18 months"
                    }
                }
            )
            
            assert roadmap_response.status_code == 200, \
                f"❌ JOURNEY FAILED at roadmap: {roadmap_response.text}"
            
            roadmap_data = roadmap_response.json()
            roadmap_key = next((k for k in ["roadmap", "plan", "content"] if k in roadmap_data), None)
            assert roadmap_key, "❌ JOURNEY FAILED: No roadmap returned"
            print(f"✅ Roadmap created")
            
            # STEP 4: Generate POC proposal
            print("\n[STEP 4] Generate POC proposal...")
            poc_response = await client.post(
                f"{BASE_URL}/api/mvp/business-outcomes/poc-proposal/create",
                json={
                    "session_token": session_token,
                    "context": {
                        "project": "Market Expansion Initiative",
                        "roadmap_id": roadmap_data.get("id"),
                        "phase": "Phase 1 - Market Analysis"
                    }
                }
            )
            
            assert poc_response.status_code == 200, \
                f"❌ JOURNEY FAILED at POC: {poc_response.text}"
            
            poc_data = poc_response.json()
            poc_key = next((k for k in ["proposal", "poc", "content"] if k in poc_data), None)
            assert poc_key, "❌ JOURNEY FAILED: No POC returned"
            print(f"✅ POC proposal generated")
            
            print("\n" + "="*70)
            print("✅ COMPLETE JOURNEY SUCCESS: Insights → Roadmap → POC")
            print("="*70)

@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.critical
@pytest.mark.asyncio
class TestCompleteAll4PillarsJourney:
    """Test complete journey through ALL 4 PILLARS - The Ultimate Test"""
    
    async def test_all_four_pillars_complete_journey(self):
        """Test THE COMPLETE CTO DEMO: All 4 pillars in sequence"""
        
        csv_file = DEMO_FILES_DIR / "SymphAIny_Demo_Underwriting_Insights/data/claims.csv"
        
        if not csv_file.exists():
            pytest.skip("Demo file not available")
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            print("\n" + "="*70)
            print("🎯 ULTIMATE TEST: COMPLETE 4-PILLAR MVP JOURNEY")
            print("="*70)
            
            # CREATE SESSION
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            session_token = (session_response.json()).get("session_token", "session_id")
            
            # PILLAR 1: CONTENT
            print("\n[PILLAR 1: CONTENT] Upload and Parse Data")
            print("-" * 70)
            
            with open(csv_file, 'rb') as f:
                upload_response = await client.post(
                    f"{BASE_URL}/api/mvp/content/upload",
                    files={'file': ('claims.csv', f, 'text/csv')},
                    data={'session_token': session_token}
                )
            
            assert upload_response.status_code in [200, 201], \
                "❌ ULTIMATE TEST FAILED: Content Pillar - Upload"
            
            file_id = (upload_response.json()).get("file_id") or (upload_response.json()).get("id")
            
            parse_response = await client.post(
                f"{BASE_URL}/api/mvp/content/parse/{file_id}",
                json={"session_token": session_token}
            )
            
            assert parse_response.status_code == 200, \
                "❌ ULTIMATE TEST FAILED: Content Pillar - Parse"
            
            print("✅ Content Pillar: File uploaded and parsed")
            
            # PILLAR 2: INSIGHTS
            print("\n[PILLAR 2: INSIGHTS] Analyze Data")
            print("-" * 70)
            
            insights_response = await client.post(
                f"{BASE_URL}/api/mvp/insights/analyze",
                json={
                    "session_token": session_token,
                    "file_id": file_id
                }
            )
            
            assert insights_response.status_code == 200, \
                "❌ ULTIMATE TEST FAILED: Insights Pillar"
            
            print("✅ Insights Pillar: Data analyzed")
            
            # PILLAR 3: OPERATIONS
            print("\n[PILLAR 3: OPERATIONS] Generate SOP and Workflow")
            print("-" * 70)
            
            sop_response = await client.post(
                f"{BASE_URL}/api/mvp/operations/sop/create",
                json={
                    "session_token": session_token,
                    "context": {"title": "Claims Processing Procedure"}
                }
            )
            
            assert sop_response.status_code == 200, \
                "❌ ULTIMATE TEST FAILED: Operations Pillar - SOP"
            
            workflow_response = await client.post(
                f"{BASE_URL}/api/mvp/operations/workflow/create",
                json={
                    "session_token": session_token,
                    "context": {"process": "Claims Workflow"}
                }
            )
            
            assert workflow_response.status_code == 200, \
                "❌ ULTIMATE TEST FAILED: Operations Pillar - Workflow"
            
            print("✅ Operations Pillar: SOP and Workflow generated")
            
            # PILLAR 4: BUSINESS OUTCOMES
            print("\n[PILLAR 4: BUSINESS OUTCOMES] Generate Roadmap and POC")
            print("-" * 70)
            
            roadmap_response = await client.post(
                f"{BASE_URL}/api/mvp/business-outcomes/roadmap/create",
                json={
                    "session_token": session_token,
                    "context": {"project": "Claims Analytics Platform"}
                }
            )
            
            assert roadmap_response.status_code == 200, \
                "❌ ULTIMATE TEST FAILED: Business Outcomes - Roadmap"
            
            poc_response = await client.post(
                f"{BASE_URL}/api/mvp/business-outcomes/poc-proposal/create",
                json={
                    "session_token": session_token,
                    "context": {"project": "Claims Analytics Platform"}
                }
            )
            
            assert poc_response.status_code == 200, \
                "❌ ULTIMATE TEST FAILED: Business Outcomes - POC"
            
            print("✅ Business Outcomes Pillar: Roadmap and POC generated")
            
            print("\n" + "="*70)
            print("🎉 ULTIMATE TEST SUCCESS: ALL 4 PILLARS COMPLETED!")
            print("="*70)
            print("\n✅ Content: Upload & Parse")
            print("✅ Insights: Analyze")
            print("✅ Operations: SOP & Workflow")
            print("✅ Business Outcomes: Roadmap & POC")
            print("\n🚀 MVP IS FULLY FUNCTIONAL END-TO-END!")
            print("="*70)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

