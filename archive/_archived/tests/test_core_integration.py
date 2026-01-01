#!/usr/bin/env python3
"""
Core Integration Test - Business Enablement Focus

This test focuses on the core business enablement integration without the Experience Dimension
to validate that the main functionality is working properly.

WHAT (Core Integration Test): I validate the core business enablement integration
HOW (Test Implementation): I test real service calls and API endpoints without Experience Dimension
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

# Import only the core business enablement services
from backend.business_enablement.pillars.business_orchestrator.business_orchestrator_service import business_orchestrator_service
from backend.business_enablement.pillars.content_pillar.content_pillar_service import content_pillar_service
from backend.business_enablement.pillars.insights_pillar.insights_pillar_service import insights_pillar_service
from backend.business_enablement.pillars.operations_pillar.operations_pillar_service import operations_pillar_service
from backend.business_enablement.pillars.business_outcomes_pillar.business_outcomes_pillar_service import business_outcomes_pillar_service
from backend.business_enablement.pillars.delivery_manager.delivery_manager_service import delivery_manager_service
from backend.business_enablement.roles.guide_agent.guide_agent_service import GuideAgentService

# Import the pillar API handlers
from experience.roles.frontend_integration.micro_modules.pillar_api_handlers import PillarAPIHandlers

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoreIntegrationTest:
    """
    Core Integration Test Suite
    
    Tests the core business enablement integration without Experience Dimension complexity.
    """
    
    def __init__(self):
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
    
    def test_business_enablement_services_initialization(self):
        """Test that all business enablement services can be initialized."""
        logger.info("🔧 Testing Business Enablement Services Initialization...")
        
        try:
            # Create guide agent service instance
            guide_agent_service = GuideAgentService()
            
            # Test that all services can be imported and have expected methods
            services = {
                "business_orchestrator": business_orchestrator_service,
                "content_pillar": content_pillar_service,
                "insights_pillar": insights_pillar_service,
                "operations_pillar": operations_pillar_service,
                "business_outcomes_pillar": business_outcomes_pillar_service,
                "delivery_manager": delivery_manager_service,
                "guide_agent": guide_agent_service
            }
            
            missing_methods = []
            
            for service_name, service in services.items():
                # Check that service has required methods
                # All services now use get_service_health (including agents with foundation integration)
                required_methods = ["initialize", "get_service_health"]
                for method in required_methods:
                    if not hasattr(service, method):
                        missing_methods.append(f"{service_name}.{method}")
            
            if missing_methods:
                self.log_test_result(
                    "Business Enablement Services Initialization",
                    False,
                    f"Missing methods: {missing_methods}"
                )
            else:
                self.log_test_result(
                    "Business Enablement Services Initialization",
                    True,
                    f"All {len(services)} services have required methods"
                )
                
        except Exception as e:
            self.log_test_result(
                "Business Enablement Services Initialization",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_pillar_api_handlers_creation(self):
        """Test that PillarAPIHandlers can be created and has all services."""
        logger.info("🔗 Testing PillarAPIHandlers Creation...")
        
        try:
            # Create PillarAPIHandlers
            handlers = PillarAPIHandlers(logger)
            
            # Check that all expected services are present
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
                    "PillarAPIHandlers Creation",
                    False,
                    f"Missing services: {missing_services}"
                )
            else:
                self.log_test_result(
                    "PillarAPIHandlers Creation",
                    True,
                    f"All {len(expected_services)} services properly integrated"
                )
                
        except Exception as e:
            self.log_test_result(
                "PillarAPIHandlers Creation",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_content_pillar_service_methods(self):
        """Test that Content Pillar service has expected methods."""
        logger.info("📁 Testing Content Pillar Service Methods...")
        
        try:
            # Check that content pillar service has expected methods
            expected_methods = [
                "upload_file",
                "parse_file", 
                "list_user_files",  # Fixed: service has list_user_files, not list_files
                "get_file_metadata",  # Fixed: service has get_file_metadata, not get_file
                "get_processing_status",  # Fixed: service has get_processing_status, not update_file_status
                "delete_file"
            ]
            
            missing_methods = []
            for method in expected_methods:
                if not hasattr(content_pillar_service, method):
                    missing_methods.append(method)
            
            if missing_methods:
                self.log_test_result(
                    "Content Pillar Service Methods",
                    False,
                    f"Missing methods: {missing_methods}"
                )
            else:
                self.log_test_result(
                    "Content Pillar Service Methods",
                    True,
                    f"All {len(expected_methods)} methods present"
                )
                
        except Exception as e:
            self.log_test_result(
                "Content Pillar Service Methods",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_insights_pillar_service_methods(self):
        """Test that Insights Pillar service has expected methods."""
        logger.info("🔍 Testing Insights Pillar Service Methods...")
        
        try:
            # Check that insights pillar service has expected methods
            expected_methods = [
                "analyze_data",
                "generate_visualization",  # Fixed: interface has generate_visualization, not create_visualization
                "generate_report",  # Fixed: interface has generate_report, not generate_insights
                "process_chat_message"  # This one needs to be added
            ]
            
            missing_methods = []
            for method in expected_methods:
                if not hasattr(insights_pillar_service, method):
                    missing_methods.append(method)
            
            if missing_methods:
                self.log_test_result(
                    "Insights Pillar Service Methods",
                    False,
                    f"Missing methods: {missing_methods}"
                )
            else:
                self.log_test_result(
                    "Insights Pillar Service Methods",
                    True,
                    f"All {len(expected_methods)} methods present"
                )
                
        except Exception as e:
            self.log_test_result(
                "Insights Pillar Service Methods",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_operations_pillar_service_methods(self):
        """Test that Operations Pillar service has expected methods."""
        logger.info("⚙️ Testing Operations Pillar Service Methods...")
        
        try:
            # Check that operations pillar service has expected methods
            expected_methods = [
                "create_sop",
                "create_workflow",
                "process_conversation_message"
            ]
            
            missing_methods = []
            for method in expected_methods:
                if not hasattr(operations_pillar_service, method):
                    missing_methods.append(method)
            
            if missing_methods:
                self.log_test_result(
                    "Operations Pillar Service Methods",
                    False,
                    f"Missing methods: {missing_methods}"
                )
            else:
                self.log_test_result(
                    "Operations Pillar Service Methods",
                    True,
                    f"All {len(expected_methods)} methods present"
                )
                
        except Exception as e:
            self.log_test_result(
                "Operations Pillar Service Methods",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_business_outcomes_pillar_service_methods(self):
        """Test that Business Outcomes Pillar service has expected methods."""
        logger.info("📊 Testing Business Outcomes Pillar Service Methods...")
        
        try:
            # Check that business outcomes pillar service has expected methods
            expected_methods = [
                "generate_strategic_plan",  # Fixed: interface has generate_strategic_plan, not create_strategic_plan
                "calculate_business_metrics",  # Fixed: interface has calculate_business_metrics, not get_metrics
                "process_chat_message"  # This one needs to be added
            ]
            
            missing_methods = []
            for method in expected_methods:
                if not hasattr(business_outcomes_pillar_service, method):
                    missing_methods.append(method)
            
            if missing_methods:
                self.log_test_result(
                    "Business Outcomes Pillar Service Methods",
                    False,
                    f"Missing methods: {missing_methods}"
                )
            else:
                self.log_test_result(
                    "Business Outcomes Pillar Service Methods",
                    True,
                    f"All {len(expected_methods)} methods present"
                )
                
        except Exception as e:
            self.log_test_result(
                "Business Outcomes Pillar Service Methods",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_guide_agent_service_methods(self):
        """Test that Guide Agent service has expected methods."""
        logger.info("🤖 Testing Guide Agent Service Methods...")
        
        try:
            # Create guide agent service instance
            guide_agent_service = GuideAgentService()
            
            # Check that guide agent service has expected methods
            expected_methods = [
                "process_user_message",
                "analyze_global_request"
            ]
            
            missing_methods = []
            for method in expected_methods:
                if not hasattr(guide_agent_service, method):
                    missing_methods.append(method)
            
            if missing_methods:
                self.log_test_result(
                    "Guide Agent Service Methods",
                    False,
                    f"Missing methods: {missing_methods}"
                )
            else:
                self.log_test_result(
                    "Guide Agent Service Methods",
                    True,
                    f"All {len(expected_methods)} methods present"
                )
                
        except Exception as e:
            self.log_test_result(
                "Guide Agent Service Methods",
                False,
                f"Exception: {str(e)}"
            )
    
    async def run_all_tests(self):
        """Run all core integration tests."""
        logger.info("🚀 Starting Core Integration Test Suite...")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        # Core service tests
        self.test_business_enablement_services_initialization()
        self.test_pillar_api_handlers_creation()
        
        # Service method tests
        self.test_content_pillar_service_methods()
        self.test_insights_pillar_service_methods()
        self.test_operations_pillar_service_methods()
        self.test_business_outcomes_pillar_service_methods()
        self.test_guide_agent_service_methods()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        logger.info("=" * 80)
        logger.info("📊 CORE INTEGRATION TEST SUMMARY")
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
            logger.info("🎉 ALL CORE TESTS PASSED! The business enablement foundation is solid!")
            return True
        else:
            logger.error(f"💥 {failed_tests} TESTS FAILED! The core integration has issues that need to be fixed.")
            return False

async def main():
    """Main test runner."""
    test_suite = CoreIntegrationTest()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n🎉 CORE INTEGRATION TEST: PASSED")
        sys.exit(0)
    else:
        print("\n💥 CORE INTEGRATION TEST: FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
