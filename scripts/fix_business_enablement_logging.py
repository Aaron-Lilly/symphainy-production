#!/usr/bin/env python3
"""
Surgical script to fix utility logging violations in Business Enablement realm.

Removes `import logging` and replaces `logging.getLogger()` with DI Container access.
"""

import sys
from pathlib import Path
import re
from typing import List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.fixtures.smart_city_usage_validator import SmartCityUsageValidator


def fix_logging_imports_and_calls(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Fix logging imports and calls in a file.
    
    Returns:
        (changed, messages) - Whether file was changed and any messages
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        original_lines = lines.copy()
        changed = False
        messages = []
        
        # Track if we need to add TYPE_CHECKING import
        needs_type_checking = False
        has_type_checking_import = False
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Remove standalone `import logging` (not in TYPE_CHECKING block)
            if re.match(r'^\s*import\s+logging\s*$', line):
                # Check if it's in a TYPE_CHECKING block (look backwards)
                in_type_checking = False
                for j in range(i - 1, max(-1, i - 20), -1):
                    if 'if TYPE_CHECKING:' in lines[j] or 'if typing.TYPE_CHECKING:' in lines[j]:
                        in_type_checking = True
                        break
                    if lines[j].strip() and not lines[j].strip().startswith('#'):
                        if not lines[j].strip().startswith('import') and not lines[j].strip().startswith('from'):
                            break
                
                if not in_type_checking:
                    lines[i] = ''  # Remove the line
                    changed = True
                    messages.append(f"Removed `import logging` at line {i+1}")
            
            # Replace `logging.getLogger(...)` with DI Container access
            if 'logging.getLogger' in line:
                # Check if it's in a TYPE_CHECKING block
                in_type_checking = False
                for j in range(i - 1, max(-1, i - 20), -1):
                    if 'if TYPE_CHECKING:' in lines[j] or 'if typing.TYPE_CHECKING:' in lines[j]:
                        in_type_checking = True
                        break
                    if lines[j].strip() and not lines[j].strip().startswith('#'):
                        if not lines[j].strip().startswith('import') and not lines[j].strip().startswith('from'):
                            break
                
                if not in_type_checking:
                    # Pattern: self.logger = logging.getLogger(...)
                    if re.search(r'self\.logger\s*=\s*logging\.getLogger', line):
                        # Extract the argument to getLogger
                        match = re.search(r'logging\.getLogger\(([^)]+)\)', line)
                        if match:
                            get_logger_arg = match.group(1).strip()
                            # Replace with DI Container access
                            # For micro-modules: self.service.di_container.get_logger(...)
                            # For service classes: self.di_container.get_logger(...)
                            if 'self.service' in line or 'class' in lines[max(0, i-10):i]:
                                # Check if this is a micro-module (has self.service)
                                replacement = f"self.service.di_container.get_logger({get_logger_arg})"
                            else:
                                replacement = f"self.di_container.get_logger({get_logger_arg})"
                            
                            new_line = re.sub(
                                r'logging\.getLogger\([^)]+\)',
                                replacement,
                                line
                            )
                            lines[i] = new_line
                            changed = True
                            messages.append(f"Replaced `logging.getLogger()` with DI Container at line {i+1}")
                    
                    # Pattern: logger = logging.getLogger(...) or logger=logging.getLogger(...)
                    elif re.search(r'logger\s*=\s*logging\.getLogger', line):
                        match = re.search(r'logging\.getLogger\(([^)]+)\)', line)
                        if match:
                            get_logger_arg = match.group(1).strip()
                            # Check context to determine if it's self.service or self
                            if any('self.service' in lines[j] for j in range(max(0, i-5), i)):
                                replacement = f"self.service.di_container.get_logger({get_logger_arg})"
                            else:
                                replacement = f"self.di_container.get_logger({get_logger_arg})"
                            
                            new_line = re.sub(
                                r'logging\.getLogger\([^)]+\)',
                                replacement,
                                line
                            )
                            lines[i] = new_line
                            changed = True
                            messages.append(f"Replaced `logging.getLogger()` with DI Container at line {i+1}")
                    
                    # Pattern: logger or logging.getLogger(...) (fallback pattern)
                    elif re.search(r'logger\s+or\s+logging\.getLogger', line):
                        match = re.search(r'logging\.getLogger\(([^)]+)\)', line)
                        if match:
                            get_logger_arg = match.group(1).strip()
                            # Replace the fallback pattern
                            if 'self.service' in line:
                                replacement = f"logger or self.service.di_container.get_logger({get_logger_arg})"
                            else:
                                replacement = f"logger or self.di_container.get_logger({get_logger_arg})"
                            
                            new_line = re.sub(
                                r'logging\.getLogger\([^)]+\)',
                                replacement.split(' or ')[1],  # Just replace the logging part
                                line
                            )
                            # Actually, we need to replace the whole pattern
                            new_line = re.sub(
                                r'logger\s+or\s+logging\.getLogger\([^)]+\)',
                                replacement,
                                line
                            )
                            lines[i] = new_line
                            changed = True
                            messages.append(f"Replaced fallback `logging.getLogger()` with DI Container at line {i+1}")
        
        if changed:
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        
        return changed, messages
    
    except Exception as e:
        return False, [f"Error processing file: {str(e)}"]


def main():
    """Fix logging violations in Business Enablement realm."""
    symphainy_platform_root = project_root / 'symphainy-platform'
    business_enablement_root = symphainy_platform_root / 'backend' / 'business_enablement'
    
    if not business_enablement_root.exists():
        print(f"❌ Error: Business Enablement directory not found at {business_enablement_root}")
        sys.exit(1)
    
    print("🔧 Fixing utility logging violations in Business Enablement realm...")
    print(f"   Directory: {business_enablement_root}")
    print()
    
    # Get list of files with violations
    validator = SmartCityUsageValidator(symphainy_platform_root)
    results = validator.validate_realm('business_enablement')
    
    # Filter to active code (exclude archive)
    active_violations = [v for v in results['violations'] if 'archive' not in v['file']]
    
    # Filter to utility violations (forbidden_import and forbidden_call related to logging)
    logging_violations = [
        v for v in active_violations 
        if v.get('type') in ('forbidden_import', 'forbidden_call') and 'logging' in v.get('message', '').lower()
    ]
    
    # Get unique files
    files_to_fix = set(v['file'] for v in logging_violations)
    
    print(f"Found {len(logging_violations)} logging violations in {len(files_to_fix)} files")
    print()
    
    if not files_to_fix:
        print("✅ No logging violations to fix!")
        return 0
    
    # Ask for confirmation
    import sys
    if '--yes' not in sys.argv:
        response = input(f"Fix logging violations in {len(files_to_fix)} files? (yes/no): ")
        if response.lower() not in ('yes', 'y'):
            print("Cancelled.")
            return 0
    
    # Fix files
    fixed_count = 0
    total_messages = []
    
    for file_rel_path in sorted(files_to_fix):
        file_path = symphainy_platform_root / file_rel_path
        
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        changed, messages = fix_logging_imports_and_calls(file_path)
        
        if changed:
            fixed_count += 1
            print(f"✅ Fixed: {file_rel_path}")
            for msg in messages:
                print(f"   {msg}")
            total_messages.extend(messages)
        else:
            if messages:
                print(f"⚠️  {file_rel_path}: {messages[0]}")
    
    print()
    print("=" * 80)
    print(f"Fixed {fixed_count} files")
    print(f"Total changes: {len(total_messages)}")
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

