#!/usr/bin/env python3
"""
Simple Interface Compliance Test

A lightweight test that checks interface compliance without complex dependencies.
Tests that our services properly implement their interfaces.

WHAT (Testing Role): I need to validate interface compliance without complex setup
HOW (Simple Test): I check method signatures and interface implementation
"""

import os
import sys
import inspect
from typing import Dict, Any, List, Type, get_type_hints

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import interfaces only (no service dependencies)
from backend.smart_city.interfaces.security_guard_interface import ISecurityGuard
from backend.smart_city.interfaces.traffic_cop_interface import ITrafficCop
from backend.smart_city.interfaces.conductor_interface import IConductor
from backend.smart_city.interfaces.nurse_interface import INurse
from backend.smart_city.interfaces.librarian_interface import ILibrarian
from backend.smart_city.interfaces.data_steward_interface import IDataSteward
from backend.smart_city.interfaces.post_office_interface import IPostOffice
from backend.smart_city.interfaces.city_manager_interface import ICityManager


class SimpleInterfaceTester:
    """Simple interface compliance tester."""
    
    def __init__(self):
        """Initialize the tester."""
        self.interfaces = [
            ISecurityGuard,
            ITrafficCop,
            IConductor,
            INurse,
            ILibrarian,
            IDataSteward,
            IPostOffice,
            ICityManager
        ]
        
        self.test_results = {
            "total_interfaces": len(self.interfaces),
            "interface_details": {},
            "overall_status": "unknown"
        }
    
    def get_interface_methods(self, interface_class: Type) -> List[str]:
        """Get all methods from an interface class."""
        methods = []
        for name, method in inspect.getmembers(interface_class, predicate=inspect.isfunction):
            if not name.startswith('_'):
                methods.append(name)
        return methods
    
    def analyze_interface(self, interface_class: Type) -> Dict[str, Any]:
        """Analyze an interface for method signatures and types."""
        interface_name = interface_class.__name__
        methods = self.get_interface_methods(interface_class)
        
        method_details = {}
        for method_name in methods:
            method = getattr(interface_class, method_name)
            
            # Get method signature
            signature = inspect.signature(method)
            
            # Get type hints
            type_hints = get_type_hints(method)
            
            # Check if method is async
            is_async = inspect.iscoroutinefunction(method)
            
            method_details[method_name] = {
                "signature": str(signature),
                "type_hints": type_hints,
                "is_async": is_async,
                "parameters": list(signature.parameters.keys()),
                "return_type": type_hints.get('return', 'Any')
            }
        
        return {
            "interface_name": interface_name,
            "total_methods": len(methods),
            "methods": methods,
            "method_details": method_details,
            "has_async_methods": any(details["is_async"] for details in method_details.values()),
            "has_type_hints": any(details["type_hints"] for details in method_details.values())
        }
    
    def run_tests(self):
        """Run interface analysis tests."""
        print("🎯 Simple Interface Compliance Test")
        print("=" * 50)
        
        for interface in self.interfaces:
            print(f"\n🔍 Analyzing {interface.__name__}...")
            
            analysis = self.analyze_interface(interface)
            self.test_results["interface_details"][interface.__name__] = analysis
            
            print(f"  📊 Methods: {analysis['total_methods']}")
            print(f"  🔄 Async Methods: {'Yes' if analysis['has_async_methods'] else 'No'}")
            print(f"  🏷️ Type Hints: {'Yes' if analysis['has_type_hints'] else 'No'}")
            
            # Show method details
            for method_name, details in analysis["method_details"].items():
                async_indicator = "🔄" if details["is_async"] else "⚡"
                print(f"    {async_indicator} {method_name}{details['signature']}")
        
        # Calculate overall status
        total_methods = sum(details["total_methods"] for details in self.test_results["interface_details"].values())
        interfaces_with_type_hints = sum(1 for details in self.test_results["interface_details"].values() 
                                       if details["has_type_hints"])
        
        self.test_results["overall_status"] = "✅ PASS" if interfaces_with_type_hints == len(self.interfaces) else "⚠️ PARTIAL"
        
        return True
    
    def generate_report(self) -> str:
        """Generate a test report."""
        report = []
        report.append("📋 INTERFACE ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"Total Interfaces: {self.test_results['total_interfaces']}")
        
        total_methods = sum(details["total_methods"] for details in self.test_results["interface_details"].values())
        report.append(f"Total Methods: {total_methods}")
        
        interfaces_with_type_hints = sum(1 for details in self.test_results["interface_details"].values() 
                                       if details["has_type_hints"])
        report.append(f"Interfaces with Type Hints: {interfaces_with_type_hints}/{self.test_results['total_interfaces']}")
        
        report.append(f"Overall Status: {self.test_results['overall_status']}")
        report.append("")
        
        # Interface details
        for interface_name, details in self.test_results["interface_details"].items():
            report.append(f"🔍 {interface_name}:")
            report.append(f"  Methods: {details['total_methods']}")
            report.append(f"  Type Hints: {'✅' if details['has_type_hints'] else '❌'}")
            report.append(f"  Async Methods: {'✅' if details['has_async_methods'] else '❌'}")
            
            for method_name, method_details in details["method_details"].items():
                async_indicator = "🔄" if method_details["is_async"] else "⚡"
                report.append(f"    {async_indicator} {method_name}")
        
        return "\n".join(report)


def main():
    """Main test execution."""
    print("🚀 Starting Simple Interface Compliance Test")
    
    tester = SimpleInterfaceTester()
    success = tester.run_tests()
    
    if success:
        report = tester.generate_report()
        print("\n" + report)
        
        # Save report
        report_file = "/home/founders/demoversion/symphainy_source/symphainy-platform/docs/SIMPLE_INTERFACE_TEST_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(f"# Simple Interface Test Report\n\n```\n{report}\n```")
        
        print(f"\n📄 Report saved to: {report_file}")
        
        return True
    else:
        print("❌ Test failed")
        return False


if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 Interface analysis completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Interface analysis failed.")
        sys.exit(1)

















