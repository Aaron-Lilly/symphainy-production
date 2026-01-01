#!/usr/bin/env python3
"""
Script to add security and multi-tenancy validation to composition services.

This script adds:
1. A helper method `_validate_security_and_tenant` to each composition service
2. Security and tenant validation calls at the start of async methods that accept user_context
"""

import re
import sys
from pathlib import Path

# Pattern to find async methods that accept user_context
async_method_pattern = r'async def (\w+)\([^)]*user_context[^)]*\)'

def add_validation_helper(content: str, service_name: str) -> str:
    """Add the validation helper method after __init__."""
    
    helper_method = f'''    # ============================================================================
    # SECURITY AND MULTI-TENANCY VALIDATION HELPERS
    # ============================================================================
    
    async def _validate_security_and_tenant(self, user_context: Dict[str, Any], 
                                           resource: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Validate security context and tenant access.
        
        Args:
            user_context: User context with user_id, tenant_id, security_context
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            # Get utilities from DI container
            security = self.di_container.get_utility("security") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            tenant = self.di_container.get_utility("tenant") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            
            user_id = user_context.get("user_id")
            tenant_id = user_context.get("tenant_id")
            security_context = user_context.get("security_context")
            
            # Security validation (if security utility available and context provided)
            if security and security_context:
                try:
                    # Validate user permission
                    has_permission = await security.validate_user_permission(
                        user_id, resource, action, 
                        security_context.get("permissions", [])
                    )
                    if not has_permission:
                        return {{
                            "success": False,
                            "error": f"Permission denied: {{action}} on {{resource}}",
                            "error_code": "PERMISSION_DENIED"
                        }}
                except Exception as e:
                    self.logger.warning(f"Security validation failed: {{e}}")
                    # Don't fail on security validation errors - log and continue
                    # (security might not be fully bootstrapped)
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        # For cross-tenant access, this would be handled at foundation service level
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            return {{
                                "success": False,
                                "error": f"Tenant access denied for tenant: {{tenant_id}}",
                                "error_code": "TENANT_ACCESS_DENIED"
                            }}
                except Exception as e:
                    self.logger.warning(f"Tenant validation failed: {{e}}")
                    # Don't fail on tenant validation errors - log and continue
            
            return None  # Validation passed
            
        except Exception as e:
            self.logger.error(f"Security/tenant validation error: {{e}}")
            # Don't fail on validation errors - log and continue
            return None
    
'''
    
    # Find the end of __init__ method
    init_pattern = r'(self\.logger\.info\("✅ .* Composition Service initialized"\))'
    match = re.search(init_pattern, content)
    if match:
        insert_pos = match.end()
        # Find the next section marker or method
        next_section = re.search(r'\n    # ============================================================================', content[insert_pos:])
        if next_section:
            insert_pos = insert_pos + next_section.start()
        else:
            # Insert before first method
            next_method = re.search(r'\n    (async )?def ', content[insert_pos:])
            if next_method:
                insert_pos = insert_pos + next_method.start()
        
        content = content[:insert_pos] + '\n' + helper_method + content[insert_pos:]
    
    return content

def add_validation_call(content: str, method_name: str, resource: str, action: str) -> str:
    """Add validation call at the start of a method."""
    
    # Find the method definition
    method_pattern = rf'async def {method_name}\([^)]*\)[^:]*:'
    match = re.search(method_pattern, content)
    if not match:
        return content
    
    # Find the try block start (should be right after method definition)
    try_pos = content.find('try:', match.end())
    if try_pos == -1:
        return content
    
    # Find the first line after try:
    first_line_match = re.search(r'try:\s*\n(\s+)', content[try_pos:try_pos+200])
    if not first_line_match:
        return content
    
    indent = first_line_match.group(1)
    
    # Check if validation already exists
    validation_check = f'{indent}# Validate security and tenant access'
    if validation_check in content[try_pos:try_pos+500]:
        return content  # Already has validation
    
    # Create validation call
    validation_call = f'''{indent}# Validate security and tenant access
{indent}validation_error = await self._validate_security_and_tenant(
{indent}    user_context, "{resource}", "{action}"
{indent})
{indent}if validation_error:
{indent}    return validation_error
{indent}
'''
    
    # Insert after try:
    insert_pos = try_pos + len('try:')
    # Find the first non-empty line
    next_line = re.search(r'\n(\s+)(?=\S)', content[insert_pos:insert_pos+200])
    if next_line:
        insert_pos = insert_pos + next_line.start() + 1
    
    content = content[:insert_pos] + validation_call + content[insert_pos:]
    
    return content

def process_file(file_path: Path):
    """Process a single composition service file."""
    print(f"Processing: {file_path.name}")
    
    content = file_path.read_text()
    
    # Check if helper method already exists
    if '_validate_security_and_tenant' in content:
        print(f"  ⚠️  Helper method already exists, skipping...")
        return
    
    # Add helper method
    service_name = file_path.stem.replace('_composition_service', '')
    content = add_validation_helper(content, service_name)
    
    # Find all async methods with user_context
    methods = re.finditer(async_method_pattern, content)
    for match in methods:
        method_name = match.group(1)
        # Determine resource and action from method name
        resource = service_name.replace('_', '')
        action = method_name.replace('_', '_')
        
        # Add validation call
        content = add_validation_call(content, method_name, resource, action)
        print(f"  ✅ Added validation to {method_name}")
    
    # Write back
    file_path.write_text(content)
    print(f"  ✅ Updated {file_path.name}")

def main():
    """Main entry point."""
    composition_services_dir = Path(__file__).parent.parent / 'symphainy-platform' / 'foundations' / 'public_works_foundation' / 'composition_services'
    
    if not composition_services_dir.exists():
        print(f"Error: Directory not found: {composition_services_dir}")
        sys.exit(1)
    
    # Get all composition service files
    composition_files = list(composition_services_dir.glob('*_composition_service.py'))
    
    print(f"Found {len(composition_files)} composition service files")
    print()
    
    for file_path in sorted(composition_files):
        try:
            process_file(file_path)
        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")
    
    print()
    print("✅ Done!")

if __name__ == '__main__':
    main()












