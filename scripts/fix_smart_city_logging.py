#!/usr/bin/env python3
"""
Fix Smart City Logging Anti-Patterns

Removes direct logging imports and calls, replaces with DI Container access.
"""

import re
from pathlib import Path
from typing import List, Tuple

def fix_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Fix logging anti-patterns in a file."""
    changes = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        modified = False
        new_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            # Skip if we're removing this line
            if skip_next:
                skip_next = False
                continue
            
            # Remove standalone 'import logging' (not in TYPE_CHECKING)
            if line.strip() == 'import logging' and not 'TYPE_CHECKING' in '\n'.join(lines[max(0, i-5):i]):
                # Check if it's actually used
                remaining_content = '\n'.join(lines[i+1:])
                if 'logging.getLogger' in remaining_content or 'logging.' in remaining_content:
                    # It's used, we'll replace it
                    modified = True
                    changes.append(f"Line {i+1}: Removed 'import logging'")
                    continue  # Skip this line
                else:
                    # Not used, just remove it
                    modified = True
                    changes.append(f"Line {i+1}: Removed unused 'import logging'")
                    continue
            
            # Replace logging.getLogger() calls in __init__ methods
            if 'logging.getLogger' in line and '__init__' in '\n'.join(lines[max(0, i-10):i+1]):
                # Find the pattern: self.logger = logging.getLogger(...)
                match = re.search(r'self\.logger\s*=\s*logging\.getLogger\(([^)]+)\)', line)
                if match:
                    # Get the logger name from the match
                    logger_name = match.group(1)
                    # Replace with DI Container access
                    new_line = line.replace(
                        f'self.logger = logging.getLogger({logger_name})',
                        f'self.logger = self.service.di_container.get_logger({logger_name})'
                    )
                    new_lines.append(new_line)
                    modified = True
                    changes.append(f"Line {i+1}: Replaced logging.getLogger() with DI Container access")
                    continue
            
            # Replace other logging.getLogger() patterns
            if 'logging.getLogger' in line and 'self.logger' in line:
                new_line = re.sub(
                    r'logging\.getLogger\(([^)]+)\)',
                    r'self.service.di_container.get_logger(\1)',
                    line
                )
                if new_line != line:
                    new_lines.append(new_line)
                    modified = True
                    changes.append(f"Line {i+1}: Replaced logging.getLogger() with DI Container access")
                    continue
            
            new_lines.append(line)
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            return True, changes
        
        return False, []
    
    except Exception as e:
        return False, [f"Error: {e}"]

def main():
    """Fix all Smart City logging violations."""
    project_root = Path(__file__).parent.parent
    smart_city_path = project_root / 'symphainy-platform' / 'backend' / 'smart_city'
    
    # Get all Python files
    python_files = list(smart_city_path.rglob('*.py'))
    
    # Exclude test files
    python_files = [f for f in python_files if 'test' not in str(f) and '__pycache__' not in str(f)]
    
    total_fixed = 0
    total_changes = 0
    
    for file_path in python_files:
        fixed, changes = fix_file(file_path)
        if fixed:
            total_fixed += 1
            total_changes += len(changes)
            print(f"✅ Fixed: {file_path.relative_to(project_root)}")
            for change in changes:
                print(f"   {change}")
    
    print(f"\n📊 Summary:")
    print(f"   Files fixed: {total_fixed}")
    print(f"   Total changes: {total_changes}")

if __name__ == '__main__':
    main()

