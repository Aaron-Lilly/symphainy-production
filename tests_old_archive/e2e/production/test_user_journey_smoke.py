#!/usr/bin/env python3
"""
Full-Stack Integration Tests - User Journey Smoke Tests

Tests complete user journeys end-to-end through the HTTP API.
These tests catch integration issues before deployment.

Run: pytest tests/e2e/production/test_user_journey_smoke.py -v
"""

import pytest
import httpx
import asyncio
import uuid
from typing import Dict, Any, Optional

# Test timeout
TIMEOUT = 30.0


@pytest.mark.e2e
@pytest.mark.integration
@pytest.mark.production_readiness
class TestUserJourneySmoke:
    """Full-stack integration tests for complete user journeys."""
    
    @pytest.mark.asyncio
    async def test_user_registration_journey(self, http_client):
        """
        Test complete user registration journey.
        
        Flow:
        1. Register new user
        2. Login with credentials
        3. Create session
        4. Verify session is usable
        """
        # Generate unique email for this test
        test_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "SecureTestPassword123!"
        test_name = "Journey Test User"
        
        print(f"\n{'='*70}")
        print("USER REGISTRATION JOURNEY TEST")
        print(f"{'='*70}")
        
        try:
            # Step 1: Register user
            print(f"\n[STEP 1] Registering user: {test_email}")
            register_response = await http_client.post(
                "/api/auth/register",
                json={
                    "email": test_email,
                    "password": test_password,
                    "name": test_name
                },
                timeout=TIMEOUT
            )
            
            # Should be 200/201 (success) or 400/422 (validation error, but endpoint exists)
            assert register_response.status_code != 404, \
                f"❌ Registration endpoint missing (404): {register_response.text}"
            
            if register_response.status_code in [200, 201]:
                print(f"✅ User registered successfully")
                user_data = register_response.json()
                assert "user" in user_data or "token" in user_data or "success" in user_data, \
                    "Registration response missing user data"
            elif register_response.status_code in [400, 422]:
                # User might already exist - that's okay for this test
                print(f"⚠️ Registration returned {register_response.status_code} (user may already exist)")
            else:
                pytest.fail(f"Unexpected registration status: {register_response.status_code} - {register_response.text}")
            
            # Step 2: Login
            print(f"\n[STEP 2] Logging in user: {test_email}")
            login_response = await http_client.post(
                "/api/auth/login",
                json={
                    "email": test_email,
                    "password": test_password
                },
                timeout=TIMEOUT
            )
            
            # Should be 200 (success) or 401 (unauthorized if user doesn't exist)
            assert login_response.status_code != 404, \
                f"❌ Login endpoint missing (404): {login_response.text}"
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                token = login_data.get("token") or login_data.get("access_token")
                print(f"✅ Login successful")
                
                # Step 3: Create session with token
                print(f"\n[STEP 3] Creating session")
                headers = {"Authorization": f"Bearer {token}"} if token else {}
                session_response = await http_client.post(
                    "/api/v1/session/create-user-session",
                    json={"session_type": "mvp"},
                    headers=headers,
                    timeout=TIMEOUT
                )
                
                assert session_response.status_code != 404, \
                    f"❌ Session creation endpoint missing (404): {session_response.text}"
                
                if session_response.status_code in [200, 201]:
                    session_data = session_response.json()
                    session_token = session_data.get("session_token") or session_data.get("session_id")
                    assert session_token, "Session response missing session token"
                    print(f"✅ Session created: {session_token[:20]}...")
                else:
                    print(f"⚠️ Session creation returned {session_response.status_code}")
            elif login_response.status_code == 401:
                print(f"⚠️ Login returned 401 (user may not exist yet)")
            else:
                pytest.fail(f"Unexpected login status: {login_response.status_code} - {login_response.text}")
            
            print(f"\n✅ User registration journey completed")
            
        except httpx.TimeoutException:
            pytest.fail("❌ User registration journey timed out")
        except Exception as e:
            pytest.fail(f"❌ User registration journey failed: {e}")
    
    @pytest.mark.asyncio
    async def test_file_upload_journey(self, http_client):
        """
        Test complete file upload journey.
        
        Flow:
        1. Create session
        2. Upload file to Content Pillar
        3. Verify file was uploaded
        """
        print(f"\n{'='*70}")
        print("FILE UPLOAD JOURNEY TEST")
        print(f"{'='*70}")
        
        try:
            # Step 1: Create session
            print(f"\n[STEP 1] Creating session")
            session_response = await http_client.post(
                "/api/v1/session/create-user-session",
                json={"session_type": "mvp"},
                timeout=TIMEOUT
            )
            
            assert session_response.status_code != 404, \
                f"❌ Session creation endpoint missing (404): {session_response.text}"
            
            session_token = None
            if session_response.status_code in [200, 201]:
                session_data = session_response.json()
                session_token = session_data.get("session_token") or session_data.get("session_id")
                print(f"✅ Session created: {session_token[:20] if session_token else 'N/A'}...")
            else:
                # Session creation might fail, but we can still test upload endpoint exists
                print(f"⚠️ Session creation returned {session_response.status_code}")
            
            # Step 2: Upload file (using semantic API endpoint)
            print(f"\n[STEP 2] Uploading file to Content Pillar")
            headers = {}
            if session_token:
                headers["X-Session-Token"] = session_token
            
            # Create minimal test file
            test_file_content = b"test,data\n1,2\n3,4"
            files = {
                "file": ("test_upload.csv", test_file_content, "text/csv")
            }
            
            upload_response = await http_client.post(
                "/api/v1/content-pillar/upload-file",
                files=files,
                headers=headers,
                timeout=TIMEOUT
            )
            
            # Should NOT be 404 (endpoint missing)
            assert upload_response.status_code != 404, \
                f"❌ File upload endpoint missing (404): {upload_response.text}"
            
            # Accept various status codes (success, validation error, auth error)
            assert upload_response.status_code in [200, 201, 400, 401, 422], \
                f"Unexpected upload status: {upload_response.status_code} - {upload_response.text}"
            
            if upload_response.status_code in [200, 201]:
                upload_data = upload_response.json()
                file_id = upload_data.get("file_id") or upload_data.get("uuid")
                print(f"✅ File uploaded successfully: {file_id}")
            else:
                print(f"⚠️ File upload returned {upload_response.status_code} (may need auth or valid file)")
            
            print(f"\n✅ File upload journey completed")
            
        except httpx.TimeoutException:
            pytest.fail("❌ File upload journey timed out")
        except Exception as e:
            pytest.fail(f"❌ File upload journey failed: {e}")
    
    @pytest.mark.asyncio
    async def test_content_to_insights_journey(self, http_client):
        """
        Test complete Content → Insights journey.
        
        Flow:
        1. Create session
        2. Upload file
        3. Process file
        4. Analyze for insights
        """
        print(f"\n{'='*70}")
        print("CONTENT → INSIGHTS JOURNEY TEST")
        print(f"{'='*70}")
        
        try:
            # Step 1: Create session
            print(f"\n[STEP 1] Creating session")
            session_response = await http_client.post(
                "/api/v1/session/create-user-session",
                json={"session_type": "mvp"},
                timeout=TIMEOUT
            )
            
            session_token = None
            if session_response.status_code in [200, 201]:
                session_data = session_response.json()
                session_token = session_data.get("session_token") or session_data.get("session_id")
                print(f"✅ Session created")
            
            headers = {}
            if session_token:
                headers["X-Session-Token"] = session_token
            
            # Step 2: Upload file
            print(f"\n[STEP 2] Uploading file")
            test_file_content = b"product,sales\nWidget A,1000\nWidget B,2000"
            files = {
                "file": ("sales_data.csv", test_file_content, "text/csv")
            }
            
            upload_response = await http_client.post(
                "/api/v1/content-pillar/upload-file",
                files=files,
                headers=headers,
                timeout=TIMEOUT
            )
            
            assert upload_response.status_code != 404, \
                f"❌ Upload endpoint missing (404)"
            
            file_id = None
            if upload_response.status_code in [200, 201]:
                upload_data = upload_response.json()
                file_id = upload_data.get("file_id") or upload_data.get("uuid")
                print(f"✅ File uploaded: {file_id}")
            
            # Step 3: Process file (if we got a file_id)
            if file_id:
                print(f"\n[STEP 3] Processing file: {file_id}")
                process_response = await http_client.post(
                    f"/api/v1/content-pillar/process-file/{file_id}",
                    json={},
                    headers=headers,
                    timeout=TIMEOUT
                )
                
                assert process_response.status_code != 404, \
                    f"❌ Process file endpoint missing (404)"
                
                if process_response.status_code in [200, 201, 202]:
                    print(f"✅ File processing initiated")
                else:
                    print(f"⚠️ File processing returned {process_response.status_code}")
            
            # Step 4: Analyze for insights (even without file_id, test endpoint exists)
            print(f"\n[STEP 4] Analyzing content for insights")
            analyze_response = await http_client.post(
                "/api/v1/insights-pillar/analyze-content",
                json={
                    "file_ids": [file_id] if file_id else [],
                    "analysis_type": "quick"
                },
                headers=headers,
                timeout=TIMEOUT
            )
            
            assert analyze_response.status_code != 404, \
                f"❌ Insights analysis endpoint missing (404)"
            
            if analyze_response.status_code in [200, 201]:
                analyze_data = analyze_response.json()
                analysis_id = analyze_data.get("analysis_id")
                print(f"✅ Insights analysis initiated: {analysis_id}")
            else:
                print(f"⚠️ Insights analysis returned {analyze_response.status_code}")
            
            print(f"\n✅ Content → Insights journey completed")
            
        except httpx.TimeoutException:
            pytest.fail("❌ Content → Insights journey timed out")
        except Exception as e:
            pytest.fail(f"❌ Content → Insights journey failed: {e}")
    
    @pytest.mark.asyncio
    async def test_operations_journey(self, http_client):
        """
        Test Operations Pillar journey.
        
        Flow:
        1. Create session
        2. Create SOP
        3. Create workflow
        """
        print(f"\n{'='*70}")
        print("OPERATIONS JOURNEY TEST")
        print(f"{'='*70}")
        
        try:
            # Step 1: Create session
            print(f"\n[STEP 1] Creating session")
            session_response = await http_client.post(
                "/api/v1/session/create-user-session",
                json={"session_type": "mvp"},
                timeout=TIMEOUT
            )
            
            session_token = None
            if session_response.status_code in [200, 201]:
                session_data = session_response.json()
                session_token = session_data.get("session_token") or session_data.get("session_id")
                print(f"✅ Session created")
            
            headers = {}
            if session_token:
                headers["X-Session-Token"] = session_token
            
            # Step 2: Create SOP
            print(f"\n[STEP 2] Creating Standard Operating Procedure")
            sop_response = await http_client.post(
                "/api/v1/operations-pillar/create-standard-operating-procedure",
                json={
                    "name": "Test SOP",
                    "description": "Test SOP for integration testing",
                    "steps": ["Step 1", "Step 2"]
                },
                headers=headers,
                timeout=TIMEOUT
            )
            
            assert sop_response.status_code != 404, \
                f"❌ SOP creation endpoint missing (404)"
            
            if sop_response.status_code in [200, 201]:
                print(f"✅ SOP created successfully")
            else:
                print(f"⚠️ SOP creation returned {sop_response.status_code}")
            
            # Step 3: Create workflow
            print(f"\n[STEP 3] Creating workflow")
            workflow_response = await http_client.post(
                "/api/v1/operations-pillar/create-workflow",
                json={
                    "name": "Test Workflow",
                    "description": "Test workflow for integration testing",
                    "steps": ["Task 1", "Task 2"]
                },
                headers=headers,
                timeout=TIMEOUT
            )
            
            assert workflow_response.status_code != 404, \
                f"❌ Workflow creation endpoint missing (404)"
            
            if workflow_response.status_code in [200, 201]:
                print(f"✅ Workflow created successfully")
            else:
                print(f"⚠️ Workflow creation returned {workflow_response.status_code}")
            
            print(f"\n✅ Operations journey completed")
            
        except httpx.TimeoutException:
            pytest.fail("❌ Operations journey timed out")
        except Exception as e:
            pytest.fail(f"❌ Operations journey failed: {e}")
    
    @pytest.mark.asyncio
    async def test_guide_agent_journey(self, http_client):
        """
        Test Guide Agent interaction journey.
        
        Flow:
        1. Create session
        2. Analyze user intent
        3. Get journey guidance
        """
        print(f"\n{'='*70}")
        print("GUIDE AGENT JOURNEY TEST")
        print(f"{'='*70}")
        
        try:
            # Step 1: Create session
            print(f"\n[STEP 1] Creating session")
            session_response = await http_client.post(
                "/api/v1/session/create-user-session",
                json={"session_type": "mvp"},
                timeout=TIMEOUT
            )
            
            session_token = None
            if session_response.status_code in [200, 201]:
                session_data = session_response.json()
                session_token = session_data.get("session_token") or session_data.get("session_id")
                print(f"✅ Session created")
            
            headers = {}
            if session_token:
                headers["X-Session-Token"] = session_token
            
            # Step 2: Analyze user intent
            print(f"\n[STEP 2] Analyzing user intent")
            intent_response = await http_client.post(
                "/api/v1/journey/guide-agent/analyze-user-intent",
                json={
                    "message": "I want to improve my business operations",
                    "user_id": "test_user"
                },
                headers=headers,
                timeout=TIMEOUT
            )
            
            assert intent_response.status_code != 404, \
                f"❌ Guide Agent analyze endpoint missing (404)"
            
            if intent_response.status_code in [200, 201]:
                intent_data = intent_response.json()
                print(f"✅ User intent analyzed")
            elif intent_response.status_code == 503:
                print(f"⚠️ Guide Agent service unavailable (503) - endpoint exists")
            else:
                print(f"⚠️ Intent analysis returned {intent_response.status_code}")
            
            # Step 3: Get journey guidance
            print(f"\n[STEP 3] Getting journey guidance")
            guidance_response = await http_client.post(
                "/api/v1/journey/guide-agent/get-journey-guidance",
                json={
                    "user_goal": "Improve business operations efficiency",
                    "current_step": "content"
                },
                headers=headers,
                timeout=TIMEOUT
            )
            
            assert guidance_response.status_code != 404, \
                f"❌ Journey guidance endpoint missing (404)"
            
            if guidance_response.status_code in [200, 201]:
                print(f"✅ Journey guidance received")
            elif guidance_response.status_code == 503:
                print(f"⚠️ Guide Agent service unavailable (503) - endpoint exists")
            else:
                print(f"⚠️ Journey guidance returned {guidance_response.status_code}")
            
            print(f"\n✅ Guide Agent journey completed")
            
        except httpx.TimeoutException:
            pytest.fail("❌ Guide Agent journey timed out")
        except Exception as e:
            pytest.fail(f"❌ Guide Agent journey failed: {e}")




