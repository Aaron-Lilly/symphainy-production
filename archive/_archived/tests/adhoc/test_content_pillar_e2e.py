#!/usr/bin/env python3
"""
Content Pillar E2E Integration Test

Test script to validate end-to-end integration of the Content Pillar.

WHAT (Test Role): I validate the complete E2E integration of Content Pillar
HOW (Test Implementation): I test the full flow from Experience Dimension to Content Pillar
"""

import asyncio
import sys
import os
from typing import Dict, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from backend.business_pillars.business_orchestrator.service.business_orchestrator_service_refactored import BusinessOrchestratorService
from experience.service.experience_service import ExperienceService
from backend.business_pillars.content_pillar.service.content_pillar_service import ContentPillarService
from backend.business_pillars.content_pillar.specialist_agents.content_liaison_agent import ContentLiaisonAgent


class ContentPillarE2ETest:
    """End-to-End test for Content Pillar integration."""
    
    def __init__(self):
        self.business_orchestrator = None
        self.experience_service = None
        self.content_pillar_service = None
        self.content_liaison_agent = None
        self.test_results = []
    
    async def initialize_services(self):
        """Initialize all services for testing."""
        try:
            print("🔧 Initializing services for E2E test...")
            
            # Initialize Business Orchestrator
            print("  - Initializing Business Orchestrator...")
            self.business_orchestrator = BusinessOrchestratorService()
            await self.business_orchestrator.initialize()
            print("  ✅ Business Orchestrator initialized")
            
            # Initialize Experience Service
            print("  - Initializing Experience Service...")
            self.experience_service = ExperienceService()
            await self.experience_service.initialize()
            print("  ✅ Experience Service initialized")
            
            # Get Content Pillar service from orchestrator
            if "content" in self.business_orchestrator.pillar_services:
                self.content_pillar_service = self.business_orchestrator.pillar_services["content"]
                print("  ✅ Content Pillar service retrieved")
            else:
                print("  ❌ Content Pillar service not found in orchestrator")
                return False
            
            # Get Content Liaison Agent
            if "content" in self.business_orchestrator.pillar_liaison_agents:
                self.content_liaison_agent = self.business_orchestrator.pillar_liaison_agents["content"]["agent_instance"]
                print("  ✅ Content Liaison Agent retrieved")
            else:
                print("  ❌ Content Liaison Agent not found in orchestrator")
                return False
            
            print("✅ All services initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize services: {e}")
            return False
    
    async def test_content_pillar_health(self):
        """Test Content Pillar health check."""
        try:
            print("\n🏥 Testing Content Pillar health...")
            
            health_result = await self.content_pillar_service.get_health_status()
            
            if health_result.get("success"):
                print("  ✅ Content Pillar health check passed")
                self.test_results.append({"test": "content_pillar_health", "status": "passed"})
                return True
            else:
                print(f"  ❌ Content Pillar health check failed: {health_result.get('error')}")
                self.test_results.append({"test": "content_pillar_health", "status": "failed", "error": health_result.get('error')})
                return False
                
        except Exception as e:
            print(f"  ❌ Content Pillar health check error: {e}")
            self.test_results.append({"test": "content_pillar_health", "status": "error", "error": str(e)})
            return False
    
    async def test_content_liaison_agent(self):
        """Test Content Liaison Agent functionality."""
        try:
            print("\n🤖 Testing Content Liaison Agent...")
            
            agent_status = await self.content_liaison_agent.get_agent_status()
            
            if agent_status.get("status") == "healthy":
                print("  ✅ Content Liaison Agent is healthy")
                print(f"  📊 Capabilities: {agent_status.get('capabilities', [])}")
                self.test_results.append({"test": "content_liaison_agent", "status": "passed"})
                return True
            else:
                print(f"  ❌ Content Liaison Agent health check failed: {agent_status.get('error')}")
                self.test_results.append({"test": "content_liaison_agent", "status": "failed", "error": agent_status.get('error')})
                return False
                
        except Exception as e:
            print(f"  ❌ Content Liaison Agent test error: {e}")
            self.test_results.append({"test": "content_liaison_agent", "status": "error", "error": str(e)})
            return False
    
    async def test_business_orchestrator_routing(self):
        """Test Business Orchestrator routing to Content Pillar."""
        try:
            print("\n🔄 Testing Business Orchestrator routing...")
            
            # Test content request routing
            test_request = {
                "type": "content_file_upload",
                "data": {
                    "filename": "test.csv",
                    "content": "test,data\n1,2\n3,4",
                    "content_type": "text/csv"
                },
                "user_context": {
                    "user_id": "test_user",
                    "session_id": "test_session"
                }
            }
            
            result = await self.business_orchestrator.handle_frontend_request(test_request)
            
            if result.get("success"):
                print("  ✅ Business Orchestrator routing to Content Pillar successful")
                self.test_results.append({"test": "business_orchestrator_routing", "status": "passed"})
                return True
            else:
                print(f"  ❌ Business Orchestrator routing failed: {result.get('error')}")
                self.test_results.append({"test": "business_orchestrator_routing", "status": "failed", "error": result.get('error')})
                return False
                
        except Exception as e:
            print(f"  ❌ Business Orchestrator routing test error: {e}")
            self.test_results.append({"test": "business_orchestrator_routing", "status": "error", "error": str(e)})
            return False
    
    async def test_experience_dimension_integration(self):
        """Test Experience Dimension integration with Content Pillar."""
        try:
            print("\n🎭 Testing Experience Dimension integration...")
            
            # Test chat message routing to content pillar
            test_message = "I want to upload a file for processing"
            user_context = {
                "user_id": "test_user",
                "session_id": "test_session"
            }
            
            result = await self.experience_service.handle_chat_message(
                message=test_message,
                user_context=user_context,
                conversation_id="test_conversation"
            )
            
            if result.get("routed_to") == "content":
                print("  ✅ Experience Dimension correctly routed to Content Pillar")
                self.test_results.append({"test": "experience_dimension_integration", "status": "passed"})
                return True
            else:
                print(f"  ❌ Experience Dimension routing failed: {result.get('routed_to')}")
                self.test_results.append({"test": "experience_dimension_integration", "status": "failed", "error": f"Expected 'content', got '{result.get('routed_to')}'"})
                return False
                
        except Exception as e:
            print(f"  ❌ Experience Dimension integration test error: {e}")
            self.test_results.append({"test": "experience_dimension_integration", "status": "error", "error": str(e)})
            return False
    
    async def test_content_pillar_capabilities(self):
        """Test Content Pillar specific capabilities."""
        try:
            print("\n📁 Testing Content Pillar capabilities...")
            
            # Test file upload capability
            file_data = {
                "filename": "test.csv",
                "content": "name,age\nJohn,25\nJane,30",
                "content_type": "text/csv",
                "size": 25
            }
            
            upload_result = await self.content_pillar_service.upload_file(
                file_data=file_data,
                user_context={"user_id": "test_user"}
            )
            
            if upload_result.get("success"):
                print("  ✅ File upload capability working")
                file_id = upload_result.get("file_id")
                
                # Test file parsing capability
                parse_result = await self.content_pillar_service.parse_document(
                    file_id=file_id,
                    user_context={"user_id": "test_user"}
                )
                
                if parse_result.get("success"):
                    print("  ✅ File parsing capability working")
                    self.test_results.append({"test": "content_pillar_capabilities", "status": "passed"})
                    return True
                else:
                    print(f"  ❌ File parsing failed: {parse_result.get('error')}")
                    self.test_results.append({"test": "content_pillar_capabilities", "status": "failed", "error": f"Parsing failed: {parse_result.get('error')}"})
                    return False
            else:
                print(f"  ❌ File upload failed: {upload_result.get('error')}")
                self.test_results.append({"test": "content_pillar_capabilities", "status": "failed", "error": f"Upload failed: {upload_result.get('error')}"})
                return False
                
        except Exception as e:
            print(f"  ❌ Content Pillar capabilities test error: {e}")
            self.test_results.append({"test": "content_pillar_capabilities", "status": "error", "error": str(e)})
            return False
    
    async def run_all_tests(self):
        """Run all E2E tests."""
        print("🚀 Starting Content Pillar E2E Integration Tests")
        print("=" * 60)
        
        # Initialize services
        if not await self.initialize_services():
            print("❌ Service initialization failed, aborting tests")
            return False
        
        # Run tests
        tests = [
            self.test_content_pillar_health,
            self.test_content_liaison_agent,
            self.test_business_orchestrator_routing,
            self.test_experience_dimension_integration,
            self.test_content_pillar_capabilities
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if await test():
                    passed_tests += 1
            except Exception as e:
                print(f"  ❌ Test failed with exception: {e}")
        
        # Print results
        print("\n" + "=" * 60)
        print("📊 E2E Test Results Summary")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests / total_tests) * 100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "passed" else "❌"
            print(f"  {status_emoji} {result['test']}: {result['status']}")
            if "error" in result:
                print(f"      Error: {result['error']}")
        
        return passed_tests == total_tests
    
    async def cleanup(self):
        """Cleanup services after testing."""
        try:
            print("\n🧹 Cleaning up services...")
            
            if self.content_liaison_agent:
                await self.content_liaison_agent.shutdown()
                print("  ✅ Content Liaison Agent shutdown")
            
            if self.experience_service:
                await self.experience_service.shutdown()
                print("  ✅ Experience Service shutdown")
            
            if self.business_orchestrator:
                await self.business_orchestrator.shutdown()
                print("  ✅ Business Orchestrator shutdown")
            
            print("✅ Cleanup complete")
            
        except Exception as e:
            print(f"❌ Cleanup error: {e}")


async def main():
    """Main test function."""
    test_runner = ContentPillarE2ETest()
    
    try:
        success = await test_runner.run_all_tests()
        
        if success:
            print("\n🎉 All E2E tests passed! Content Pillar integration is working correctly.")
            return 0
        else:
            print("\n❌ Some E2E tests failed. Please check the results above.")
            return 1
            
    except Exception as e:
        print(f"\n💥 E2E test runner failed: {e}")
        return 1
        
    finally:
        await test_runner.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)



