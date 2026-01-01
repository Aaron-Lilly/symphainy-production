#!/usr/bin/env python3
"""
Script to validate Smart City usage patterns in upstream realms.

Validates that Business Enablement, Journey, and Solution realms:
1. Use Smart City SOA APIs (not direct service access)
2. Use Platform Gateway for Public Works abstractions (not direct foundation access)
3. Follow DI Container and Utility patterns
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.fixtures.smart_city_usage_validator import SmartCityUsageValidator


def main():
    """Run Smart City usage validation on all upstream realms."""
    # project_root is symphainy_source, need symphainy-platform
    symphainy_platform_root = project_root / 'symphainy-platform'
    
    if not symphainy_platform_root.exists():
        print(f"❌ Error: symphainy-platform directory not found at {symphainy_platform_root}")
        sys.exit(1)
    
    print("🔍 Validating Smart City usage patterns in upstream realms...")
    print(f"   Project root: {symphainy_platform_root}")
    print()
    
    validator = SmartCityUsageValidator(symphainy_platform_root)
    
    # Validate all upstream realms
    results = validator.validate_all_upstream_realms()
    
    # Print summary
    print("=" * 80)
    print("SMART CITY USAGE VALIDATION RESULTS")
    print("=" * 80)
    print()
    print(f"Realms Validated: {', '.join(results['realms_validated'])}")
    print()
    print(f"Total Violations: {results['total_violations']}")
    print(f"  - Smart City Usage Violations: {results['total_smart_city_violations']}")
    print(f"  - DI Container Violations: {results['total_di_container_violations']}")
    print(f"  - Utility Violations: {results['total_utility_violations']}")
    print(f"  - Foundation Usage Violations: {results['total_foundation_violations']}")
    print()
    
    # Print per-realm results
    for realm, realm_results in results['realm_results'].items():
        if realm_results.get('status') == 'error':
            print(f"❌ {realm}: {realm_results.get('error', 'Unknown error')}")
            continue
        
        print(f"📊 {realm.upper()}:")
        print(f"   Total Violations: {realm_results['total_violations']}")
        print(f"   - Smart City: {realm_results['smart_city_violations']}")
        print(f"   - DI Container: {realm_results['di_container_violations']}")
        print(f"   - Utility: {realm_results['utility_violations']}")
        print(f"   - Foundation: {realm_results['foundation_violations']}")
        print()
    
    # Print detailed violations if any
    if results['total_violations'] > 0:
        print("=" * 80)
        print("DETAILED VIOLATIONS")
        print("=" * 80)
        print()
        
        for realm, realm_results in results['realm_results'].items():
            if realm_results.get('status') == 'error':
                continue
            
            violations = realm_results.get('violations', [])
            if violations:
                print(f"\n{realm.upper()} REALM VIOLATIONS:")
                print("-" * 80)
                
                # Group by type
                by_type = {}
                for v in violations:
                    v_type = v.get('type', 'unknown')
                    if v_type not in by_type:
                        by_type[v_type] = []
                    by_type[v_type].append(v)
                
                for v_type, type_violations in sorted(by_type.items()):
                    print(f"\n  {v_type.upper()} ({len(type_violations)} violations):")
                    for v in type_violations[:10]:  # Show first 10 of each type
                        print(f"    {v['file']}:{v['line']} - {v['message']}")
                        print(f"      → {v.get('recommendation', 'No recommendation')}")
                    if len(type_violations) > 10:
                        print(f"    ... and {len(type_violations) - 10} more")
    
    print()
    print("=" * 80)
    if results['total_violations'] == 0:
        print("✅ All upstream realms properly use Smart City SOA APIs and Platform Gateway!")
    else:
        print(f"⚠️  Found {results['total_violations']} violations. Please review and fix.")
    print("=" * 80)
    
    return 0 if results['total_violations'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

