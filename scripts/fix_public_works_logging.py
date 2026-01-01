#!/usr/bin/env python3
"""
Fix Public Works Foundation Logging Anti-Patterns

Removes unused imports and fixes direct logging.getLogger() calls to use DI Container.

WHAT: Fix logging anti-patterns in Public Works Foundation
HOW: Remove unused imports, update direct logging calls to use DI Container
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.fixtures.utility_usage_validator import UtilityUsageValidator


def remove_unused_logging_import(file_path: Path) -> bool:
    """Remove unused 'import logging' statement."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check if file has 'import logging' and doesn't use logging directly
        import_line = None
        uses_logging_directly = False
        
        for i, line in enumerate(lines):
            # Check for 'import logging' (standalone, not in TYPE_CHECKING)
            if re.search(r'^\s*import\s+logging\s*$', line):
                # Check if it's inside TYPE_CHECKING block
                is_in_type_checking = False
                for j in range(max(0, i-10), i):
                    if 'if TYPE_CHECKING:' in lines[j] or 'if TYPE_CHECKING' in lines[j]:
                        is_in_type_checking = True
                        break
                
                if not is_in_type_checking:
                    import_line = i
            
            # Check if logging is used directly (logging.getLogger, logging.info, etc.)
            if re.search(r'\blogging\.', line):
                uses_logging_directly = True
        
        if import_line is not None and not uses_logging_directly:
            # Remove the import line
            new_lines = []
            for i, line in enumerate(lines):
                if i != import_line:
                    new_lines.append(line)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def fix_direct_logging_calls(file_path: Path) -> Tuple[bool, str]:
    """
    Fix direct logging.getLogger() calls.
    
    Returns: (changed, message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        changed = False
        changes = []
        
        for i, line in enumerate(lines):
            # Check for self.logger = logging.getLogger(...)
            match = re.search(r'self\.logger\s*=\s*logging\.getLogger\(([^)]+)\)', line)
            if match:
                # Check if class has di_container available
                # For now, we'll add a comment and suggest fix
                # Actual fix requires understanding the class structure
                logger_name = match.group(1)
                new_line = f"        # TODO: Use DI Container - self.logger = self.di_container.get_logger({logger_name})"
                changes.append(f"Line {i+1}: {line.strip()} -> {new_line.strip()}")
                # Don't auto-fix yet - need to check class structure
                # lines[i] = new_line
                # changed = True
        
        if changed:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
        
        return changed, '\n'.join(changes) if changes else ''
    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    public_works_dir = project_root / 'symphainy-platform' / 'foundations' / 'public_works_foundation'
    
    validator = UtilityUsageValidator(project_root)
    violations = validator.validate_directory(public_works_dir)
    
    # Separate violations
    unused_imports = [v for v in violations if v['type'] == 'forbidden_import']
    direct_calls = [v for v in violations if v['type'] == 'forbidden_call']
    
    print("🔧 Fixing Public Works Foundation Logging Anti-Patterns")
    print("=" * 80)
    print(f"\nUnused imports: {len(unused_imports)}")
    print(f"Direct logging calls: {len(direct_calls)}")
    print()
    
    # Fix unused imports - use validator output directly
    print("1️⃣ Removing unused 'import logging' statements...")
    fixed_imports = 0
    files_to_fix = {}
    
    # Group by file
    for v in unused_imports:
        file_path = v['file']
        if file_path not in files_to_fix:
            files_to_fix[file_path] = []
        files_to_fix[file_path].append(v['line'])
    
    # Remove imports from files
    for file_path_str, line_numbers in files_to_fix.items():
        file_path = project_root / file_path_str
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Remove lines (convert to 0-based index)
            lines_to_remove = [ln - 1 for ln in line_numbers]
            new_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            fixed_imports += len(line_numbers)
            print(f"   ✅ Removed {len(line_numbers)} unused import(s): {file_path_str}")
        except Exception as e:
            print(f"   ❌ Error fixing {file_path_str}: {e}")
    
    print(f"\n   Fixed: {fixed_imports}/{len(unused_imports)} unused imports")
    print()
    
    # Report direct calls (need manual review)
    print("2️⃣ Direct logging.getLogger() calls (need manual fix):")
    files_with_calls = {}
    for v in direct_calls:
        file_path = v['file']
        if file_path not in files_with_calls:
            files_with_calls[file_path] = []
        files_with_calls[file_path].append(v)
    
    for file_path, vlist in sorted(files_with_calls.items()):
        print(f"\n   📄 {file_path}: {len(vlist)} call(s)")
        for v in vlist:
            print(f"      Line {v['line']}: {v['message']}")
    
    print(f"\n   ⚠️  {len(files_with_calls)} files need manual fixes")
    print()
    
    print("=" * 80)
    print("✅ Unused imports removed!")
    print("⚠️  Direct logging calls need manual review/fix")
    print("=" * 80)


if __name__ == '__main__':
    main()

