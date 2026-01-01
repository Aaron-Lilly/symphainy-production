#!/usr/bin/env python3
"""
Surgical script to find and fix missing logging imports in Public Works Foundation abstractions.

WHAT: Find abstractions that use logging.getLogger() but don't import logging
HOW: Scan abstraction files, detect usage without import, add import statement
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Target directory - Public Works Foundation abstractions
ABSTRACTION_DIR = Path(__file__).parent.parent / "foundations" / "public_works_foundation" / "infrastructure_abstractions"

# Patterns
LOGGING_USAGE_PATTERN = re.compile(r'\blogging\.getLogger\b')
MODULE_LOGGER_PATTERN = re.compile(r'^logger\s*=\s*logging\.getLogger')
IMPORT_LOGGING_PATTERN = re.compile(r'^import\s+logging\s*$|^from\s+logging\s+import')

def has_logging_usage(content: str) -> bool:
    return bool(LOGGING_USAGE_PATTERN.search(content) or MODULE_LOGGER_PATTERN.search(content))

def has_logging_import(content: str) -> bool:
    for line in content.split('\n'):
        if IMPORT_LOGGING_PATTERN.match(line.strip()):
            return True
    return False

def find_import_insertion_point(lines: List[str]) -> int:
    stdlib_imports = ['os', 'sys', 'json', 'datetime', 'typing', 'pathlib', 're', 'asyncio', 'time']
    last_stdlib_import = -1
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        if stripped.startswith('import ') or stripped.startswith('from '):
            if stripped.startswith('import '):
                module = stripped.split()[1].split('.')[0]
            else:
                module = stripped.split()[1].split('.')[0]
            if module in stdlib_imports:
                last_stdlib_import = i
            else:
                if last_stdlib_import >= 0:
                    return last_stdlib_import + 1
                else:
                    return i
    if last_stdlib_import >= 0:
        return last_stdlib_import + 1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
            return i
    return 1

def fix_file(file_path: Path) -> Tuple[bool, str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if not has_logging_usage(content):
            return (False, "No logging usage found")
        if has_logging_import(content):
            return (False, "Already has logging import")
        lines = content.split('\n')
        insert_line = find_import_insertion_point(lines)
        lines.insert(insert_line, 'import logging')
        new_content = '\n'.join(lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return (True, f"Added 'import logging' at line {insert_line + 1}")
    except Exception as e:
        return (False, f"Error: {str(e)}")

def main():
    auto_yes = '--yes' in sys.argv or '-y' in sys.argv
    print("=" * 70)
    print("Surgical Script: Fix Missing Logging Imports (Abstractions)")
    print("=" * 70)
    print(f"\nTarget directory: {ABSTRACTION_DIR}")
    print(f"Directory exists: {ABSTRACTION_DIR.exists()}\n")
    
    if not ABSTRACTION_DIR.exists():
        print(f"❌ Error: Directory not found: {ABSTRACTION_DIR}")
        return 1
    
    python_files = list(ABSTRACTION_DIR.rglob('*.py'))
    print(f"Found {len(python_files)} Python files\n")
    
    files_to_fix = []
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if has_logging_usage(content) and not has_logging_import(content):
                files_to_fix.append(file_path)
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
    
    print(f"📋 Analysis Results:")
    print(f"   Files that need fixing: {len(files_to_fix)}\n")
    
    if not files_to_fix:
        print("✅ No files need fixing!")
        return 0
    
    print("📝 Files that will be fixed:")
    for file_path in files_to_fix:
        rel_path = file_path.relative_to(ABSTRACTION_DIR.parent.parent.parent)
        print(f"   - {rel_path}")
    print()
    
    if not auto_yes:
        response = input("Proceed with fixes? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("❌ Aborted by user")
            return 1
    else:
        print("🔧 Auto-confirmed (--yes flag provided)\n")
    
    print("\n🔧 Applying fixes...\n")
    fixed_count = 0
    error_count = 0
    
    for file_path in files_to_fix:
        rel_path = file_path.relative_to(ABSTRACTION_DIR.parent.parent.parent)
        success, message = fix_file(file_path)
        if success:
            print(f"✅ {rel_path}: {message}")
            fixed_count += 1
        else:
            print(f"⚠️  {rel_path}: {message}")
            error_count += 1
    
    print("\n" + "=" * 70)
    print("Summary:")
    print(f"   ✅ Fixed: {fixed_count}")
    print(f"   ⚠️  Errors: {error_count}")
    print("=" * 70)
    
    return 0 if error_count == 0 else 1

if __name__ == "__main__":
    exit(main())

