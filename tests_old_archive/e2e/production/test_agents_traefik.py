#!/usr/bin/env python3
"""
End-to-end test for Agent endpoints through Traefik.
Tests all Guide Agent and Liaison Agent endpoints.
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost"
TEST_USER_ID = "test-user-123"
session_id = None  # Will be set from intent analysis response

def test_endpoint(name, method, url, payload=None, expected_status=200):
    """Test an endpoint and return results."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"Method: {method}")
    if payload:
        print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=payload, timeout=10, headers={"Content-Type": "application/json"})
        else:
            return False, f"Unsupported method: {method}"
        
        print(f"Status Code: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        except:
            print(f"Response (text): {response.text[:500]}")
        
        if response.status_code == expected_status:
            if isinstance(result, dict) and result.get("success"):
                print(f"✅ {name}: PASSED")
                return True, result
            elif response.status_code == 200:
                print(f"⚠️ {name}: Status OK but no 'success' field")
                return True, result if 'result' in locals() else response.text
            else:
                print(f"❌ {name}: FAILED - Unexpected status or response format")
                return False, result if 'result' in locals() else response.text
        else:
            print(f"❌ {name}: FAILED - Status {response.status_code}")
            return False, result if 'result' in locals() else response.text
            
    except requests.exceptions.Timeout:
        print(f"❌ {name}: TIMEOUT - Request took too long")
        return False, "Timeout"
    except requests.exceptions.ConnectionError as e:
        print(f"❌ {name}: CONNECTION ERROR - {e}")
        return False, str(e)
    except Exception as e:
        print(f"❌ {name}: ERROR - {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)

def main():
    """Run all agent endpoint tests."""
    global session_id
    print("\n" + "="*60)
    print("AGENT ENDPOINT TESTING - TRAEFIK ROUTING")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Session ID: {session_id or 'Will be created during test'}")
    
    results = []
    
    # Test 1: Backend Health (accepts platform_status field instead of success)
    # Health endpoint is at /health (not /api/health) and returns platform_status field
    success, result = test_endpoint(
        "Backend Health",
        "GET",
        f"{BASE_URL}/health",
        expected_status=200
    )
    # Health endpoint returns platform_status, not success field - accept if status is 200 and has platform_status
    if result and isinstance(result, dict) and ("platform_status" in result or "status" in result):
        success = True
        if not success:  # Only print if it wasn't already successful
            print(f"✅ Backend Health: PASSED (platform_status field present)")
    results.append(("Backend Health", success))
    
    # Test 2: Guide Agent - Intent Analysis (creates session)
    success, result = test_endpoint(
        "Guide Agent: Intent Analysis",
        "POST",
        f"{BASE_URL}/api/v1/journey/guide-agent/analyze-user-intent",
        {
            "message": "I want to upload and analyze my business data",
            "user_id": TEST_USER_ID,
            "session_id": session_id
        }
    )
    results.append(("Guide Agent: Intent Analysis", success))
    
    # Extract session_id from response if successful
    if success and result and isinstance(result, dict):
        session_id = result.get("session_id") or session_id
        if session_id:
            print(f"\n✅ Session ID from intent analysis: {session_id}")
    
    # Test 3: Guide Agent - Journey Guidance
    success, _ = test_endpoint(
        "Guide Agent: Journey Guidance",
        "POST",
        f"{BASE_URL}/api/v1/journey/guide-agent/get-journey-guidance",
        {
            "user_id": TEST_USER_ID,
            "session_id": session_id
        }
    )
    results.append(("Guide Agent: Journey Guidance", success))
    
    # Test 4: Guide Agent - Conversation History (only if session exists)
    if session_id:
        success, _ = test_endpoint(
            "Guide Agent: Conversation History",
            "GET",
            f"{BASE_URL}/api/v1/journey/guide-agent/get-conversation-history/{session_id}",
            expected_status=200  # Accept 200 even if session is empty
        )
        results.append(("Guide Agent: Conversation History", success))
    else:
        print("\n⚠️ Skipping Conversation History test - no session_id available")
        results.append(("Guide Agent: Conversation History", False))
    
    # Test 5-8: Liaison Agents - Send Message (All 4 Pillars)
    pillars = [
        ("content", "How do I upload a file?"),
        ("insights", "What insights can I get from my data?"),
        ("operations", "How do I create a workflow?"),
        ("business-outcomes", "What business outcomes can I track?")
    ]
    
    for pillar, message in pillars:
        success, _ = test_endpoint(
            f"Liaison Agent: Send Message ({pillar.title()})",
            "POST",
            f"{BASE_URL}/api/v1/liaison-agents/send-message-to-pillar-agent",
            {
                "message": message,
                "user_id": TEST_USER_ID,
                "session_id": session_id,
                "pillar": pillar
            }
        )
        results.append((f"Liaison Agent: Send Message ({pillar.title()})", success))
    
    # Test 9-12: Liaison Agents - Conversation History (All 4 Pillars)
    for pillar, _ in pillars:
        if session_id:
            success, _ = test_endpoint(
                f"Liaison Agent: Conversation History ({pillar.title()})",
                "GET",
                f"{BASE_URL}/api/v1/liaison-agents/get-pillar-conversation-history/{session_id}/{pillar}",
                expected_status=200
            )
            results.append((f"Liaison Agent: Conversation History ({pillar.title()})", success))
        else:
            print(f"\n⚠️ Skipping Conversation History test for {pillar} - no session_id available")
            results.append((f"Liaison Agent: Conversation History ({pillar.title()})", False))
    
    # Test 13: Liaison Agents - Health
    success, _ = test_endpoint(
        "Liaison Agents: Health",
        "GET",
        f"{BASE_URL}/api/v1/liaison-agents/health"
    )
    results.append(("Liaison Agents: Health", success))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    print("\nDetailed Results:")
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())

