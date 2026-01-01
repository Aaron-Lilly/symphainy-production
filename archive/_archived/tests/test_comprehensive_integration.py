#!/usr/bin/env python3
"""
Comprehensive Integration Test - Real End-to-End Validation

This test ensures that ALL components are properly connected and working:
- Backend services are actually initialized and functional
- API endpoints call real service methods (not placeholders)
- WebSocket connections work with real agent services
- Frontend can communicate with backend through all expected paths
- No "house of cards" - everything is actually connected

WHAT (Integration Test): I validate the complete frontend-backend integration
HOW (Test Implementation): I test real service calls, WebSocket connections, and data flow
"""

import asyncio
import json
import logging
import os
import sys
import time
import websockets
from typing import Dict, Any, List
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

import requests
from fastapi.testclient import TestClient

# Import the main app
from main import app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveIntegrationTest:
    """
    Comprehensive Integration Test Suite
    
    Tests the complete integration from frontend expectations to backend reality.
    Ensures no placeholders or "house of cards" implementations.
    """
    
    def __init__(self):
        self.client = TestClient(app)
        self.base_url = "http://127.0.0.1:8000"
        self.ws_url = "ws://127.0.0.1:8000"
        self.test_results = []
        self.failed_tests = []
        
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result with timestamp."""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        if success:
            logger.info(f"✅ {test_name}: PASSED - {details}")
        else:
            logger.error(f"❌ {test_name}: FAILED - {details}")
            self.failed_tests.append(result)
    
    def test_backend_services_initialization(self):
        """Test that all backend services are properly initialized."""
        logger.info("🔧 Testing Backend Services Initialization...")
        
        try:
            # Test health endpoint
            response = self.client.get("/health")
            assert response.status_code == 200
            
            health_data = response.json()
            assert "services" in health_data
            
            # Check that all expected services are initialized
            expected_services = [
                "business_orchestrator",
                "content_pillar", 
                "insights_pillar",
                "operations_pillar",
                "business_outcomes_pillar",
                "delivery_manager",
                "guide_agent",
                "experience_manager",
                "journey_manager",
                "frontend_integration"
            ]
            
            services_status = health_data["services"]
            missing_services = []
            
            for service in expected_services:
                if service not in services_status:
                    missing_services.append(service)
                else:
                    service_status = services_status[service]
                    if service_status.get("status") != "healthy":
                        missing_services.append(f"{service} (unhealthy)")
            
            if missing_services:
                self.log_test_result(
                    "Backend Services Initialization",
                    False,
                    f"Missing or unhealthy services: {missing_services}"
                )
            else:
                self.log_test_result(
                    "Backend Services Initialization",
                    True,
                    f"All {len(expected_services)} services initialized and healthy"
                )
                
        except Exception as e:
            self.log_test_result(
                "Backend Services Initialization",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_pillar_api_handlers_integration(self):
        """Test that pillar API handlers are properly integrated and call real services."""
        logger.info("🔗 Testing Pillar API Handlers Integration...")
        
        try:
            # Test that pillar_handlers is initialized in app.state
            assert hasattr(app.state, 'pillar_handlers'), "pillar_handlers not found in app.state"
            assert app.state.pillar_handlers is not None, "pillar_handlers is None"
            
            # Test that pillar_handlers has all expected services
            handlers = app.state.pillar_handlers
            expected_services = [
                "content_service",
                "insights_service", 
                "operations_service",
                "business_outcomes_service"
            ]
            
            missing_services = []
            for service_name in expected_services:
                if not hasattr(handlers, service_name):
                    missing_services.append(service_name)
                elif getattr(handlers, service_name) is None:
                    missing_services.append(f"{service_name} (None)")
            
            if missing_services:
                self.log_test_result(
                    "Pillar API Handlers Integration",
                    False,
                    f"Missing services in handlers: {missing_services}"
                )
            else:
                self.log_test_result(
                    "Pillar API Handlers Integration",
                    True,
                    f"All {len(expected_services)} services properly integrated in handlers"
                )
                
        except Exception as e:
            self.log_test_result(
                "Pillar API Handlers Integration",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_content_pillar_real_service_calls(self):
        """Test that Content Pillar endpoints call real service methods."""
        logger.info("📁 Testing Content Pillar Real Service Calls...")
        
        try:
            # Test file listing endpoint
            response = self.client.get("/api/content/files")
            assert response.status_code == 200
            
            response_data = response.json()
            
            # Check that response has expected structure from real service
            assert "success" in response_data, "Response missing 'success' field"
            assert "files" in response_data, "Response missing 'files' field"
            assert "message" in response_data, "Response missing 'message' field"
            
            # Verify it's not a placeholder response
            assert response_data["message"] != "File listing endpoint ready", "Still returning placeholder response"
            assert response_data["message"] != "File listing endpoint ready", "Still returning placeholder response"
            
            self.log_test_result(
                "Content Pillar Real Service Calls",
                True,
                f"Real service call successful: {response_data['message']}"
            )
            
        except Exception as e:
            self.log_test_result(
                "Content Pillar Real Service Calls",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_insights_pillar_real_service_calls(self):
        """Test that Insights Pillar endpoints call real service methods."""
        logger.info("🔍 Testing Insights Pillar Real Service Calls...")
        
        try:
            # Test analysis endpoint with real data
            test_dataset = {
                "data": [1, 2, 3, 4, 5],
                "columns": ["value"],
                "type": "test"
            }
            
            response = self.client.post(
                "/api/insights/analyze",
                json={"dataset": test_dataset, "analysis_type": "comprehensive"}
            )
            assert response.status_code == 200
            
            response_data = response.json()
            
            # Check that response has expected structure from real service
            assert "success" in response_data, "Response missing 'success' field"
            assert "analysis_results" in response_data, "Response missing 'analysis_results' field"
            assert "insights" in response_data, "Response missing 'insights' field"
            
            # Verify it's not a placeholder response
            assert response_data["message"] != "Analysis endpoint ready", "Still returning placeholder response"
            
            self.log_test_result(
                "Insights Pillar Real Service Calls",
                True,
                f"Real service call successful: {response_data['message']}"
            )
            
        except Exception as e:
            self.log_test_result(
                "Insights Pillar Real Service Calls",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_operations_pillar_real_service_calls(self):
        """Test that Operations Pillar endpoints call real service methods."""
        logger.info("⚙️ Testing Operations Pillar Real Service Calls...")
        
        try:
            # Test SOP builder endpoint
            test_sop_data = {
                "title": "Test SOP",
                "description": "Test SOP for integration testing",
                "steps": ["Step 1", "Step 2", "Step 3"]
            }
            
            response = self.client.post(
                "/api/operations/sop-builder",
                json={"sop_data": test_sop_data}
            )
            assert response.status_code == 200
            
            response_data = response.json()
            
            # Check that response has expected structure from real service
            assert "success" in response_data, "Response missing 'success' field"
            assert "sop_id" in response_data, "Response missing 'sop_id' field"
            assert "sop_content" in response_data, "Response missing 'sop_content' field"
            
            # Verify it's not a placeholder response
            assert response_data["message"] != "SOP builder endpoint ready", "Still returning placeholder response"
            
            self.log_test_result(
                "Operations Pillar Real Service Calls",
                True,
                f"Real service call successful: {response_data['message']}"
            )
            
        except Exception as e:
            self.log_test_result(
                "Operations Pillar Real Service Calls",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_business_outcomes_pillar_real_service_calls(self):
        """Test that Business Outcomes Pillar endpoints call real service methods."""
        logger.info("📊 Testing Business Outcomes Pillar Real Service Calls...")
        
        try:
            # Test strategic planning endpoint
            test_plan_data = {
                "title": "Test Strategic Plan",
                "objectives": ["Objective 1", "Objective 2"],
                "timeline": "6 months"
            }
            
            response = self.client.post(
                "/api/business-outcomes/strategic-planning",
                json={"plan_data": test_plan_data}
            )
            assert response.status_code == 200
            
            response_data = response.json()
            
            # Check that response has expected structure from real service
            assert "success" in response_data, "Response missing 'success' field"
            assert "plan_id" in response_data, "Response missing 'plan_id' field"
            assert "strategic_plan" in response_data, "Response missing 'strategic_plan' field"
            
            # Verify it's not a placeholder response
            assert response_data["message"] != "Strategic plan endpoint ready", "Still returning placeholder response"
            
            self.log_test_result(
                "Business Outcomes Pillar Real Service Calls",
                True,
                f"Real service call successful: {response_data['message']}"
            )
            
        except Exception as e:
            self.log_test_result(
                "Business Outcomes Pillar Real Service Calls",
                False,
                f"Exception: {str(e)}"
            )
    
    async def test_guide_agent_websocket_connection(self):
        """Test that Guide Agent WebSocket connection works with real service."""
        logger.info("🤖 Testing Guide Agent WebSocket Connection...")
        
        try:
            # Connect to WebSocket
            uri = f"{self.ws_url}/smart-chat"
            async with websockets.connect(uri) as websocket:
                # Send a test message
                test_message = {
                    "message": "Hello, Guide Agent! Can you help me navigate the platform?",
                    "session_token": "test_session_123",
                    "file_context": {}
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                response_data = json.loads(response)
                
                # Check that response has expected structure
                assert "success" in response_data, "WebSocket response missing 'success' field"
                assert response_data["success"] == True, "WebSocket response not successful"
                assert "content" in response_data, "WebSocket response missing 'content' field"
                assert "agent" in response_data, "WebSocket response missing 'agent' field"
                assert response_data["agent"] == "GuideAgent", "WebSocket response not from GuideAgent"
                
                # Verify it's not a placeholder response
                assert response_data["content"] != "No response", "WebSocket returning placeholder response"
                assert len(response_data["content"]) > 10, "WebSocket response too short (likely placeholder)"
                
                self.log_test_result(
                    "Guide Agent WebSocket Connection",
                    True,
                    f"WebSocket connection successful, received response: {response_data['content'][:50]}..."
                )
                
        except Exception as e:
            self.log_test_result(
                "Guide Agent WebSocket Connection",
                False,
                f"Exception: {str(e)}"
            )
    
    async def test_agent_chat_websocket_connection(self):
        """Test that general agent chat WebSocket connection works."""
        logger.info("💬 Testing Agent Chat WebSocket Connection...")
        
        try:
            # Connect to WebSocket
            uri = f"{self.ws_url}/api/ws/agent-chat"
            async with websockets.connect(uri) as websocket:
                # Send a test message for insights agent
                test_message = {
                    "message": "Can you analyze this data for me?",
                    "agent_type": "insights"
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                response_data = json.loads(response)
                
                # Check that response has expected structure
                assert "success" in response_data, "WebSocket response missing 'success' field"
                assert response_data["success"] == True, "WebSocket response not successful"
                assert "content" in response_data, "WebSocket response missing 'content' field"
                assert "agent" in response_data, "WebSocket response missing 'agent' field"
                
                self.log_test_result(
                    "Agent Chat WebSocket Connection",
                    True,
                    f"WebSocket connection successful, received response from {response_data['agent']}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Agent Chat WebSocket Connection",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_liaison_agent_rest_endpoints(self):
        """Test that all liaison agent REST endpoints work."""
        logger.info("🎭 Testing Liaison Agent REST Endpoints...")
        
        liaison_endpoints = [
            ("/api/insights/chat", "InsightsLiaisonAgent"),
            ("/api/operations/conversation", "OperationsLiaisonAgent"),
            ("/api/content/chat", "ContentLiaisonAgent"),
            ("/api/business-outcomes/chat", "BusinessOutcomesLiaisonAgent")
        ]
        
        all_passed = True
        
        for endpoint, expected_agent in liaison_endpoints:
            try:
                response = self.client.post(
                    endpoint,
                    json={"message": f"Test message for {expected_agent}", "context": {}}
                )
                assert response.status_code == 200
                
                response_data = response.json()
                assert "success" in response_data, f"{endpoint} response missing 'success' field"
                assert response_data["success"] == True, f"{endpoint} response not successful"
                assert "agent" in response_data, f"{endpoint} response missing 'agent' field"
                assert response_data["agent"] == expected_agent, f"{endpoint} wrong agent: {response_data['agent']}"
                
                logger.info(f"✅ {endpoint}: PASSED")
                
            except Exception as e:
                logger.error(f"❌ {endpoint}: FAILED - {str(e)}")
                all_passed = False
        
        if all_passed:
            self.log_test_result(
                "Liaison Agent REST Endpoints",
                True,
                f"All {len(liaison_endpoints)} liaison agent endpoints working"
            )
        else:
            self.log_test_result(
                "Liaison Agent REST Endpoints",
                False,
                "Some liaison agent endpoints failed"
            )
    
    def test_global_agent_analysis_endpoint(self):
        """Test the global agent analysis endpoint."""
        logger.info("🌐 Testing Global Agent Analysis Endpoint...")
        
        try:
            test_data = {
                "request_type": "analysis",
                "data": {"test": "data"},
                "context": {"user_id": "test_user"}
            }
            
            response = self.client.post(
                "/api/global/agent/analyze",
                json=test_data
            )
            assert response.status_code == 200
            
            response_data = response.json()
            assert "success" in response_data, "Response missing 'success' field"
            assert response_data["success"] == True, "Response not successful"
            assert "analysis" in response_data, "Response missing 'analysis' field"
            assert "agent" in response_data, "Response missing 'agent' field"
            assert response_data["agent"] == "GuideAgent", "Wrong agent for global analysis"
            
            self.log_test_result(
                "Global Agent Analysis Endpoint",
                True,
                "Global agent analysis endpoint working correctly"
            )
            
        except Exception as e:
            self.log_test_result(
                "Global Agent Analysis Endpoint",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_frontend_expected_endpoints_exist(self):
        """Test that all endpoints the frontend expects actually exist."""
        logger.info("🎯 Testing Frontend Expected Endpoints...")
        
        # Endpoints that the frontend expects to exist
        expected_endpoints = [
            # Content Pillar
            ("GET", "/api/content/health"),
            ("POST", "/api/content/upload"),
            ("GET", "/api/content/files"),
            ("POST", "/api/content/parse"),
            ("POST", "/api/content/analyze"),
            ("GET", "/api/content/files/{file_id}"),
            ("PUT", "/api/content/files/{file_id}/status"),
            ("DELETE", "/api/content/files/{file_id}"),
            
            # Insights Pillar
            ("GET", "/api/insights/health"),
            ("POST", "/api/insights/analyze"),
            ("GET", "/api/insights/insights"),
            ("POST", "/api/insights/chat"),
            
            # Operations Pillar
            ("GET", "/api/operations/health"),
            ("POST", "/api/operations/sop-builder"),
            ("POST", "/api/operations/workflow-builder"),
            ("POST", "/api/operations/conversation"),
            ("POST", "/api/operations/liaison/conversation"),
            
            # Business Outcomes Pillar
            ("GET", "/api/business-outcomes/health"),
            ("POST", "/api/business-outcomes/strategic-planning"),
            ("GET", "/api/business-outcomes/metrics"),
            ("POST", "/api/business-outcomes/chat"),
            
            # Global endpoints
            ("POST", "/api/global/agent/analyze"),
            
            # WebSocket endpoints (tested separately)
            # ("WS", "/smart-chat"),
            # ("WS", "/api/ws/agent-chat"),
        ]
        
        missing_endpoints = []
        
        for method, endpoint in expected_endpoints:
            try:
                if method == "GET":
                    response = self.client.get(endpoint.replace("{file_id}", "test_id"))
                elif method == "POST":
                    response = self.client.post(endpoint, json={})
                elif method == "PUT":
                    response = self.client.put(endpoint.replace("{file_id}", "test_id"), json={})
                elif method == "DELETE":
                    response = self.client.delete(endpoint.replace("{file_id}", "test_id"))
                
                # We expect either 200 (success) or 422 (validation error) or 404 (not found)
                # 404 means the endpoint doesn't exist
                if response.status_code == 404:
                    missing_endpoints.append(f"{method} {endpoint}")
                    
            except Exception as e:
                missing_endpoints.append(f"{method} {endpoint} (error: {str(e)})")
        
        if missing_endpoints:
            self.log_test_result(
                "Frontend Expected Endpoints",
                False,
                f"Missing endpoints: {missing_endpoints}"
            )
        else:
            self.log_test_result(
                "Frontend Expected Endpoints",
                True,
                f"All {len(expected_endpoints)} expected endpoints exist"
            )
    
    async def run_all_tests(self):
        """Run all integration tests."""
        logger.info("🚀 Starting Comprehensive Integration Test Suite...")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        # Backend service tests
        self.test_backend_services_initialization()
        self.test_pillar_api_handlers_integration()
        
        # Real service call tests
        self.test_content_pillar_real_service_calls()
        self.test_insights_pillar_real_service_calls()
        self.test_operations_pillar_real_service_calls()
        self.test_business_outcomes_pillar_real_service_calls()
        
        # Agent tests
        await self.test_guide_agent_websocket_connection()
        await self.test_agent_chat_websocket_connection()
        self.test_liaison_agent_rest_endpoints()
        self.test_global_agent_analysis_endpoint()
        
        # Frontend integration tests
        self.test_frontend_expected_endpoints_exist()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        logger.info("=" * 80)
        logger.info("📊 COMPREHENSIVE INTEGRATION TEST SUMMARY")
        logger.info("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = len(self.failed_tests)
        
        logger.info(f"⏱️  Total Duration: {duration:.2f} seconds")
        logger.info(f"📈 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            logger.info("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                logger.info(f"   - {test['test']}: {test['details']}")
        
        logger.info("=" * 80)
        
        if failed_tests == 0:
            logger.info("🎉 ALL TESTS PASSED! The integration is solid and ready for production!")
            return True
        else:
            logger.error(f"💥 {failed_tests} TESTS FAILED! The integration has issues that need to be fixed.")
            return False

async def main():
    """Main test runner."""
    test_suite = ComprehensiveIntegrationTest()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n🎉 COMPREHENSIVE INTEGRATION TEST: PASSED")
        sys.exit(0)
    else:
        print("\n💥 COMPREHENSIVE INTEGRATION TEST: FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())


