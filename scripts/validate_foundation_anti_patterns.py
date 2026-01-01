#!/usr/bin/env python3
"""
Foundation Anti-Pattern Validation Script

Validates foundation services for DI Container and Utility usage anti-patterns.
Provides comprehensive reporting and actionable recommendations.

WHAT: Validate foundation services for anti-patterns
HOW: Run DI Container and Utility validators, report violations, provide fixes
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.fixtures.di_container_usage_validator import DIContainerUsageValidator
from tests.fixtures.utility_usage_validator import UtilityUsageValidator


class FoundationValidator:
    """Comprehensive foundation validation with reporting."""
    
    def __init__(self, project_root: Path):
        """Initialize validators."""
        self.project_root = project_root
        self.di_validator = DIContainerUsageValidator(project_root)
        self.util_validator = UtilityUsageValidator(project_root)
    
    def validate_foundation(self, foundation_name: str) -> Dict[str, Any]:
        """
        Validate a foundation service for anti-patterns.
        
        Args:
            foundation_name: Name of foundation (e.g., 'public_works_foundation')
        
        Returns:
            Dictionary with validation results
        """
        foundation_path = self.project_root / 'symphainy-platform' / 'foundations' / foundation_name
        
        if not foundation_path.exists():
            return {
                'foundation': foundation_name,
                'status': 'error',
                'message': f"Foundation path not found: {foundation_path}",
                'di_violations': [],
                'util_violations': []
            }
        
        # Run validators
        di_violations = self.di_validator.validate_directory(foundation_path)
        util_violations = self.util_validator.validate_directory(foundation_path)
        
        # Group violations by file
        di_by_file = self._group_by_file(di_violations)
        util_by_file = self._group_by_file(util_violations)
        
        return {
            'foundation': foundation_name,
            'status': 'success' if not di_violations and not util_violations else 'violations',
            'di_violations': di_violations,
            'util_violations': util_violations,
            'di_by_file': di_by_file,
            'util_by_file': util_by_file,
            'total_di_violations': len(di_violations),
            'total_util_violations': len(util_violations),
            'files_with_di_violations': len(di_by_file),
            'files_with_util_violations': len(util_by_file)
        }
    
    def _group_by_file(self, violations: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group violations by file path."""
        by_file = {}
        for v in violations:
            file_path = v['file']
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(v)
        return by_file
    
    def print_report(self, results: Dict[str, Any]):
        """Print comprehensive validation report."""
        foundation = results['foundation']
        status = results['status']
        
        print(f"\n{'=' * 80}")
        print(f"Foundation: {foundation.upper().replace('_', ' ')}")
        print(f"{'=' * 80}")
        print(f"Status: {status.upper()}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # DI Container Violations
        print(f"📦 DI Container Usage Violations: {results['total_di_violations']}")
        if results['di_violations']:
            print(f"   Files affected: {results['files_with_di_violations']}")
            for file_path, violations in sorted(results['di_by_file'].items()):
                print(f"\n   📄 {file_path}: {len(violations)} violation(s)")
                for v in violations[:5]:  # Show first 5 per file
                    print(f"      Line {v['line']}: {v['type']}")
                    print(f"         {v['message']}")
                    if 'recommendation' in v:
                        print(f"         💡 {v['recommendation']}")
                if len(violations) > 5:
                    print(f"      ... and {len(violations) - 5} more")
        else:
            print("   ✅ No violations found!")
        
        print()
        
        # Utility Violations
        print(f"🔧 Utility Usage Violations: {results['total_util_violations']}")
        if results['util_violations']:
            print(f"   Files affected: {results['files_with_util_violations']}")
            for file_path, violations in sorted(results['util_by_file'].items()):
                print(f"\n   📄 {file_path}: {len(violations)} violation(s)")
                for v in violations[:5]:  # Show first 5 per file
                    print(f"      Line {v['line']}: {v['type']}")
                    print(f"         {v['message']}")
                if len(violations) > 5:
                    print(f"      ... and {len(violations) - 5} more")
        else:
            print("   ✅ No violations found!")
        
        print()
        
        # Summary
        total_violations = results['total_di_violations'] + results['total_util_violations']
        if total_violations == 0:
            print("✅ Foundation is clean - no anti-patterns detected!")
        else:
            print(f"⚠️  Total violations: {total_violations}")
            print(f"   DI Container: {results['total_di_violations']}")
            print(f"   Utility: {results['total_util_violations']}")
        
        print(f"{'=' * 80}\n")
    
    def validate_multiple(self, foundation_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """Validate multiple foundations."""
        all_results = {}
        for foundation_name in foundation_names:
            all_results[foundation_name] = self.validate_foundation(foundation_name)
        return all_results
    
    def print_summary(self, all_results: Dict[str, Dict[str, Any]]):
        """Print summary across all foundations."""
        print(f"\n{'=' * 80}")
        print("VALIDATION SUMMARY")
        print(f"{'=' * 80}")
        print(f"Foundations validated: {len(all_results)}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        total_di = 0
        total_util = 0
        clean_foundations = []
        violations_foundations = []
        
        for foundation_name, results in sorted(all_results.items()):
            di_count = results['total_di_violations']
            util_count = results['total_util_violations']
            total = di_count + util_count
            
            total_di += di_count
            total_util += util_count
            
            if total == 0:
                clean_foundations.append(foundation_name)
                status_icon = "✅"
            else:
                violations_foundations.append(foundation_name)
                status_icon = "⚠️"
            
            print(f"{status_icon} {foundation_name.replace('_', ' ').title()}")
            print(f"   DI Container: {di_count} violations")
            print(f"   Utility: {util_count} violations")
            print()
        
        print(f"{'=' * 80}")
        print("OVERALL SUMMARY")
        print(f"{'=' * 80}")
        print(f"Total DI Container violations: {total_di}")
        print(f"Total Utility violations: {total_util}")
        print(f"Total violations: {total_di + total_util}")
        print()
        
        if clean_foundations:
            print(f"✅ Clean foundations ({len(clean_foundations)}):")
            for f in clean_foundations:
                print(f"   - {f.replace('_', ' ').title()}")
            print()
        
        if violations_foundations:
            print(f"⚠️  Foundations with violations ({len(violations_foundations)}):")
            for f in violations_foundations:
                print(f"   - {f.replace('_', ' ').title()}")
            print()
        
        print(f"{'=' * 80}\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate foundation services for anti-patterns'
    )
    parser.add_argument(
        'foundations',
        nargs='*',
        default=['public_works_foundation', 'curator_foundation', 'communication_foundation'],
        help='Foundation names to validate (default: public_works_foundation curator_foundation communication_foundation)'
    )
    parser.add_argument(
        '--summary-only',
        action='store_true',
        help='Show only summary, not detailed reports'
    )
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    validator = FoundationValidator(project_root)
    
    # Validate foundations
    all_results = validator.validate_multiple(args.foundations)
    
    # Print reports
    if not args.summary_only:
        for foundation_name in args.foundations:
            if foundation_name in all_results:
                validator.print_report(all_results[foundation_name])
    
    # Print summary
    validator.print_summary(all_results)
    
    # Exit with error code if violations found
    total_violations = sum(
        r['total_di_violations'] + r['total_util_violations']
        for r in all_results.values()
    )
    
    if total_violations > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

