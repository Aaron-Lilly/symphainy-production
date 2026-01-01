#!/usr/bin/env python3
"""
Precise Fix for Public Works Abstractions

Fixes the specific pattern of damage:
1. Empty try: blocks followed by except:
2. Orphaned raise statements outside except blocks
3. Broken utility getter blocks with empty try/except
4. Orphaned telemetry code fragments

Target: Clean abstractions with proper exception handling
"""

import re
from pathlib import Path
from typing import Tuple


def fix_empty_try_except_pattern(content: str) -> str:
    """Fix empty try: followed by except: pattern."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Pattern: try: on one line, except: on next
        if re.match(r'^\s+try:\s*$', line):
            # Check if next line is except
            if i + 1 < len(lines) and re.match(r'^\s+except', lines[i+1]):
                # This is an empty try/except block - remove both
                i += 2
                # Skip any code in the except block until we find something at same or less indentation
                try_indent = len(line) - len(line.lstrip())
                while i < len(lines):
                    next_line = lines[i]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    # If we've gone back to same or less indentation, we're done
                    if next_line.strip() and next_indent <= try_indent and not next_line.strip().startswith('#'):
                        break
                    i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def fix_orphaned_raise_statements(content: str) -> str:
    """Remove raise statements that are outside except blocks."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Pattern: raise statement with comment about re-raising
        if re.match(r'^\s+raise\s*#.*Re-raise', line):
            # Check if we're in an except block
            in_except = False
            except_indent = 0
            
            # Look back for except block
            for j in range(max(0, i-20), i):
                if re.match(r'^\s+except', lines[j]):
                    in_except = True
                    except_indent = len(lines[j]) - len(lines[j].lstrip())
                    break
            
            if not in_except:
                # This raise is orphaned - remove it
                i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def remove_broken_utility_getter_blocks(content: str) -> str:
    """Remove broken utility getter blocks completely."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Pattern: if self.di_container and hasattr(self.di_container, 'get_utility'):
        if re.search(r'if.*di_container.*get_utility', line):
            indent = len(line) - len(line.lstrip())
            # Check if this block is broken (has empty try/except inside)
            # Look ahead to see if there's an empty try/except
            j = i + 1
            found_empty_try = False
            while j < len(lines) and j < i + 10:
                next_line = lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # If we've gone back to same or less indentation, we're done with this if block
                if next_line.strip() and next_indent <= indent and not next_line.strip().startswith('#'):
                    break
                
                # Check for empty try/except pattern
                if re.match(r'^\s+try:\s*$', next_line):
                    if j + 1 < len(lines) and re.match(r'^\s+except', lines[j+1]):
                        found_empty_try = True
                        break
                
                j += 1
            
            if found_empty_try:
                # This is a broken utility getter block - remove the entire if block
                # Skip until we're back at the same indentation level
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_line.strip() and next_indent <= indent and not next_line.strip().startswith('#'):
                        break
                    i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def remove_orphaned_telemetry_fragments(content: str) -> str:
    """Remove orphaned telemetry code fragments."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip telemetry comment lines
        if re.search(r'Record telemetry on success|Full telemetry handled', line):
            i += 1
            continue
        
        # Skip orphaned telemetry call parameters (standalone lines with service_name=, operation=, etc.)
        if (line.strip() and 
            (line.strip().startswith('service_name=') or 
             line.strip().startswith('operation=') or
             line.strip().startswith('status=') or
             line.strip().startswith('metadata='))):
            # Check if this is part of a broken call (followed by closing paren or another parameter)
            j = i + 1
            is_orphaned = False
            while j < len(lines) and j < i + 5:
                next_line = lines[j]
                if next_line.strip() == ')':
                    is_orphaned = True
                    break
                if (next_line.strip() and 
                    not next_line.strip().startswith(('service_name=', 'operation=', 'status=', 'metadata=', '#'))):
                    break
                j += 1
            
            if is_orphaned:
                # Skip all these lines including the closing paren
                i = j + 1
                continue
        
        # Skip standalone closing parens after comments or empty lines
        if line.strip() == ')' and i > 0:
            prev_line = lines[i-1].strip()
            if prev_line == '' or prev_line.startswith('#') or prev_line.endswith(('=', ':')):
                i += 1
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
        content = remove_broken_utility_getter_blocks(content)
        
        # Step 2: Fix empty try/except patterns
        content = fix_empty_try_except_pattern(content)
        
        # Step 3: Remove orphaned raise statements
        content = fix_orphaned_raise_statements(content)
        
        # Step 4: Remove orphaned telemetry fragments
        content = remove_orphaned_telemetry_fragments(content)
        
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
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
            
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
    print(f"🔧 Precisely fixing abstractions...\n")
    
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
            print(f"✓  {file_path.name}: {message}")
            verified_count += 1
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Fixed: {fixed_count}")
    print(f"  ✓  Verified: {verified_count}")
    print(f"  ❌ Errors: {error_count}")


if __name__ == "__main__":
    main()





