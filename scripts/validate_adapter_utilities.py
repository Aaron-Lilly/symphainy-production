#!/usr/bin/env python3
"""
Adapter Utility Usage Validator

Validates that all Public Works Foundation adapters:
1. Have DI container integration (if applicable)
2. Use error_handler utility in exception blocks (if applicable)
3. Use telemetry utility in success paths (if applicable)
4. Can be imported and have valid syntax

Note: Adapters are Layer 1 (raw technology clients) and may use basic logging only.
This validator identifies adapters that have DI container but aren't using utilities.
"""

import os
import sys
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict

# Adapters that might be exempt from utilities (raw technology clients)
# These are Layer 1 and may use basic logging only
RAW_TECHNOLOGY_ADAPTERS = {
    'redis_adapter',
    'supabase_adapter',
    'arangodb_adapter',
    'openai_adapter',
    'anthropic_adapter',
    'meilisearch_knowledge_adapter',
    'pytesseract_ocr_adapter',
    'pypdf2_text_extractor',
    'pdfplumber_table_extractor',
    'python_docx_adapter',
    'opencv_image_processor',
    'beautifulsoup_html_adapter',
    'bpmn_adapter',
    'bpmn_processing_adapter',
    'cobol_processing_adapter',
    'sop_parsing_adapter',
    'sop_enhancement_adapter',
    'jwt_adapter',
    'websocket_adapter',
    'tempo_adapter',
    'celery_adapter',
    'resource_adapter',
    'config_adapter',
}

# Foundational infrastructure adapters that provide utilities
# These should NOT use utilities to avoid circular dependencies
FOUNDATIONAL_UTILITY_ADAPTERS = {
    'opentelemetry_health_adapter',  # Provides health monitoring - using telemetry would be circular
    'telemetry_adapter',  # Provides telemetry - using telemetry would be circular
}

class AdapterValidator:
    """Validates adapter utility usage."""
    
    def __init__(self, adapters_dir: str):
        self.adapters_dir = Path(adapters_dir)
        self.results = defaultdict(dict)
        self.errors = []
        
    def validate_all(self) -> Dict[str, any]:
        """Validate all adapters."""
        adapter_files = list(self.adapters_dir.glob("*.py"))
        adapter_files = [f for f in adapter_files if not f.name.startswith("__")]
        
        print(f"\n🔍 Validating {len(adapter_files)} adapter files...\n")
        
        for file_path in sorted(adapter_files):
            self.validate_file(file_path)
        
        return self.generate_report()
    
    def validate_file(self, file_path: Path):
        """Validate a single adapter file."""
        file_name = file_path.name
        adapter_name = file_path.stem
        
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
            'is_raw_technology': adapter_name in RAW_TECHNOLOGY_ADAPTERS,
            'is_foundational_utility': adapter_name in FOUNDATIONAL_UTILITY_ADAPTERS,
            'uses_basic_logging': False,
            'errors': []
        }
        
        try:
            # Check syntax
            with open(file_path, 'r') as f:
                content = f.read()
                ast.parse(content)
            result['syntax_valid'] = True
            
            # Check for basic logging
            if 'logger.error' in content or 'logger.warning' in content or 'logger.info' in content:
                result['uses_basic_logging'] = True
            
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
                module_name = f"foundations.public_works_foundation.infrastructure_adapters.{adapter_name}"
                # Just check if we can parse it, not actually import (would require full setup)
                result['importable'] = True  # Syntax check passed, assume importable
            except:
                pass
            
        except SyntaxError as e:
            result['errors'].append(f"Syntax error: {e}")
        except Exception as e:
            result['errors'].append(f"Validation error: {e}")
        
        self.results[adapter_name] = result
    
    def generate_report(self) -> Dict[str, any]:
        """Generate validation report."""
        total = len(self.results)
        has_di_container = sum(1 for r in self.results.values() if r['has_di_container'])
        has_error_handler = sum(1 for r in self.results.values() if r['has_error_handler'])
        has_telemetry = sum(1 for r in self.results.values() if r['has_telemetry'])
        syntax_valid = sum(1 for r in self.results.values() if r['syntax_valid'])
        uses_basic_logging = sum(1 for r in self.results.values() if r['uses_basic_logging'])
        is_raw_technology = sum(1 for r in self.results.values() if r['is_raw_technology'])
        
        # Count adapters with DI container that should use utilities
        adapters_with_di_but_no_utilities = []
        for name, result in self.results.items():
            if result['has_di_container'] and not result['is_raw_technology'] and not result['is_foundational_utility']:
                if not result['has_error_handler'] and result['exception_blocks'] > 0:
                    adapters_with_di_but_no_utilities.append({
                        'file': result['file'],
                        'issue': f"Has DI container but missing error_handler ({result['exception_blocks']} exception blocks)"
                    })
                if not result['has_telemetry'] and result['success_paths'] > 0:
                    adapters_with_di_but_no_utilities.append({
                        'file': result['file'],
                        'issue': f"Has DI container but missing telemetry ({result['success_paths']} success paths)"
                    })
        
        # Calculate exception block coverage
        total_exception_blocks = sum(r['exception_blocks'] for r in self.results.values())
        exception_blocks_with_handler = sum(r['exception_blocks_with_handler'] for r in self.results.values())
        
        print("\n" + "="*80)
        print("📊 ADAPTER UTILITY USAGE VALIDATION REPORT")
        print("="*80)
        print(f"\n✅ Total Adapters: {total}")
        print(f"✅ Syntax Valid: {syntax_valid}/{total} ({100*syntax_valid/total:.1f}%)")
        print(f"✅ DI Container Integration: {has_di_container}/{total} ({100*has_di_container/total:.1f}%)")
        print(f"✅ Basic Logging Usage: {uses_basic_logging}/{total} ({100*uses_basic_logging/total:.1f}%)")
        print(f"\n📋 Raw Technology Adapters (may use basic logging only): {is_raw_technology}")
        print(f"📋 Adapters with DI Container: {has_di_container}")
        print(f"\n✅ Error Handler Usage: {has_error_handler}/{total} ({100*has_error_handler/total:.1f}%)")
        print(f"✅ Telemetry Usage: {has_telemetry}/{total} ({100*has_telemetry/total:.1f}%)")
        print(f"\n📊 Exception Block Coverage: {exception_blocks_with_handler}/{total_exception_blocks} ({100*exception_blocks_with_handler/max(total_exception_blocks,1):.1f}%)")
        
        # Find violations
        violations = []
        for name, result in self.results.items():
            issues = []
            
            # Raw technology adapters and foundational utility adapters are exempt
            if result['is_raw_technology'] or result['is_foundational_utility']:
                continue
            
            # Check adapters with DI container
            if result['has_di_container']:
                if not result['has_error_handler'] and result['exception_blocks'] > 0:
                    issues.append(f"Missing error_handler ({result['exception_blocks']} exception blocks)")
                if not result['has_telemetry'] and result['success_paths'] > 0:
                    issues.append(f"Missing telemetry ({result['success_paths']} success paths)")
            
            if not result['syntax_valid']:
                issues.append("Syntax errors")
            
            if issues:
                violations.append({
                    'file': result['file'],
                    'has_di_container': result['has_di_container'],
                    'issues': issues
                })
        
        if violations:
            print(f"\n⚠️  VIOLATIONS FOUND: {len(violations)} adapters")
            print("-"*80)
            for v in violations[:20]:  # Show first 20
                di_status = "✅ Has DI" if v['has_di_container'] else "❌ No DI"
                print(f"\n{di_status} {v['file']}")
                for issue in v['issues']:
                    print(f"   - {issue}")
            if len(violations) > 20:
                print(f"\n... and {len(violations) - 20} more violations")
        else:
            print("\n✅ NO VIOLATIONS FOUND - All adapters comply!")
        
        # Summary
        print("\n" + "="*80)
        if len(violations) == 0:
            print("🎉 SUCCESS: All adapters properly configured!")
        else:
            print(f"⚠️  WARNING: {len(violations)} adapters need attention")
        print("="*80 + "\n")
        
        return {
            'total': total,
            'has_di_container': has_di_container,
            'has_error_handler': has_error_handler,
            'has_telemetry': has_telemetry,
            'violations': violations,
            'adapters_with_di_but_no_utilities': adapters_with_di_but_no_utilities,
            'results': dict(self.results)
        }


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    adapters_dir = project_root / "symphainy-platform" / "foundations" / "public_works_foundation" / "infrastructure_adapters"
    
    if not adapters_dir.exists():
        print(f"❌ Error: Adapters directory not found: {adapters_dir}")
        sys.exit(1)
    
    validator = AdapterValidator(str(adapters_dir))
    report = validator.validate_all()
    
    # Exit with error code if violations found
    if report['violations']:
        sys.exit(1)
    else:
        sys.exit(0)

