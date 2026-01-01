#!/usr/bin/env python3
"""
Experience Dimension Refactoring Validation

Validates that the Experience Dimension refactoring was successful by checking
file structure, content, and architecture patterns.

WHAT (Validation): I verify that the refactoring was completed successfully
HOW (Validation): I check file structure, content patterns, and architecture compliance
"""

import os
import sys
import re
from typing import Dict, Any, List


def check_file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    return os.path.exists(file_path)


def check_file_content(file_path: str, patterns: List[str]) -> Dict[str, bool]:
    """Check if file contains specific patterns."""
    if not check_file_exists(file_path):
        return {pattern: False for pattern in patterns}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = {}
        for pattern in patterns:
            results[pattern] = bool(re.search(pattern, content, re.MULTILINE))
        
        return results
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {pattern: False for pattern in patterns}


def validate_frontend_integration_service():
    """Validate FrontendIntegrationService refactoring."""
    print("🔍 Validating FrontendIntegrationService...")
    
    file_path = "roles/frontend_integration/frontend_integration_service.py"
    
    # Check file exists
    if not check_file_exists(file_path):
        print("❌ FrontendIntegrationService file not found")
        return False
    
    # Check for DI-based patterns
    patterns = [
        r"class FrontendIntegrationService\(ExperienceServiceBase, IFrontendIntegrationService\):",
        r"def __init__\(self, foundation_services: DIContainerService,",
        r"self\.foundation_services = foundation_services",
        r"architecture = \"DI-Based\"",
        r"# Store dependencies via DI",
        r"super\(\)\.__init__\(\"frontend_integration\", ExperienceServiceType\.FRONTEND_INTEGRATION, foundation_services\)"
    ]
    
    results = check_file_content(file_path, patterns)
    
    all_passed = all(results.values())
    for pattern, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {pattern[:50]}...")
    
    if all_passed:
        print("✅ FrontendIntegrationService refactoring validated")
    else:
        print("❌ FrontendIntegrationService refactoring validation failed")
    
    return all_passed


def validate_experience_manager_service():
    """Validate ExperienceManagerService refactoring."""
    print("🔍 Validating ExperienceManagerService...")
    
    file_path = "roles/experience_manager/experience_manager_service.py"
    
    # Check file exists
    if not check_file_exists(file_path):
        print("❌ ExperienceManagerService file not found")
        return False
    
    # Check for DI-based patterns
    patterns = [
        r"class ExperienceManagerService\(ExperienceServiceBase, IExperienceManagerService\):",
        r"def __init__\(self, foundation_services: DIContainerService,",
        r"self\.foundation_services = foundation_services",
        r"architecture = \"DI-Based\"",
        r"# Store dependencies via DI",
        r"super\(\)\.__init__\(\"experience_manager\", ExperienceServiceType\.EXPERIENCE_MANAGER, foundation_services\)"
    ]
    
    results = check_file_content(file_path, patterns)
    
    all_passed = all(results.values())
    for pattern, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {pattern[:50]}...")
    
    if all_passed:
        print("✅ ExperienceManagerService refactoring validated")
    else:
        print("❌ ExperienceManagerService refactoring validation failed")
    
    return all_passed


def validate_journey_manager_service():
    """Validate JourneyManagerService refactoring."""
    print("🔍 Validating JourneyManagerService...")
    
    file_path = "roles/journey_manager/journey_manager_service.py"
    
    # Check file exists
    if not check_file_exists(file_path):
        print("❌ JourneyManagerService file not found")
        return False
    
    # Check for DI-based patterns
    patterns = [
        r"class JourneyManagerService\(ExperienceServiceBase, IJourneyManagerService\):",
        r"def __init__\(self, foundation_services: DIContainerService,",
        r"self\.foundation_services = foundation_services",
        r"architecture = \"DI-Based\"",
        r"# Store dependencies via DI",
        r"super\(\)\.__init__\(\"journey_manager\", ExperienceServiceType\.JOURNEY_MANAGER, foundation_services\)"
    ]
    
    results = check_file_content(file_path, patterns)
    
    all_passed = all(results.values())
    for pattern, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {pattern[:50]}...")
    
    if all_passed:
        print("✅ JourneyManagerService refactoring validated")
    else:
        print("❌ JourneyManagerService refactoring validation failed")
    
    return all_passed


def validate_protocols():
    """Validate that protocols were created."""
    print("🔍 Validating Experience Layer Protocols...")
    
    protocol_files = [
        "protocols/experience_soa_service_protocol.py",
        "protocols/experience_frontend_api_protocol.py",
        "protocols/experience_smart_city_api_protocol.py",
        "protocols/experience_abstraction_protocol.py"
    ]
    
    all_exist = True
    for file_path in protocol_files:
        if check_file_exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            all_exist = False
    
    if all_exist:
        print("✅ All Experience Layer protocols validated")
    else:
        print("❌ Some Experience Layer protocols missing")
    
    return all_exist


def validate_interfaces():
    """Validate that interfaces were created."""
    print("🔍 Validating Experience Layer Interfaces...")
    
    interface_files = [
        "interfaces/experience_service_interface.py"
    ]
    
    all_exist = True
    for file_path in interface_files:
        if check_file_exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            all_exist = False
    
    if all_exist:
        print("✅ All Experience Layer interfaces validated")
    else:
        print("❌ Some Experience Layer interfaces missing")
    
    return all_exist


def validate_backup_files():
    """Validate that backup files were created."""
    print("🔍 Validating backup files...")
    
    backup_files = [
        "roles/frontend_integration/frontend_integration_service_old.py",
        "roles/experience_manager/experience_manager_service_old.py",
        "roles/journey_manager/journey_manager_service_old.py"
    ]
    
    all_exist = True
    for file_path in backup_files:
        if check_file_exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            all_exist = False
    
    if all_exist:
        print("✅ All backup files validated")
    else:
        print("❌ Some backup files missing")
    
    return all_exist


def validate_architecture_compliance():
    """Validate architecture compliance."""
    print("🔍 Validating architecture compliance...")
    
    # Check for anti-patterns (inheritance from FoundationServiceBase)
    anti_patterns = [
        r"FoundationServiceBase",
        r"from foundations\.utility_foundation",
        r"super\(\)\.__init__\(utility_foundation"
    ]
    
    service_files = [
        "roles/frontend_integration/frontend_integration_service.py",
        "roles/experience_manager/experience_manager_service.py",
        "roles/journey_manager/journey_manager_service.py"
    ]
    
    all_compliant = True
    for file_path in service_files:
        if check_file_exists(file_path):
            results = check_file_content(file_path, anti_patterns)
            has_anti_patterns = any(results.values())
            
            if has_anti_patterns:
                print(f"   ❌ {file_path} contains anti-patterns")
                all_compliant = False
            else:
                print(f"   ✅ {file_path} is architecture compliant")
    
    if all_compliant:
        print("✅ All services are architecture compliant")
    else:
        print("❌ Some services contain anti-patterns")
    
    return all_compliant


def main():
    """Run all validations."""
    print("🚀 Starting Experience Dimension Refactoring Validation...")
    print("=" * 60)
    
    validation_results = []
    
    # Run validations
    validation_results.append(validate_frontend_integration_service())
    print()
    
    validation_results.append(validate_experience_manager_service())
    print()
    
    validation_results.append(validate_journey_manager_service())
    print()
    
    validation_results.append(validate_protocols())
    print()
    
    validation_results.append(validate_interfaces())
    print()
    
    validation_results.append(validate_backup_files())
    print()
    
    validation_results.append(validate_architecture_compliance())
    print()
    
    # Summary
    print("=" * 60)
    print("📊 Validation Results Summary:")
    print(f"✅ Passed: {sum(validation_results)}")
    print(f"❌ Failed: {len(validation_results) - sum(validation_results)}")
    print(f"📈 Success Rate: {sum(validation_results) / len(validation_results) * 100:.1f}%")
    
    if all(validation_results):
        print("🎉 All validations passed! Experience Dimension refactoring is complete!")
        print("🔧 Services are ready for frontend integration!")
        print("📋 Next steps:")
        print("   1. Integrate with frontend authentication system")
        print("   2. Connect WebSocket endpoints for real-time communication")
        print("   3. Test end-to-end user journeys")
        print("   4. Deploy and monitor performance")
        return True
    else:
        print("⚠️ Some validations failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
