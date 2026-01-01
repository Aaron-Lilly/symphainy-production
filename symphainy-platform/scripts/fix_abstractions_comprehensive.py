#!/usr/bin/env python3
"""
Comprehensive Fix for Public Works Abstractions

Fixes broken code left by refactoring script and ensures architecturally compliant pattern:
- Removes empty try/except blocks
- Removes orphaned telemetry comments
- Fixes else: after except: syntax errors
- Ensures proper exception re-raising
- Removes all utility-related code
- Keeps only basic logging

Pattern: Pure infrastructure, no utilities, re-raise exceptions
"""

import re
import ast
from pathlib import Path
from typing import List, Tuple


def fix_empty_try_except(content: str) -> str:
    """Fix empty try/except blocks."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for empty try block
        if re.match(r'^\s+try:\s*$', line):
            # Check if next line is except or pass
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # If next line is except, remove the try
                if re.match(r'^\s+except', next_line):
                    i += 1
                    continue
                # If next line is pass or empty, check further
                elif next_line.strip() in ['', 'pass']:
                    # Look for except
                    j = i + 2
                    while j < len(lines) and (lines[j].strip() == '' or lines[j].strip() == 'pass'):
                        j += 1
                    if j < len(lines) and re.match(r'^\s+except', lines[j]):
                        # Remove try and pass lines
                        i = j
                        continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def fix_else_after_except(content: str) -> str:
    """Fix else: after except: syntax errors."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for except block
        if re.match(r'^\s+except.*:\s*$', line):
            new_lines.append(line)
            i += 1
            
            # Look ahead for else: after except
            while i < len(lines):
                next_line = lines[i]
                
                # Skip comments and empty lines
                if next_line.strip().startswith('#') or next_line.strip() == '':
                    new_lines.append(next_line)
                    i += 1
                    continue
                
                # If we find else: after except, remove it
                if re.match(r'^\s+else:\s*$', next_line):
                    # Skip the else: line
                    i += 1
                    # Keep the logger.error line that follows
                    if i < len(lines) and 'logger.error' in lines[i]:
                        new_lines.append(lines[i])
                        i += 1
                    continue
                
                # If we find another except or return or raise, we're done with this except block
                if (re.match(r'^\s+except', next_line) or 
                    re.match(r'^\s+return', next_line) or
                    re.match(r'^\s+raise', next_line) or
                    (next_line.strip() and not next_line.strip().startswith('#') and 
                     len(next_line) - len(next_line.lstrip()) <= len(line) - len(line.lstrip()))):
                    break
                
                new_lines.append(next_line)
                i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def remove_orphaned_telemetry_comments(content: str) -> str:
    """Remove orphaned telemetry comments."""
    # Remove lines with only telemetry comments
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        # Skip lines that are only telemetry comments
        if re.search(r'Record telemetry on success|Full telemetry handled at service layer', line):
            # Check if it's a standalone comment line
            if line.strip().startswith('#') and (i == 0 or lines[i-1].strip() == '' or lines[i-1].strip().endswith(':')):
                # Check if next line is also a comment or empty
                if i + 1 < len(lines) and (lines[i+1].strip().startswith('#') or lines[i+1].strip() == ''):
                    # Skip this line
                    continue
                # If next line is just a closing paren or similar, also skip
                if i + 1 < len(lines) and lines[i+1].strip() == ')':
                    continue
        
        new_lines.append(line)
    
    return '\n'.join(new_lines)


def remove_orphaned_closing_parens(content: str) -> str:
    """Remove orphaned closing parentheses left by removed telemetry calls."""
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        # Skip lines that are just closing parens with no context
        if line.strip() == ')' and i > 0:
            prev_line = lines[i-1].strip()
            # If previous line is a comment or empty, this is likely orphaned
            if prev_line == '' or prev_line.startswith('#'):
                # Check if there's a matching opening somewhere
                # For now, just skip standalone closing parens after comments
                continue
        
        new_lines.append(line)
    
    return '\n'.join(new_lines)


def fix_empty_utility_getter_blocks(content: str) -> str:
    """Fix empty utility getter blocks."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for utility getter pattern
        if re.search(r'if.*di_container.*get_utility', line):
            # This is the if statement, keep it but check what follows
            new_lines.append(line)
            i += 1
            
            # Look for empty try/except inside
            while i < len(lines):
                next_line = lines[i]
                indent = len(next_line) - len(next_line.lstrip())
                line_indent = len(line) - len(line.lstrip())
                
                # If we've gone back to the same or less indentation, we're done
                if next_line.strip() and indent <= line_indent and not next_line.strip().startswith('#'):
                    break
                
                # Check for empty try block
                if re.match(r'^\s+try:\s*$', next_line):
                    # Check if next is except
                    if i + 1 < len(lines) and re.match(r'^\s+except', lines[i+1]):
                        # Remove both try and except
                        i += 2
                        # Skip pass if present
                        if i < len(lines) and lines[i].strip() == 'pass':
                            i += 1
                        continue
                    # If next is pass, remove try and pass
                    elif i + 1 < len(lines) and lines[i+1].strip() == 'pass':
                        i += 2
                        continue
                
                new_lines.append(next_line)
                i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def ensure_proper_exception_handling(content: str) -> str:
    """Ensure exceptions are re-raised, not handled."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for except block
        if re.match(r'^\s+except.*:\s*$', line):
            new_lines.append(line)
            i += 1
            
            # Look for error handling in the except block
            has_raise = False
            has_logger_error = False
            block_lines = []
            
            while i < len(lines):
                next_line = lines[i]
                except_indent = len(line) - len(line.lstrip())
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # If we've gone back to same or less indentation, we're done with except block
                if next_line.strip() and next_indent <= except_indent and not next_line.strip().startswith('#'):
                    break
                
                if 'raise' in next_line:
                    has_raise = True
                if 'logger.error' in next_line:
                    has_logger_error = True
                
                block_lines.append(next_line)
                i += 1
            
            # If no raise, add one
            if block_lines and not has_raise:
                # Add logger.error if not present
                if not has_logger_error:
                    # Find a good place to add it (after comments)
                    insert_idx = 0
                    for j, bl in enumerate(block_lines):
                        if bl.strip() and not bl.strip().startswith('#'):
                            insert_idx = j
                            break
                    
                    # Add logger.error
                    indent = ' ' * (len(block_lines[insert_idx]) - len(block_lines[insert_idx].lstrip()))
                    block_lines.insert(insert_idx, f'{indent}self.logger.error(f"❌ Error: {{e}}")')
                
                # Add raise at the end
                if block_lines:
                    last_line = block_lines[-1]
                    indent = ' ' * (len(last_line) - len(last_line.lstrip()))
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
        
        # Step 1: Fix else: after except: syntax errors
        content = fix_else_after_except(content)
        
        # Step 2: Remove orphaned telemetry comments
        content = remove_orphaned_telemetry_comments(content)
        
        # Step 3: Remove orphaned closing parens
        content = remove_orphaned_closing_parens(content)
        
        # Step 4: Fix empty try/except blocks
        content = fix_empty_try_except(content)
        
        # Step 5: Fix empty utility getter blocks
        content = fix_empty_utility_getter_blocks(content)
        
        # Step 6: Ensure proper exception handling
        content = ensure_proper_exception_handling(content)
        
        # Step 7: Clean up multiple blank lines
        content = re.sub(r'\n\n\n+', '\n\n', content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Verify syntax
            try:
                compile(content, str(file_path), 'exec')
                return True, "Fixed and verified"
            except SyntaxError as e:
                return False, f"Fixed but syntax error: {e}"
        else:
            # Still verify syntax
            try:
                compile(content, str(file_path), 'exec')
                return False, "No changes needed (verified)"
            except SyntaxError as e:
                return False, f"Syntax error: {e}"
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Fix all abstraction files."""
    # Get project root (3 levels up from scripts/)
    base_dir = Path(__file__).parent.parent.parent
    abstracts_path = base_dir / "symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions"
    
    if not abstracts_path.exists():
        print(f"❌ Abstractions directory not found: {abstracts_path}")
        return
    
    abstraction_files = list(abstracts_path.glob("*.py"))
    abstraction_files = [f for f in abstraction_files if not f.name.startswith("__")]
    
    print(f"📁 Found {len(abstraction_files)} abstraction files")
    print(f"🔧 Fixing abstractions in: {abstracts_path}\n")
    
    fixed_count = 0
    verified_count = 0
    error_count = 0
    
    for file_path in sorted(abstraction_files):
        fixed, message = fix_file(file_path)
        if fixed:
            print(f"✅ {file_path.name}: {message}")
            fixed_count += 1
        elif "verified" in message.lower():
            print(f"✓  {file_path.name}: {message}")
            verified_count += 1
        else:
            print(f"❌ {file_path.name}: {message}")
            error_count += 1
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Fixed: {fixed_count}")
    print(f"  ✓  Verified (no changes): {verified_count}")
    print(f"  ❌ Errors: {error_count}")


if __name__ == "__main__":
    main()

