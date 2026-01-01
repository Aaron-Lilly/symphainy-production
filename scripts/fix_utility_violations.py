#!/usr/bin/env python3
"""
Utility Violation Fixer

Systematically fixes utility usage violations in services:
1. Error handling - Adds handle_error_with_audit to all try/except blocks
2. Telemetry - Adds telemetry tracking to operation methods
3. Error codes - Adds error_code to error responses

This script applies fixes based on established patterns from FileParserService and WorkflowManagerService.
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import ast


@dataclass
class Fix:
    """Represents a fix to apply."""
    file_path: str
    line_number: int
    fix_type: str
    old_code: str
    new_code: str
    description: str


class UtilityViolationFixer:
    """Fixes utility usage violations in services."""
    
    def __init__(self, project_root: str, dry_run: bool = True):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.fixes: List[Fix] = []
        
    def fix_file(self, file_path: str) -> List[Fix]:
        """Fix violations in a single file."""
        full_path = self.project_root / file_path if not Path(file_path).is_absolute() else Path(file_path)
        
        if not full_path.exists():
            return []
        
        try:
            content = full_path.read_text()
            lines = content.split('\n')
            file_fixes = []
            
            # Fix 1: Add error handling to try/except blocks
            file_fixes.extend(self._fix_error_handling(content, lines, str(full_path)))
            
            # Fix 2: Add error_code to error responses
            file_fixes.extend(self._fix_error_responses(content, lines, str(full_path)))
            
            return file_fixes
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return []
    
    def _fix_error_handling(self, content: str, lines: List[str], file_path: str) -> List[Fix]:
        """Fix error handling in try/except blocks."""
        fixes = []
        
        # Find all except blocks that don't have handle_error_with_audit
        except_pattern = r'except\s+(?:Exception|BaseException|\w+Error)\s+as\s+\w+:'
        
        for i, line in enumerate(lines):
            if re.search(except_pattern, line):
                # Check if this except block already has handle_error_with_audit
                # Look ahead in the except block
                except_start = i
                except_end = self._find_except_block_end(lines, except_start)
                
                if except_end:
                    except_block = '\n'.join(lines[except_start:except_end])
                    
                    # Skip if already has handle_error_with_audit
                    if 'handle_error_with_audit' in except_block:
                        continue
                    
                    # Find the exception variable name
                    match = re.search(r'except\s+(?:Exception|BaseException|\w+Error)\s+as\s+(\w+)', line)
                    if not match:
                        continue
                    
                    exception_var = match.group(1)
                    
                    # Find the method name (look backwards for async def or def)
                    method_name = self._find_method_name(lines, except_start)
                    if not method_name:
                        method_name = "unknown_operation"
                    
                    # Find where to insert the fix (after except line, before logger.error if present)
                    insert_line = except_start + 1
                    
                    # Check if there's a logger.error line
                    logger_error_line = None
                    for j in range(except_start + 1, min(except_start + 5, len(lines))):
                        if 'logger.error' in lines[j] or 'self.logger.error' in lines[j]:
                            logger_error_line = j
                            break
                    
                    # Create fix
                    indent = len(lines[except_start]) - len(lines[except_start].lstrip())
                    indent_str = ' ' * indent
                    
                    # Insert handle_error_with_audit before logger.error (if present) or after except
                    if logger_error_line:
                        insert_line = logger_error_line
                        old_code = lines[logger_error_line]
                        new_code = f"{indent_str}    # Error handling with audit\n{indent_str}    await self.handle_error_with_audit({exception_var}, \"{method_name}\")\n{old_code}"
                    else:
                        # Insert after except line
                        old_code = lines[insert_line] if insert_line < len(lines) else ""
                        new_code = f"{indent_str}    # Error handling with audit\n{indent_str}    await self.handle_error_with_audit({exception_var}, \"{method_name}\")\n{old_code}"
                    
                    fixes.append(Fix(
                        file_path=file_path,
                        line_number=insert_line + 1,  # 1-indexed
                        fix_type="error_handling",
                        old_code=old_code,
                        new_code=new_code,
                        description=f"Add error handling with audit to {method_name}"
                    ))
        
        return fixes
    
    def _fix_error_responses(self, content: str, lines: List[str], file_path: str) -> List[Fix]:
        """Fix error responses to include error_code."""
        fixes = []
        
        # Find return statements with error dictionaries
        for i, line in enumerate(lines):
            # Look for return statements with dictionaries
            if 'return {' in line or (line.strip().startswith('return') and '{' in line):
                # Find the dictionary in the return statement
                dict_start = i
                dict_end = self._find_dict_end(lines, dict_start)
                
                if dict_end is not None:
                    dict_lines = lines[dict_start:dict_end+1]
                    dict_content = '\n'.join(dict_lines)
                    
                    # Skip if already has error_code
                    if 'error_code' in dict_content:
                        continue
                    
                    # Check if it's an error response (has success: False or error:)
                    if '"success": False' in dict_content or '"error":' in dict_content:
                        # Find the exception variable in the except block above
                        exception_var = self._find_exception_var(lines, dict_start)
                        
                        # Find the last line before closing brace (the actual last content line)
                        last_line_idx = dict_end - 1
                        while last_line_idx > dict_start:
                            line_stripped = lines[last_line_idx].strip()
                            if line_stripped and line_stripped != '}':
                                break
                            last_line_idx -= 1
                        
                        if last_line_idx <= dict_start:
                            continue
                        
                        # Add error_code before closing brace
                        indent = len(lines[last_line_idx]) - len(lines[last_line_idx].lstrip())
                        indent_str = ' ' * indent
                        
                        # Check if last line has a comma
                        last_line = lines[last_line_idx]
                        last_line_stripped = last_line.rstrip()
                        needs_comma = not last_line_stripped.endswith(',') and not last_line_stripped.endswith('{')
                        
                        if exception_var:
                            error_code_value = f"type({exception_var}).__name__"
                        else:
                            error_code_value = '"UNKNOWN_ERROR"'
                        
                        # Insert error_code before closing brace (inside the dict)
                        if needs_comma:
                            # Add comma to last line, then add error_code on new line
                            new_last_line = f"{last_line_stripped},\n{indent_str}    \"error_code\": {error_code_value}"
                        else:
                            # Last line already has comma, just add error_code
                            new_last_line = f"{indent_str}    \"error_code\": {error_code_value}"
                        
                        fixes.append(Fix(
                            file_path=file_path,
                            line_number=last_line_idx + 1,
                            fix_type="error_code",
                            old_code=last_line,
                            new_code=new_line,
                            description="Add error_code to error response"
                        ))
        
        return fixes
    
    def _find_except_block_end(self, lines: List[str], start_line: int) -> Optional[int]:
        """Find the end of an except block."""
        indent_level = len(lines[start_line]) - len(lines[start_line].lstrip())
        
        for i in range(start_line + 1, len(lines)):
            if not lines[i].strip():
                continue
            
            line_indent = len(lines[i]) - len(lines[i].lstrip())
            
            # If we hit a line at same or less indent (and it's not a comment), we're done
            if line_indent <= indent_level and not lines[i].strip().startswith('#'):
                return i
        
        return len(lines)
    
    def _find_method_name(self, lines: List[str], line_num: int) -> Optional[str]:
        """Find the method name containing this line."""
        for i in range(line_num, -1, -1):
            if i >= len(lines):
                continue
            match = re.search(r'(?:async\s+)?def\s+(\w+)\(', lines[i])
            if match:
                return match.group(1)
        return None
    
    def _find_dict_start(self, lines: List[str], line_num: int) -> Optional[int]:
        """Find the start of a dictionary."""
        for i in range(line_num, -1, -1):
            if '{' in lines[i]:
                return i
        return None
    
    def _find_dict_end(self, lines: List[str], start_line: int) -> Optional[int]:
        """Find the end of a dictionary."""
        brace_count = 0
        for i in range(start_line, len(lines)):
            brace_count += lines[i].count('{') - lines[i].count('}')
            if brace_count == 0 and '{' in lines[start_line]:
                return i
        return None
    
    def _find_exception_var(self, lines: List[str], line_num: int) -> Optional[str]:
        """Find the exception variable in the except block above."""
        for i in range(line_num, max(0, line_num - 10), -1):
            match = re.search(r'except\s+(?:Exception|BaseException|\w+Error)\s+as\s+(\w+)', lines[i])
            if match:
                return match.group(1)
        return None
    
    def apply_fixes(self, fixes: List[Fix]) -> Dict[str, int]:
        """Apply fixes to files."""
        if self.dry_run:
            print("DRY RUN MODE - No files will be modified")
            print(f"Would apply {len(fixes)} fixes")
            return {"applied": 0, "skipped": len(fixes)}
        
        applied = 0
        skipped = 0
        
        # Group fixes by file
        fixes_by_file = {}
        for fix in fixes:
            if fix.file_path not in fixes_by_file:
                fixes_by_file[fix.file_path] = []
            fixes_by_file[fix.file_path].append(fix)
        
        # Apply fixes to each file
        for file_path, file_fixes in fixes_by_file.items():
            try:
                # Sort fixes by line number (descending) to avoid line number shifts
                file_fixes.sort(key=lambda f: f.line_number, reverse=True)
                
                # Read file
                content = Path(file_path).read_text()
                lines = content.split('\n')
                
                # Apply fixes
                for fix in file_fixes:
                    if fix.line_number <= len(lines):
                        # Replace the line
                        lines[fix.line_number - 1] = fix.new_code
                        applied += 1
                    else:
                        skipped += 1
                
                # Write file
                Path(file_path).write_text('\n'.join(lines))
                print(f"✅ Applied {len(file_fixes)} fixes to {file_path}")
                
            except Exception as e:
                print(f"❌ Error applying fixes to {file_path}: {e}")
                skipped += len(file_fixes)
        
        return {"applied": applied, "skipped": skipped}


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix utility usage violations")
    parser.add_argument("--directory", type=str, help="Directory to fix", default="symphainy-platform/backend/business_enablement")
    parser.add_argument("--project-root", type=str, help="Project root directory", default=".")
    parser.add_argument("--apply", action="store_true", help="Apply fixes (default is dry-run)")
    parser.add_argument("--file", type=str, help="Fix specific file only")
    
    args = parser.parse_args()
    
    fixer = UtilityViolationFixer(args.project_root, dry_run=not args.apply)
    
    # Find all service files
    if args.file:
        files_to_fix = [args.file]
    else:
        dir_path = Path(args.project_root) / args.directory
        files_to_fix = []
        for py_file in dir_path.rglob("*.py"):
            # Skip test files, __init__, and archive
            if any(skip in str(py_file) for skip in ["test_", "__pycache__", "archive", "tests"]):
                continue
            # Check if it's a service file
            try:
                content = py_file.read_text()
                if any(base in content for base in [
                    "RealmServiceBase",
                    "FoundationServiceBase",
                    "SmartCityRoleBase",
                    "OrchestratorBase"
                ]):
                    files_to_fix.append(str(py_file.relative_to(args.project_root)))
            except Exception:
                pass
    
    print(f"Found {len(files_to_fix)} service files to process")
    
    # Fix each file
    all_fixes = []
    for file_path in files_to_fix:
        fixes = fixer.fix_file(file_path)
        all_fixes.extend(fixes)
        if fixes:
            print(f"Found {len(fixes)} fixes in {file_path}")
    
    print(f"\nTotal fixes found: {len(all_fixes)}")
    
    # Group by fix type
    fixes_by_type = {}
    for fix in all_fixes:
        if fix.fix_type not in fixes_by_type:
            fixes_by_type[fix.fix_type] = []
        fixes_by_type[fix.fix_type].append(fix)
    
    print("\nFixes by type:")
    for fix_type, fixes in fixes_by_type.items():
        print(f"  {fix_type}: {len(fixes)}")
    
    # Show sample fixes
    if all_fixes:
        print("\nSample fixes (first 5):")
        for fix in all_fixes[:5]:
            print(f"\n  File: {fix.file_path}")
            print(f"  Line: {fix.line_number}")
            print(f"  Type: {fix.fix_type}")
            print(f"  Description: {fix.description}")
            print(f"  Old: {fix.old_code[:80]}...")
            print(f"  New: {fix.new_code[:80]}...")
    
    # Apply fixes
    if args.apply:
        print("\nApplying fixes...")
        result = fixer.apply_fixes(all_fixes)
        print(f"✅ Applied: {result['applied']}, Skipped: {result['skipped']}")
    else:
        print("\n💡 Run with --apply to apply fixes")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

