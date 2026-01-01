#!/usr/bin/env python3
"""
Quick Verification Script: Enabling Services Refactoring

This script quickly verifies that all enabling services have been properly refactored:
1. Extend RealmServiceBase
2. Have utility methods
3. Use Dict[str, Any] for user_context (not UserContext)
4. Have Phase 2 Curator registration

Run with: python verify_enabling_services_refactoring.py
"""

import os
import sys
import asyncio
import inspect
from typing import Dict, Any, List, Optional, Tuple

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'symphainy-platform'))

# All enabling services
ENABLING_SERVICES = [
    "file_parser_service",
    "data_analyzer_service",
    "metrics_calculator_service",
    "validation_engine_service",
    "transformation_engine_service",
    "schema_mapper_service",
    "workflow_manager_service",
    "visualization_engine_service",
    "report_generator_service",
    "export_formatter_service",
    "data_compositor_service",
    "reconciliation_service",
    "notification_service",
    "audit_trail_service",
    "configuration_service",
    "data_insights_query_service",
    "format_composer_service",
    "roadmap_generation_service",
    "insights_generator_service",
    "workflow_conversion_service",
    "sop_builder_service",
    "coexistence_analysis_service",
    "poc_generation_service",
    "apg_processor_service",
    "insights_orchestrator_service"
]


def get_service_class(service_name: str):
    """Get service class from service name."""
    # Convert service_name to class name (e.g., "file_parser_service" -> "FileParserService")
    class_name = ''.join(word.capitalize() for word in service_name.split('_'))
    
    # Special cases - map service names to actual class names
    class_name_map = {
        "insights_generator_service": "InsightsGeneratorService",
        "insights_orchestrator_service": "InsightsOrchestrationService",
        "apg_processor_service": "APGProcessingService",
        "sop_builder_service": "SOPBuilderService",
        "poc_generation_service": "POCGenerationService",
        "workflow_conversion_service": "WorkflowConversionService",
        "coexistence_analysis_service": "CoexistenceAnalysisService",
        "roadmap_generation_service": "RoadmapGenerationService",
        "data_insights_query_service": "DataInsightsQueryService",
        "format_composer_service": "FormatComposerService"
    }
    
    if service_name in class_name_map:
        class_name = class_name_map[service_name]
    
    module_path = f"backend.business_enablement.enabling_services.{service_name}.{service_name}"
    
    try:
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        # Try to find the class by inspecting the module
        try:
            module = __import__(module_path, fromlist=['*'])
            # Look for any class that ends with "Service"
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (inspect.isclass(attr) and 
                    attr_name.endswith("Service") and 
                    attr_name != "RealmServiceBase"):
                    return attr
        except:
            pass
        return None


def verify_service_base(service_class):
    """Verify service extends RealmServiceBase."""
    from bases.realm_service_base import RealmServiceBase
    
    if not service_class:
        return False, "Service class not found"
    
    if not issubclass(service_class, RealmServiceBase):
        return False, f"Does not extend RealmServiceBase"
    
    return True, "✅ Extends RealmServiceBase"


def verify_utility_methods(service_class):
    """Verify service has all required utility methods."""
    required_methods = [
        "log_operation_with_telemetry",
        "get_security",
        "get_tenant",
        "handle_error_with_audit",
        "record_health_metric",
        "register_with_curator"
    ]
    
    missing = []
    for method_name in required_methods:
        if not hasattr(service_class, method_name):
            missing.append(method_name)
    
    if missing:
        return False, missing
    
    return True, []


def verify_user_context_type(service_class):
    """Verify SOA API methods use Dict[str, Any] for user_context."""
    issues = []
    
    # Get all public async methods (SOA APIs)
    for name, method in inspect.getmembers(service_class, predicate=inspect.isfunction):
        if name.startswith('_'):
            continue
        
        sig = inspect.signature(method)
        if "user_context" in sig.parameters:
            param = sig.parameters["user_context"]
            annotation = param.annotation
            
            # Check if it's Optional[Dict[str, Any]] or Dict[str, Any]
            if annotation != inspect.Signature.empty:
                # Check if it's the correct type
                if "UserContext" in str(annotation):
                    issues.append(f"{name}: uses UserContext instead of Dict[str, Any]")
    
    if issues:
        return False, issues
    
    return True, []


def verify_initialize_method(service_class):
    """Verify initialize() method exists and is async."""
    if not hasattr(service_class, "initialize"):
        return False, "Missing initialize() method"
    
    method = getattr(service_class, "initialize")
    if not inspect.iscoroutinefunction(method):
        return False, "initialize() is not async"
    
    return True, "✅ Has async initialize() method"


def main():
    """Run verification for all enabling services."""
    print("=" * 80)
    print("ENABLING SERVICES REFACTORING VERIFICATION")
    print("=" * 80)
    print()
    
    results = {
        "total": len(ENABLING_SERVICES),
        "passed": 0,
        "failed": 0,
        "not_found": 0,
        "details": []
    }
    
    for service_name in ENABLING_SERVICES:
        print(f"Checking {service_name}...")
        
        service_class = get_service_class(service_name)
        
        if not service_class:
            print(f"  ❌ Service class not found")
            results["not_found"] += 1
            results["details"].append({
                "service": service_name,
                "status": "not_found",
                "issues": ["Service class not found"]
            })
            continue
        
        issues = []
        
        # Check 1: Extends RealmServiceBase
        base_check, base_msg = verify_service_base(service_class)
        if not base_check:
            issues.append(base_msg)
        else:
            print(f"  {base_msg}")
        
        # Check 2: Has utility methods
        util_check, missing_methods = verify_utility_methods(service_class)
        if not util_check:
            issues.append(f"Missing utility methods: {', '.join(missing_methods)}")
        else:
            print(f"  ✅ Has all utility methods")
        
        # Check 3: UserContext type
        user_ctx_check, user_ctx_issues = verify_user_context_type(service_class)
        if not user_ctx_check:
            issues.extend(user_ctx_issues)
        else:
            print(f"  ✅ Uses Dict[str, Any] for user_context")
        
        # Check 4: Initialize method
        init_check, init_msg = verify_initialize_method(service_class)
        if not init_check:
            issues.append(init_msg)
        else:
            print(f"  {init_msg}")
        
        if issues:
            print(f"  ❌ Issues found:")
            for issue in issues:
                print(f"     - {issue}")
            results["failed"] += 1
            results["details"].append({
                "service": service_name,
                "status": "failed",
                "issues": issues
            })
        else:
            print(f"  ✅ All checks passed")
            results["passed"] += 1
            results["details"].append({
                "service": service_name,
                "status": "passed",
                "issues": []
            })
        
        print()
    
    # Print summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total services: {results['total']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"⚠️  Not found: {results['not_found']}")
    print()
    
    if results["failed"] > 0:
        print("FAILED SERVICES:")
        for detail in results["details"]:
            if detail["status"] == "failed":
                print(f"  - {detail['service']}: {', '.join(detail['issues'])}")
        print()
        return 1
    
    if results["not_found"] > 0:
        print("NOT FOUND SERVICES:")
        for detail in results["details"]:
            if detail["status"] == "not_found":
                print(f"  - {detail['service']}")
        print()
        return 1
    
    print("✅ All services passed verification!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

