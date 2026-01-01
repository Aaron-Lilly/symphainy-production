#!/usr/bin/env python3
"""
Interface Implementation Validation

Validates that our services have the correct interface method implementations.
This is a lightweight validation that doesn't require complex service instantiation.

WHAT (Testing Role): I need to validate interface method implementations
HOW (Validation): I check method signatures and implementation patterns
"""

import os
import sys
import inspect
import ast
from typing import Dict, Any, List, Set

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


class InterfaceImplementationValidator:
    """Validate interface method implementations in service files."""
    
    def __init__(self):
        """Initialize the validator."""
        self.service_interface_mapping = {
            "security_guard_service.py": ISecurityGuard,
            "traffic_cop_service.py": ITrafficCop,
            "conductor_service.py": IConductor,
            "nurse_service.py": INurse,
            "librarian_service.py": ILibrarian,
            "data_steward_service.py": IDataSteward,
            "post_office_service.py": IPostOffice,
            "city_manager_service.py": ICityManager
        }
        
        self.validation_results = {
            "total_services": len(self.service_interface_mapping),
            "validated_services": 0,
            "service_details": {},
            "overall_success": False
        }
    
    def get_interface_methods(self, interface_class) -> Set[str]:
        """Get all methods from an interface class."""
        methods = set()
        for name, method in inspect.getmembers(interface_class, predicate=inspect.isfunction):
            if not name.startswith('_'):
                methods.add(name)
        return methods
    
    def parse_service_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a service file to extract method definitions."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            methods = set()
            class_names = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_names.add(node.name)
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if not item.name.startswith('_'):
                                methods.add(item.name)
            
            return {
                "success": True,
                "methods": methods,
                "class_names": class_names,
                "file_path": file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def validate_service_implementation(self, service_file: str, interface_class) -> Dict[str, Any]:
        """Validate that a service file implements its interface methods."""
        interface_name = interface_class.__name__
        interface_methods = self.get_interface_methods(interface_class)
        
        # Construct file path
        service_name = service_file.replace('_service.py', '')
        file_path = f"/home/founders/demoversion/symphainy_source/symphainy-platform/backend/smart_city/services/{service_name}/{service_file}"
        
        print(f"🔍 Validating {service_file} -> {interface_name}")
        
        # Parse service file
        parse_result = self.parse_service_file(file_path)
        
        validation_result = {
            "service_file": service_file,
            "interface_name": interface_name,
            "file_parsed": parse_result["success"],
            "interface_methods": list(interface_methods),
            "service_methods": [],
            "missing_methods": [],
            "extra_methods": [],
            "compliant": False,
            "errors": []
        }
        
        if not parse_result["success"]:
            validation_result["errors"].append(f"Failed to parse file: {parse_result['error']}")
            print(f"  ❌ Failed to parse file: {parse_result['error']}")
            return validation_result
        
        service_methods = parse_result["methods"]
        validation_result["service_methods"] = list(service_methods)
        
        # Check for missing methods
        missing_methods = interface_methods - service_methods
        validation_result["missing_methods"] = list(missing_methods)
        
        # Check for extra methods (not in interface)
        extra_methods = service_methods - interface_methods
        validation_result["extra_methods"] = list(extra_methods)
        
        # Determine compliance
        validation_result["compliant"] = len(missing_methods) == 0
        
        if validation_result["compliant"]:
            print(f"  ✅ Interface compliant ({len(interface_methods)} methods)")
            self.validation_results["validated_services"] += 1
        else:
            print(f"  ❌ Interface non-compliant")
            if missing_methods:
                print(f"    Missing methods: {list(missing_methods)}")
        
        return validation_result
    
    def run_validation(self):
        """Run validation for all services."""
        print("🎯 Interface Implementation Validation")
        print("=" * 50)
        
        for service_file, interface_class in self.service_interface_mapping.items():
            validation_result = self.validate_service_implementation(service_file, interface_class)
            self.validation_results["service_details"][service_file] = validation_result
        
        # Calculate overall success
        compliant_services = sum(1 for details in self.validation_results["service_details"].values() 
                               if details["compliant"])
        self.validation_results["overall_success"] = (
            compliant_services == self.validation_results["total_services"]
        )
        
        return True
    
    def generate_report(self) -> str:
        """Generate a validation report."""
        report = []
        report.append("📋 INTERFACE IMPLEMENTATION VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Total Services: {self.validation_results['total_services']}")
        report.append(f"Validated Services: {self.validation_results['validated_services']}")
        report.append(f"Overall Success: {'✅ PASS' if self.validation_results['overall_success'] else '❌ FAIL'}")
        report.append("")
        
        # Service details
        report.append("📋 SERVICE DETAILS:")
        report.append("-" * 40)
        
        for service_file, details in self.validation_results["service_details"].items():
            status = "✅ COMPLIANT" if details["compliant"] else "❌ NON-COMPLIANT"
            report.append(f"\n{service_file}: {status}")
            report.append(f"  Interface: {details['interface_name']}")
            report.append(f"  File Parsed: {'✅ Success' if details['file_parsed'] else '❌ Failed'}")
            
            if details["file_parsed"]:
                report.append(f"  Interface Methods: {len(details['interface_methods'])}")
                report.append(f"  Service Methods: {len(details['service_methods'])}")
                
                if details["missing_methods"]:
                    report.append(f"  Missing Methods: {details['missing_methods']}")
                
                if details["extra_methods"]:
                    report.append(f"  Extra Methods: {len(details['extra_methods'])}")
            else:
                report.append(f"  Parse Error: {details['errors']}")
        
        # Summary
        report.append("\n" + "=" * 60)
        report.append("📊 SUMMARY:")
        report.append(f"Overall Success: {'✅ PASS' if self.validation_results['overall_success'] else '❌ FAIL'}")
        
        if self.validation_results["overall_success"]:
            report.append("🎉 All services properly implement their interfaces!")
            report.append("✅ Week 2 interface implementation work is validated!")
        else:
            report.append("⚠️ Some services are missing interface method implementations.")
            report.append("🔧 Review the missing methods and implement them.")
        
        return "\n".join(report)


def main():
    """Main validation execution."""
    print("🚀 Starting Interface Implementation Validation")
    
    validator = InterfaceImplementationValidator()
    success = validator.run_validation()
    
    if success:
        report = validator.generate_report()
        print("\n" + report)
        
        # Save report
        report_file = "/home/founders/demoversion/symphainy_source/symphainy-platform/docs/INTERFACE_IMPLEMENTATION_VALIDATION_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(f"# Interface Implementation Validation Report\n\n```\n{report}\n```")
        
        print(f"\n📄 Report saved to: {report_file}")
        
        return validator.validation_results["overall_success"]
    else:
        print("❌ Validation failed")
        return False


if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 Interface implementation validation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Interface implementation validation failed.")
        sys.exit(1)

















