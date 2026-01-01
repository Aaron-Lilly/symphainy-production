#!/usr/bin/env python3
"""
Insights Business Logic Test

Test the extracted business logic services for the Insights Pillar.
This test validates that the business logic has been successfully
extracted from the infrastructure and is working correctly.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../symphainy-platform'))

from utilities import UserContext

# Import business services
from foundations.agentic_foundation.business_services.data_analysis_service import DataAnalysisService, AnalysisType
from foundations.agentic_foundation.business_services.visualization_service import VisualizationService, VisualizationType
from foundations.agentic_foundation.business_services.insights_generation_service import InsightsGenerationService, InsightType
from foundations.agentic_foundation.business_services.apg_processing_service import APGProcessingService, APGMode
from foundations.agentic_foundation.business_services.metrics_calculation_service import MetricsCalculationService, MetricType
from foundations.agentic_foundation.business_services.insights_orchestration_service import InsightsOrchestrationService, WorkflowType


class InsightsBusinessLogicTest:
    """Test class for insights business logic validation."""
    
    def __init__(self):
        """Initialize the test."""
        self.logger = logging.getLogger("InsightsBusinessLogicTest")
        self.test_results = []
        
        # Create test data
        self.test_data = {
            "values": [
                {"x": 1, "y": 100, "category": "A"},
                {"x": 2, "y": 120, "category": "B"},
                {"x": 3, "y": 110, "category": "A"},
                {"x": 4, "y": 140, "category": "B"},
                {"x": 5, "y": 130, "category": "A"}
            ],
            "metadata": {
                "source": "test_data",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Create test user context
        self.user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["user", "read", "write"],
            tenant_id="test_tenant"
        )
    
    async def test_data_analysis_service(self):
        """Test data analysis service business logic."""
        try:
            self.logger.info("Testing Data Analysis Service...")
            
            # Create service
            service = DataAnalysisService()
            
            # Test descriptive analysis
            result = await service.analyze_data(
                self.test_data, 
                AnalysisType.DESCRIPTIVE, 
                self.user_context, 
                "test_session",
                "test_tenant",
                "test_analysis_123"
            )
            
            # Validate result
            assert result["success"], f"Data analysis failed: {result.get('error')}"
            assert "analysis_id" in result, "Missing analysis_id in result"
            assert "results" in result, "Missing results in result"
            assert "insights" in result, "Missing insights in result"
            assert "confidence_score" in result, "Missing confidence_score in result"
            
            self.logger.info("✅ Data Analysis Service test passed")
            self.test_results.append({
                "service": "DataAnalysisService",
                "status": "passed",
                "details": "Business logic working correctly"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Data Analysis Service test failed: {e}")
            self.test_results.append({
                "service": "DataAnalysisService",
                "status": "failed",
                "error": str(e)
            })
    
    async def test_visualization_service(self):
        """Test visualization service business logic."""
        try:
            self.logger.info("Testing Visualization Service...")
            
            # Create service
            service = VisualizationService()
            
            # Test line chart creation
            result = await service.create_visualization(
                self.test_data,
                VisualizationType.LINE_CHART,
                self.user_context,
                "test_session"
            )
            
            # Validate result
            assert result["success"], f"Visualization creation failed: {result.get('error')}"
            assert "visualization_id" in result, "Missing visualization_id in result"
            assert "chart_data" in result, "Missing chart_data in result"
            assert "chart_config" in result, "Missing chart_config in result"
            
            self.logger.info("✅ Visualization Service test passed")
            self.test_results.append({
                "service": "VisualizationService",
                "status": "passed",
                "details": "Business logic working correctly"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Visualization Service test failed: {e}")
            self.test_results.append({
                "service": "VisualizationService",
                "status": "failed",
                "error": str(e)
            })
    
    async def test_insights_generation_service(self):
        """Test insights generation service business logic."""
        try:
            self.logger.info("Testing Insights Generation Service...")
            
            # Create service
            service = InsightsGenerationService()
            
            # Test insights generation
            result = await service.generate_insights(
                self.test_data,
                self.user_context,
                "test_session",
                "test_tenant",
                "test_analysis_123"
            )
            
            # Validate result
            assert result["success"], f"Insights generation failed: {result.get('error')}"
            assert "insights_id" in result, "Missing insights_id in result"
            assert "business_insights" in result, "Missing business_insights in result"
            assert "recommendations" in result, "Missing recommendations in result"
            assert "confidence_score" in result, "Missing confidence_score in result"
            
            self.logger.info("✅ Insights Generation Service test passed")
            self.test_results.append({
                "service": "InsightsGenerationService",
                "status": "passed",
                "details": "Business logic working correctly"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Insights Generation Service test failed: {e}")
            self.test_results.append({
                "service": "InsightsGenerationService",
                "status": "failed",
                "error": str(e)
            })
    
    async def test_apg_processing_service(self):
        """Test APG processing service business logic."""
        try:
            self.logger.info("Testing APG Processing Service...")
            
            # Create service
            service = APGProcessingService()
            
            # Test APG processing
            result = await service.process_apg_mode(
                self.test_data,
                self.user_context,
                "test_session",
                APGMode.AUTO
            )
            
            # Validate result
            assert result["success"], f"APG processing failed: {result.get('error')}"
            assert "apg_id" in result, "Missing apg_id in result"
            assert "patterns" in result, "Missing patterns in result"
            assert "insights" in result, "Missing insights in result"
            assert "recommendations" in result, "Missing recommendations in result"
            
            self.logger.info("✅ APG Processing Service test passed")
            self.test_results.append({
                "service": "APGProcessingService",
                "status": "passed",
                "details": "Business logic working correctly"
            })
            
        except Exception as e:
            self.logger.error(f"❌ APG Processing Service test failed: {e}")
            self.test_results.append({
                "service": "APGProcessingService",
                "status": "failed",
                "error": str(e)
            })
    
    async def test_metrics_calculation_service(self):
        """Test metrics calculation service business logic."""
        try:
            self.logger.info("Testing Metrics Calculation Service...")
            
            # Create service
            service = MetricsCalculationService()
            
            # Test metrics calculation
            result = await service.calculate_metrics(
                self.test_data,
                [MetricType.BUSINESS_KPI, MetricType.PERFORMANCE_METRIC],
                self.user_context,
                "test_session"
            )
            
            # Validate result
            assert result["success"], f"Metrics calculation failed: {result.get('error')}"
            assert "metrics" in result, "Missing metrics in result"
            assert "business_kpi" in result["metrics"], "Missing business_kpi in metrics"
            assert "performance_metric" in result["metrics"], "Missing performance_metric in metrics"
            
            self.logger.info("✅ Metrics Calculation Service test passed")
            self.test_results.append({
                "service": "MetricsCalculationService",
                "status": "passed",
                "details": "Business logic working correctly"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Metrics Calculation Service test failed: {e}")
            self.test_results.append({
                "service": "MetricsCalculationService",
                "status": "failed",
                "error": str(e)
            })
    
    async def test_insights_orchestration_service(self):
        """Test insights orchestration service business logic."""
        try:
            self.logger.info("Testing Insights Orchestration Service...")
            
            # Create service
            service = InsightsOrchestrationService()
            
            # Test end-to-end insights workflow
            result = await service.execute_end_to_end_insights(
                self.test_data,
                self.user_context,
                "test_session"
            )
            
            # Validate result
            assert result["success"], f"End-to-end insights workflow failed: {result.get('error')}"
            assert "workflow" in result, "Missing workflow in result"
            assert "steps" in result, "Missing steps in result"
            assert "insights" in result, "Missing insights in result"
            assert "recommendations" in result, "Missing recommendations in result"
            
            self.logger.info("✅ Insights Orchestration Service test passed")
            self.test_results.append({
                "service": "InsightsOrchestrationService",
                "status": "passed",
                "details": "Business logic working correctly"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Insights Orchestration Service test failed: {e}")
            self.test_results.append({
                "service": "InsightsOrchestrationService",
                "status": "failed",
                "error": str(e)
            })
    
    async def test_business_service_health_checks(self):
        """Test business service health checks."""
        try:
            self.logger.info("Testing Business Service Health Checks...")
            
            # Test each service health check
            services = [
                DataAnalysisService(),
                VisualizationService(),
                InsightsGenerationService(),
                APGProcessingService(),
                MetricsCalculationService(),
                InsightsOrchestrationService()
            ]
            
            for service in services:
                health_result = await service.health_check()
                assert health_result["status"] == "healthy", f"Service {service.service_name} is unhealthy"
                assert "timestamp" in health_result, "Missing timestamp in health result"
            
            self.logger.info("✅ Business Service Health Checks test passed")
            self.test_results.append({
                "service": "HealthChecks",
                "status": "passed",
                "details": "All services are healthy"
            })
            
        except Exception as e:
            self.logger.error(f"❌ Business Service Health Checks test failed: {e}")
            self.test_results.append({
                "service": "HealthChecks",
                "status": "failed",
                "error": str(e)
            })
    
    async def run_all_tests(self):
        """Run all business logic tests."""
        self.logger.info("🚀 Starting Insights Business Logic Tests...")
        
        # Run individual service tests
        await self.test_data_analysis_service()
        await self.test_visualization_service()
        await self.test_insights_generation_service()
        await self.test_apg_processing_service()
        await self.test_metrics_calculation_service()
        await self.test_insights_orchestration_service()
        await self.test_business_service_health_checks()
        
        # Print results
        self.print_test_results()
    
    def print_test_results(self):
        """Print test results summary."""
        self.logger.info("\n" + "="*60)
        self.logger.info("INSIGHTS BUSINESS LOGIC TEST RESULTS")
        self.logger.info("="*60)
        
        passed = sum(1 for result in self.test_results if result["status"] == "passed")
        failed = sum(1 for result in self.test_results if result["status"] == "failed")
        total = len(self.test_results)
        
        self.logger.info(f"Total Tests: {total}")
        self.logger.info(f"Passed: {passed}")
        self.logger.info(f"Failed: {failed}")
        self.logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        
        self.logger.info("\nDetailed Results:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "passed" else "❌"
            self.logger.info(f"{status_icon} {result['service']}: {result['status']}")
            if result["status"] == "failed":
                self.logger.info(f"   Error: {result['error']}")
        
        self.logger.info("="*60)
        
        if failed == 0:
            self.logger.info("🎉 All business logic tests passed! Business logic extraction successful.")
        else:
            self.logger.warning(f"⚠️ {failed} tests failed. Business logic extraction needs attention.")


async def main():
    """Main test function."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run tests
    test = InsightsBusinessLogicTest()
    await test.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
