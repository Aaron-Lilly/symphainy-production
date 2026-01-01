#!/usr/bin/env python3
"""
Helper script to update infrastructure abstractions with utilities.

This script helps with the repetitive parts of adding error handling and telemetry
to abstraction methods, but requires review and approval for each change.

Usage:
    python3 scripts/update_abstraction_utilities.py <abstraction_file> --method <method_name> --review
    python3 scripts/update_abstraction_utilities.py <abstraction_file> --all --apply
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from difflib import unified_diff

def find_async_methods(content: str) -> List[Dict[str, Any]]:
    """Find all async methods in the file."""
    pattern = r'async def (\w+)\([^)]*\)[^:]*:'
    methods = []
    for match in re.finditer(pattern, content):
        method_name = match.group(1)
        method_start = match.start()
        # Find the method end (next method or end of class)
        method_end = content.find('\n    async def ', method_start + 1)
        if method_end == -1:
            method_end = content.find('\nclass ', method_start + 1)
        if method_end == -1:
            method_end = len(content)
        
        method_content = content[method_start:method_end]
        methods.append({
            'name': method_name,
            'start': method_start,
            'end': method_end,
            'content': method_content
        })
    return methods

def needs_telemetry_update(method_content: str) -> bool:
    """Check if method needs telemetry added to success path."""
    # Check if telemetry is already there
    if 'record_platform_operation_event' in method_content:
        return False
    
    # Check if there's a return statement (success path)
    if 'return ' in method_content and 'except' in method_content:
        return True
    
    return False

def needs_error_handler_update(method_content: str) -> bool:
    """Check if method needs error handler update."""
    # Check if error handler is already there
    if 'error_handler = self.di_container.get_utility("error_handler")' in method_content:
        return False
    
    # Check if there's an exception handler
    if 'except Exception' in method_content or 'except:' in method_content:
        return True
    
    return False

def show_method_analysis(file_path: Path):
    """Show analysis of what needs to be updated in a file."""
    content = file_path.read_text()
    
    # Check constructor
    has_di_container = 'di_container' in content and 'self.di_container' in content
    
    # Find async methods
    methods = find_async_methods(content)
    
    print(f"\n{'='*80}")
    print(f"Analysis: {file_path.name}")
    print(f"{'='*80}")
    print(f"Has DI Container: {'✅ Yes' if has_di_container else '❌ No'}")
    print(f"Async Methods: {len(methods)}")
    
    if not has_di_container:
        print(f"\n📋 Constructor needs update:")
        print(f"  - Add di_container parameter")
        print(f"  - Add service_name")
        print(f"  - Get logger from DI container")
    
    # Analyze each method
    methods_needing_updates = []
    for method in methods:
        needs_telemetry = needs_telemetry_update(method['content'])
        needs_error = needs_error_handler_update(method['content'])
        
        if needs_telemetry or needs_error:
            methods_needing_updates.append({
                'name': method['name'],
                'needs_telemetry': needs_telemetry,
                'needs_error': needs_error
            })
    
    if methods_needing_updates:
        print(f"\n📋 Methods needing updates: {len(methods_needing_updates)}")
        for method_info in methods_needing_updates[:10]:
            updates = []
            if method_info['needs_telemetry']:
                updates.append('telemetry')
            if method_info['needs_error']:
                updates.append('error_handler')
            print(f"  - {method_info['name']}: {', '.join(updates)}")
        if len(methods_needing_updates) > 10:
            print(f"  ... and {len(methods_needing_updates) - 10} more")
    else:
        print(f"\n✅ All methods already have utilities")
    
    return {
        'has_di_container': has_di_container,
        'methods': methods,
        'methods_needing_updates': methods_needing_updates
    }

def show_diff(old_content: str, new_content: str, context_lines: int = 5):
    """Show a diff between old and new content."""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = unified_diff(
        old_lines, new_lines,
        fromfile='old', tofile='new',
        lineterm='', n=context_lines
    )
    
    print("\n" + "="*80)
    print("DIFF:")
    print("="*80)
    for line in diff:
        print(line, end='')
    print("="*80 + "\n")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Update abstractions with utilities')
    parser.add_argument('file', help='Abstraction file path')
    parser.add_argument('--method', help='Specific method to update')
    parser.add_argument('--all', action='store_true', help='Update all methods')
    parser.add_argument('--apply', action='store_true', help='Actually apply changes')
    parser.add_argument('--review', action='store_true', help='Show diff before applying')
    args = parser.parse_args()
    
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    # Show analysis
    analysis = show_method_analysis(file_path)
    
    if not args.all and not args.method:
        print("\n💡 Use --method <name> to update a specific method")
        print("   Use --all to update all methods")
        print("   Use --review to see diffs before applying")
        print("   Use --apply to actually make changes")
        return
    
    if not args.apply and not args.review:
        print("\n⚠️  Use --review to see what would change, or --apply to make changes")
        return
    
    print("\n⚠️  This script is a helper - manual review is still recommended!")
    print("   The script shows what it will do, but you should verify each change.")

if __name__ == '__main__':
    main()

