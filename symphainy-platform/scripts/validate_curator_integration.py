#!/usr/bin/env python3
"""
Curator Foundation Integration Validation Script

This script validates that all dimensions have proper Curator Foundation integration.
"""

import sys
import os
import asyncio
from typing import Dict, Any, List
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all services can be imported successfully."""
    print("🔍 Testing Service Imports...")
    print("=" * 50)
    
    # Test Smart City services
    smart_city_services = [
        'backend.smart_city.services.security_guard.security_guard_service',
        'backend.smart_city.services.traffic_cop.traffic_cop_service',
        'backend.smart_city.services.conductor.conductor_service',
        'backend.smart_city.services.nurse.nurse_service',
        'backend.smart_city.services.librarian.librarian_service',
        'backend.smart_city.services.data_steward.data_steward_service',
        'backend.smart_city.services.post_office.post_office_service'
    ]
    
    # Test Business Enablement services
    business_services = [
        'backend.business_enablement.pillars.content_pillar.content_pillar_service',
        'backend.business_enablement.pillars.business_orchestrator.business_orchestrator_service',
        'backend.business_enablement.pillars.operations_pillar.operations_pillar_service',
        'backend.business_enablement.pillars.insights_pillar.insights_pillar_service',
        'backend.business_enablement.pillars.delivery_manager.delivery_manager_service',
        'backend.business_enablement.pillars.business_outcomes_pillar.business_outcomes_pillar_service'
    ]
    
    # Test Experience services
    experience_services = [
        'experience.roles.experience_manager.experience_manager_service',
        'experience.roles.journey_manager.journey_manager_service',
        'experience.roles.frontend_integration.frontend_integration_service'
    ]
    
    # Test Agentic services
    agentic_services = [
        'agentic.agent_sdk.agent_base'
    ]
    
    all_services = {
        "Smart City": smart_city_services,
        "Business Enablement": business_services,
        "Experience": experience_services,
        "Agentic": agentic_services
    }
    
    all_working = True
    total_services = 0
    working_services = 0
    
    for dimension, services in all_services.items():
        print(f"\n📋 {dimension} Services:")
        for service in services:
            total_services += 1
            try:
                __import__(service)
                print(f'✅ {service}: Import successful')
                working_services += 1
            except Exception as e:
                print(f'❌ {service}: Import failed - {e}')
                all_working = False
    
    print(f"\n📊 Import Results: {working_services}/{total_services} services working")
    return all_working

def test_curator_methods():
    """Test that all services have Curator Foundation integration methods."""
    print("\n🔍 Testing Curator Foundation Integration Methods...")
    print("=" * 60)
    
    # Test Smart City services
    smart_city_services = [
        'backend.smart_city.services.security_guard.security_guard_service',
        'backend.smart_city.services.traffic_cop.traffic_cop_service',
        'backend.smart_city.services.conductor.conductor_service',
        'backend.smart_city.services.nurse.nurse_service',
        'backend.smart_city.services.librarian.librarian_service',
        'backend.smart_city.services.data_steward.data_steward_service',
        'backend.smart_city.services.post_office.post_office_service'
    ]
    
    # Test Business Enablement services
    business_services = [
        'backend.business_enablement.pillars.content_pillar.content_pillar_service',
        'backend.business_enablement.pillars.business_orchestrator.business_orchestrator_service',
        'backend.business_enablement.pillars.operations_pillar.operations_pillar_service',
        'backend.business_enablement.pillars.insights_pillar.insights_pillar_service',
        'backend.business_enablement.pillars.delivery_manager.delivery_manager_service',
        'backend.business_enablement.pillars.business_outcomes_pillar.business_outcomes_pillar_service'
    ]
    
    # Test Experience services
    experience_services = [
        'experience.roles.experience_manager.experience_manager_service',
        'experience.roles.journey_manager.journey_manager_service',
        'experience.roles.frontend_integration.frontend_integration_service'
    ]
    
    # Test Agentic services
    agentic_services = [
        'agentic.agent_sdk.agent_base'
    ]
    
    all_services = {
        "Smart City": smart_city_services,
        "Business Enablement": business_services,
        "Experience": experience_services,
        "Agentic": agentic_services
    }
    
    required_methods = [
        'register_with_curator',
        'validate_with_curator',
        'generate_documentation_with_curator'
    ]
    
    # Agentic has additional methods
    agentic_methods = required_methods + [
        'register_mcp_tools_with_curator',
        'get_curator_report'
    ]
    
    all_working = True
    total_services = 0
    working_services = 0
    
    for dimension, services in all_services.items():
        print(f"\n📋 {dimension} Services:")
        methods_to_check = agentic_methods if dimension == "Agentic" else required_methods
        
        for service in services:
            total_services += 1
            try:
                module = __import__(service, fromlist=['*'])
                
                # Find the main service class
                service_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        hasattr(attr, '__module__') and 
                        attr.__module__ == service and
                        'Service' in attr_name):
                        service_class = attr
                        break
                
                if not service_class:
                    print(f'❌ {service}: No service class found')
                    all_working = False
                    continue
                
                # Check for required methods
                missing_methods = []
                for method in methods_to_check:
                    if not hasattr(service_class, method):
                        missing_methods.append(method)
                
                if missing_methods:
                    print(f'❌ {service}: Missing methods: {missing_methods}')
                    all_working = False
                else:
                    print(f'✅ {service}: All required methods present')
                    working_services += 1
                    
            except Exception as e:
                print(f'❌ {service}: Error checking methods - {e}')
                all_working = False
    
    print(f"\n📊 Method Check Results: {working_services}/{total_services} services have all required methods")
    return all_working

def test_curator_foundation():
    """Test that Curator Foundation can be imported and has required methods."""
    print("\n🔍 Testing Curator Foundation...")
    print("=" * 40)
    
    try:
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        print('✅ CuratorFoundationService: Import successful')
        
        # Check for required methods
        required_methods = [
            'register_service',
            'validate_pattern',
            'generate_documentation',
            'register_agent_with_curator',
            'get_agent_curator_report',
            'get_agentic_dimension_summary'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(CuratorFoundationService, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f'❌ CuratorFoundationService: Missing methods: {missing_methods}')
            return False
        else:
            print('✅ CuratorFoundationService: All required methods present')
            return True
            
    except Exception as e:
        print(f'❌ CuratorFoundationService: Import failed - {e}')
        return False

def main():
    """Main validation function."""
    print("🎯 Curator Foundation Integration Validation")
    print("=" * 60)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test Curator Foundation
    curator_ok = test_curator_foundation()
    
    # Test integration methods
    methods_ok = test_curator_methods()
    
    print("\n🎯 Overall Validation Results:")
    print("=" * 40)
    print(f"✅ Service Imports: {'PASS' if imports_ok else 'FAIL'}")
    print(f"✅ Curator Foundation: {'PASS' if curator_ok else 'FAIL'}")
    print(f"✅ Integration Methods: {'PASS' if methods_ok else 'FAIL'}")
    
    overall_success = imports_ok and curator_ok and methods_ok
    
    if overall_success:
        print("\n🎉🎉🎉 SUCCESS! All Curator Foundation integrations are working! 🎉🎉🎉")
        print("✅ All dimensions have complete Curator Foundation integration")
        print("✅ All services can be imported successfully")
        print("✅ All services have required integration methods")
        print("✅ Curator Foundation has all required capabilities")
    else:
        print("\n❌ Some integrations need attention")
        print("Please review the failed tests above and fix any issues")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

















