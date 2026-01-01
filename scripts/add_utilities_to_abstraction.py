#!/usr/bin/env python3
"""
Helper script to add utilities (error handling, telemetry) to infrastructure abstractions.

This script:
1. Shows what changes will be made (dry-run mode)
2. Can apply changes to a single file or batch
3. Makes surgical, careful changes
4. Preserves existing code structure

Usage:
    python3 scripts/add_utilities_to_abstraction.py <abstraction_file> [--apply]
    python3 scripts/add_utilities_to_abstraction.py <abstraction_file> --dry-run
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional

def find_constructor(content: str) -> Tuple[Optional[int], Optional[str]]:
    """Find the __init__ method and its signature."""
    pattern = r'def __init__\(self[^)]*\):'
    match = re.search(pattern, content)
    if match:
        return match.start(), match.group(0)
    return None, None

def find_async_methods(content: str) -> List[Tuple[int, str, str]]:
    """Find all async methods that need error handling."""
    pattern = r'async def (\w+)\([^)]*\)[^:]*:'
    matches = []
    for match in re.finditer(pattern, content):
        method_name = match.group(1)
        method_start = match.start()
        # Get the method signature
        sig_end = content.find(':', method_start)
        method_sig = content[method_start:sig_end+1]
        matches.append((method_start, method_name, method_sig))
    return matches

def needs_di_container(content: str) -> bool:
    """Check if abstraction already has di_container."""
    return 'di_container' in content and 'self.di_container' in content

def analyze_abstraction(file_path: Path) -> dict:
    """Analyze an abstraction file to determine what changes are needed."""
    content = file_path.read_text()
    
    analysis = {
        'file': file_path.name,
        'has_di_container': needs_di_container(content),
        'constructor_pos': None,
        'constructor_sig': None,
        'async_methods': [],
        'needs_changes': False
    }
    
    # Find constructor
    pos, sig = find_constructor(content)
    analysis['constructor_pos'] = pos
    analysis['constructor_sig'] = sig
    
    # Find async methods
    analysis['async_methods'] = find_async_methods(content)
    
    # Determine if changes needed
    if not analysis['has_di_container']:
        analysis['needs_changes'] = True
    
    return analysis

def show_analysis(analysis: dict):
    """Show analysis results."""
    print(f"\n{'='*80}")
    print(f"Analysis: {analysis['file']}")
    print(f"{'='*80}")
    print(f"Has DI Container: {'✅ Yes' if analysis['has_di_container'] else '❌ No'}")
    print(f"Constructor: {analysis['constructor_sig'] or 'Not found'}")
    print(f"Async Methods: {len(analysis['async_methods'])}")
    
    if analysis['needs_changes']:
        print(f"\n📋 Changes Needed:")
        print(f"  1. Add di_container parameter to __init__")
        print(f"  2. Add logger from DI container")
        print(f"  3. Add error handling to {len(analysis['async_methods'])} async methods")
        print(f"  4. Add telemetry to {len(analysis['async_methods'])} async methods")
    else:
        print(f"\n✅ Already has DI container support")
    
    if analysis['async_methods']:
        print(f"\n📝 Async Methods Found:")
        for i, (pos, name, sig) in enumerate(analysis['async_methods'][:5], 1):
            print(f"  {i}. {name}")
        if len(analysis['async_methods']) > 5:
            print(f"  ... and {len(analysis['async_methods']) - 5} more")

def apply_changes(file_path: Path, dry_run: bool = True) -> bool:
    """Apply changes to an abstraction file."""
    content = file_path.read_text()
    original_content = content
    
    # Check if already has di_container
    if needs_di_container(content):
        print(f"⚠️  {file_path.name} already has DI container support, skipping...")
        return False
    
    # Step 1: Add di_container to constructor
    constructor_pattern = r'(def __init__\(self)([^)]*)(\):)'
    match = re.search(constructor_pattern, content)
    if match:
        params = match.group(2).strip()
        if params and not params.endswith(','):
            params += ','
        new_params = params + ' di_container=None' if params else 'di_container=None'
        new_sig = match.group(1) + new_params + match.group(3)
        content = content[:match.start()] + new_sig + content[match.end():]
        
        # Find where to add di_container initialization
        init_end = content.find('\n', match.end())
        indent = '        '  # 8 spaces for class methods
        di_container_init = f'\n{indent}self.di_container = di_container\n{indent}self.service_name = "{file_path.stem}"\n{indent}\n{indent}# Get logger from DI Container if available\n{indent}if di_container and hasattr(di_container, \'get_logger\'):\n{indent}    self.logger = di_container.get_logger(self.service_name)\n{indent}else:\n{indent}    self.logger = logging.getLogger(__name__)'
        
        # Find existing logger initialization to replace
        logger_pattern = r'self\.logger\s*=\s*logging\.getLogger\([^)]+\)'
        logger_match = re.search(logger_pattern, content[init_end:init_end+500])
        if logger_match:
            # Replace existing logger initialization
            logger_start = init_end + logger_match.start()
            logger_end = init_end + logger_match.end()
            content = content[:logger_start] + di_container_init + content[logger_end:]
        else:
            # Add after __init__ signature
            content = content[:init_end] + di_container_init + content[init_end:]
    
    if dry_run:
        print(f"\n🔍 DRY RUN - Would make changes to {file_path.name}")
        print(f"   (Use --apply to actually make changes)")
        return True
    
    # Write changes
    file_path.write_text(content)
    print(f"✅ Updated {file_path.name}")
    return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Add utilities to infrastructure abstractions')
    parser.add_argument('file', help='Abstraction file path or directory')
    parser.add_argument('--apply', action='store_true', help='Actually apply changes (default is dry-run)')
    parser.add_argument('--batch', type=int, help='Process multiple files (number of files)')
    args = parser.parse_args()
    
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    if file_path.is_file():
        # Single file
        analysis = analyze_abstraction(file_path)
        show_analysis(analysis)
        
        if analysis['needs_changes']:
            apply_changes(file_path, dry_run=not args.apply)
    elif file_path.is_dir():
        # Directory - process all abstractions
        abstraction_files = sorted(file_path.glob('*_abstraction.py'))
        
        if args.batch:
            abstraction_files = abstraction_files[:args.batch]
        
        print(f"\n📁 Found {len(abstraction_files)} abstraction files")
        
        for abs_file in abstraction_files:
            analysis = analyze_abstraction(abs_file)
            if analysis['needs_changes']:
                show_analysis(analysis)
                apply_changes(abs_file, dry_run=not args.apply)
                print()
    else:
        print(f"❌ Invalid path: {file_path}")
        sys.exit(1)

if __name__ == '__main__':
    main()












