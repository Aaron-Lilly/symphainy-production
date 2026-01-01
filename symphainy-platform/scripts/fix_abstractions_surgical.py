#!/usr/bin/env python3
"""
Surgical Fix for Public Works Abstractions

Fixes broken code with precise pattern matching:
1. Removes broken utility getter blocks (empty try/except)
2. Removes orphaned telemetry code fragments
3. Fixes broken code structure (raise before try, etc.)
4. Ensures proper exception handling pattern

Target Pattern (from messaging_abstraction.py):
- NO utility getters
- NO telemetry calls
- Basic logging only
- Re-raise exceptions
"""

import re
import ast
from pathlib import Path
from typing import List, Tuple


def remove_broken_utility_getters(content: str) -> str:
    """Remove broken utility getter blocks completely."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Pattern: if self.di_container and hasattr(self.di_container, 'get_utility'):
        if re.search(r'if.*di_container.*get_utility', line):
            indent = len(line) - len(line.lstrip())
            new_lines.append(line)  # Keep the if statement
            i += 1
            
            # Skip everything until we find the matching else or end of block
            while i < len(lines):
                next_line = lines[i]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # If we've gone back to same or less indentation, we're done
                if next_line.strip() and next_indent <= indent and not next_line.strip().startswith('#'):
                    break
                
                # Skip empty try/except blocks
                if re.match(r'^\s+try:\s*$', next_line):
                    # Check if next is except
                    if i + 1 < len(lines) and re.match(r'^\s+except', lines[i+1]):
                        # Skip both
                        i += 2
                        # Skip pass if present
                        if i < len(lines) and lines[i].strip() == 'pass':
                            i += 1
                        continue
                
                # Skip lines with utility getter calls
                if re.search(r'get_utility\(["\'](telemetry|error_handler)', next_line):
                    i += 1
                    continue
                
                # Skip error_handler references in except blocks
                if 'error_handler' in next_line and 'except' in lines[max(0, i-3):i]:
                    i += 1
                    continue
                
                # Skip pass statements in utility blocks
                if next_line.strip() == 'pass' and i > 0 and 'get_utility' in lines[max(0, i-5):i]:
                    i += 1
                    continue
                
                new_lines.append(next_line)
                i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def remove_orphaned_telemetry_code(content: str) -> str:
    """Remove orphaned telemetry code fragments."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Pattern: Lines that are just telemetry call fragments
        # e.g., "service_name=self.service_name," or just ")"
        if re.search(r'Record telemetry on success|Full telemetry handled', line):
            # Skip this comment line
            i += 1
            continue
        
        # Pattern: Orphaned telemetry call parameters
        if (line.strip().startswith('service_name=') or 
            line.strip().startswith('operation=') or
            line.strip().startswith('status=') or
            line.strip().startswith('metadata=')):
            # Check if this is part of a broken telemetry call
            # Look ahead for closing paren
            j = i + 1
            found_closing = False
            while j < len(lines) and j < i + 5:
                if lines[j].strip() == ')':
                    found_closing = True
                    break
                if lines[j].strip() and not lines[j].strip().startswith(('service_name=', 'operation=', 'status=', 'metadata=', '#')):
                    break
                j += 1
            
            if found_closing:
                # Skip all these lines
                i = j + 1
                continue
        
        # Pattern: Standalone closing paren after comments
        if line.strip() == ')' and i > 0:
            prev_line = lines[i-1].strip()
            if prev_line == '' or prev_line.startswith('#') or prev_line.endswith(('service_name=', 'operation=', 'status=', 'metadata=')):
                # Check if there's a matching opening somewhere reasonable
                # For now, skip standalone closing parens
                i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def fix_broken_code_structure(content: str) -> str:
    """Fix broken code structure (raise before try, etc.)."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Pattern: raise statement before try block
        if re.match(r'^\s+raise\s*#.*Re-raise', line):
            # Check if next line is try
            if i + 1 < len(lines) and re.match(r'^\s+try:', lines[i+1]):
                # Remove the raise statement
                i += 1
                continue
        
        # Pattern: raise statement in wrong place (not in except block)
        if re.match(r'^\s+raise\s*#.*Re-raise', line):
            # Check context - if not in except block, it might be misplaced
            # Look back for except
            found_except = False
            for j in range(max(0, i-10), i):
                if re.match(r'^\s+except', lines[j]):
                    found_except = True
                    break
            
            if not found_except:
                # This raise is misplaced, remove it
                i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def ensure_proper_exception_pattern(content: str) -> str:
    """Ensure proper exception handling pattern."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for except block
        if re.match(r'^\s+except.*:\s*$', line):
            new_lines.append(line)
            i += 1
            
            except_indent = len(line) - len(line.lstrip())
            has_logger_error = False
            has_raise = False
            block_lines = []
            
            # Collect except block content
            while i < len(lines):
                next_line = lines[i]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # If we've gone back to same or less indentation, we're done
                if next_line.strip() and next_indent <= except_indent and not next_line.strip().startswith('#'):
                    break
                
                if 'logger.error' in next_line:
                    has_logger_error = True
                if 'raise' in next_line:
                    has_raise = True
                
                block_lines.append(next_line)
                i += 1
            
            # Ensure we have logger.error and raise
            if block_lines:
                if not has_logger_error:
                    # Add logger.error after comments
                    insert_idx = 0
                    for j, bl in enumerate(block_lines):
                        if bl.strip() and not bl.strip().startswith('#'):
                            insert_idx = j
                            break
                    
                    indent = ' ' * except_indent
                    block_lines.insert(insert_idx, f'{indent}self.logger.error(f"❌ Error: {{e}}")')
                
                if not has_raise:
                    # Add raise at the end
                    indent = ' ' * except_indent
                    block_lines.append(f'{indent}raise  # Re-raise for service layer to handle')
            
            new_lines.extend(block_lines)
            continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def fix_file(file_path: Path) -> Tuple[bool, str]:
    """Fix a single abstraction file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Step 1: Remove broken utility getter blocks
        content = remove_broken_utility_getters(content)
        
        # Step 2: Remove orphaned telemetry code
        content = remove_orphaned_telemetry_code(content)
        
        # Step 3: Fix broken code structure
        content = fix_broken_code_structure(content)
        
        # Step 4: Ensure proper exception handling
        content = ensure_proper_exception_pattern(content)
        
        # Step 5: Clean up multiple blank lines
        content = re.sub(r'\n\n\n+', '\n\n', content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Verify syntax
        try:
            compile(content, str(file_path), 'exec')
            return (content != original_content), "Fixed and verified" if content != original_content else "Verified (no changes)"
        except SyntaxError as e:
            return False, f"Syntax error: {e} (line {e.lineno})"
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Fix all abstraction files."""
    base_dir = Path(__file__).parent.parent.parent
    abstracts_path = base_dir / "symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions"
    
    if not abstracts_path.exists():
        print(f"❌ Abstractions directory not found: {abstracts_path}")
        return
    
    abstraction_files = list(abstracts_path.glob("*.py"))
    abstraction_files = [f for f in abstraction_files if not f.name.startswith("__")]
    
    print(f"📁 Found {len(abstraction_files)} abstraction files")
    print(f"🔧 Surgically fixing abstractions...\n")
    
    fixed_count = 0
    verified_count = 0
    error_count = 0
    errors = []
    
    for file_path in sorted(abstraction_files):
        fixed, message = fix_file(file_path)
        if "Syntax error" in message:
            print(f"❌ {file_path.name}: {message}")
            errors.append((file_path.name, message))
            error_count += 1
        elif fixed:
            print(f"✅ {file_path.name}: {message}")
            fixed_count += 1
        else:
            print(f"✓  {file_path.name}: {message}")
            verified_count += 1
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Fixed: {fixed_count}")
    print(f"  ✓  Verified: {verified_count}")
    print(f"  ❌ Errors: {error_count}")
    
    if errors:
        print(f"\n⚠️  Files with remaining syntax errors:")
        for filename, error in errors[:10]:  # Show first 10
            print(f"    - {filename}: {error}")
        if len(errors) > 10:
            print(f"    ... and {len(errors) - 10} more")


if __name__ == "__main__":
    main()





