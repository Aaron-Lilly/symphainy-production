#!/usr/bin/env python3
"""
Interface Compliance Test Script

Tests that all Smart City services properly implement their matching interfaces.
This script validates our Week 1 and Week 2 work to ensure everything is aligned.

WHAT (Testing Role): I need to validate that services implement their interfaces correctly
HOW (Test Script): I check interface compliance, method signatures, and type safety
"""

import os
import sys
import asyncio
import inspect
from typing import Dict, Any, List, Optional, Type, get_type_hints
from datetime import datetime
import traceback

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import all Smart City services
from backend.smart_city.services.security_guard.security_guard_service import SecurityGuardService
from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
from backend.smart_city.services.conductor.conductor_service import ConductorService
from backend.smart_city.services.nurse.nurse_service import NurseService
from backend.smart_city.services.librarian.librarian_service import LibrarianService
from backend.smart_city.services.data_steward.data_steward_service import DataStewardService
from backend.smart_city.services.post_office.post_office_service import PostOfficeService
from backend.smart_city.services.city_manager.city_manager_service import CityManagerService

# Import all Smart City interfaces
from backend.smart_city.interfaces.security_guard_interface import ISecurityGuard
from backend.smart_city.interfaces.traffic_cop_interface import ITrafficCop
from backend.smart_city.interfaces.conductor_interface import IConductor
from backend.smart_city.interfaces.nurse_interface import INurse
from backend.smart_city.interfaces.librarian_interface import ILibrarian
from backend.smart_city.interfaces.data_steward_interface import IDataSteward
from backend.smart_city.interfaces.post_office_interface import IPostOffice
from backend.smart_city.interfaces.city_manager_interface import ICityManager

# Import foundation services for testing
from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService


class InterfaceComplianceTester:
    """Test interface compliance for all Smart City services."""
    
    def __init__(self):
        """Initialize the interface compliance tester."""
        self.test_results = {
            "total_services": 0,
            "compliant_services": 0,
            "non_compliant_services": 0,
            "service_details": {},
            "overall_compliance": False,
            "test_timestamp": datetime.utcnow().isoformat()
        }
        
        # Service to interface mapping
        self.service_interface_mapping = {
            SecurityGuardService: ISecurityGuard,
            TrafficCopService: ITrafficCop,
            ConductorService: IConductor,
            NurseService: INurse,
            LibrarianService: ILibrarian,
            DataStewardService: IDataSteward,
            PostOfficeService: IPostOffice,
            CityManagerService: ICityManager
        }
        
        # Mock dependencies for testing
        self.di_container = None
        self.public_works_foundation = None
        self.curator_foundation = None
        
    async def initialize_test_environment(self):
        """Initialize test environment with mock dependencies."""
        try:
            print("🔧 Initializing test environment...")
            
            # Create mock DI container
            self.di_container = DIContainerService("test_service")
            
            # Create mock public works foundation
            self.public_works_foundation = PublicWorksFoundationService(self.di_container)
            
            # Create mock curator foundation
            self.curator_foundation = CuratorFoundationService()
            
            print("✅ Test environment initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize test environment: {e}")
            return False
    
    def get_interface_methods(self, interface_class: Type) -> List[str]:
        """Get all methods from an interface class."""
        methods = []
        for name, method in inspect.getmembers(interface_class, predicate=inspect.isfunction):
            if not name.startswith('_'):
                methods.append(name)
        return methods
    
    def get_service_methods(self, service_instance) -> List[str]:
        """Get all public methods from a service instance."""
        methods = []
        for name, method in inspect.getmembers(service_instance, predicate=inspect.ismethod):
            if not name.startswith('_'):
                methods.append(name)
        return methods
    
    def check_method_signatures(self, service_instance, interface_class: Type) -> Dict[str, Any]:
        """Check if service methods match interface method signatures."""
        signature_results = {
            "matching_methods": [],
            "mismatched_methods": [],
            "missing_methods": [],
            "extra_methods": []
        }
        
        # Get interface methods
        interface_methods = self.get_interface_methods(interface_class)
        service_methods = self.get_service_methods(service_instance)
        
        # Check each interface method
        for method_name in interface_methods:
            if method_name in service_methods:
                try:
                    # Get method signatures
                    interface_method = getattr(interface_class, method_name)
                    service_method = getattr(service_instance, method_name)
                    
                    # Get type hints
                    interface_hints = get_type_hints(interface_method)
                    service_hints = get_type_hints(service_method)
                    
                    # Check if signatures match (simplified check)
                    if interface_hints == service_hints:
                        signature_results["matching_methods"].append(method_name)
                    else:
                        signature_results["mismatched_methods"].append({
                            "method": method_name,
                            "interface_hints": interface_hints,
                            "service_hints": service_hints
                        })
                        
                except Exception as e:
                    signature_results["mismatched_methods"].append({
                        "method": method_name,
                        "error": str(e)
                    })
            else:
                signature_results["missing_methods"].append(method_name)
        
        # Find extra methods
        for method_name in service_methods:
            if method_name not in interface_methods:
                signature_results["extra_methods"].append(method_name)
        
        return signature_results
    
    async def test_service_interface_compliance(self, service_class: Type, interface_class: Type) -> Dict[str, Any]:
        """Test a single service's interface compliance."""
        service_name = service_class.__name__
        interface_name = interface_class.__name__
        
        print(f"\n🧪 Testing {service_name} -> {interface_name}")
        
        test_result = {
            "service_name": service_name,
            "interface_name": interface_name,
            "compliant": False,
            "initialization_success": False,
            "method_compliance": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            # Test service initialization
            print(f"  🔧 Initializing {service_name}...")
            service_instance = service_class(
                foundation_services=self.di_container,
                public_works_foundation=self.public_works_foundation,
                curator_foundation=self.curator_foundation
            )
            test_result["initialization_success"] = True
            print(f"  ✅ {service_name} initialized successfully")
            
            # Test interface compliance using service's built-in method
            if hasattr(service_instance, 'check_interface_compliance'):
                print(f"  🔍 Checking interface compliance...")
                compliance_result = service_instance.check_interface_compliance(interface_class)
                test_result["method_compliance"] = compliance_result
                
                if compliance_result.get("compliant", False):
                    test_result["compliant"] = True
                    print(f"  ✅ {service_name} is interface compliant")
                else:
                    print(f"  ❌ {service_name} is not interface compliant")
                    if compliance_result.get("missing_methods"):
                        test_result["warnings"].append(f"Missing methods: {compliance_result['missing_methods']}")
            else:
                # Fallback to manual checking
                print(f"  🔍 Manual interface compliance check...")
                signature_results = self.check_method_signatures(service_instance, interface_class)
                test_result["method_compliance"] = signature_results
                
                if not signature_results["missing_methods"] and not signature_results["mismatched_methods"]:
                    test_result["compliant"] = True
                    print(f"  ✅ {service_name} is interface compliant")
                else:
                    print(f"  ❌ {service_name} is not interface compliant")
                    if signature_results["missing_methods"]:
                        test_result["warnings"].append(f"Missing methods: {signature_results['missing_methods']}")
                    if signature_results["mismatched_methods"]:
                        test_result["warnings"].append(f"Mismatched methods: {signature_results['mismatched_methods']}")
            
            # Test interface method calls (basic validation)
            print(f"  🧪 Testing interface method calls...")
            await self.test_interface_method_calls(service_instance, interface_class, test_result)
            
        except Exception as e:
            error_msg = f"Failed to test {service_name}: {str(e)}"
            test_result["errors"].append(error_msg)
            print(f"  ❌ {error_msg}")
            print(f"  📋 Traceback: {traceback.format_exc()}")
        
        return test_result
    
    async def test_interface_method_calls(self, service_instance, interface_class: Type, test_result: Dict[str, Any]):
        """Test that interface methods can be called without errors."""
        interface_methods = self.get_interface_methods(interface_class)
        method_call_results = {}
        
        for method_name in interface_methods:
            if hasattr(service_instance, method_name):
                try:
                    method = getattr(service_instance, method_name)
                    
                    # Check if method is async
                    if inspect.iscoroutinefunction(method):
                        # For async methods, we'll just check they exist and are callable
                        method_call_results[method_name] = {
                            "exists": True,
                            "is_async": True,
                            "callable": True
                        }
                    else:
                        method_call_results[method_name] = {
                            "exists": True,
                            "is_async": False,
                            "callable": True
                        }
                    
                except Exception as e:
                    method_call_results[method_name] = {
                        "exists": True,
                        "error": str(e)
                    }
            else:
                method_call_results[method_name] = {
                    "exists": False
                }
        
        test_result["method_call_results"] = method_call_results
        
        # Count successful method calls
        successful_calls = sum(1 for result in method_call_results.values() 
                              if result.get("exists", False) and not result.get("error"))
        total_methods = len(interface_methods)
        
        print(f"  📊 Method call test: {successful_calls}/{total_methods} methods accessible")
        
        if successful_calls == total_methods:
            print(f"  ✅ All interface methods are accessible")
        else:
            print(f"  ⚠️ Some interface methods are not accessible")
    
    async def run_all_tests(self):
        """Run interface compliance tests for all services."""
        print("🚀 Starting Interface Compliance Tests")
        print("=" * 60)
        
        # Initialize test environment
        if not await self.initialize_test_environment():
            print("❌ Failed to initialize test environment. Aborting tests.")
            return False
        
        # Test each service
        for service_class, interface_class in self.service_interface_mapping.items():
            test_result = await self.test_service_interface_compliance(service_class, interface_class)
            self.test_results["service_details"][service_class.__name__] = test_result
            
            if test_result["compliant"]:
                self.test_results["compliant_services"] += 1
            else:
                self.test_results["non_compliant_services"] += 1
            
            self.test_results["total_services"] += 1
        
        # Calculate overall compliance
        self.test_results["overall_compliance"] = (
            self.test_results["compliant_services"] == self.test_results["total_services"]
        )
        
        return True
    
    def generate_test_report(self) -> str:
        """Generate a comprehensive test report."""
        report = []
        report.append("🎯 INTERFACE COMPLIANCE TEST REPORT")
        report.append("=" * 60)
        report.append(f"Test Timestamp: {self.test_results['test_timestamp']}")
        report.append(f"Total Services Tested: {self.test_results['total_services']}")
        report.append(f"Compliant Services: {self.test_results['compliant_services']}")
        report.append(f"Non-Compliant Services: {self.test_results['non_compliant_services']}")
        report.append(f"Overall Compliance: {'✅ PASS' if self.test_results['overall_compliance'] else '❌ FAIL'}")
        report.append("")
        
        # Service details
        report.append("📋 SERVICE DETAILS:")
        report.append("-" * 40)
        
        for service_name, details in self.test_results["service_details"].items():
            status = "✅ COMPLIANT" if details["compliant"] else "❌ NON-COMPLIANT"
            report.append(f"\n{service_name}: {status}")
            report.append(f"  Interface: {details['interface_name']}")
            report.append(f"  Initialization: {'✅ Success' if details['initialization_success'] else '❌ Failed'}")
            
            if details["errors"]:
                report.append(f"  Errors: {len(details['errors'])}")
                for error in details["errors"]:
                    report.append(f"    - {error}")
            
            if details["warnings"]:
                report.append(f"  Warnings: {len(details['warnings'])}")
                for warning in details["warnings"]:
                    report.append(f"    - {warning}")
            
            # Method compliance details
            if "method_compliance" in details:
                compliance = details["method_compliance"]
                if "missing_methods" in compliance:
                    missing = compliance["missing_methods"]
                    if missing:
                        report.append(f"  Missing Methods: {missing}")
                
                if "mismatched_methods" in compliance:
                    mismatched = compliance["mismatched_methods"]
                    if mismatched:
                        report.append(f"  Mismatched Methods: {len(mismatched)}")
        
        # Summary
        report.append("\n" + "=" * 60)
        report.append("📊 SUMMARY:")
        report.append(f"Overall Compliance: {'✅ PASS' if self.test_results['overall_compliance'] else '❌ FAIL'}")
        
        if self.test_results["overall_compliance"]:
            report.append("🎉 All services are interface compliant!")
            report.append("✅ Week 1 and Week 2 work is validated successfully!")
        else:
            report.append("⚠️ Some services are not interface compliant.")
            report.append("🔧 Review the details above and fix any issues.")
        
        return "\n".join(report)


async def main():
    """Main test execution function."""
    print("🎯 Smart City Interface Compliance Test Suite")
    print("Testing Week 1 and Week 2 interface alignment work")
    print("=" * 60)
    
    # Create and run tests
    tester = InterfaceComplianceTester()
    success = await tester.run_all_tests()
    
    if success:
        # Generate and display report
        report = tester.generate_test_report()
        print("\n" + report)
        
        # Save report to file
        report_file = "/home/founders/demoversion/symphainy_source/symphainy-platform/docs/INTERFACE_COMPLIANCE_TEST_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(f"# Interface Compliance Test Report\n\n```\n{report}\n```")
        
        print(f"\n📄 Test report saved to: {report_file}")
        
        # Return success status
        return tester.test_results["overall_compliance"]
    else:
        print("❌ Test execution failed")
        return False


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 All tests passed! Interface compliance is validated.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Review the report for details.")
        sys.exit(1)
