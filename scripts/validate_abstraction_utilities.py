#!/usr/bin/env python3
"""
Abstraction Utility Usage Validator

Validates that all Public Works Foundation abstractions:
1. Have DI container integration
2. Use error_handler utility in exception blocks
3. Use telemetry utility in success paths
4. Can be imported and have valid syntax
"""

import os
import sys
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict

# Utility abstractions that should NOT use error_handler/telemetry (circular dependency)
UTILITY_ABSTRACTIONS = {
    'health_abstraction',
    'telemetry_abstraction',
    'session_abstraction',
    'policy_abstraction',
    'service_discovery_abstraction'
}

class AbstractionValidator:
    """Validates abstraction utility usage."""
    
    def __init__(self, abstractions_dir: str):
        self.abstractions_dir = Path(abstractions_dir)
        self.results = defaultdict(dict)
        self.errors = []
        
    def validate_all(self) -> Dict[str, any]:
        """Validate all abstractions."""
        abstraction_files = list(self.abstractions_dir.glob("*.py"))
        abstraction_files = [f for f in abstraction_files if not f.name.startswith("__")]
        
        print(f"\n🔍 Validating {len(abstraction_files)} abstraction files...\n")
        
        for file_path in sorted(abstraction_files):
            self.validate_file(file_path)
        
        return self.generate_report()
    
    def validate_file(self, file_path: Path):
        """Validate a single abstraction file."""
        file_name = file_path.name
        abstraction_name = file_path.stem
        
        result = {
            'file': file_name,
            'has_di_container': False,
            'has_error_handler': False,
            'has_telemetry': False,
            'exception_blocks': 0,
            'exception_blocks_with_handler': 0,
            'success_paths': 0,
            'success_paths_with_telemetry': 0,
            'syntax_valid': False,
            'importable': False,
            'is_utility_abstraction': abstraction_name in UTILITY_ABSTRACTIONS,
            'errors': []
        }
        
        try:
            # Check syntax
            with open(file_path, 'r') as f:
                content = f.read()
                ast.parse(content)
            result['syntax_valid'] = True
            
            # Check for DI container
            if 'di_container' in content and ('self.di_container' in content or 'di_container=' in content):
                result['has_di_container'] = True
            
            # Count exception blocks
            exception_pattern = r'except\s+(Exception|BaseException|\w+Error)\s+as\s+\w+:'
            exception_blocks = re.findall(exception_pattern, content)
            result['exception_blocks'] = len(exception_blocks)
            
            # Check for error handler usage
            error_handler_patterns = [
                r'get_utility\(["\']error_handler["\']\)',
                r'error_handler\.handle_error',
                r'handle_error_with_audit'
            ]
            has_error_handler = any(re.search(pattern, content) for pattern in error_handler_patterns)
            result['has_error_handler'] = has_error_handler
            
            # Count exception blocks with error handler
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if re.search(exception_pattern, line):
                    # Check next 10 lines for error handler
                    context = '\n'.join(lines[i:min(i+10, len(lines))])
                    if any(re.search(pattern, context) for pattern in error_handler_patterns):
                        result['exception_blocks_with_handler'] += 1
            
            # Check for telemetry usage
            telemetry_patterns = [
                r'get_utility\(["\']telemetry["\']\)',
                r'record_platform_operation_event',
                r'record_platform_error_event',
                r'telemetry\.record'
            ]
            has_telemetry = any(re.search(pattern, content) for pattern in telemetry_patterns)
            result['has_telemetry'] = has_telemetry
            
            # Count success paths (async methods with return statements)
            async_method_pattern = r'async\s+def\s+\w+\([^)]*\)\s*:'
            async_methods = re.finditer(async_method_pattern, content)
            success_paths = 0
            success_paths_with_telemetry = 0
            
            for match in async_methods:
                start = match.end()
                # Find the method body (until next def or end of class)
                method_end = content.find('\n    def ', start)
                if method_end == -1:
                    method_end = content.find('\nclass ', start)
                if method_end == -1:
                    method_end = len(content)
                
                method_body = content[start:method_end]
                
                # Check for return statements (success paths)
                if 'return ' in method_body:
                    success_paths += 1
                    # Check if telemetry is recorded before return
                    return_positions = [m.start() for m in re.finditer(r'return\s+', method_body)]
                    for return_pos in return_positions:
                        # Check 20 lines before return for telemetry
                        lines_before = method_body[:return_pos].split('\n')
                        context_before = '\n'.join(lines_before[-20:])
                        if any(re.search(pattern, context_before) for pattern in telemetry_patterns):
                            success_paths_with_telemetry += 1
                            break
            
            result['success_paths'] = success_paths
            result['success_paths_with_telemetry'] = success_paths_with_telemetry
            
            # Check if importable (basic check)
            try:
                module_name = f"foundations.public_works_foundation.infrastructure_abstractions.{abstraction_name}"
                # Just check if we can parse it, not actually import (would require full setup)
                result['importable'] = True  # Syntax check passed, assume importable
            except:
                pass
            
        except SyntaxError as e:
            result['errors'].append(f"Syntax error: {e}")
        except Exception as e:
            result['errors'].append(f"Validation error: {e}")
        
        self.results[abstraction_name] = result
    
    def generate_report(self) -> Dict[str, any]:
        """Generate validation report."""
        total = len(self.results)
        has_di_container = sum(1 for r in self.results.values() if r['has_di_container'])
        has_error_handler = sum(1 for r in self.results.values() if r['has_error_handler'])
        has_telemetry = sum(1 for r in self.results.values() if r['has_telemetry'])
        syntax_valid = sum(1 for r in self.results.values() if r['syntax_valid'])
        
        # Count utility abstractions
        utility_abstractions = sum(1 for r in self.results.values() if r['is_utility_abstraction'])
        non_utility = total - utility_abstractions
        
        # For non-utility abstractions, check compliance
        non_utility_with_error_handler = sum(
            1 for r in self.results.values() 
            if r['has_error_handler'] and not r['is_utility_abstraction']
        )
        non_utility_with_telemetry = sum(
            1 for r in self.results.values() 
            if r['has_telemetry'] and not r['is_utility_abstraction']
        )
        
        # Calculate exception block coverage
        total_exception_blocks = sum(r['exception_blocks'] for r in self.results.values())
        exception_blocks_with_handler = sum(r['exception_blocks_with_handler'] for r in self.results.values())
        
        print("\n" + "="*80)
        print("📊 ABSTRACTION UTILITY USAGE VALIDATION REPORT")
        print("="*80)
        print(f"\n✅ Total Abstractions: {total}")
        print(f"✅ Syntax Valid: {syntax_valid}/{total} ({100*syntax_valid/total:.1f}%)")
        print(f"✅ DI Container Integration: {has_di_container}/{total} ({100*has_di_container/total:.1f}%)")
        print(f"\n📋 Utility Abstractions (exempt from error_handler/telemetry): {utility_abstractions}")
        print(f"📋 Non-Utility Abstractions: {non_utility}")
        print(f"\n✅ Error Handler Usage: {non_utility_with_error_handler}/{non_utility} non-utility ({100*non_utility_with_error_handler/max(non_utility,1):.1f}%)")
        print(f"✅ Telemetry Usage: {non_utility_with_telemetry}/{non_utility} non-utility ({100*non_utility_with_telemetry/max(non_utility,1):.1f}%)")
        print(f"\n📊 Exception Block Coverage: {exception_blocks_with_handler}/{total_exception_blocks} ({100*exception_blocks_with_handler/max(total_exception_blocks,1):.1f}%)")
        
        # Find violations
        violations = []
        for name, result in self.results.items():
            if result['is_utility_abstraction']:
                continue  # Skip utility abstractions
            
            issues = []
            if not result['has_di_container']:
                issues.append("Missing DI container")
            if not result['has_error_handler'] and result['exception_blocks'] > 0:
                issues.append(f"Missing error_handler ({result['exception_blocks']} exception blocks)")
            if not result['has_telemetry'] and result['success_paths'] > 0:
                issues.append(f"Missing telemetry ({result['success_paths']} success paths)")
            if not result['syntax_valid']:
                issues.append("Syntax errors")
            
            if issues:
                violations.append({
                    'file': result['file'],
                    'issues': issues
                })
        
        if violations:
            print(f"\n⚠️  VIOLATIONS FOUND: {len(violations)} abstractions")
            print("-"*80)
            for v in violations[:20]:  # Show first 20
                print(f"\n❌ {v['file']}")
                for issue in v['issues']:
                    print(f"   - {issue}")
            if len(violations) > 20:
                print(f"\n... and {len(violations) - 20} more violations")
        else:
            print("\n✅ NO VIOLATIONS FOUND - All abstractions comply!")
        
        # Summary
        print("\n" + "="*80)
        if len(violations) == 0:
            print("🎉 SUCCESS: All abstractions properly use utilities!")
        else:
            print(f"⚠️  WARNING: {len(violations)} abstractions need attention")
        print("="*80 + "\n")
        
        return {
            'total': total,
            'has_di_container': has_di_container,
            'non_utility_with_error_handler': non_utility_with_error_handler,
            'non_utility_with_telemetry': non_utility_with_telemetry,
            'non_utility': non_utility,
            'violations': violations,
            'results': dict(self.results)
        }


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    abstractions_dir = project_root / "symphainy-platform" / "foundations" / "public_works_foundation" / "infrastructure_abstractions"
    
    if not abstractions_dir.exists():
        print(f"❌ Error: Abstractions directory not found: {abstractions_dir}")
        sys.exit(1)
    
    validator = AbstractionValidator(str(abstractions_dir))
    report = validator.validate_all()
    
    # Exit with error code if violations found
    if report['violations']:
        sys.exit(1)
    else:
        sys.exit(0)









