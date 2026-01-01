#!/usr/bin/env python3
"""
Hybrid script to update infrastructure abstractions with utilities.

This script automates:
1. Constructor updates (di_container, service_name, logger from DI)
2. Exception handler updates (error_handler and telemetry utilities)

Telemetry placement is left for manual review (needs context awareness).

Usage:
    python3 scripts/update_abstraction_utilities_hybrid.py <abstraction_file> --review
    python3 scripts/update_abstraction_utilities_hybrid.py <abstraction_file> --apply
"""

import re
import sys
import shutil
import argparse
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from difflib import unified_diff
from datetime import datetime

def find_constructor(content: str) -> Optional[Dict[str, Any]]:
    """Find the __init__ method."""
    pattern = r'def __init__\([^)]*\)[^:]*:'
    match = re.search(pattern, content)
    if not match:
        return None
    
    init_start = match.start()
    # Find the end of __init__ (next method or end of class)
    init_end = content.find('\n    def ', init_start + 1)
    if init_end == -1:
        init_end = content.find('\n    async def ', init_start + 1)
    if init_end == -1:
        init_end = content.find('\nclass ', init_start + 1)
    if init_end == -1:
        init_end = len(content)
    
    return {
        'start': init_start,
        'end': init_end,
        'content': content[init_start:init_end]
    }

def find_class_name(content: str) -> str:
    """Find the main abstraction class name (the one with Abstraction in the name)."""
    # First try to find class with "Abstraction" in name
    match = re.search(r'class (\w*Abstraction\w*)', content)
    if match:
        return match.group(1)
    # Fallback to first class
    match = re.search(r'class (\w+)', content)
    return match.group(1) if match else "Unknown"

def update_constructor(content: str, class_name: str) -> Tuple[str, bool]:
    """
    Update constructor to add di_container, service_name, and logger from DI.
    Based on the pattern from analytics_abstraction.py.
    
    Returns:
        (updated_content, was_updated)
    """
    constructor = find_constructor(content)
    if not constructor:
        return content, False
    
    constructor_content = constructor['content']
    
    # Check if already updated
    if 'self.di_container = di_container' in constructor_content:
        return content, False
    
    # Extract service name from class name
    service_name = class_name.lower().replace('abstraction', '').replace('_abstraction', '') + '_abstraction'
    
    # Find __init__ signature line
    init_line_match = re.search(r'def __init__\((.*?)\):', constructor_content)
    if not init_line_match:
        return content, False
    
    params = init_line_match.group(1)
    
    # Add di_container parameter if not present
    if 'di_container' not in params:
        if params.strip():
            # Add as last parameter
            params = params.rstrip().rstrip(',') + ', di_container=None'
        else:
            params = 'di_container=None'
    
    # Find where to insert di_container and service_name
    # Look for the last self. assignment before any logger calls
    lines = constructor_content.split('\n')
    insert_pos = len(lines)
    
    # Find the last self. assignment
    for i, line in enumerate(lines):
        if line.strip().startswith('self.') and '=' in line and 'self.logger' not in line:
            insert_pos = i + 1
    
    # Build the new lines to insert
    new_lines = []
    new_lines.append(f"        self.di_container = di_container")
    new_lines.append(f"        self.service_name = \"{service_name}\"")
    new_lines.append("")
    new_lines.append("        # Get logger from DI Container if available")
    new_lines.append("        if di_container and hasattr(di_container, 'get_logger'):")
    new_lines.append(f"            self.logger = di_container.get_logger(self.service_name)")
    new_lines.append("        else:")
    new_lines.append("            self.logger = logging.getLogger(__name__)")
    new_lines.append("")
    
    # Update the __init__ signature
    updated_init_line = f"    def __init__({params}):"
    
    # Update docstring to include di_container
    docstring_updated = False
    for i, line in enumerate(lines):
        if '"""' in line and not docstring_updated:
            # Check if di_container is already in docstring
            if 'di_container' not in constructor_content:
                # Find the Args section and add di_container
                for j in range(i, min(i+20, len(lines))):
                    if 'Args:' in lines[j]:
                        # Find where to insert
                        for k in range(j+1, min(j+15, len(lines))):
                            if lines[k].strip() and not lines[k].strip().startswith((':', '"""', 'Args:')):
                                # Insert before this line
                                lines.insert(k, f"            di_container: Dependency injection container")
                                docstring_updated = True
                                break
                        break
            break
    
    # Rebuild constructor
    new_constructor_lines = []
    found_init = False
    for i, line in enumerate(lines):
        if line.strip().startswith('def __init__'):
            new_constructor_lines.append(updated_init_line)
            found_init = True
        elif found_init and i == insert_pos:
            # Insert new lines here
            new_constructor_lines.extend(new_lines)
            new_constructor_lines.append(line)
        else:
            new_constructor_lines.append(line)
    
    # Update logger.info if it exists
    for i, line in enumerate(new_constructor_lines):
        if 'logger.info' in line and 'self.logger' not in line:
            # Replace logger.info with self.logger.info and update message
            new_constructor_lines[i] = line.replace('logger.info', 'self.logger.info')
            if '"' in line or "'" in line:
                # Update message to include checkmark
                new_constructor_lines[i] = re.sub(
                    r'(".*?")|(\'.*?\')',
                    lambda m: m.group(0).replace(m.group(0), f'"✅ {class_name} initialized"') if 'initialized' in m.group(0).lower() else m.group(0),
                    new_constructor_lines[i]
                )
    
    new_constructor = '\n'.join(new_constructor_lines)
    
    # Replace constructor in content
    new_content = content[:constructor['start']] + new_constructor + content[constructor['end']:]
    
    return new_content, True

def find_exception_handlers(content: str) -> List[Dict[str, Any]]:
    """Find all exception handlers in the file."""
    handlers = []
    # Match: except Exception as e: or except: or except SomeError as e:
    pattern = r'(\s+)except\s+(?:Exception|:|\w+Error)\s+(?:as\s+(\w+))?:'
    
    for match in re.finditer(pattern, content):
        indent = match.group(1)
        exception_var = match.group(2) if match.groups() and match.group(2) else 'e'
        handler_start = match.start()
        
        # Find the end of the exception handler block
        # Look for next except, next method, or end of method
        handler_end = content.find(f'\n{indent}except ', handler_start + 1)
        if handler_end == -1:
            handler_end = content.find('\n    async def ', handler_start + 1)
        if handler_end == -1:
            handler_end = content.find('\n    def ', handler_start + 1)
        if handler_end == -1:
            handler_end = len(content)
        
        handler_content = content[handler_start:handler_end]
        handlers.append({
            'start': handler_start,
            'end': handler_end,
            'content': handler_content,
            'indent': indent,
            'exception_var': exception_var
        })
    
    return handlers

def update_exception_handler(handler_content: str, indent: str, exception_var: str, method_name: str = "<method_name>") -> Tuple[str, bool]:
    """
    Update exception handler to add error_handler and telemetry utilities.
    Based on the pattern from analytics_abstraction.py.
    
    Returns:
        (updated_handler, was_updated)
    """
    # Check if already updated
    if 'error_handler = self.di_container.get_utility("error_handler")' in handler_content:
        return handler_content, False
    
    # Find the except line
    except_match = re.search(r'(\s+)except\s+(Exception|:|\w+Error)\s+(?:as\s+(\w+))?:', handler_content)
    if not except_match:
        return handler_content, False
    
    except_line = except_match.group(0)
    exception_type = except_match.group(2)
    if except_match.group(3):
        exception_var = except_match.group(3)
    
    # Get existing body (everything after except line)
    body_start = handler_content.find(except_line) + len(except_line)
    existing_body = handler_content[body_start:].lstrip('\n')
    
    # Find existing return statement and logger.error
    existing_return = None
    existing_logger = None
    
    for line in existing_body.split('\n'):
        stripped = line.strip()
        if stripped.startswith('return '):
            existing_return = line
        elif 'logger.error' in stripped or 'logger.warning' in stripped:
            existing_logger = line
    
    # Build new handler
    new_handler = f"""{indent}except Exception as {exception_var}:
{indent}    # Use error handler with telemetry
{indent}    error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
{indent}    telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
{indent}    if error_handler:
{indent}        await error_handler.handle_error({exception_var}, {{
{indent}            "operation": "{method_name}",
{indent}            "service": self.service_name
{indent}        }}, telemetry=telemetry)
{indent}    else:
"""
    
    # Add logger fallback
    if existing_logger:
        # Update logger to self.logger and add checkmark
        updated_logger = existing_logger.replace('logger.', 'self.logger.')
        if '❌' not in updated_logger:
            updated_logger = updated_logger.replace('error(f"', 'error(f"❌ ')
        new_handler += f"{indent}        {updated_logger.strip()}\n"
    else:
        new_handler += f'{indent}        self.logger.error(f"❌ Operation failed: {{{exception_var}}}")\n'
    
    # Add return if it exists
    if existing_return:
        new_handler += f"{indent}    {existing_return.strip()}\n"
    
    return new_handler, True

def find_method_name_for_handler(handler_content: str, content: str, handler_start: int) -> str:
    """Find the method name that contains this exception handler."""
    # Look backwards for the method definition
    before_handler = content[:handler_start]
    method_match = re.search(r'async def (\w+)\(', before_handler)
    if method_match:
        return method_match.group(1)
    method_match = re.search(r'def (\w+)\(', before_handler)
    if method_match:
        return method_match.group(1)
    return "<method_name>"

def update_all_exception_handlers(content: str) -> Tuple[str, int]:
    """
    Update all exception handlers in the file.
    
    Returns:
        (updated_content, number_of_updates)
    """
    handlers = find_exception_handlers(content)
    if not handlers:
        return content, 0
    
    # Process from end to start to preserve indices
    updated_count = 0
    for handler in reversed(handlers):
        method_name = find_method_name_for_handler(handler['content'], content, handler['start'])
        updated_handler, was_updated = update_exception_handler(
            handler['content'],
            handler['indent'],
            handler['exception_var'],
            method_name
        )
        
        if was_updated:
            content = content[:handler['start']] + updated_handler + content[handler['end']:]
            updated_count += 1
    
    return content, updated_count

def add_imports_if_needed(content: str) -> str:
    """Add logging import if not present."""
    if 'import logging' not in content:
        # Find the first import line
        import_match = re.search(r'^(import |from )', content, re.MULTILINE)
        if import_match:
            insert_pos = import_match.start()
            content = content[:insert_pos] + 'import logging\n' + content[insert_pos:]
    
    return content

def show_diff(old_content: str, new_content: str, context_lines: int = 10):
    """Show a diff between old and new content."""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = unified_diff(
        old_lines, new_lines,
        fromfile='old', tofile='new',
        lineterm='', n=context_lines
    )
    
    print("\n" + "="*80)
    print("DIFF:")
    print("="*80)
    for line in diff:
        print(line, end='')
    print("="*80 + "\n")

def analyze_file(file_path: Path) -> Dict[str, Any]:
    """Analyze file and return what needs updating."""
    content = file_path.read_text()
    class_name = find_class_name(content)
    
    # Check constructor
    constructor = find_constructor(content)
    has_di_container = constructor and 'self.di_container = di_container' in constructor['content']
    
    # Check exception handlers
    handlers = find_exception_handlers(content)
    handlers_updated = sum(1 for h in handlers if 'error_handler = self.di_container.get_utility("error_handler")' in h['content'])
    
    return {
        'class_name': class_name,
        'has_di_container': has_di_container,
        'total_handlers': len(handlers),
        'handlers_updated': handlers_updated,
        'handlers_needing_update': len(handlers) - handlers_updated
    }

def process_file(file_path: Path, apply: bool = False, review: bool = False) -> bool:
    """
    Process a file to add utilities.
    
    Returns:
        True if changes were made
    """
    # Create backup
    backup_path = file_path.with_suffix(f'.py.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    
    content = file_path.read_text()
    original_content = content
    class_name = find_class_name(content)
    
    print(f"\n{'='*80}")
    print(f"Processing: {file_path.name}")
    print(f"Class: {class_name}")
    print(f"{'='*80}")
    
    # Analyze
    analysis = analyze_file(file_path)
    print(f"Has DI Container: {'✅ Yes' if analysis['has_di_container'] else '❌ No'}")
    print(f"Exception Handlers: {analysis['total_handlers']} total, {analysis['handlers_updated']} updated, {analysis['handlers_needing_update']} needing update")
    
    # Add imports if needed
    content = add_imports_if_needed(content)
    
    # Update constructor
    if not analysis['has_di_container']:
        print("\n📋 Updating constructor...")
        content, constructor_updated = update_constructor(content, class_name)
        if constructor_updated:
            print("✅ Constructor updated")
        else:
            print("⚠️  Constructor update failed")
    else:
        print("\n✅ Constructor already has DI container")
    
    # Update exception handlers
    if analysis['handlers_needing_update'] > 0:
        print(f"\n📋 Updating {analysis['handlers_needing_update']} exception handlers...")
        content, handler_count = update_all_exception_handlers(content)
        print(f"✅ Updated {handler_count} exception handlers")
    else:
        print("\n✅ All exception handlers already updated")
    
    # Show diff if requested
    if review or apply:
        if content != original_content:
            show_diff(original_content, content)
        else:
            print("\n✅ No changes needed")
    
    # Apply changes
    if apply and content != original_content:
        # Create backup
        shutil.copy2(file_path, backup_path)
        print(f"\n💾 Backup created: {backup_path.name}")
        
        # Write updated content
        file_path.write_text(content)
        print(f"✅ Changes applied to {file_path.name}")
        return True
    elif apply:
        print("\n✅ No changes to apply")
        return False
    else:
        print("\n💡 Use --apply to actually make changes")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Hybrid script to update abstractions with utilities')
    parser.add_argument('file', help='Abstraction file path')
    parser.add_argument('--apply', action='store_true', help='Actually apply changes (creates backup)')
    parser.add_argument('--review', action='store_true', help='Show diff before applying')
    args = parser.parse_args()
    
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    # Process file
    if args.review or args.apply:
        process_file(file_path, apply=args.apply, review=True)
    else:
        # Just analyze
        analysis = analyze_file(file_path)
        print(f"\n{'='*80}")
        print(f"Analysis: {file_path.name}")
        print(f"{'='*80}")
        print(f"Class: {analysis['class_name']}")
        print(f"Has DI Container: {'✅ Yes' if analysis['has_di_container'] else '❌ No'}")
        print(f"Exception Handlers: {analysis['total_handlers']} total")
        print(f"  - Updated: {analysis['handlers_updated']}")
        print(f"  - Needing update: {analysis['handlers_needing_update']}")
        print(f"\n💡 Use --review to see what would change")
        print(f"   Use --apply to make changes (creates backup)")

if __name__ == '__main__':
    main()
