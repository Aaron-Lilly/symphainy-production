#!/usr/bin/env python3
"""
Fix Foundation Service Methods - Update to New Utility Pattern

Updates methods in Public Works Foundation Service to use new utility pattern:
- Replace get_utility("telemetry") with log_operation_with_telemetry()
- Replace get_utility("error_handler") with handle_error_with_audit()
- Replace record_platform_operation_event() with record_health_metric()
"""

import re
from pathlib import Path

SERVICE_FILE = Path("foundations/public_works_foundation/public_works_foundation_service.py")


def fix_method_utilities(content: str) -> str:
    """Fix utility calls in methods."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip old utility getter patterns
        if re.search(r'telemetry\s*=\s*self\.get_utility\(["\']telemetry["\']\)', line):
            # Skip this line and the if block
            i += 1
            if i < len(lines) and lines[i].strip().startswith('if telemetry:'):
                # Skip the if block
                indent = len(lines[i]) - len(lines[i].lstrip())
                i += 1
                while i < len(lines):
                    if lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) <= indent:
                        break
                    i += 1
                continue
        
        if re.search(r'error_handler\s*=\s*self\.get_utility\(["\']error_handler["\']\)', line):
            # Skip this line and the if block
            i += 1
            if i < len(lines) and lines[i].strip().startswith('if error_handler:'):
                # Skip the if block
                indent = len(lines[i]) - len(lines[i].lstrip())
                i += 1
                while i < len(lines):
                    if lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) <= indent:
                        break
                    i += 1
                continue
        
        # Replace record_platform_operation_event with record_health_metric
        if 'record_platform_operation_event' in line:
            # This will be handled by manual fixes
            new_lines.append(line)
            i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def main():
    """Fix foundation service methods."""
    base_dir = Path(__file__).parent.parent
    service_file = base_dir / SERVICE_FILE
    
    if not service_file.exists():
        print(f"❌ Service file not found: {service_file}")
        return
    
    print(f"📁 Fixing utilities in: {service_file}\n")
    print("⚠️  This script identifies methods that need fixing.")
    print("⚠️  Manual fixes are required for complex cases.\n")
    
    with open(service_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find methods using old pattern
    old_pattern_methods = []
    
    # Find methods with get_utility("telemetry")
    for match in re.finditer(r'async def (\w+)\([^)]*\):', content):
        method_name = match.group(1)
        method_start = match.start()
        # Find the method body (next 200 lines or until next def)
        method_end = content.find('\n    async def ', method_start + 1)
        if method_end == -1:
            method_end = content.find('\n    def ', method_start + 1)
        if method_end == -1:
            method_end = min(method_start + 2000, len(content))
        
        method_body = content[method_start:method_end]
        
        if 'get_utility("telemetry")' in method_body or 'get_utility("error_handler")' in method_body or 'record_platform_operation_event' in method_body:
            old_pattern_methods.append(method_name)
    
    print(f"📋 Found {len(old_pattern_methods)} methods using old pattern:")
    for method in old_pattern_methods[:20]:
        print(f"  - {method}")
    if len(old_pattern_methods) > 20:
        print(f"  ... and {len(old_pattern_methods) - 20} more")
    
    print(f"\n⚠️  Manual fixes required for these methods.")


if __name__ == "__main__":
    main()







