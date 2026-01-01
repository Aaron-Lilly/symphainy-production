#!/usr/bin/env python3
"""
Base Class Validator

Validates that base classes properly use DI Container AND Utilities.
BUILDS ON: DI Container Usage Validator + Utilities Usage Validator

WHAT: Validate base class compliance
HOW: Check that base classes use both DI Container and Utilities correctly
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add tests to path for import
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.fixtures.di_container_usage_validator import DIContainerUsageValidator
from tests.fixtures.utility_usage_validator import UtilityUsageValidator


class BaseClassValidator:
    """
    Validates that base classes properly use DI Container AND Utilities.
    BUILDS ON: DIContainerUsageValidator + UtilityUsageValidator
    
    Checks:
    1. Base classes use DI Container properly
    2. Base classes use Utilities via DI Container
    3. Base classes inherit from correct mixins
    4. Base classes expose correct methods
    """
    
    def __init__(self, project_root: Path):
        """Initialize validator."""
        self.project_root = project_root
        
        # Build on existing validators
        self.di_container_validator = DIContainerUsageValidator(project_root)
        self.utility_validator = UtilityUsageValidator(project_root)
    
    def validate_base_class(self, base_class_path: Path) -> Dict[str, Any]:
        """
        Comprehensive validation of a base class.
        
        Checks:
        1. Uses DI Container properly
        2. Uses Utilities via DI Container
        3. Inherits from correct mixins
        4. Exposes correct methods
        """
        # Get violations from both validators
        di_container_result = self.di_container_validator.validate_service_uses_di_container(base_class_path)
        utility_result = self.utility_validator.validate_comprehensive(base_class_path)
        
        # Combine violations
        all_violations = di_container_result['violations'] + utility_result['all_violations']
        
        # Check for required mixins and methods
        mixin_violations = self._check_required_mixins(base_class_path)
        method_violations = self._check_required_methods(base_class_path)
        
        all_violations.extend(mixin_violations)
        all_violations.extend(method_violations)
        
        # Determine if valid
        is_valid = len(all_violations) == 0
        
        return {
            'file': str(base_class_path.relative_to(self.project_root)),
            'di_container_violations': di_container_result['violations'],
            'utility_violations': utility_result['utility_violations'],
            'di_container_violations_from_utility': utility_result['di_container_violations'],
            'mixin_violations': mixin_violations,
            'method_violations': method_violations,
            'all_violations': all_violations,
            'is_valid': is_valid,
            'di_container_count': len(di_container_result['violations']),
            'utility_count': len(utility_result['utility_violations']),
            'mixin_count': len(mixin_violations),
            'method_count': len(method_violations),
            'total_count': len(all_violations)
        }
    
    def _check_required_mixins(self, base_class_path: Path) -> List[Dict[str, Any]]:
        """Check that base class inherits from required mixins."""
        violations = []
        
        try:
            with open(base_class_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine which mixins are required based on base class type
            base_class_name = base_class_path.stem
            
            if 'foundation_service' in base_class_name.lower():
                required_mixins = ['UtilityAccessMixin', 'InfrastructureAccessMixin']
            elif 'realm_service' in base_class_name.lower():
                required_mixins = ['UtilityAccessMixin', 'InfrastructureAccessMixin', 'SecurityMixin']
            elif 'smart_city_role' in base_class_name.lower():
                required_mixins = ['UtilityAccessMixin', 'InfrastructureAccessMixin', 'SecurityMixin']
            else:
                # Default: at least UtilityAccessMixin
                required_mixins = ['UtilityAccessMixin']
            
            # Check for each required mixin
            for mixin in required_mixins:
                if mixin not in content:
                    violations.append({
                        'file': str(base_class_path.relative_to(self.project_root)),
                        'line': 0,
                        'type': 'missing_mixin',
                        'message': f"Base class missing required mixin: {mixin}",
                        'recommendation': f"Inherit from {mixin} to access utilities/infrastructure via DI Container"
                    })
        
        except Exception as e:
            violations.append({
                'file': str(base_class_path.relative_to(self.project_root)),
                'line': 0,
                'type': 'parse_error',
                'message': f"Failed to check mixins: {e}",
                'recommendation': 'Check file syntax'
            })
        
        return violations
    
    def _check_required_methods(self, base_class_path: Path) -> List[Dict[str, Any]]:
        """Check that base class exposes required methods."""
        violations = []
        
        try:
            with open(base_class_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Required methods for all base classes
            required_methods = ['get_utility', 'initialize']
            
            # Check for each required method
            for method in required_methods:
                if method not in content:
                    violations.append({
                        'file': str(base_class_path.relative_to(self.project_root)),
                        'line': 0,
                        'type': 'missing_method',
                        'message': f"Base class missing required method: {method}",
                        'recommendation': f"Implement {method}() method or inherit from mixin that provides it"
                    })
        
        except Exception as e:
            violations.append({
                'file': str(base_class_path.relative_to(self.project_root)),
                'line': 0,
                'type': 'parse_error',
                'message': f"Failed to check methods: {e}",
                'recommendation': 'Check file syntax'
            })
        
        return violations
    
    def validate_directory(self, directory: Path, exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """
        Validate all base classes in a directory.
        
        Returns summary with violations from all validators.
        """
        if exclude_patterns is None:
            exclude_patterns = ['test_', '__pycache__', 'archive', 'archived', 'tests']
        
        base_class_files = []
        for file_path in directory.rglob('*_base.py'):
            # Skip excluded patterns
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue
            
            # Skip test files
            if 'test' in file_path.name.lower():
                continue
            
            base_class_files.append(file_path)
        
        # Validate each base class
        results = []
        for base_file in base_class_files:
            result = self.validate_base_class(base_file)
            results.append(result)
        
        # Aggregate violations
        all_violations = []
        for result in results:
            all_violations.extend(result['all_violations'])
        
        # Group by type
        by_type = {}
        for v in all_violations:
            vtype = v['type']
            if vtype not in by_type:
                by_type[vtype] = []
            by_type[vtype].append(v)
        
        return {
            'total_violations': len(all_violations),
            'base_classes_validated': len(results),
            'base_classes_valid': sum(1 for r in results if r['is_valid']),
            'base_classes_invalid': sum(1 for r in results if not r['is_valid']),
            'results': results,
            'violations_by_type': by_type,
            'all_violations': all_violations
        }
