#!/usr/bin/env python3
"""
Refactor Public Works Abstractions - Remove Utility Calls

Removes utility calls from abstractions following the "utilities at service layer" pattern:
- Remove get_utility() calls
- Remove error_handler.handle_error() calls
- Remove telemetry.record_platform_operation_event() calls
- Keep basic logging
- Re-raise exceptions instead of handling them
"""

import re
import os
from pathlib import Path
from typing import List, Tuple

ABSTRACTS_DIR = Path("foundations/public_works_foundation/infrastructure_abstractions")


def remove_utility_calls(content: str) -> str:
    """Remove utility calls from abstraction code."""
    lines = content.split('\n')
    new_lines = []
    skip_until_else = False
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip utility getter lines
        if re.search(r'get_utility\(["\'](telemetry|error_handler)', line):
            # Skip this line and check if next line is if statement
            if i + 1 < len(lines) and 'if ' in lines[i + 1]:
                # Skip the if block
                i += 1
                indent = len(lines[i]) - len(lines[i].lstrip())
                while i < len(lines):
                    if lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) <= indent and not lines[i].strip().startswith('#'):
                        if lines[i].strip() in ['else:', 'elif ', 'except']:
                            break
                        if not lines[i].strip().startswith('if '):
                            break
                    i += 1
                continue
            else:
                i += 1
                continue
        
        # Remove telemetry.record_platform_operation_event calls
        if 'record_platform_operation_event' in line:
            # Skip this line
            i += 1
            continue
        
        # Remove error_handler.handle_error calls (but keep the except block structure)
        if 'error_handler.handle_error' in line or 'await error_handler.handle_error' in line:
            # Find the corresponding else block and remove it
            # Keep the basic logger.error line
            i += 1
            # Look for else: block
            while i < len(lines):
                if 'else:' in lines[i]:
                    # Skip else: and the logger.error line
                    i += 1
                    if i < len(lines) and 'logger.error' in lines[i]:
                        # Keep this line but remove utility calls
                        new_lines.append(lines[i])
                        i += 1
                    break
                i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def refactor_exception_handling(content: str) -> str:
    """Refactor exception handling to re-raise instead of returning None/False."""
    
    # Pattern 1: return None after error handling
    pattern1 = re.compile(
        r'(except Exception as e:.*?)(return None)',
        re.DOTALL
    )
    content = pattern1.sub(r'\1raise  # Re-raise for service layer to handle', content)
    
    # Pattern 2: return False after error handling
    pattern2 = re.compile(
        r'(except Exception as e:.*?)(return False)',
        re.DOTALL
    )
    content = pattern2.sub(r'\1raise  # Re-raise for service layer to handle', content)
    
    # Pattern 3: return [] after error handling
    pattern3 = re.compile(
        r'(except Exception as e:.*?)(return \[\])',
        re.DOTALL
    )
    content = pattern3.sub(r'\1raise  # Re-raise for service layer to handle', content)
    
    # Pattern 4: return {"error": ...} after error handling
    pattern4 = re.compile(
        r'(except Exception as e:.*?)(return \{"error":.*?\})',
        re.DOTALL
    )
    content = pattern4.sub(r'\1raise  # Re-raise for service layer to handle', content)
    
    return content


def clean_utility_blocks(content: str) -> str:
    """Remove entire utility-related code blocks."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip lines with utility calls
        if any(pattern in line for pattern in [
            'get_utility("telemetry")',
            'get_utility("error_handler")',
            'record_platform_operation_event',
            'error_handler.handle_error',
            'await error_handler.handle_error',
            'telemetry=telemetry'
        ]):
            # Skip this line
            i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)


def refactor_file(file_path: Path) -> Tuple[bool, str]:
    """Refactor a single abstraction file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Step 1: Remove utility getter blocks
        content = remove_utility_calls(content)
        
        # Step 2: Clean up any remaining utility blocks
        content = clean_utility_blocks(content)
        
        # Step 3: Refactor exception handling to re-raise
        content = refactor_exception_handling(content)
        
        # Step 4: Ensure time import is present if we're tracking performance
        if 'time.time()' in content and 'import time' not in content:
            # Add time import after other imports
            import_match = re.search(r'(import logging\n)', content)
            if import_match:
                content = content[:import_match.end()] + 'import time\n' + content[import_match.end():]
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Refactored"
        else:
            return False, "No changes needed"
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Refactor all abstraction files."""
    base_dir = Path(__file__).parent.parent
    abstracts_path = base_dir / ABSTRACTS_DIR
    
    if not abstracts_path.exists():
        print(f"❌ Abstractions directory not found: {abstracts_path}")
        return
    
    abstraction_files = list(abstracts_path.glob("*.py"))
    abstraction_files = [f for f in abstraction_files if not f.name.startswith("__")]
    
    print(f"📁 Found {len(abstraction_files)} abstraction files")
    print(f"🔧 Refactoring abstractions in: {abstracts_path}\n")
    
    refactored_count = 0
    skipped_count = 0
    error_count = 0
    
    for file_path in sorted(abstraction_files):
        changed, message = refactor_file(file_path)
        if changed:
            print(f"✅ {file_path.name}: {message}")
            refactored_count += 1
        elif "Error" in message:
            print(f"❌ {file_path.name}: {message}")
            error_count += 1
        else:
            print(f"⏭️  {file_path.name}: {message}")
            skipped_count += 1
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Refactored: {refactored_count}")
    print(f"  ⏭️  Skipped: {skipped_count}")
    print(f"  ❌ Errors: {error_count}")


if __name__ == "__main__":
    main()







