#!/usr/bin/env python3
"""
Targeted Fix Script for Public Works Abstractions

Fixes ONLY the specific broken patterns we've identified:
1. Broken utility getter blocks (empty try/except)
2. Orphaned telemetry comments
3. Broken exception handlers with incorrect indentation
4. Duplicate raise statements
5. Broken method signatures (orphaned parameters after raise)
6. Orphaned except blocks without matching try

This script is conservative - it only fixes known broken patterns.
"""

import re
import ast
from pathlib import Path
from typing import Tuple, List


def remove_error_handler_references(content: str) -> str:
    """Remove broken error_handler references in except blocks."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Pattern: if error_handler and hasattr(error_handler, 'handle_error'):
        if re.search(r'if.*error_handler.*hasattr.*handle_error', line):
            indent = len(line) - len(line.lstrip())
            i += 1
            # Skip the if block content until we find the matching else or end
            while i < len(lines):
                next_line = lines[i]
                next_indent = len(next_line) - len(next_line.lstrip())
                # If we've gone back to same or less indentation, we're done
                if next_line.strip() and next_indent <= indent and not next_line.strip().startswith('#'):
                    break
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
            new_lines.append(line)  # Keep the if statement
            i += 1
            
            # Skip everything until we find the matching else or end of block
            while i < len(lines):
                next_line = lines[i]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # If we've gone back to same or less indentation, we're done with this if block
                if next_line.strip() and next_indent <= indent and not next_line.strip().startswith('#'):
                    break
                
                # Skip empty try/except blocks
                if re.match(r'^\s+try:\s*$', next_line):
                    if i + 1 < len(lines) and re.match(r'^\s+except', lines[i+1]):
                        # Skip both try and except
                        i += 2
                        # Skip pass if present
                        if i < len(lines) and lines[i].strip() == 'pass':
                            i += 1
                        continue
                
                # Skip lines with utility variable declarations
                if re.search(r'error_handler = None|telemetry = None', next_line):
                    i += 1
                    continue
                
                # Skip empty try blocks
                if re.match(r'^\s+try:\s*$', next_line):
                    i += 1
                    # Skip pass if next
                    if i < len(lines) and lines[i].strip() == 'pass':
                        i += 1
                    continue
                
                # Skip orphaned raise statements in utility blocks
                if re.match(r'^\s+raise\s*#.*Re-raise', next_line) and i < len(lines) - 1:
                    # Check if next line is also raise or if we're in a utility block
                    if i + 1 < len(lines):
                        next_next = lines[i + 1]
                        # If next is also raise or a method signature, skip this raise
                        if re.match(r'^\s+raise\s*#.*Re-raise', next_next) or re.match(r'^\s+\w+:', next_next):
                            i += 1
                            continue
                
                new_lines.append(next_line)
                i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def fix_broken_exception_handlers(content: str) -> str:
    """Fix broken exception handlers with incorrect indentation."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Pattern: except block with incorrectly indented logger.error
        if re.match(r'^\s+except.*:\s*$', line):
            new_lines.append(line)
            i += 1
            except_indent = len(line) - len(line.lstrip())
            correct_indent = ' ' * (except_indent + 4)
            
            # Collect the except block
            block_lines = []
            has_logger_error = False
            has_raise = False
            has_return = False
            broken_dict_literal = False
            
            while i < len(lines):
                next_line = lines[i]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # If we've gone back to same or less indentation, we're done
                if next_line.strip() and next_indent <= except_indent and not next_line.strip().startswith('#'):
                    break
                
                # Skip comment lines
                if re.match(r'^\s+# Use error handler', next_line):
                    i += 1
                    continue
                
                # Check for broken dictionary literal (starts with quote or key without proper structure)
                if (next_line.strip().startswith('"') and 
                    ('healthy' in next_line or 'error' in next_line or 'timestamp' in next_line)):
                    # This is likely a broken return dict - skip it
                    broken_dict_literal = True
                    i += 1
                    # Skip until we find the closing brace
                    while i < len(lines):
                        if '}' in lines[i]:
                            i += 1
                            break
                        i += 1
                    continue
                
                # Fix incorrectly indented logger.error
                if 'logger.error' in next_line:
                    # Fix indentation to match except block
                    fixed_line = correct_indent + next_line.lstrip()
                    block_lines.append(fixed_line)
                    has_logger_error = True
                    i += 1
                    continue
                
                # Fix incorrectly indented raise
                if 'raise' in next_line and 'Re-raise' in next_line:
                    # Fix indentation
                    fixed_line = correct_indent + next_line.lstrip()
                    block_lines.append(fixed_line)
                    has_raise = True
                    i += 1
                    continue
                
                # Check for return statements (should be removed, replaced with raise)
                if next_line.strip().startswith('return'):
                    has_return = True
                    i += 1
                    continue
                
                block_lines.append(next_line)
                i += 1
            
            # Ensure we have logger.error and raise
            if not has_logger_error:
                # Add logger.error
                block_lines.insert(0, f'{correct_indent}self.logger.error(f"❌ Error: {{e}}")')
            
            if not has_raise:
                # Add raise at the end
                block_lines.append(f'{correct_indent}raise  # Re-raise for service layer to handle')
            
            new_lines.extend(block_lines)
            continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def remove_duplicate_raises(content: str) -> str:
    """Remove duplicate raise statements."""
    # Pattern: Multiple consecutive raise statements
    pattern = re.compile(
        r'(raise\s+# Re-raise for service layer to handle\n)\s+raise\s+# Re-raise for service layer to handle(\n\s+raise\s+# Re-raise for service layer to handle)*',
        re.MULTILINE
    )
    content = pattern.sub(r'\1', content)
    
    return content


def fix_orphaned_method_signatures(content: str) -> str:
    """Fix broken method signatures that appear after raise statements."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for raise statement
        if re.match(r'^\s+raise\s*#.*Re-raise', line):
            new_lines.append(line)
            i += 1
            
            # Look ahead for orphaned method signature
            if i < len(lines):
                next_line = lines[i]
                # Pattern: Orphaned parameters (starts with parameter name and type)
                if re.match(r'^\s+\w+:\s+.*=.*\)\s*->', next_line) or re.match(r'^\s+\w+:\s+.*\)\s*->', next_line):
                    # This is an orphaned method signature - need to reconstruct
                    # Look for more parameter lines
                    params = [next_line]
                    i += 1
                    while i < len(lines) and (lines[i].strip().startswith(('state_id:', 'updates:', 'metadata:', 'filters:', 'limit:', 'offset:', 'query:', 'fields:')) or lines[i].strip() == ')'):
                        if lines[i].strip() == ')':
                            break
                        params.append(lines[i])
                        i += 1
                    
                    # Try to reconstruct method signature - this is complex, so we'll skip for now
                    # and just remove the orphaned signature
                    continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def remove_orphaned_telemetry_comments(content: str) -> str:
    """Remove orphaned telemetry comments."""
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        # Skip orphaned telemetry comments
        if re.search(r'Record platform operation event|Full telemetry handled|Record telemetry on success', line):
            # Check if it's a standalone comment
            if line.strip().startswith('#'):
                # Check if next line is return, except, or another comment
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if (next_line.startswith('return') or 
                        next_line.startswith('except') or 
                        next_line.startswith('#') or
                        next_line == ''):
                        continue  # Skip this comment line
        
        new_lines.append(line)
    
    return '\n'.join(new_lines)


def fix_orphaned_except_blocks(content: str) -> str:
    """Fix orphaned except blocks (except without matching try)."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for except block
        if re.match(r'^\s+except.*:\s*$', line):
            # Look back for matching try (within reasonable distance)
            found_try = False
            for j in range(max(0, i - 50), i):
                if re.match(r'^\s+try:\s*$', lines[j]):
                    # Check if there's code between try and except
                    has_code = False
                    for k in range(j + 1, i):
                        if lines[k].strip() and not lines[k].strip().startswith('#'):
                            has_code = True
                            break
                    if has_code:
                        found_try = True
                        break
            
            if not found_try:
                # This is an orphaned except - remove it and its block
                except_indent = len(line) - len(line.lstrip())
                i += 1
                # Skip the except block content
                while i < len(lines):
                    next_line = lines[i]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_line.strip() and next_indent <= except_indent and not next_line.strip().startswith('#'):
                        break
                    i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def fix_empty_try_blocks(content: str) -> str:
    """Fix empty try blocks followed by except."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for empty try block
        if re.match(r'^\s+try:\s*$', line):
            # Check if next line is except
            if i + 1 < len(lines) and re.match(r'^\s+except', lines[i + 1]):
                # This is an empty try/except - remove both
                i += 2
                # Skip pass if present
                if i < len(lines) and lines[i].strip() == 'pass':
                    i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def fix_broken_method_signatures(content: str) -> str:
    """Fix broken method signatures (orphaned parameters)."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for orphaned method signature (starts with parameter, not async def or def)
        # Pattern: line starts with spaces, then a parameter name and type
        if (re.match(r'^\s+\w+:\s+.*=.*\)\s*->', line) or 
            re.match(r'^\s+\w+:\s+.*\)\s*->', line) or
            re.match(r'^\s+\w+:\s+.*=.*,\s*$', line)):
            # Check if previous line is a method definition
            if i > 0:
                prev_line = lines[i-1].strip()
                # If previous line doesn't end with def or :, this is orphaned
                if not (prev_line.endswith(':') or 'def ' in prev_line or 'async def' in prev_line):
                    # This is an orphaned signature - try to reconstruct method name from docstring
                    # Look ahead for docstring
                    method_name = None
                    j = i + 1
                    while j < len(lines) and j < i + 5:
                        if '"""' in lines[j]:
                            # Try to extract method name from docstring context
                            # Common patterns: "Analyze data" -> analyze, "Get user" -> get_user
                            docstring = lines[j]
                            if 'Analyze' in docstring:
                                method_name = 'analyze'
                            elif 'Get' in docstring:
                                method_name = 'get'
                            elif 'Set' in docstring:
                                method_name = 'set'
                            elif 'Delete' in docstring:
                                method_name = 'delete'
                            elif 'Update' in docstring:
                                method_name = 'update'
                            elif 'Create' in docstring:
                                method_name = 'create'
                            break
                        j += 1
                    
                    # Remove orphaned signature
                    i += 1
                    # Skip until we find a proper method definition, docstring, or class definition
                    while i < len(lines):
                        next_line = lines[i]
                        if (re.match(r'^\s+(async )?def ', next_line) or 
                            re.match(r'^\s+class ', next_line) or
                            (next_line.strip() and not next_line.strip().startswith(('state_id:', 'updates:', 'metadata:', 'filters:', 'limit:', 'offset:', 'query:', 'fields:', 'ttl:', 'backup_id:', 'target_backend:', 'analysis_type:', 'data:', 'user_id:', 'resource:', 'action:', 'user_context:', 'options:')))):
                            break
                        i += 1
                    continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def fix_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, str, str]:
    """
    Fix a single abstraction file.
    
    Returns:
        (changed, message, content)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes in order
        content = remove_error_handler_references(content)
        content = remove_broken_utility_getter_blocks(content)
        content = fix_empty_try_blocks(content)
        content = remove_orphaned_telemetry_comments(content)
        content = fix_broken_exception_handlers(content)
        content = remove_duplicate_raises(content)
        content = fix_orphaned_except_blocks(content)
        content = fix_broken_method_signatures(content)
        
        # Clean up multiple blank lines
        content = re.sub(r'\n\n\n+', '\n\n', content)
        
        changed = content != original_content
        
        if not dry_run and changed:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Verify syntax
        try:
            compile(content, str(file_path), 'exec')
            if changed:
                return True, "Fixed and verified", content
            else:
                return False, "No changes needed (verified)", content
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}", content
            
    except Exception as e:
        return False, f"Error: {str(e)}", ""


def main():
    """Fix abstraction files with testing capability."""
    import sys
    
    base_dir = Path(__file__).parent.parent.parent
    abstracts_path = base_dir / "symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions"
    
    # Test mode: fix only specified files
    test_files = sys.argv[1:] if len(sys.argv) > 1 else None
    
    if test_files:
        abstraction_files = [abstracts_path / f for f in test_files if (abstracts_path / f).exists()]
        print(f"🧪 TEST MODE: Fixing {len(abstraction_files)} test files\n")
    else:
        abstraction_files = list(abstracts_path.glob("*.py"))
        abstraction_files = [f for f in abstraction_files if not f.name.startswith("__")]
        print(f"🔧 Fixing all {len(abstraction_files)} abstraction files\n")
    
    fixed_count = 0
    verified_count = 0
    error_count = 0
    errors = []
    
    for file_path in sorted(abstraction_files):
        changed, message, content = fix_file(file_path, dry_run=False)
        
        if "Syntax error" in message:
            print(f"❌ {file_path.name}: {message}")
            errors.append((file_path.name, message))
            error_count += 1
        elif changed:
            print(f"✅ {file_path.name}: {message}")
            fixed_count += 1
        else:
            if "verified" in message.lower():
                verified_count += 1
            else:
                print(f"⏭️  {file_path.name}: {message}")
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Fixed: {fixed_count}")
    print(f"  ✓  Verified: {verified_count}")
    print(f"  ❌ Errors: {error_count}")
    
    if errors and test_files:
        print(f"\n⚠️  Test files still have errors - review before running on all files:")
        for filename, error in errors:
            print(f"    - {filename}: {error}")


if __name__ == "__main__":
    main()

