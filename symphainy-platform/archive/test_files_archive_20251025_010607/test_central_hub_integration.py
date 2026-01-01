#!/usr/bin/env python3
"""
Central Hub Integration Test
Test the central hub architecture with all Business Pillars
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.business_pillars.delivery_manager.server.delivery_manager_server import DeliveryManagerMCPServer
from backend.business_pillars.content_pillar.server.content_pillar_server import ContentPillarMCPServer
from backend.business_pillars.insights_pillar.server.insights_pillar_server import InsightsPillarMCPServer
from backend.business_pillars.operations_pillar.server.operations_pillar_server import OperationsPillarMCPServer
from backend.business_pillars.business_outcomes_pillar.server.business_outcomes_pillar_server import BusinessOutcomesPillarMCPServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CentralHubIntegrationTest:
    """Test central hub integration with all Business Pillars"""
    
    def __init__(self):
        self.test_results = []
        self.delivery_manager = None
        self.content_pillar = None
        self.insights_pillar = None
        self.operations_pillar = None
        self.business_outcomes_pillar = None
    
    def record_test_result(self, test_name: str, status: str, message: str = ""):
        """Record test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "message": message,
            "timestamp": self.get_timestamp()
        }
        self.test_results.append(result)
        print(f"{'✅' if status == 'PASS' else '❌'} {test_name}: {status}")
        if message:
            print(f"   {message}")
    
    def get_timestamp(self):
        """Get current timestamp"""
        import time
        return time.time()
    
    async def test_central_hub_initialization(self):
        """Test central hub initialization"""
        try:
            # Initialize Delivery Manager
            self.delivery_manager = DeliveryManagerMCPServer()
            await self.delivery_manager.initialize()
            
            # Initialize all pillars
            self.content_pillar = ContentPillarMCPServer()
            await self.content_pillar.initialize()
            
            self.insights_pillar = InsightsPillarMCPServer()
            await self.insights_pillar.initialize()
            
            self.operations_pillar = OperationsPillarMCPServer()
            await self.operations_pillar.initialize()
            
            self.business_outcomes_pillar = BusinessOutcomesPillarMCPServer()
            await self.business_outcomes_pillar.initialize()
            
            # Set pillar references in Delivery Manager
            self.delivery_manager.set_pillar_references(
                self.content_pillar,
                self.insights_pillar,
                self.operations_pillar,
                self.business_outcomes_pillar
            )
            
            self.record_test_result("Central Hub Initialization", "PASS", "All pillars initialized and connected")
            return True
            
        except Exception as e:
            self.record_test_result("Central Hub Initialization", "FAIL", f"Initialization failed: {str(e)}")
            return False
    
    async def test_data_routing(self):
        """Test data routing through central hub"""
        try:
            user_id = "test_user_001"
            test_data = {
                "content": {"files": ["test1.csv", "test2.xlsx"]},
                "insights": {"analysis_type": "comprehensive"},
                "operations": {"optimization_goals": ["efficiency", "cost_reduction"]},
                "business_outcomes": {"objectives": ["roi_improvement", "customer_satisfaction"]}
            }
            
            # Test getting available data
            available_data = await self.delivery_manager.get_available_data(user_id)
            if available_data.get("status") != "success":
                raise Exception("Failed to get available data")
            
            # Test data routing to specific pillars
            for pillar_name in ["content", "insights", "operations", "business_outcomes"]:
                pillar_data = await self.delivery_manager.get_data_for_pillar(pillar_name, user_id, "comprehensive")
                if pillar_data.get("status") != "success":
                    raise Exception(f"Failed to get data for {pillar_name} pillar")
            
            self.record_test_result("Data Routing", "PASS", "Data routing through central hub successful")
            return True
            
        except Exception as e:
            self.record_test_result("Data Routing", "FAIL", f"Data routing failed: {str(e)}")
            return False
    
    async def test_pillar_independence(self):
        """Test pillar independence"""
        try:
            user_id = "test_user_002"
            
            # Test that each pillar can work independently
            content_data = await self.content_pillar.get_user_data(user_id)
            insights_data = await self.insights_pillar.get_user_data(user_id)
            operations_data = await self.operations_pillar.get_user_data(user_id)
            business_outcomes_data = await self.business_outcomes_pillar.get_user_data(user_id)
            
            # Verify all pillars return data independently
            for pillar_name, data in [("content", content_data), ("insights", insights_data), 
                                    ("operations", operations_data), ("business_outcomes", business_outcomes_data)]:
                if data.get("status") != "success":
                    raise Exception(f"{pillar_name} pillar failed independent operation")
            
            self.record_test_result("Pillar Independence", "PASS", "All pillars operate independently")
            return True
            
        except Exception as e:
            self.record_test_result("Pillar Independence", "FAIL", f"Pillar independence test failed: {str(e)}")
            return False
    
    async def test_cross_pillar_communication(self):
        """Test cross-pillar communication through central hub"""
        try:
            user_id = "test_user_003"
            test_data = {"test_key": "test_value", "source": "content"}
            
            # Test data exchange between pillars
            # Content -> Insights
            insights_result = await self.insights_pillar.receive_data(user_id, test_data, "content")
            if insights_result.get("status") != "success":
                raise Exception("Content -> Insights communication failed")
            
            # Insights -> Operations
            operations_result = await self.operations_pillar.receive_data(user_id, test_data, "insights")
            if operations_result.get("status") != "success":
                raise Exception("Insights -> Operations communication failed")
            
            # Operations -> Business Outcomes
            outcomes_result = await self.business_outcomes_pillar.receive_data(user_id, test_data, "operations")
            if outcomes_result.get("status") != "success":
                raise Exception("Operations -> Business Outcomes communication failed")
            
            self.record_test_result("Cross-Pillar Communication", "PASS", "All pillar communication successful")
            return True
            
        except Exception as e:
            self.record_test_result("Cross-Pillar Communication", "FAIL", f"Cross-pillar communication failed: {str(e)}")
            return False
    
    async def test_user_flow_flexibility(self):
        """Test flexible user flows"""
        try:
            user_id = "test_user_004"
            
            # Test linear flow
            linear_flow = await self.delivery_manager.route_user_request(user_id, "I want to analyze my data")
            if linear_flow.get("status") != "success":
                raise Exception("Linear flow routing failed")
            
            # Test non-linear flow (jump from content to business outcomes)
            jump_flow = await self.delivery_manager.route_user_request(user_id, "I want to create a business roadmap")
            if jump_flow.get("status") != "success":
                raise Exception("Jump flow routing failed")
            
            # Test operations-focused flow
            operations_flow = await self.delivery_manager.route_user_request(user_id, "I want to optimize my processes")
            if operations_flow.get("status") != "success":
                raise Exception("Operations flow routing failed")
            
            self.record_test_result("User Flow Flexibility", "PASS", "All user flow types supported")
            return True
            
        except Exception as e:
            self.record_test_result("User Flow Flexibility", "FAIL", f"User flow flexibility test failed: {str(e)}")
            return False
    
    async def test_health_monitoring(self):
        """Test health monitoring across all pillars"""
        try:
            # Test health checks for all pillars
            content_health = await self.content_pillar.health_check()
            insights_health = await self.insights_pillar.health_check()
            operations_health = await self.operations_pillar.health_check()
            business_outcomes_health = await self.business_outcomes_pillar.health_check()
            
            # Verify all health checks pass
            for pillar_name, health in [("content", content_health), ("insights", insights_health),
                                      ("operations", operations_health), ("business_outcomes", business_outcomes_health)]:
                if health.get("status") != "success":
                    raise Exception(f"{pillar_name} pillar health check failed")
            
            self.record_test_result("Health Monitoring", "PASS", "All pillars healthy")
            return True
            
        except Exception as e:
            self.record_test_result("Health Monitoring", "FAIL", f"Health monitoring test failed: {str(e)}")
            return False
    
    async def test_parallel_processing(self):
        """Test parallel processing capabilities"""
        try:
            user_id = "test_user_005"
            test_data = {"parallel_test": True}
            
            # Test parallel processing across multiple pillars
            content_parallel = await self.content_pillar.process_parallel(user_id, test_data)
            insights_parallel = await self.insights_pillar.process_parallel(user_id, test_data)
            operations_parallel = await self.operations_pillar.process_parallel(user_id, test_data)
            business_outcomes_parallel = await self.business_outcomes_pillar.process_parallel(user_id, test_data)
            
            # Verify all parallel processing succeeds
            for pillar_name, result in [("content", content_parallel), ("insights", insights_parallel),
                                      ("operations", operations_parallel), ("business_outcomes", business_outcomes_parallel)]:
                if result.get("status") != "success":
                    raise Exception(f"{pillar_name} pillar parallel processing failed")
            
            self.record_test_result("Parallel Processing", "PASS", "All pillars support parallel processing")
            return True
            
        except Exception as e:
            self.record_test_result("Parallel Processing", "FAIL", f"Parallel processing test failed: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all central hub integration tests"""
        print("🚀 Starting Central Hub Integration Tests")
        print("=" * 50)
        
        # Run all tests
        await self.test_central_hub_initialization()
        await self.test_data_routing()
        await self.test_pillar_independence()
        await self.test_cross_pillar_communication()
        await self.test_user_flow_flexibility()
        await self.test_health_monitoring()
        await self.test_parallel_processing()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 CENTRAL HUB INTEGRATION TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! Central Hub Architecture is fully functional!")
        else:
            print(f"\n⚠️  {failed_tests} tests failed. Check the details above.")
        
        return failed_tests == 0

async def main():
    """Main test execution"""
    test_suite = CentralHubIntegrationTest()
    success = await test_suite.run_all_tests()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
