#!/usr/bin/env python3
"""
Fix Common Broken Patterns in Abstraction Files

Fixes the most common broken patterns found across abstraction files:
1. Broken exception handlers with incorrect indentation
2. Orphaned telemetry comments
3. Duplicate raise statements
"""

import re
from pathlib import Path
from typing import Tuple


def fix_broken_exception_handlers(content: str) -> str:
    """Fix broken exception handlers with incorrect indentation."""
    # Pattern: except block with incorrectly indented logger.error
    pattern = re.compile(
        r'(\s+except Exception as e:\s*\n)\s+# Use error handler with telemetry\s*\n\s+(self\.logger\.error\([^)]+\))\s*\n\s+(raise[^\n]*)',
        re.MULTILINE
    )
    content = pattern.sub(r'\1            \2\n            \3', content)
    
    # Pattern: except block with just incorrectly indented logger.error (no comment)
    pattern2 = re.compile(
        r'(\s+except Exception as e:\s*\n)\s+(self\.logger\.error\([^)]+\))\s*\n\s+(raise[^\n]*)',
        re.MULTILINE
    )
    content = pattern2.sub(r'\1            \2\n            \3', content)
    
    return content


def remove_orphaned_comments(content: str) -> str:
    """Remove orphaned telemetry comments."""
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        # Skip orphaned telemetry comments
        if re.search(r'Record platform operation event|Full telemetry handled', line):
            # Check if it's a standalone comment
            if line.strip().startswith('#'):
                # Check if next line is return or except
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('return') or next_line.startswith('except'):
                        continue  # Skip this comment line
        
        new_lines.append(line)
    
    return '\n'.join(new_lines)


def fix_duplicate_raises(content: str) -> str:
    """Remove duplicate raise statements."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for raise statement
        if re.match(r'^\s+raise\s*#.*Re-raise', line):
            new_lines.append(line)
            i += 1
            
            # Check if next lines are also raise statements
            while i < len(lines):
                next_line = lines[i]
                if re.match(r'^\s+raise\s*#.*Re-raise', next_line):
                    # Skip duplicate
                    i += 1
                    continue
                elif next_line.strip() == '' or next_line.strip().startswith('#'):
                    # Skip empty lines and comments
                    i += 1
                    continue
                else:
                    break
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def fix_file(file_path: Path) -> Tuple[bool, str]:
    """Fix common patterns in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        content = fix_broken_exception_handlers(content)
        content = remove_orphaned_comments(content)
        content = fix_duplicate_raises(content)
        
        # Clean up multiple blank lines
        content = re.sub(r'\n\n\n+', '\n\n', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Verify syntax
        try:
            compile(content, str(file_path), 'exec')
            return (content != original_content), "Fixed and verified" if content != original_content else "Verified"
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Fix common patterns in all abstraction files."""
    base_dir = Path(__file__).parent.parent.parent
    abstracts_path = base_dir / "symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions"
    
    abstraction_files = list(abstracts_path.glob("*.py"))
    abstraction_files = [f for f in abstraction_files if not f.name.startswith("__")]
    
    print(f"🔧 Fixing common patterns in {len(abstraction_files)} files...\n")
    
    fixed_count = 0
    verified_count = 0
    error_count = 0
    
    for file_path in sorted(abstraction_files):
        fixed, message = fix_file(file_path)
        if "Syntax error" in message:
            print(f"❌ {file_path.name}: {message}")
            error_count += 1
        elif fixed:
            print(f"✅ {file_path.name}: {message}")
            fixed_count += 1
        else:
            verified_count += 1
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Fixed: {fixed_count}")
    print(f"  ✓  Verified: {verified_count}")
    print(f"  ❌ Errors: {error_count}")


if __name__ == "__main__":
    main()





