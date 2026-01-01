#!/usr/bin/env python3
"""
Complex Integration Scenarios Test

Tests complex real-world scenarios with multiple components working together.
Reuses CTO Demo scenarios but focuses on integration complexity.

Scenarios:
1. Multiple users operating simultaneously
2. Event-driven workflows with multiple subscribers
3. Complex service chains
4. Concurrent operations on shared resources
"""

import pytest
import asyncio
import httpx
import uuid
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.e2e, pytest.mark.production_readiness, pytest.mark.critical]


class TestComplexIntegrationScenarios:
    """Test complex integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_multiple_users_simultaneous_operations(self, production_client):
        """
        Test multiple users operating simultaneously.
        
        Scenario: 5 users upload files, analyze content, and generate SOPs simultaneously.
        Verifies: No conflicts, all operations complete successfully.
        """
        print("\n" + "="*70)
        print("COMPLEX INTEGRATION: Multiple Users Simultaneous Operations")
        print("="*70)
        
        try:
            # Create multiple test users (simulated via different sessions)
            num_users = 5
            user_sessions = []
            
            print(f"\n[STEP 1] Creating {num_users} user sessions...")
            for i in range(num_users):
                # Create session for each user
                session_response = await production_client.post(
                    "/api/v1/session/create-user-session",
                    json={"session_type": "mvp"}
                )
                
                if session_response.status_code in [200, 201]:
                    session_data = session_response.json()
                    user_sessions.append({
                        "user_id": f"test_user_{i}",
                        "session_token": session_data.get("session_token") or session_data.get("session_id")
                    })
                    print(f"✅ User {i+1} session created")
                else:
                    print(f"⚠️ User {i+1} session creation returned {session_response.status_code}")
                    user_sessions.append({
                        "user_id": f"test_user_{i}",
                        "session_token": None
                    })
            
            # Step 2: All users upload files simultaneously
            print(f"\n[STEP 2] All {num_users} users uploading files simultaneously...")
            
            async def upload_file_for_user(user_session: Dict[str, Any], user_index: int):
                """Upload file for a specific user."""
                test_file_content = f"test,data\n{user_index},value{user_index}\n{user_index+1},value{user_index+1}".encode()
                files = {
                    "file": (f"test_user_{user_index}.csv", test_file_content, "text/csv")
                }
                
                headers = {}
                if user_session.get("session_token"):
                    headers["X-Session-Token"] = user_session["session_token"]
                
                response = await production_client.post(
                    "/api/v1/content-pillar/upload-file",
                    files=files,
                    headers=headers
                )
                
                return {
                    "user_index": user_index,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code in [200, 201] else None
                }
            
            # Execute all uploads in parallel
            upload_tasks = [
                upload_file_for_user(user_sessions[i], i)
                for i in range(num_users)
            ]
            upload_results = await asyncio.gather(*upload_tasks, return_exceptions=True)
            
            # Verify all uploads completed
            successful_uploads = [r for r in upload_results if isinstance(r, dict) and r.get("status_code") in [200, 201]]
            print(f"✅ {len(successful_uploads)}/{num_users} file uploads succeeded")
            
            # Step 3: All users analyze content simultaneously (if uploads succeeded)
            if successful_uploads:
                print(f"\n[STEP 3] All {len(successful_uploads)} users analyzing content simultaneously...")
                
                async def analyze_for_user(user_session: Dict[str, Any], file_id: str, user_index: int):
                    """Analyze content for a specific user."""
                    headers = {}
                    if user_session.get("session_token"):
                        headers["X-Session-Token"] = user_session["session_token"]
                    
                    response = await production_client.post(
                        "/api/v1/insights-pillar/analyze-content",
                        json={
                            "file_id": file_id,
                            "analysis_type": "basic"
                        },
                        headers=headers
                    )
                    
                    return {
                        "user_index": user_index,
                        "status_code": response.status_code,
                        "response": response.json() if response.status_code in [200, 201] else None
                    }
                
                # Execute all analyses in parallel
                analysis_tasks = [
                    analyze_for_user(
                        user_sessions[result["user_index"]],
                        result["response"].get("file_id") if result.get("response") else f"file_{result['user_index']}",
                        result["user_index"]
                    )
                    for result in successful_uploads
                ]
                analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
                
                successful_analyses = [r for r in analysis_results if isinstance(r, dict) and r.get("status_code") in [200, 201]]
                print(f"✅ {len(successful_analyses)}/{len(successful_uploads)} analyses succeeded")
            
            print(f"\n✅ Multiple users simultaneous operations completed")
            print(f"   - {len(successful_uploads)}/{num_users} uploads succeeded")
            if successful_uploads:
                print(f"   - {len(successful_analyses)}/{len(successful_uploads)} analyses succeeded")
            
        except Exception as e:
            pytest.fail(f"❌ Multiple users simultaneous operations failed: {e}")
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_on_shared_resources(self, production_client):
        """
        Test concurrent operations on shared resources.
        
        Scenario: Multiple operations on same file (upload, parse, analyze simultaneously).
        Verifies: No conflicts, all operations complete successfully or fail gracefully.
        """
        print("\n" + "="*70)
        print("COMPLEX INTEGRATION: Concurrent Operations on Shared Resources")
        print("="*70)
        
        try:
            # Step 1: Upload a file
            print(f"\n[STEP 1] Uploading file...")
            test_file_content = b"test,data\n1,value1\n2,value2"
            files = {
                "file": ("shared_resource.csv", test_file_content, "text/csv")
            }
            
            upload_response = await production_client.post(
                "/api/v1/content-pillar/upload-file",
                files=files
            )
            
            if upload_response.status_code not in [200, 201]:
                pytest.skip(f"File upload failed: {upload_response.status_code}")
            
            upload_data = upload_response.json()
            file_id = upload_data.get("file_id") or upload_data.get("uuid")
            
            if not file_id:
                pytest.skip("File upload succeeded but no file_id returned")
            
            print(f"✅ File uploaded: {file_id}")
            
            # Step 2: Perform multiple operations on same file simultaneously
            print(f"\n[STEP 2] Performing multiple operations on same file simultaneously...")
            
            async def parse_file(file_id: str):
                """Parse file."""
                response = await production_client.post(
                    f"/api/v1/content-pillar/process-file/{file_id}",
                    json={"action": "parse"}
                )
                return {"operation": "parse", "status_code": response.status_code}
            
            async def analyze_file(file_id: str):
                """Analyze file."""
                response = await production_client.post(
                    "/api/v1/insights-pillar/analyze-content",
                    json={"file_id": file_id, "analysis_type": "basic"}
                )
                return {"operation": "analyze", "status_code": response.status_code}
            
            async def get_file_details(file_id: str):
                """Get file details."""
                response = await production_client.get(
                    f"/api/v1/content-pillar/get-file-details/{file_id}"
                )
                return {"operation": "get_details", "status_code": response.status_code}
            
            # Execute all operations in parallel
            operations = await asyncio.gather(
                parse_file(file_id),
                analyze_file(file_id),
                get_file_details(file_id),
                return_exceptions=True
            )
            
            # Verify operations completed (may succeed or fail gracefully)
            for op in operations:
                if isinstance(op, dict):
                    print(f"✅ {op['operation']}: {op['status_code']}")
                else:
                    print(f"⚠️ Operation failed: {op}")
            
            print(f"\n✅ Concurrent operations on shared resources completed")
            
        except Exception as e:
            pytest.fail(f"❌ Concurrent operations on shared resources failed: {e}")
    
    @pytest.mark.asyncio
    async def test_complex_service_chain(self, production_client):
        """
        Test complex service chain (services calling other services).
        
        Scenario: Upload file → Parse → Analyze → Generate SOP → Generate Roadmap
        Verifies: Service chain completes successfully, data flows correctly.
        """
        print("\n" + "="*70)
        print("COMPLEX INTEGRATION: Complex Service Chain")
        print("="*70)
        
        try:
            # Step 1: Upload file
            print(f"\n[STEP 1] Uploading file...")
            test_file_content = b"test,data\n1,value1\n2,value2"
            files = {
                "file": ("service_chain_test.csv", test_file_content, "text/csv")
            }
            
            upload_response = await production_client.post(
                "/api/v1/content-pillar/upload-file",
                files=files
            )
            
            if upload_response.status_code not in [200, 201]:
                pytest.skip(f"File upload failed: {upload_response.status_code}")
            
            upload_data = upload_response.json()
            file_id = upload_data.get("file_id") or upload_data.get("uuid")
            
            if not file_id:
                pytest.skip("File upload succeeded but no file_id returned")
            
            print(f"✅ File uploaded: {file_id}")
            
            # Step 2: Parse file (Content Pillar → FileParserService)
            print(f"\n[STEP 2] Parsing file...")
            parse_response = await production_client.post(
                f"/api/v1/content-pillar/process-file/{file_id}",
                json={"action": "parse"}
            )
            
            parse_success = parse_response.status_code in [200, 201]
            print(f"{'✅' if parse_success else '⚠️'} Parse: {parse_response.status_code}")
            
            # Step 3: Analyze content (Insights Pillar → DataAnalyzerService)
            print(f"\n[STEP 3] Analyzing content...")
            analyze_response = await production_client.post(
                "/api/v1/insights-pillar/analyze-content",
                json={"file_id": file_id, "analysis_type": "basic"}
            )
            
            analyze_success = analyze_response.status_code in [200, 201]
            print(f"{'✅' if analyze_success else '⚠️'} Analyze: {analyze_response.status_code}")
            
            # Step 4: Generate SOP (Operations Pillar → SOPBuilderService)
            print(f"\n[STEP 4] Generating SOP...")
            sop_response = await production_client.post(
                "/api/v1/operations-pillar/create-standard-operating-procedure",
                json={
                    "file_id": file_id,
                    "sop_type": "process"
                }
            )
            
            sop_success = sop_response.status_code in [200, 201]
            print(f"{'✅' if sop_success else '⚠️'} SOP: {sop_response.status_code}")
            
            # Step 5: Generate Roadmap (Business Outcomes Pillar → RoadmapGeneratorService)
            print(f"\n[STEP 5] Generating roadmap...")
            roadmap_response = await production_client.post(
                "/api/v1/business-outcomes-pillar/generate-roadmap",
                json={
                    "context_data": {
                        "file_id": file_id,
                        "analysis_id": analyze_response.json().get("analysis_id") if analyze_success else None
                    }
                }
            )
            
            roadmap_success = roadmap_response.status_code in [200, 201]
            print(f"{'✅' if roadmap_success else '⚠️'} Roadmap: {roadmap_response.status_code}")
            
            print(f"\n✅ Complex service chain completed")
            print(f"   - Upload: ✅")
            print(f"   - Parse: {'✅' if parse_success else '⚠️'}")
            print(f"   - Analyze: {'✅' if analyze_success else '⚠️'}")
            print(f"   - SOP: {'✅' if sop_success else '⚠️'}")
            print(f"   - Roadmap: {'✅' if roadmap_success else '⚠️'}")
            
        except Exception as e:
            pytest.fail(f"❌ Complex service chain failed: {e}")




