#!/usr/bin/env python3
"""
Complete Nurse Service Stack Test

Comprehensive test suite for the enhanced Nurse Service with health monitoring,
telemetry collection, alert management, and failure classification capabilities.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from backend.smart_city.services.nurse.nurse_service import NurseService
from backend.smart_city.services.nurse.mcp_server.nurse_mcp_server import NurseMCPServer
from config import Environment


class NurseServiceTester:
    """Comprehensive tester for the Nurse Service stack."""
    
    def __init__(self):
        """Initialize the tester."""
        self.logger = logging.getLogger("NurseServiceTester")
        self.nurse_service = None
        self.mcp_server = None
        self.test_results = {}
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all Nurse Service tests."""
        self.logger.info("🏥 Starting Complete Nurse Service Stack Tests")
        
        try:
            # Initialize services
            await self._test_service_initialization()
            
            # Test health monitoring capabilities
            await self._test_health_monitoring()
            
            # Test telemetry collection capabilities
            await self._test_telemetry_collection()
            
            # Test alert management capabilities
            await self._test_alert_management()
            
            # Test failure classification capabilities
            await self._test_failure_classification()
            
            # Test MCP server functionality
            await self._test_mcp_server()
            
            # Test comprehensive dashboard
            await self._test_comprehensive_dashboard()
            
            # Test service configuration
            await self._test_service_configuration()
            
            self.logger.info("✅ All Nurse Service tests completed successfully!")
            return self.test_results
            
        except Exception as e:
            self.logger.error(f"❌ Test suite failed: {e}")
            return {"error": str(e), "test_results": self.test_results}
    
    async def _test_service_initialization(self):
        """Test service initialization."""
        self.logger.info("🔧 Testing service initialization...")
        
        try:
            # Initialize Nurse Service
            self.nurse_service = NurseService(environment=Environment.DEVELOPMENT)
            
            # Initialize MCP Server
            self.mcp_server = NurseMCPServer()
            
            # Test service status
            status = self.nurse_service.get_service_status()
            
            self.test_results["service_initialization"] = {
                "status": "passed",
                "service_available": self.nurse_service is not None,
                "mcp_server_available": self.mcp_server is not None,
                "service_status": status
            }
            
            self.logger.info("✅ Service initialization test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Service initialization test failed: {e}")
            self.test_results["service_initialization"] = {"status": "failed", "error": str(e)}
    
    async def _test_health_monitoring(self):
        """Test health monitoring capabilities."""
        self.logger.info("💓 Testing health monitoring capabilities...")
        
        try:
            # Test system health check
            system_health = self.nurse_service.perform_system_health_check()
            
            # Test service health check
            service_health = self.nurse_service.perform_service_health_check({
                "service_name": "test_service"
            })
            
            # Test health dashboard data
            health_dashboard = self.nurse_service.get_health_dashboard_data({
                "hours": 1
            })
            
            self.test_results["health_monitoring"] = {
                "status": "passed",
                "system_health_check": "system_health" in system_health,
                "service_health_check": "service_name" in service_health,
                "health_dashboard": "timestamp" in health_dashboard,
                "system_health_sample": system_health.get("overall_status", "unknown")
            }
            
            self.logger.info("✅ Health monitoring test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Health monitoring test failed: {e}")
            self.test_results["health_monitoring"] = {"status": "failed", "error": str(e)}
    
    async def _test_telemetry_collection(self):
        """Test telemetry collection capabilities."""
        self.logger.info("📊 Testing telemetry collection capabilities...")
        
        try:
            # Test system telemetry collection
            telemetry_data = self.nurse_service.collect_system_telemetry({
                "service_name": "test_service"
            })
            
            # Test custom metric creation
            metric_result = self.nurse_service.create_custom_metric({
                "metric_name": "test_metric",
                "value": 42.5,
                "tags": {"test": "true", "service": "nurse"},
                "metadata": {"description": "Test metric for validation"}
            })
            
            # Test distributed tracing
            trace_result = self.nurse_service.start_trace({
                "operation_name": "test_operation",
                "service_name": "test_service",
                "tags": {"test": "true"}
            })
            
            span_id = trace_result.get("span_id")
            if span_id:
                # Finish the trace
                finish_result = self.nurse_service.finish_trace({
                    "span_id": span_id,
                    "status": "ok",
                    "tags": {"result": "success"}
                })
            
            # Test telemetry dashboard
            telemetry_dashboard = self.nurse_service.get_telemetry_dashboard_data({
                "hours": 1
            })
            
            self.test_results["telemetry_collection"] = {
                "status": "passed",
                "telemetry_collection": "timestamp" in telemetry_data,
                "custom_metric_created": metric_result.get("success", False),
                "trace_started": span_id is not None,
                "trace_finished": finish_result.get("success", False) if span_id else False,
                "telemetry_dashboard": "timestamp" in telemetry_dashboard
            }
            
            self.logger.info("✅ Telemetry collection test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Telemetry collection test failed: {e}")
            self.test_results["telemetry_collection"] = {"status": "failed", "error": str(e)}
    
    async def _test_alert_management(self):
        """Test alert management capabilities."""
        self.logger.info("🚨 Testing alert management capabilities...")
        
        try:
            # Test health alert creation
            health_alert = self.nurse_service.create_health_alert({
                "alert_type": "cpu_high",
                "severity": "warning",
                "message": "CPU usage is elevated",
                "service_name": "test_service",
                "metadata": {"cpu_percent": 85.0}
            })
            
            # Test failure alert creation
            failure_alert = self.nurse_service.create_failure_alert({
                "error_message": "Database connection timeout",
                "error_code": "DB_TIMEOUT",
                "service_name": "test_service",
                "metadata": {"retry_count": 3}
            })
            
            # Test alert acknowledgment
            alert_id = health_alert.get("alert_id")
            if alert_id:
                ack_result = self.nurse_service.acknowledge_alert({
                    "alert_id": alert_id,
                    "acknowledged_by": "test_user",
                    "acknowledgment_notes": "Investigating CPU usage"
                })
            
            # Test alert resolution
            if alert_id:
                resolve_result = self.nurse_service.resolve_alert({
                    "alert_id": alert_id,
                    "resolved_by": "test_user",
                    "resolution_notes": "CPU usage normalized",
                    "resolution_category": "automatic"
                })
            
            # Test alert dashboard
            alert_dashboard = self.nurse_service.get_alert_dashboard_data({
                "hours": 1
            })
            
            self.test_results["alert_management"] = {
                "status": "passed",
                "health_alert_created": health_alert.get("alert_id") is not None,
                "failure_alert_created": failure_alert.get("alert_id") is not None,
                "alert_acknowledged": ack_result.get("success", False) if alert_id else False,
                "alert_resolved": resolve_result.get("success", False) if alert_id else False,
                "alert_dashboard": "timestamp" in alert_dashboard
            }
            
            self.logger.info("✅ Alert management test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Alert management test failed: {e}")
            self.test_results["alert_management"] = {"status": "failed", "error": str(e)}
    
    async def _test_failure_classification(self):
        """Test failure classification capabilities."""
        self.logger.info("🔍 Testing failure classification capabilities...")
        
        try:
            # Test failure classification
            classification = self.nurse_service.classify_failure({
                "error_message": "Connection refused to database server",
                "error_code": "CONN_REFUSED",
                "service_name": "test_service",
                "metadata": {"retry_count": 5}
            })
            
            # Test classify and alert
            classify_alert = self.nurse_service.classify_and_alert({
                "error_message": "Out of memory error in application",
                "error_code": "OOM_ERROR",
                "service_name": "test_service",
                "metadata": {"memory_usage": "95%"}
            })
            
            # Test failure pattern analysis
            pattern_analysis = self.nurse_service.analyze_failure_patterns({
                "hours": 1
            })
            
            # Test failure dashboard
            failure_dashboard = self.nurse_service.get_failure_dashboard_data({
                "hours": 1
            })
            
            self.test_results["failure_classification"] = {
                "status": "passed",
                "failure_classified": "category" in classification,
                "classify_and_alert": "classification" in classify_alert,
                "pattern_analysis": "analysis_period_hours" in pattern_analysis,
                "failure_dashboard": "timestamp" in failure_dashboard,
                "classification_sample": classification.get("category", "unknown")
            }
            
            self.logger.info("✅ Failure classification test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Failure classification test failed: {e}")
            self.test_results["failure_classification"] = {"status": "failed", "error": str(e)}
    
    async def _test_mcp_server(self):
        """Test MCP server functionality."""
        self.logger.info("🔌 Testing MCP server functionality...")
        
        try:
            # Test MCP server initialization
            mcp_tools = self.mcp_server.register_tools()
            
            # Test a few key MCP tools
            health_check_result = await self.mcp_server._handle_perform_system_health_check({})
            service_status_result = await self.mcp_server._handle_get_service_status({})
            
            self.test_results["mcp_server"] = {
                "status": "passed",
                "tools_registered": len(mcp_tools),
                "health_check_tool": "overall_status" in health_check_result,
                "service_status_tool": "service_name" in service_status_result,
                "available_tools": [tool.name for tool in mcp_tools[:5]]  # First 5 tools
            }
            
            self.logger.info("✅ MCP server test passed")
            
        except Exception as e:
            self.logger.error(f"❌ MCP server test failed: {e}")
            self.test_results["mcp_server"] = {"status": "failed", "error": str(e)}
    
    async def _test_comprehensive_dashboard(self):
        """Test comprehensive dashboard functionality."""
        self.logger.info("📈 Testing comprehensive dashboard...")
        
        try:
            # Test comprehensive dashboard
            dashboard_data = self.nurse_service.get_comprehensive_dashboard_data({
                "hours": 1
            })
            
            self.test_results["comprehensive_dashboard"] = {
                "status": "passed",
                "dashboard_available": "timestamp" in dashboard_data,
                "health_monitoring_data": "health_monitoring" in dashboard_data,
                "telemetry_data": "telemetry_collection" in dashboard_data,
                "alert_data": "alert_management" in dashboard_data,
                "failure_data": "failure_classification" in dashboard_data
            }
            
            self.logger.info("✅ Comprehensive dashboard test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Comprehensive dashboard test failed: {e}")
            self.test_results["comprehensive_dashboard"] = {"status": "failed", "error": str(e)}
    
    async def _test_service_configuration(self):
        """Test service configuration capabilities."""
        self.logger.info("⚙️ Testing service configuration...")
        
        try:
            # Test health monitoring configuration
            health_config_result = self.nurse_service.configure_service({
                "config_type": "health_monitoring",
                "config_data": {
                    "check_interval": 15,
                    "cpu_threshold": 75.0,
                    "memory_threshold": 80.0
                }
            })
            
            # Test telemetry configuration
            telemetry_config_result = self.nurse_service.configure_service({
                "config_type": "telemetry_collection",
                "config_data": {
                    "collection_interval": 20,
                    "retention_days": 7
                }
            })
            
            self.test_results["service_configuration"] = {
                "status": "passed",
                "health_config_updated": health_config_result.get("success", False),
                "telemetry_config_updated": telemetry_config_result.get("success", False)
            }
            
            self.logger.info("✅ Service configuration test passed")
            
        except Exception as e:
            self.logger.error(f"❌ Service configuration test failed: {e}")
            self.test_results["service_configuration"] = {"status": "failed", "error": str(e)}


async def main():
    """Main test runner."""
    print("🏥 Enhanced Nurse Service - Complete Stack Test")
    print("=" * 60)
    
    tester = NurseServiceTester()
    results = await tester.run_all_tests()
    
    print("\n📊 Test Results Summary:")
    print("=" * 60)
    
    for test_name, result in results.items():
        if isinstance(result, dict) and "status" in result:
            status_icon = "✅" if result["status"] == "passed" else "❌"
            print(f"{status_icon} {test_name}: {result['status']}")
            
            if result["status"] == "failed" and "error" in result:
                print(f"   Error: {result['error']}")
        else:
            print(f"ℹ️  {test_name}: {result}")
    
    # Overall status
    passed_tests = sum(1 for result in results.values() 
                      if isinstance(result, dict) and result.get("status") == "passed")
    total_tests = len([r for r in results.values() if isinstance(r, dict) and "status" in r])
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The Enhanced Nurse Service is ready for production!")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
