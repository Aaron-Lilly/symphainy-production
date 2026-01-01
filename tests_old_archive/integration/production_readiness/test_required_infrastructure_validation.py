"""
Test Required Infrastructure Validation

Finds instances where required infrastructure is incorrectly allowed to be None.
All required adapters and abstractions should fail gracefully (clear errors) but still fail.

This test audits the codebase to find:
1. Required adapters set to None after creation attempts
2. Required abstractions set to None after creation attempts
3. Exception handlers that set required infrastructure to None
4. Conditional None assignments for required infrastructure
"""

import pytest
import os

import re
from pathlib import Path
from typing import List, Dict, Any

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

@pytest.mark.integration
class TestRequiredInfrastructureValidation:
    """Test that required infrastructure fails gracefully but still fails."""
    
    # Required adapters (must never be None after initialization attempt)
    REQUIRED_ADAPTERS = [
        'gcs_adapter',  # Required for FileManagementAbstraction
        'supabase_adapter',  # Required for auth, tenant, file management
        'redis_adapter',  # Required for session, cache, messaging
        'arango_adapter',  # Required for content metadata, knowledge
        'session_adapter',  # Required for SessionAbstraction
        'jwt_adapter',  # Required for AuthAbstraction
    ]
    
    # Required abstractions (must never be None after initialization attempt)
    REQUIRED_ABSTRACTIONS = [
        'file_management_abstraction',  # Required for file operations
        'session_abstraction',  # Required for session management
        'auth_abstraction',  # Required for authentication
        'content_metadata_abstraction',  # Required for content operations
    ]
    
    def find_problematic_none_assignments(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Find instances where required infrastructure is set to None.
        
        Looks for patterns like:
        - self.required_adapter = None (after creation attempt)
        - except: self.adapter = None
        - if not config: self.adapter = None
        """
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Pattern 1: Direct None assignment to required adapter/abstraction
                for adapter in self.REQUIRED_ADAPTERS:
                    pattern = rf'self\.{adapter}\s*=\s*None'
                    if re.search(pattern, line):
                        # Check if this is in __init__ (initialization) vs after creation attempt
                        context_start = max(0, line_num - 10)
                        context = '\n'.join(lines[context_start:line_num + 5])
                        # Skip if it's in __init__ initialization (that's OK)
                        if '__init__' in context and 'def __init__' in context.split('\n')[0]:
                            continue
                        issues.append({
                            'file': file_path,
                            'line': line_num,
                            'content': stripped,
                            'issue': f'Required adapter {adapter} set to None (should fail gracefully instead)',
                            'type': 'adapter_none'
                        })
                
                for abstraction in self.REQUIRED_ABSTRACTIONS:
                    pattern = rf'self\.{abstraction}\s*=\s*None'
                    if re.search(pattern, line):
                        context_start = max(0, line_num - 10)
                        context = '\n'.join(lines[context_start:line_num + 5])
                        if '__init__' in context and 'def __init__' in context.split('\n')[0]:
                            continue
                        issues.append({
                            'file': file_path,
                            'line': line_num,
                            'content': stripped,
                            'issue': f'Required abstraction {abstraction} set to None (should fail gracefully instead)',
                            'type': 'abstraction_none'
                        })
                
                # Pattern 2: Exception handler setting to None
                if 'except' in stripped.lower() and '= None' in stripped:
                    # Check next few lines for None assignment
                    for i in range(1, 5):
                        if line_num + i - 1 < len(lines):
                            next_line = lines[line_num + i - 1].strip()
                            for adapter in self.REQUIRED_ADAPTERS:
                                if f'self.{adapter} = None' in next_line:
                                    issues.append({
                                        'file': file_path,
                                        'line': line_num + i,
                                        'content': next_line,
                                        'issue': f'Exception handler sets required adapter {adapter} to None (should raise RuntimeError with clear message)',
                                        'type': 'exception_none'
                                    })
                            for abstraction in self.REQUIRED_ABSTRACTIONS:
                                if f'self.{abstraction} = None' in next_line:
                                    issues.append({
                                        'file': file_path,
                                        'line': line_num + i,
                                        'content': next_line,
                                        'issue': f'Exception handler sets required abstraction {abstraction} to None (should raise RuntimeError with clear message)',
                                        'type': 'exception_none'
                                    })
                
                # Pattern 3: Conditional None assignment (if not config: adapter = None)
                for adapter in self.REQUIRED_ADAPTERS:
                    # Check if this line starts an if statement and next line sets adapter to None
                    if stripped.startswith('if') and ':' in stripped:
                        # Check next few lines for None assignment
                        for i in range(1, 5):
                            if line_num + i - 1 < len(lines):
                                next_line = lines[line_num + i - 1].strip()
                                if f'self.{adapter} = None' in next_line:
                                    issues.append({
                                        'file': file_path,
                                        'line': line_num + i,
                                        'content': next_line,
                                        'issue': f'Conditional None assignment for required adapter {adapter} (should raise ValueError with clear message)',
                                        'type': 'conditional_none'
                                    })
                                    break
        
        except Exception as e:
            pass  # Skip files that can't be read
        
        return issues
    
    def test_no_none_for_required_infrastructure(self):
        """Test that required infrastructure is never set to None after creation attempts."""
        platform_root = Path(__file__).parent.parent.parent / "symphainy-platform"
        public_works_path = platform_root / "foundations" / "public_works_foundation"
        
        if not public_works_path.exists():
            pytest.skip("Public Works Foundation path not found")
        
        all_issues = []
        
        # Check public_works_foundation_service.py (main service file)
        service_file = public_works_path / "public_works_foundation_service.py"
        if service_file.exists():
            issues = self.find_problematic_none_assignments(str(service_file))
            all_issues.extend(issues)
        
        # Check adapter files
        adapters_path = public_works_path / "infrastructure_adapters"
        if adapters_path.exists():
            for adapter_file in adapters_path.glob("*.py"):
                if adapter_file.name.startswith("__"):
                    continue
                issues = self.find_problematic_none_assignments(str(adapter_file))
                all_issues.extend(issues)
        
        # Check abstraction files
        abstractions_path = public_works_path / "infrastructure_abstractions"
        if abstractions_path.exists():
            for abstraction_file in abstractions_path.glob("*.py"):
                if abstraction_file.name.startswith("__"):
                    continue
                issues = self.find_problematic_none_assignments(str(abstraction_file))
                all_issues.extend(issues)
        
        if all_issues:
            error_msg = "Found instances where required infrastructure is incorrectly set to None:\n\n"
            for issue in all_issues:
                error_msg += f"  [{issue['type']}] {issue['file']}:{issue['line']}\n"
                error_msg += f"    Issue: {issue['issue']}\n"
                error_msg += f"    Code: {issue['content']}\n\n"
            
            error_msg += "\nRequired infrastructure should FAIL GRACEFULLY (clear error messages) but still FAIL.\n"
            error_msg += "Do not set required adapters/abstractions to None - raise RuntimeError with actionable error messages instead."
            
            pytest.fail(error_msg)
