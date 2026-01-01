#!/usr/bin/env python3
"""
Realm Foundation Usage Validation Script

Validates that realm services properly use foundations according to architectural rules.

WHAT: Validate realm services for proper foundation usage
HOW: Run Foundation Usage Validator on realm services, report violations

Architectural Rules:
1. Smart City services CAN directly access Public Works Foundation and Communications Foundation
2. Other realms (Business Enablement, Journey, Solution) MUST use Smart City SOA APIs (not direct foundation access)
3. All realms CAN access Experience Foundation and Agentic Foundation
4. Other realms can access selective Public Works abstractions via Platform Gateway (not direct foundation access)
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.fixtures.foundation_usage_validator import FoundationUsageValidator


class RealmFoundationValidator:
    """Comprehensive realm foundation validation with reporting."""
    
    def __init__(self, project_root: Path):
        """Initialize validators."""
        self.project_root = project_root
        # Validator expects symphainy-platform as project root
        symphainy_platform_root = project_root / 'symphainy-platform'
        self.validator = FoundationUsageValidator(symphainy_platform_root)
    
    def validate_realm(self, realm_name: str) -> Dict[str, Any]:
        """
        Validate a realm for foundation usage anti-patterns.
        
        Args:
            realm_name: Name of realm (e.g., 'business_enablement', 'journey', 'solution', 'smart_city')
        
        Returns:
            Dictionary with validation results
        """
        realm_path = self.project_root / 'symphainy-platform' / 'backend' / realm_name
        
        if not realm_path.exists():
            return {
                'realm': realm_name,
                'status': 'error',
                'message': f"Realm path not found: {realm_path}",
                'foundation_violations': [],
                'di_violations': [],
                'util_violations': [],
                'public_works_violations': []
            }
        
        # Run comprehensive validation
        results = self.validator.validate_directory_comprehensive(realm_path)
        
        return {
            'realm': realm_name,
            'status': 'success' if results['total_violations'] == 0 else 'violations',
            'foundation_violations': results['foundation_violations'],
            'di_violations': results['di_container_violations'],
            'util_violations': results['utility_violations'],
            'public_works_violations': results['public_works_violations'],
            'total_foundation_violations': results['foundation_count'],
            'total_di_violations': results['di_container_count'],
            'total_util_violations': results['utility_count'],
            'total_public_works_violations': results['public_works_count'],
            'total_violations': results['total_violations'],
            'violations_by_type': results['violations_by_type']
        }
    
    def validate_multiple(self, realm_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """Validate multiple realms."""
        results = {}
        for realm_name in realm_names:
            results[realm_name] = self.validate_realm(realm_name)
        return results
    
    def print_report(self, results: Dict[str, Any]):
        """Print comprehensive validation report."""
        realm = results['realm']
        status = results['status']
        
        print(f"\n{'=' * 80}")
        print(f"Realm: {realm.upper().replace('_', ' ')}")
        print(f"{'=' * 80}")
        print(f"Status: {status.upper()}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Foundation Violations
        print(f"🏛️ Foundation Usage Violations: {results['total_foundation_violations']}")
        if results['total_foundation_violations'] > 0:
            print("   Violations:")
            for v in results['foundation_violations'][:10]:  # Show first 10
                print(f"   - {v['file']}:{v['line']} - {v['message']}")
                print(f"     Recommendation: {v['recommendation']}")
            if results['total_foundation_violations'] > 10:
                print(f"   ... and {results['total_foundation_violations'] - 10} more violations")
        print()
        
        # DI Container Violations
        print(f"📦 DI Container Usage Violations: {results['total_di_violations']}")
        if results['total_di_violations'] > 0:
            print("   Violations:")
            for v in results['di_violations'][:5]:  # Show first 5
                print(f"   - {v['file']}:{v['line']} - {v['message']}")
            if results['total_di_violations'] > 5:
                print(f"   ... and {results['total_di_violations'] - 5} more violations")
        print()
        
        # Utility Violations
        print(f"🛠️ Utility Usage Violations: {results['total_util_violations']}")
        if results['total_util_violations'] > 0:
            print("   Violations:")
            for v in results['util_violations'][:5]:  # Show first 5
                print(f"   - {v['file']}:{v['line']} - {v['message']}")
            if results['total_util_violations'] > 5:
                print(f"   ... and {results['total_util_violations'] - 5} more violations")
        print()
        
        # Public Works Violations
        print(f"🏗️ Public Works Foundation Usage Violations: {results['total_public_works_violations']}")
        if results['total_public_works_violations'] > 0:
            print("   Violations:")
            for v in results['public_works_violations'][:5]:  # Show first 5
                print(f"   - {v['file']}:{v['line']} - {v['message']}")
            if results['total_public_works_violations'] > 5:
                print(f"   ... and {results['total_public_works_violations'] - 5} more violations")
        print()
        
        # Summary
        print(f"📊 Total Violations: {results['total_violations']}")
        if results['total_violations'] == 0:
            print("✅ All validations passed!")
        else:
            print("❌ Violations found - please review and fix")
        print()
    
    def print_summary(self, all_results: Dict[str, Dict[str, Any]]):
        """Print summary across all realms."""
        print(f"\n{'=' * 80}")
        print("REALM FOUNDATION USAGE VALIDATION SUMMARY")
        print(f"{'=' * 80}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        total_foundation = sum(r['total_foundation_violations'] for r in all_results.values())
        total_di = sum(r['total_di_violations'] for r in all_results.values())
        total_util = sum(r['total_util_violations'] for r in all_results.values())
        total_public_works = sum(r['total_public_works_violations'] for r in all_results.values())
        total_all = sum(r['total_violations'] for r in all_results.values())
        
        print(f"Total Foundation Violations: {total_foundation}")
        print(f"Total DI Container Violations: {total_di}")
        print(f"Total Utility Violations: {total_util}")
        print(f"Total Public Works Violations: {total_public_works}")
        print(f"Total All Violations: {total_all}")
        print()
        
        print("By Realm:")
        for realm_name, results in all_results.items():
            status_icon = "✅" if results['total_violations'] == 0 else "❌"
            print(f"  {status_icon} {realm_name}: {results['total_violations']} violations")
            if results['total_violations'] > 0:
                print(f"     - Foundation: {results['total_foundation_violations']}")
                print(f"     - DI Container: {results['total_di_violations']}")
                print(f"     - Utility: {results['total_util_violations']}")
                print(f"     - Public Works: {results['total_public_works_violations']}")
        print()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate realm foundation usage')
    parser.add_argument('realms', nargs='*', default=['business_enablement', 'journey', 'solution', 'smart_city'],
                        help='Realms to validate (default: all realms)')
    parser.add_argument('--summary-only', action='store_true',
                        help='Only show summary, not detailed reports')
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    validator = RealmFoundationValidator(project_root)
    
    # Validate realms
    all_results = validator.validate_multiple(args.realms)
    
    # Print reports
    if not args.summary_only:
        for realm_name in args.realms:
            if realm_name in all_results:
                validator.print_report(all_results[realm_name])
    
    # Print summary
    validator.print_summary(all_results)
    
    # Exit with error code if violations found
    total_violations = sum(
        r['total_violations']
        for r in all_results.values()
    )
    
    if total_violations > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

