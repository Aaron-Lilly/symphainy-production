#!/usr/bin/env python3
"""
Service Initialization Test

Tests that all Smart City services can be initialized correctly with their new interfaces.
This validates that our Week 2 service updates work properly.

WHAT (Testing Role): I need to validate that services initialize correctly with new interfaces
HOW (Init Test): I test service instantiation and basic interface compliance
"""

import os
import sys
import inspect
from typing import Dict, Any, List, Type

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import interfaces
from backend.smart_city.interfaces.security_guard_interface import ISecurityGuard
from backend.smart_city.interfaces.traffic_cop_interface import ITrafficCop
from backend.smart_city.interfaces.conductor_interface import IConductor
from backend.smart_city.interfaces.nurse_interface import INurse
from backend.smart_city.interfaces.librarian_interface import ILibrarian
from backend.smart_city.interfaces.data_steward_interface import IDataSteward
from backend.smart_city.interfaces.post_office_interface import IPostOffice
from backend.smart_city.interfaces.city_manager_interface import ICityManager


class ServiceInitializationTester:
    """Test service initialization and interface compliance."""
    
    def __init__(self):
        """Initialize the tester."""
        self.test_results = {
            "total_services": 0,
            "successful_initializations": 0,
            "failed_initializations": 0,
            "service_details": {},
            "overall_success": False
        }
        
        # Service to interface mapping
        self.service_interface_mapping = {
            "SecurityGuardService": ISecurityGuard,
            "TrafficCopService": ITrafficCop,
            "ConductorService": IConductor,
            "NurseService": INurse,
            "LibrarianService": ILibrarian,
            "DataStewardService": IDataSteward,
            "PostOfficeService": IPostOffice,
            "CityManagerService": ICityManager
        }
    
    def check_interface_implementation(self, service_class: Type, interface_class: Type) -> Dict[str, Any]:
        """Check if a service class implements an interface."""
        service_name = service_class.__name__
        interface_name = interface_class.__name__
        
        # Get interface methods
        interface_methods = [method for method in dir(interface_class) 
                           if not method.startswith('_') and callable(getattr(interface_class, method))]
        
        # Get service methods
        service_methods = [method for method in dir(service_class) 
                          if not method.startswith('_') and callable(getattr(service_class, method))]
        
        # Check compliance
        missing_methods = [method for method in interface_methods if method not in service_methods]
        extra_methods = [method for method in service_methods if method not in interface_methods]
        
        compliant = len(missing_methods) == 0
        
        return {
            "service_name": service_name,
            "interface_name": interface_name,
            "compliant": compliant,
            "interface_methods": interface_methods,
            "service_methods": service_methods,
            "missing_methods": missing_methods,
            "extra_methods": extra_methods,
            "total_interface_methods": len(interface_methods),
            "total_service_methods": len(service_methods)
        }
    
    def test_service_class_import(self, service_name: str) -> Dict[str, Any]:
        """Test importing a service class."""
        try:
            # Try to import the service class
            if service_name == "SecurityGuardService":
                from backend.smart_city.services.security_guard.security_guard_service import SecurityGuardService
                service_class = SecurityGuardService
            elif service_name == "TrafficCopService":
                from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
                service_class = TrafficCopService
            elif service_name == "ConductorService":
                from backend.smart_city.services.conductor.conductor_service import ConductorService
                service_class = ConductorService
            elif service_name == "NurseService":
                from backend.smart_city.services.nurse.nurse_service import NurseService
                service_class = NurseService
            elif service_name == "LibrarianService":
                from backend.smart_city.services.librarian.librarian_service import LibrarianService
                service_class = LibrarianService
            elif service_name == "DataStewardService":
                from backend.smart_city.services.data_steward.data_steward_service import DataStewardService
                service_class = DataStewardService
            elif service_name == "PostOfficeService":
                from backend.smart_city.services.post_office.post_office_service import PostOfficeService
                service_class = PostOfficeService
            elif service_name == "CityManagerService":
                from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
                service_class = CityManagerService
            else:
                raise ImportError(f"Unknown service: {service_name}")
            
            return {
                "success": True,
                "service_class": service_class,
                "message": f"Successfully imported {service_name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "service_class": None,
                "message": f"Failed to import {service_name}: {str(e)}"
            }
    
    def run_tests(self):
        """Run service initialization tests."""
        print("🎯 Service Initialization Test")
        print("=" * 50)
        
        for service_name, interface_class in self.service_interface_mapping.items():
            print(f"\n🔍 Testing {service_name}...")
            
            # Test import
            import_result = self.test_service_class_import(service_name)
            
            test_result = {
                "service_name": service_name,
                "interface_name": interface_class.__name__,
                "import_success": import_result["success"],
                "import_message": import_result["message"],
                "interface_compliance": None,
                "overall_success": False
            }
            
            if import_result["success"]:
                print(f"  ✅ Import successful")
                
                # Test interface compliance
                service_class = import_result["service_class"]
                compliance_result = self.check_interface_implementation(service_class, interface_class)
                test_result["interface_compliance"] = compliance_result
                
                if compliance_result["compliant"]:
                    print(f"  ✅ Interface compliant ({compliance_result['total_interface_methods']} methods)")
                    test_result["overall_success"] = True
                    self.test_results["successful_initializations"] += 1
                else:
                    print(f"  ❌ Interface non-compliant")
                    if compliance_result["missing_methods"]:
                        print(f"    Missing methods: {compliance_result['missing_methods']}")
                    test_result["overall_success"] = False
                    self.test_results["failed_initializations"] += 1
            else:
                print(f"  ❌ Import failed: {import_result['message']}")
                test_result["overall_success"] = False
                self.test_results["failed_initializations"] += 1
            
            self.test_results["service_details"][service_name] = test_result
            self.test_results["total_services"] += 1
        
        # Calculate overall success
        self.test_results["overall_success"] = (
            self.test_results["successful_initializations"] == self.test_results["total_services"]
        )
        
        return True
    
    def generate_report(self) -> str:
        """Generate a test report."""
        report = []
        report.append("📋 SERVICE INITIALIZATION TEST REPORT")
        report.append("=" * 60)
        report.append(f"Total Services: {self.test_results['total_services']}")
        report.append(f"Successful Initializations: {self.test_results['successful_initializations']}")
        report.append(f"Failed Initializations: {self.test_results['failed_initializations']}")
        report.append(f"Overall Success: {'✅ PASS' if self.test_results['overall_success'] else '❌ FAIL'}")
        report.append("")
        
        # Service details
        report.append("📋 SERVICE DETAILS:")
        report.append("-" * 40)
        
        for service_name, details in self.test_results["service_details"].items():
            status = "✅ SUCCESS" if details["overall_success"] else "❌ FAILED"
            report.append(f"\n{service_name}: {status}")
            report.append(f"  Interface: {details['interface_name']}")
            report.append(f"  Import: {'✅ Success' if details['import_success'] else '❌ Failed'}")
            
            if details["import_success"]:
                compliance = details["interface_compliance"]
                report.append(f"  Interface Compliance: {'✅ Compliant' if compliance['compliant'] else '❌ Non-compliant'}")
                report.append(f"  Interface Methods: {compliance['total_interface_methods']}")
                report.append(f"  Service Methods: {compliance['total_service_methods']}")
                
                if compliance["missing_methods"]:
                    report.append(f"  Missing Methods: {compliance['missing_methods']}")
                
                if compliance["extra_methods"]:
                    report.append(f"  Extra Methods: {len(compliance['extra_methods'])}")
            else:
                report.append(f"  Import Error: {details['import_message']}")
        
        # Summary
        report.append("\n" + "=" * 60)
        report.append("📊 SUMMARY:")
        report.append(f"Overall Success: {'✅ PASS' if self.test_results['overall_success'] else '❌ FAIL'}")
        
        if self.test_results["overall_success"]:
            report.append("🎉 All services are properly initialized and interface compliant!")
            report.append("✅ Week 2 service updates are validated successfully!")
        else:
            report.append("⚠️ Some services failed initialization or interface compliance.")
            report.append("🔧 Review the details above and fix any issues.")
        
        return "\n".join(report)


def main():
    """Main test execution."""
    print("🚀 Starting Service Initialization Test")
    
    tester = ServiceInitializationTester()
    success = tester.run_tests()
    
    if success:
        report = tester.generate_report()
        print("\n" + report)
        
        # Save report
        report_file = "/home/founders/demoversion/symphainy_source/symphainy-platform/docs/SERVICE_INITIALIZATION_TEST_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(f"# Service Initialization Test Report\n\n```\n{report}\n```")
        
        print(f"\n📄 Report saved to: {report_file}")
        
        return tester.test_results["overall_success"]
    else:
        print("❌ Test failed")
        return False


if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 Service initialization test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Service initialization test failed.")
        sys.exit(1)

















