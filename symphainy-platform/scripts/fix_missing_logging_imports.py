#!/usr/bin/env python3
"""
Surgical script to find and fix missing logging imports in Public Works Foundation adapters.

WHAT: Find adapters that use logging.getLogger() but don't import logging
HOW: Scan adapter files, detect usage without import, add import statement

This script is narrowly focused on:
- Only Public Works Foundation infrastructure adapters
- Only files that use logging.getLogger() without import logging
- Only adding import logging (no other changes)
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Target directory - only Public Works Foundation adapters
ADAPTER_DIR = Path(__file__).parent.parent / "foundations" / "public_works_foundation" / "infrastructure_adapters"

# Pattern to detect logging usage
LOGGING_USAGE_PATTERN = re.compile(r'\blogging\.getLogger\b')
MODULE_LOGGER_PATTERN = re.compile(r'^logger\s*=\s*logging\.getLogger')

# Pattern to detect existing import
IMPORT_LOGGING_PATTERN = re.compile(r'^import\s+logging\s*$|^from\s+logging\s+import')

def has_logging_usage(content: str) -> bool:
    """Check if file uses logging.getLogger()."""
    return bool(LOGGING_USAGE_PATTERN.search(content) or MODULE_LOGGER_PATTERN.search(content))

def has_logging_import(content: str) -> bool:
    """Check if file already imports logging."""
    for line in content.split('\n'):
        if IMPORT_LOGGING_PATTERN.match(line.strip()):
            return True
    return False

def find_import_insertion_point(lines: List[str]) -> int:
    """
    Find the best place to insert 'import logging'.
    
    Strategy:
    1. After standard library imports (os, sys, json, datetime, typing)
    2. Before third-party imports (try/except blocks)
    3. After docstring and before any imports
    """
    # Find the end of standard library imports
    stdlib_imports = ['os', 'sys', 'json', 'datetime', 'typing', 'pathlib', 're', 'asyncio', 'time']
    last_stdlib_import = -1
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            continue
        
        # Skip docstrings
        if stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        
        # Check if it's a standard library import
        if stripped.startswith('import ') or stripped.startswith('from '):
            # Extract module name
            if stripped.startswith('import '):
                module = stripped.split()[1].split('.')[0]
            else:  # from ... import
                module = stripped.split()[1].split('.')[0]
            
            if module in stdlib_imports:
                last_stdlib_import = i
            else:
                # Found non-stdlib import - insert before this
                if last_stdlib_import >= 0:
                    return last_stdlib_import + 1
                else:
                    # No stdlib imports found, insert before first import
                    return i
    
    # If we get here, insert after the last stdlib import or at line 1
    if last_stdlib_import >= 0:
        return last_stdlib_import + 1
    
    # Find first non-empty, non-comment, non-docstring line
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
            return i
    
    return 1  # Default: insert at line 1

def fix_file(file_path: Path) -> Tuple[bool, str]:
    """
    Fix a single file by adding import logging if needed.
    
    Returns:
        (success: bool, message: str)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file uses logging
        if not has_logging_usage(content):
            return (False, "No logging usage found")
        
        # Check if file already imports logging
        if has_logging_import(content):
            return (False, "Already has logging import")
        
        # Split into lines
        lines = content.split('\n')
        
        # Find insertion point
        insert_line = find_import_insertion_point(lines)
        
        # Insert import logging
        lines.insert(insert_line, 'import logging')
        
        # Write back
        new_content = '\n'.join(lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return (True, f"Added 'import logging' at line {insert_line + 1}")
    
    except Exception as e:
        return (False, f"Error: {str(e)}")

def main():
    """Main execution."""
    # Check for --yes flag
    auto_yes = '--yes' in sys.argv or '-y' in sys.argv
    
    print("=" * 70)
    print("Surgical Script: Fix Missing Logging Imports")
    print("=" * 70)
    print(f"\nTarget directory: {ADAPTER_DIR}")
    print(f"Directory exists: {ADAPTER_DIR.exists()}\n")
    
    if not ADAPTER_DIR.exists():
        print(f"❌ Error: Directory not found: {ADAPTER_DIR}")
        return 1
    
    # Find all Python files
    python_files = list(ADAPTER_DIR.rglob('*.py'))
    print(f"Found {len(python_files)} Python files\n")
    
    # Analyze files
    files_to_fix = []
    files_skipped = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if has_logging_usage(content) and not has_logging_import(content):
                files_to_fix.append(file_path)
            else:
                reason = "No logging usage" if not has_logging_usage(content) else "Already has import"
                files_skipped.append((file_path, reason))
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
    
    # Report findings
    print(f"📋 Analysis Results:")
    print(f"   Files that need fixing: {len(files_to_fix)}")
    print(f"   Files skipped: {len(files_skipped)}\n")
    
    if not files_to_fix:
        print("✅ No files need fixing!")
        return 0
    
    # Show files that will be fixed
    print("📝 Files that will be fixed:")
    for file_path in files_to_fix:
        rel_path = file_path.relative_to(ADAPTER_DIR.parent.parent.parent)
        print(f"   - {rel_path}")
    print()
    
    # Ask for confirmation (unless --yes flag)
    if not auto_yes:
        response = input("Proceed with fixes? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("❌ Aborted by user")
            return 1
    else:
        print("🔧 Auto-confirmed (--yes flag provided)\n")
    
    # Fix files
    print("\n🔧 Applying fixes...\n")
    fixed_count = 0
    error_count = 0
    
    for file_path in files_to_fix:
        rel_path = file_path.relative_to(ADAPTER_DIR.parent.parent.parent)
        success, message = fix_file(file_path)
        
        if success:
            print(f"✅ {rel_path}: {message}")
            fixed_count += 1
        else:
            print(f"⚠️  {rel_path}: {message}")
            error_count += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print(f"   ✅ Fixed: {fixed_count}")
    print(f"   ⚠️  Errors: {error_count}")
    print("=" * 70)
    
    return 0 if error_count == 0 else 1

if __name__ == "__main__":
    exit(main())

