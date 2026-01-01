#!/usr/bin/env python3
"""
Remove path manipulation from test files.

This script removes all sys.path manipulation and path calculations
from test files, since pytest.ini now handles pythonpath configuration.

Usage:
    python3 scripts/remove_path_manipulation.py
"""

import os
import re
import sys
from pathlib import Path

# Project root
project_root = Path(__file__).parent.parent
tests_dir = project_root / 'tests'

def remove_path_manipulation(filepath: Path) -> tuple[bool, str]:
    """
    Remove path manipulation from a test file.
    
    Returns:
        (changed, message) tuple
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        new_lines = []
        i = 0
        removed_sections = []
        
        while i < len(lines):
            line = lines[i]
            
            # Skip path manipulation blocks
            # Pattern 1: Module-level path setup
            if any(pattern in line for pattern in [
                '# Add project root to path',
                '# Calculate project root',
                '# Use conftest',
                'project_root = os.path.abspath',
                'project_root_path = os.path.abspath',
                '_test_file_dir = os.path.dirname',
            ]):
                # Skip this line and related lines
                removed_sections.append(f"Removed: {line.strip()}")
                i += 1
                # Skip continuation lines
                while i < len(lines) and (
                    lines[i].strip().startswith('#') or
                    'os.path' in lines[i] or
                    'sys.path' in lines[i] or
                    'project_root' in lines[i] or
                    'project_root_path' in lines[i] or
                    not lines[i].strip() or
                    lines[i].strip() == 'if project_root not in sys.path:' or
                    lines[i].strip() == 'sys.path.insert(0, project_root)'
                ):
                    if lines[i].strip() and not lines[i].strip().startswith('#'):
                        removed_sections.append(f"  Also removed: {lines[i].strip()}")
                    i += 1
                continue
            
            # Pattern 2: sys.path.insert calls
            if 'sys.path.insert' in line and 'project_root' in line:
                removed_sections.append(f"Removed: {line.strip()}")
                i += 1
                continue
            
            # Pattern 3: Path checks in fixtures
            if 'if project_root not in sys.path:' in line:
                # Skip the if block
                removed_sections.append(f"Removed path check: {line.strip()}")
                i += 1
                # Skip the sys.path.insert line
                if i < len(lines) and 'sys.path.insert' in lines[i]:
                    i += 1
                continue
            
            # Pattern 4: Import sys/os just for path manipulation
            # Keep imports if they're used elsewhere, but we'll check later
            new_lines.append(line)
            i += 1
        
        # Clean up unused imports
        content = '\n'.join(new_lines)
        
        # Remove sys import if only used for path manipulation
        if 'import sys' in content:
            # Check if sys is used elsewhere
            sys_usage = re.findall(r'\bsys\.(?!path)', content)
            if not sys_usage:
                content = re.sub(r'^import sys\s*$', '', content, flags=re.MULTILINE)
                content = re.sub(r'^\s*import sys\s*$', '', content, flags=re.MULTILINE)
        
        # Remove os import if only used for path manipulation
        if 'import os' in content:
            # Check if os is used elsewhere (not just os.path)
            os_usage = re.findall(r'\bos\.(?!path\.|path\s)', content)
            if not os_usage:
                # But keep if used in fixtures for project_root_path
                if 'os.path' not in content or 'project_root_path' in content:
                    # Keep it - might be needed
                    pass
        
        # Clean up multiple blank lines
        content = re.sub(r'\n\n\n+', '\n\n', content)
        
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            return True, f"Removed path manipulation: {', '.join(removed_sections[:3])}"
        
        return False, "No changes needed"
        
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Main function."""
    print("Removing path manipulation from test files...")
    print(f"Scanning: {tests_dir}")
    print()
    
    test_files = list(tests_dir.rglob('test_*.py'))
    print(f"Found {len(test_files)} test files")
    print()
    
    changed = 0
    errors = []
    
    for test_file in test_files:
        # Skip if in archive
        if 'archive' in str(test_file):
            continue
        
        changed_file, message = remove_path_manipulation(test_file)
        if changed_file:
            changed += 1
            print(f"✅ {test_file.relative_to(project_root)}")
            if message:
                print(f"   {message}")
        elif 'Error' in message:
            errors.append((test_file, message))
    
    print()
    print(f"✅ Updated {changed} files")
    if errors:
        print(f"❌ {len(errors)} errors:")
        for filepath, error in errors[:5]:
            print(f"   {filepath.relative_to(project_root)}: {error}")
    
    print()
    print("Next steps:")
    print("1. Review the changes")
    print("2. Run tests to verify: pytest tests/layer_4_business_enablement/compliance/ -v")
    print("3. If tests pass, commit the changes")

if __name__ == '__main__':
    main()

