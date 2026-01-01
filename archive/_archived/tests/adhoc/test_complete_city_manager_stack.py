#!/usr/bin/env python3
"""
Complete City Manager Stack Test

Comprehensive test suite for the City Manager service, including all micro-modules
and MCP server functionality.

WHAT (Test Role): I validate the complete City Manager stack functionality
HOW (Test Implementation): I test all service capabilities, micro-modules, and MCP tools
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from config.environment_loader import EnvironmentLoader
from config import Environment
from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
from backend.smart_city.services.city_manager.mcp_server.city_manager_mcp_server import CityManagerMCPServer


class CityManagerStackTester:
    """
    City Manager Stack Tester
    
    Comprehensive test suite for the complete City Manager stack.
    """
    
    def __init__(self):
        """Initialize City Manager Stack Tester."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Initialize environment loader
        self.env_loader = EnvironmentLoader(Environment.DEVELOPMENT)
        
        # Initialize services
        self.city_manager_service = None
        self.mcp_server = None
        
        # Test results
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all City Manager stack tests."""
        self.logger.info("🏛️ Starting City Manager Stack Tests")
        
        try:
            # Test 1: Service Initialization
            await self.test_service_initialization()
            
            # Test 2: Policy Management
            await self.test_policy_management()
            
            # Test 3: Resource Allocation
            await self.test_resource_allocation()
            
            # Test 4: Governance Enforcement
            await self.test_governance_enforcement()
            
            # Test 5: Strategic Coordination
            await self.test_strategic_coordination()
            
            # Test 6: City Health Monitoring
            await self.test_city_health_monitoring()
            
            # Test 7: Emergency Coordination
            await self.test_emergency_coordination()
            
            # Test 8: MCP Server
            await self.test_mcp_server()
            
            # Test 9: Comprehensive Operations
            await self.test_comprehensive_operations()
            
            # Generate test summary
            summary = self.generate_test_summary()
            
            self.logger.info(f"🏛️ City Manager Stack Tests Completed: {self.passed_tests}/{self.total_tests} passed")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Test suite failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests
            }
    
    async def test_service_initialization(self):
        """Test City Manager service initialization."""
        self.logger.info("🧪 Testing City Manager Service Initialization")
        
        try:
            # Initialize service
            self.city_manager_service = CityManagerService(environment=Environment.DEVELOPMENT)
            
            # Test service info
            service_info = self.city_manager_service.get_service_info()
            assert service_info["service_name"] == "City Manager"
            assert service_info["service_type"] == "Smart City Governance Hub"
            assert len(service_info["capabilities"]) == 6
            
            # Test capabilities
            capabilities = self.city_manager_service.get_capabilities()
            expected_capabilities = [
                "policy_management",
                "resource_allocation", 
                "governance_enforcement",
                "strategic_coordination",
                "city_health_monitoring",
                "emergency_coordination"
            ]
            assert all(cap in capabilities for cap in expected_capabilities)
            
            # Test health check
            assert self.city_manager_service.is_healthy()
            
            self._record_test_result("service_initialization", True, "Service initialized successfully")
            
        except Exception as e:
            self._record_test_result("service_initialization", False, f"Service initialization failed: {e}")
    
    async def test_policy_management(self):
        """Test policy management functionality."""
        self.logger.info("🧪 Testing Policy Management")
        
        try:
            # Test create policy
            policy_definition = {
                "id": "test_policy_1",
                "name": "Test Policy",
                "version": "1.0.0",
                "rules": ["rule1", "rule2"],
                "enforcement_level": "high"
            }
            
            create_result = await self.city_manager_service.create_city_policy(policy_definition)
            assert create_result["success"]
            assert create_result["policy_id"] == "test_policy_1"
            
            # Test list policies
            list_result = await self.city_manager_service.list_city_policies()
            assert list_result["success"]
            assert list_result["count"] >= 1
            
            # Test enforce policy
            context = {"user_id": "test_user", "action": "test_action"}
            enforce_result = await self.city_manager_service.enforce_city_policy("test_policy_1", context)
            assert enforce_result["success"]
            
            # Test get policy status
            status_result = await self.city_manager_service.get_policy_status("test_policy_1")
            assert status_result["success"]
            assert status_result["policy_id"] == "test_policy_1"
            
            self._record_test_result("policy_management", True, "Policy management tests passed")
            
        except Exception as e:
            self._record_test_result("policy_management", False, f"Policy management tests failed: {e}")
    
    async def test_resource_allocation(self):
        """Test resource allocation functionality."""
        self.logger.info("🧪 Testing Resource Allocation")
        
        try:
            # Test allocate resources
            allocation_request = {
                "request_id": "test_allocation_1",
                "resources": {"cpu": 2, "memory": 4, "storage": 100},
                "budget": 1000,
                "priority": "high",
                "requestor": "test_service"
            }
            
            allocate_result = await self.city_manager_service.allocate_city_resources(allocation_request)
            assert allocate_result["success"]
            assert allocate_result["request_id"] == "test_allocation_1"
            
            # Test get budget status
            budget_result = await self.city_manager_service.get_city_budget_status()
            assert budget_result["success"]
            assert "budget_status" in budget_result
            
            # Test optimize resources
            optimization_criteria = {"optimization_type": "cost", "target_savings": 0.1}
            optimize_result = await self.city_manager_service.optimize_city_resources(optimization_criteria)
            assert optimize_result["success"]
            
            # Test list allocations
            list_result = await self.city_manager_service.list_resource_allocations()
            assert list_result["success"]
            assert list_result["count"] >= 0
            
            self._record_test_result("resource_allocation", True, "Resource allocation tests passed")
            
        except Exception as e:
            self._record_test_result("resource_allocation", False, f"Resource allocation tests failed: {e}")
    
    async def test_governance_enforcement(self):
        """Test governance enforcement functionality."""
        self.logger.info("🧪 Testing Governance Enforcement")
        
        try:
            # Test check compliance
            component_data = {"component_id": "test_component", "status": "active"}
            compliance_result = await self.city_manager_service.check_city_compliance(
                "test_component", "authorization", component_data
            )
            assert compliance_result["success"]
            assert compliance_result["component_id"] == "test_component"
            
            # Test multi-layer compliance
            multi_layer_result = await self.city_manager_service.check_multi_layer_compliance(
                "test_component", component_data
            )
            assert multi_layer_result["success"]
            
            # Test SLA compliance
            sla_metrics = {"response_time": 100, "availability": 0.99, "throughput": 1000}
            sla_result = await self.city_manager_service.check_sla_compliance("test_service", sla_metrics)
            assert sla_result["success"]
            
            # Test governance audit
            audit_result = await self.city_manager_service.run_city_governance_audit()
            assert audit_result["success"]
            
            # Test get violations
            violations_result = await self.city_manager_service.get_governance_violations()
            assert violations_result["success"]
            assert "violations" in violations_result
            
            self._record_test_result("governance_enforcement", True, "Governance enforcement tests passed")
            
        except Exception as e:
            self._record_test_result("governance_enforcement", False, f"Governance enforcement tests failed: {e}")
    
    async def test_strategic_coordination(self):
        """Test strategic coordination functionality."""
        self.logger.info("🧪 Testing Strategic Coordination")
        
        try:
            # Test create coordination plan
            parameters = {"participants": ["role1", "role2"], "duration": 3600}
            plan_result = await self.city_manager_service.create_coordination_plan("test_operation", parameters)
            assert plan_result["success"]
            assert "plan_id" in plan_result
            
            # Test coordinate roles
            coordination_request = {
                "workflow_type": "test_workflow",
                "session_id": "test_session",
                "data": {"test": "data"}
            }
            coordinate_result = await self.city_manager_service.coordinate_city_roles(coordination_request)
            assert coordinate_result["success"]
            assert "coordination_id" in coordinate_result
            
            # Test orchestrate workflow
            workflow_definition = {
                "workflow_id": "test_workflow",
                "steps": ["step1", "step2"],
                "participants": ["role1", "role2"]
            }
            orchestrate_result = await self.city_manager_service.orchestrate_city_workflow(workflow_definition)
            assert orchestrate_result["success"]
            assert "workflow_id" in orchestrate_result
            
            # Test get city state summary
            state_result = await self.city_manager_service.get_city_state_summary()
            assert state_result["success"]
            assert "state_summary" in state_result
            
            self._record_test_result("strategic_coordination", True, "Strategic coordination tests passed")
            
        except Exception as e:
            self._record_test_result("strategic_coordination", False, f"Strategic coordination tests failed: {e}")
    
    async def test_city_health_monitoring(self):
        """Test city health monitoring functionality."""
        self.logger.info("🧪 Testing City Health Monitoring")
        
        try:
            # Test check city health
            health_result = await self.city_manager_service.check_city_health()
            assert health_result["success"]
            assert "city_health" in health_result
            
            # Test get city health status
            status_result = await self.city_manager_service.get_city_health_status()
            assert status_result["success"]
            assert "city_health" in status_result
            
            # Test monitor service health
            service_data = {"service_id": "test_service", "status": "healthy", "metrics": {}}
            monitor_result = await self.city_manager_service.monitor_service_health("test_service", service_data)
            assert monitor_result["success"]
            assert monitor_result["service_id"] == "test_service"
            
            # Test get health alerts
            alerts_result = await self.city_manager_service.get_health_alerts()
            assert alerts_result["success"]
            assert "alerts" in alerts_result
            
            self._record_test_result("city_health_monitoring", True, "City health monitoring tests passed")
            
        except Exception as e:
            self._record_test_result("city_health_monitoring", False, f"City health monitoring tests failed: {e}")
    
    async def test_emergency_coordination(self):
        """Test emergency coordination functionality."""
        self.logger.info("🧪 Testing Emergency Coordination")
        
        try:
            # Test detect emergency
            emergency_data = {
                "emergency_id": "test_emergency_1",
                "type": "system_failure",
                "severity": "high",
                "description": "Test emergency"
            }
            detect_result = await self.city_manager_service.detect_emergency(emergency_data)
            assert detect_result["success"]
            assert detect_result["emergency_id"] == "test_emergency_1"
            
            # Test coordinate emergency response
            coordination_request = {
                "workflow_type": "emergency_response",
                "session_id": "emergency_session",
                "data": {"emergency_type": "system_failure"}
            }
            coordinate_result = await self.city_manager_service.coordinate_emergency_response(
                "test_emergency_1", coordination_request
            )
            assert coordinate_result["success"]
            assert coordinate_result["emergency_id"] == "test_emergency_1"
            
            # Test get active emergencies
            active_result = await self.city_manager_service.get_active_emergencies()
            assert active_result["success"]
            assert "active_emergencies" in active_result
            
            # Test resolve emergency
            resolution_data = {"resolution_type": "manual", "notes": "Test resolution"}
            resolve_result = await self.city_manager_service.resolve_emergency("test_emergency_1", resolution_data)
            assert resolve_result["success"]
            assert resolve_result["emergency_id"] == "test_emergency_1"
            
            self._record_test_result("emergency_coordination", True, "Emergency coordination tests passed")
            
        except Exception as e:
            self._record_test_result("emergency_coordination", False, f"Emergency coordination tests failed: {e}")
    
    async def test_mcp_server(self):
        """Test MCP server functionality."""
        self.logger.info("🧪 Testing MCP Server")
        
        try:
            # Initialize MCP server
            self.mcp_server = CityManagerMCPServer(self.env_loader, None)
            
            # Test server info
            server_info = self.mcp_server.get_server_info()
            assert server_info.server_name == "CityManagerMCPServer"
            assert server_info.interface_name == "city_manager_governance"
            assert len(server_info.tools) > 0
            
            # Test tool registration
            tools = self.mcp_server.register_tools()
            assert len(tools) > 0
            
            # Test a few MCP tools
            test_tools = [
                "get_city_overview",
                "check_city_health",
                "get_city_budget_status",
                "get_active_emergencies"
            ]
            
            for tool_name in test_tools:
                tool = next((t for t in tools if t.name == tool_name), None)
                assert tool is not None, f"Tool {tool_name} not found"
                assert tool.handler is not None, f"Tool {tool_name} has no handler"
            
            # Test MCP tool execution
            overview_result = await self.mcp_server._handle_get_city_overview({}, None)
            assert overview_result["success"]
            
            health_result = await self.mcp_server._handle_check_city_health({}, None)
            assert health_result["success"]
            
            self._record_test_result("mcp_server", True, "MCP server tests passed")
            
        except Exception as e:
            self._record_test_result("mcp_server", False, f"MCP server tests failed: {e}")
    
    async def test_comprehensive_operations(self):
        """Test comprehensive city management operations."""
        self.logger.info("🧪 Testing Comprehensive Operations")
        
        try:
            # Test get city overview
            overview_result = await self.city_manager_service.get_city_overview()
            assert overview_result["success"]
            assert "city_overview" in overview_result
            assert "health_status" in overview_result["city_overview"]
            assert "governance_metrics" in overview_result["city_overview"]
            
            # Test run city maintenance
            maintenance_result = await self.city_manager_service.run_city_maintenance()
            assert maintenance_result["success"]
            assert "maintenance_results" in maintenance_result
            assert "health_check" in maintenance_result["maintenance_results"]
            assert "governance_audit" in maintenance_result["maintenance_results"]
            
            self._record_test_result("comprehensive_operations", True, "Comprehensive operations tests passed")
            
        except Exception as e:
            self._record_test_result("comprehensive_operations", False, f"Comprehensive operations tests failed: {e}")
    
    def _record_test_result(self, test_name: str, passed: bool, message: str):
        """Record test result."""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            self.logger.info(f"✅ {test_name}: {message}")
        else:
            self.failed_tests += 1
            self.logger.error(f"❌ {test_name}: {message}")
        
        self.test_results[test_name] = {
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_test_summary(self) -> Dict[str, Any]:
        """Generate test summary."""
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        return {
            "success": self.failed_tests == 0,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": success_rate,
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }


async def main():
    """Main test function."""
    print("🏛️ City Manager Stack Test Suite")
    print("=" * 50)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    tester = CityManagerStackTester()
    results = await tester.run_all_tests()
    
    # Print results
    print("\n" + "=" * 50)
    print("🏛️ TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed_tests']}")
    print(f"Failed: {results['failed_tests']}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print("=" * 50)
    
    if results['success']:
        print("🎉 ALL TESTS PASSED! City Manager stack is working correctly.")
    else:
        print("❌ Some tests failed. Check the logs for details.")
        for test_name, result in results['test_results'].items():
            if not result['passed']:
                print(f"  - {test_name}: {result['message']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
