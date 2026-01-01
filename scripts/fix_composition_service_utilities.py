#!/usr/bin/env python3
"""
Helper script to add error handling and telemetry to composition services.

This script systematically adds:
1. Error handling with error_handler utility
2. Telemetry recording for operations
3. Error codes in return values

Usage: python3 scripts/fix_composition_service_utilities.py <service_file>
"""

import re
import sys
from pathlib import Path

def fix_exception_handling(content: str, service_name: str) -> str:
    """Fix exception handling in async methods."""
    
    # Pattern 1: Simple except blocks that just log
    pattern1 = r'(\s+)except Exception as e:\s*\n(\s+)self\.logger\.error\([^)]+\)\s*\n(\s+)(return|raise)'
    
    def replace_except1(match):
        indent = match.group(1)
        logger_indent = match.group(2)
        return_indent = match.group(3)
        return_action = match.group(4)
        
        replacement = f"""{indent}except Exception as e:
{logger_indent}# Use error handler with telemetry
{logger_indent}error_handler = self.di_container.get_utility("error_handler") if hasattr(self.di_container, 'get_utility') else None
{logger_indent}telemetry = self.di_container.get_utility("telemetry") if hasattr(self.di_container, 'get_utility') else None
{logger_indent}if error_handler:
{logger_indent}    await error_handler.handle_error(e, {{
{logger_indent}        "operation": "{service_name}",
{logger_indent}        "service": self.service_name
{logger_indent}    }}, telemetry=telemetry)
{logger_indent}else:
{logger_indent}    self.logger.error(f"Error in {service_name}: {{e}}")
{return_indent}"""
        
        if return_action == "return":
            # Try to extract operation name from method signature
            replacement += f'{return_indent}return {{\n{return_indent}    "success": False,\n{return_indent}    "error": str(e),\n{return_indent}    "error_code": "{service_name.upper()}_ERROR"\n{return_indent}}}'
        else:
            replacement += f'{return_indent}raise'
        
        return replacement
    
    # Apply pattern 1
    content = re.sub(pattern1, replace_except1, content, flags=re.MULTILINE)
    
    return content

def add_telemetry_to_success(content: str, method_name: str) -> str:
    """Add telemetry recording to success paths."""
    
    # Pattern: Return statements in async methods (before except)
    # This is more complex and needs method context
    # For now, we'll do manual fixes
    
    return content

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/fix_composition_service_utilities.py <service_file>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    content = file_path.read_text()
    service_name = file_path.stem.replace("_composition_service", "")
    
    # Fix exception handling
    content = fix_exception_handling(content, service_name)
    
    # Write back
    file_path.write_text(content)
    print(f"✅ Fixed {file_path}")













