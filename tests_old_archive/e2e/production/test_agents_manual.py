#!/usr/bin/env python3
"""
Manual Agent Testing Script

Tests Guide Agent and all 4 Liaison Agents individually.
Run this script to verify agent functionality before creating E2E tests.

Usage:
    python3 tests/e2e/production/test_agents_manual.py
"""

import asyncio
import httpx
import json
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, project_root)

BACKEND_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
TIMEOUT = 30.0

# Test user and session
TEST_USER_ID = f"test-user-{datetime.now().strftime('%Y%m%d%H%M%S')}"
TEST_SESSION_TOKEN = f"test-session-{datetime.now().strftime('%Y%m%d%H%M%S')}"


class AgentTester:
    """Manual agent testing utility."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BACKEND_URL, timeout=TIMEOUT)
        self.session_id = None
        self.test_results = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_result(self, test_name: str, success: bool, response: Dict[str, Any], error: Optional[str] = None):
        """Log test result."""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "response": response,
            "error": error
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"\n{status} {test_name}")
        if error:
            print(f"   Error: {error}")
        if response:
            print(f"   Response: {json.dumps(response, indent=2)[:500]}...")
    
    async def create_session(self) -> Optional[str]:
        """Create a test session."""
        try:
            response = await self.client.post(
                "/api/v1/session/create-user-session",
                json={
                    "user_id": TEST_USER_ID,
                    "session_type": "mvp",
                    "context": {"test": True}
                }
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.session_id = data.get("session_id") or data.get("session", {}).get("session_id")
                print(f"✅ Session created: {self.session_id}")
                return self.session_id
            else:
                print(f"⚠️ Session creation returned {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"⚠️ Session creation failed: {e}")
            return None
    
    # ============================================================================
    # GUIDE AGENT TESTS
    # ============================================================================
    
    async def test_guide_agent_intent_analysis(self) -> bool:
        """Test Guide Agent intent analysis."""
        test_name = "Guide Agent: Intent Analysis"
        
        try:
            response = await self.client.post(
                "/api/v1/journey/guide-agent/analyze-user-intent",
                json={
                    "message": "I want to upload and analyze my business data",
                    "user_id": TEST_USER_ID,
                    "session_token": TEST_SESSION_TOKEN
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                has_intent = "intent_analysis" in data or "intent" in data
                self.log_result(test_name, has_intent, data)
                return has_intent
            else:
                self.log_result(test_name, False, {}, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result(test_name, False, {}, str(e))
            return False
    
    async def test_guide_agent_journey_guidance(self) -> bool:
        """Test Guide Agent journey guidance."""
        test_name = "Guide Agent: Journey Guidance"
        
        if not self.session_id:
            await self.create_session()
        
        try:
            response = await self.client.post(
                "/api/v1/journey/guide-agent/get-journey-guidance",
                json={
                    "user_goal": "Analyze my business data and generate insights",
                    "current_pillar": "content",
                    "session_id": self.session_id or "test-session-id"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                has_guidance = "guidance" in data or "next_steps" in data
                self.log_result(test_name, has_guidance, data)
                return has_guidance
            else:
                self.log_result(test_name, False, {}, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result(test_name, False, {}, str(e))
            return False
    
    async def test_guide_agent_conversation_history(self) -> bool:
        """Test Guide Agent conversation history."""
        test_name = "Guide Agent: Conversation History"
        
        if not self.session_id:
            await self.create_session()
        
        try:
            response = await self.client.get(
                f"/api/v1/journey/guide-agent/get-conversation-history/{self.session_id or 'test-session-id'}"
            )
            
            if response.status_code == 200:
                data = response.json()
                has_history = "conversation" in data or "messages" in data
                self.log_result(test_name, has_history, data)
                return has_history
            else:
                self.log_result(test_name, False, {}, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result(test_name, False, {}, str(e))
            return False
    
    # ============================================================================
    # LIAISON AGENT TESTS
    # ============================================================================
    
    async def test_liaison_agent(self, pillar: str, message: str) -> bool:
        """Test a Liaison Agent for a specific pillar."""
        test_name = f"Liaison Agent: {pillar.capitalize()} Pillar"
        
        if not self.session_id:
            await self.create_session()
        
        try:
            # Try new semantic endpoint first
            response = await self.client.post(
                "/api/v1/liaison-agents/send-message-to-pillar-agent",
                json={
                    "message": message,
                    "pillar": pillar,
                    "session_id": self.session_id or "test-session-id",
                    "conversation_id": f"test-conv-{pillar}",
                    "user_id": TEST_USER_ID
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                has_response = "response" in data or "message" in data or "success" in data
                self.log_result(test_name, has_response, data)
                return has_response
            elif response.status_code == 404:
                # Try legacy endpoint
                return await self.test_liaison_agent_legacy(pillar, message, test_name)
            else:
                self.log_result(test_name, False, {}, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result(test_name, False, {}, str(e))
            return False
    
    async def test_liaison_agent_legacy(self, pillar: str, message: str, test_name: str) -> bool:
        """Test Liaison Agent using legacy endpoint."""
        try:
            response = await self.client.post(
                "/api/chat/liaison",
                json={
                    "message": message,
                    "pillar": pillar,
                    "conversation_id": f"test-conv-{pillar}",
                    "user_id": TEST_USER_ID
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                has_response = "response" in data or "message" in data or "success" in data
                self.log_result(f"{test_name} (legacy)", has_response, data)
                return has_response
            else:
                self.log_result(f"{test_name} (legacy)", False, {}, f"Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result(f"{test_name} (legacy)", False, {}, str(e))
            return False
    
    async def test_content_liaison(self) -> bool:
        """Test Content Liaison Agent."""
        return await self.test_liaison_agent(
            "content",
            "How do I upload a file for analysis?"
        )
    
    async def test_insights_liaison(self) -> bool:
        """Test Insights Liaison Agent."""
        return await self.test_liaison_agent(
            "insights",
            "What insights can you provide about my data?"
        )
    
    async def test_operations_liaison(self) -> bool:
        """Test Operations Liaison Agent."""
        return await self.test_liaison_agent(
            "operations",
            "How do I create a standard operating procedure?"
        )
    
    async def test_business_outcomes_liaison(self) -> bool:
        """Test Business Outcomes Liaison Agent."""
        return await self.test_liaison_agent(
            "business-outcomes",
            "How can I generate a strategic roadmap?"
        )
    
    # ============================================================================
    # RUN ALL TESTS
    # ============================================================================
    
    async def run_all_tests(self):
        """Run all agent tests."""
        print("=" * 80)
        print("AGENT TESTING - Manual Test Suite")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User ID: {TEST_USER_ID}")
        print()
        
        # Create session first
        await self.create_session()
        print()
        
        # Guide Agent Tests
        print("=" * 80)
        print("GUIDE AGENT TESTS")
        print("=" * 80)
        await self.test_guide_agent_intent_analysis()
        await asyncio.sleep(1)  # Brief pause between tests
        await self.test_guide_agent_journey_guidance()
        await asyncio.sleep(1)
        await self.test_guide_agent_conversation_history()
        print()
        
        # Liaison Agent Tests
        print("=" * 80)
        print("LIAISON AGENT TESTS")
        print("=" * 80)
        await self.test_content_liaison()
        await asyncio.sleep(1)
        await self.test_insights_liaison()
        await asyncio.sleep(1)
        await self.test_operations_liaison()
        await asyncio.sleep(1)
        await self.test_business_outcomes_liaison()
        print()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        print(f"Passed: {passed}/{total}")
        print()
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["error"]:
                print(f"   Error: {result['error']}")
        
        print()
        print("=" * 80)
        
        return passed == total


async def main():
    """Main entry point."""
    async with AgentTester() as tester:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())



