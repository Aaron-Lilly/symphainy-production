#!/usr/bin/env python3
"""
Utility Usage Validator

Validates that services properly use utilities via DI Container (no spaghetti code).
BUILDS ON: DI Container Usage Validator

WHAT: Validate utility access patterns
HOW: Check for anti-patterns (direct imports, bypassing utilities)
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import re
import sys

# Add tests to path for import
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.fixtures.di_container_usage_validator import DIContainerUsageValidator


class UtilityUsageValidator:
    """
    Validates that code properly uses utilities via DI Container.
    BUILDS ON: DIContainerUsageValidator
    
    Anti-patterns to catch:
    1. Direct utility imports (e.g., `import logging`, `from utilities.logging import ...`)
    2. Bypassing DI Container (e.g., `logging.getLogger()` instead of `self.get_utility("logger")`)
    3. Hardcoded utility functionality
    4. Not using utility access mixin methods
    """
    
    # Utility modules that should NOT be directly imported
    FORBIDDEN_UTILITY_IMPORTS = {
        'logging',
        'utilities.logging',
        'utilities.health',
        'utilities.telemetry',
        'utilities.security',
        'utilities.tenant',
        'utilities.validation',
        'utilities.serialization',
        'utilities.error',
        'utilities.audit',
    }
    
    # Direct utility function calls that should use DI Container instead
    FORBIDDEN_UTILITY_CALLS = {
        'logging.getLogger',
        'logging.info',
        'logging.error',
        'logging.warning',
        'logging.debug',
        'logging.critical',
    }
    
    # Allowed patterns (exceptions)
    ALLOWED_PATTERNS = [
        r'from.*logging.*import.*getLogger.*#.*test',  # Test files can import
        r'import.*logging.*#.*test',  # Test files can import
        r'logger\s*=\s*logging\.getLogger\(__name__\)',  # Module-level logger (for utilities themselves)
        r'logger\s*=\s*logging\.getLogger\(["\']\w+["\']\)',  # Named module-level logger
        r'#.*bootstrap',  # Bootstrap code
        r'#.*initialization',  # Initialization code
        r'#.*module.*level',  # Module-level code
    ]
    
    def __init__(self, project_root: Path):
        """Initialize validator."""
        self.project_root = project_root
        self.violations: List[Dict[str, Any]] = []
        
        # DI Container validator (builds on DI Container validation)
        self.di_container_validator = DIContainerUsageValidator(project_root)
    
    def _is_utility_file(self, file_path: Path) -> bool:
        """Check if file is a utility file (utilities can import other utilities)."""
        return 'utilities' in str(file_path) and 'tests' not in str(file_path)
    
    def _is_module_level_logger(self, line: str, lines: List[str], line_index: int) -> bool:
        """Check if this is a module-level logger (allowed pattern)."""
        line_stripped = line.strip()
        
        # Check for module-level logger pattern
        if re.search(r'logger\s*=\s*logging\.getLogger\(', line_stripped):
            # Check if it's at module level (not inside a class or function)
            # Look backwards to see if we're inside a class/function
            for i in range(line_index - 1, max(0, line_index - 20), -1):
                prev_line = lines[i].strip()
                # If we hit a class or function definition, it's not module-level
                if prev_line.startswith('class ') or prev_line.startswith('def '):
                    return False
                # If we hit an import, we're still at module level
                if prev_line.startswith('import ') or prev_line.startswith('from '):
                    continue
            return True
        
        return False
    
    def _has_module_level_logger_usage(self, lines: List[str], import_line_index: int) -> bool:
        """Check if import logging is followed by module-level logger usage."""
        # Look ahead for module-level logger (within next 50 lines)
        for i in range(import_line_index + 1, min(len(lines), import_line_index + 50)):
            line = lines[i].strip()
            # If we hit a class or function definition, stop looking
            if line.startswith('class ') or line.startswith('def '):
                break
            # Check if this is a module-level logger
            if re.search(r'logger\s*=\s*logging\.getLogger\(', line):
                return True
        return False
    
    def validate_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Validate a single file for utility usage anti-patterns.
        
        Returns list of violations.
        """
        violations = []
        
        # Skip utility files (utilities can import other utilities)
        if self._is_utility_file(file_path):
            return violations
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Track if we're inside a TYPE_CHECKING block
            in_type_checking = False
            
            # Check for forbidden imports
            for i, line in enumerate(lines, 1):
                # Track TYPE_CHECKING blocks
                if 'if TYPE_CHECKING:' in line or 'if TYPE_CHECKING' in line:
                    in_type_checking = True
                    continue
                if in_type_checking and (line.strip() == '' or line.startswith('    ') or line.startswith('\t')):
                    # Still inside TYPE_CHECKING block (indented)
                    continue
                elif in_type_checking:
                    # Exited TYPE_CHECKING block
                    in_type_checking = False
                
                # Skip comments and test files
                if self._is_test_file(file_path) or line.strip().startswith('#'):
                    continue
                
                # Skip lines inside TYPE_CHECKING blocks
                if in_type_checking:
                    continue
                
                # Check for forbidden utility imports
                for forbidden_import in self.FORBIDDEN_UTILITY_IMPORTS:
                    if self._matches_forbidden_import(line, forbidden_import):
                        # Allow module-level loggers (needed for initialization)
                        if forbidden_import == 'logging':
                            # Check if this line is a module-level logger assignment
                            if self._is_module_level_logger(line, lines, i - 1):
                                continue
                            # Check if import is followed by module-level logger usage
                            if self._has_module_level_logger_usage(lines, i - 1):
                                continue
                        # Allow data class imports from utilities (e.g., AuditContext, SecurityEventContext)
                        # These are type definitions, not utility function calls
                        if line.strip().startswith('from utilities.') and re.search(r'import\s+(AuditContext|SecurityEventContext|SecurityContext|TenantContext)', line):
                            continue
                        if not self._is_allowed_pattern(line):
                            violations.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'type': 'forbidden_import',
                                'message': f"Forbidden utility import: {line.strip()}",
                                'recommendation': f"Use DI Container: self.get_utility('{self._get_utility_name(forbidden_import)}')"
                            })
                
                # Check for forbidden utility calls
                for forbidden_call in self.FORBIDDEN_UTILITY_CALLS:
                    if forbidden_call in line:
                        # Allow module-level logger calls (needed for initialization)
                        if forbidden_call == 'logging.getLogger' and self._is_module_level_logger(line, lines, i - 1):
                            continue
                        if not self._is_allowed_pattern(line):
                            violations.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'type': 'forbidden_call',
                                'message': f"Forbidden utility call: {line.strip()}",
                                'recommendation': f"Use DI Container: self.get_utility('logger').info(...)"
                            })
        
        except Exception as e:
            violations.append({
                'file': str(file_path.relative_to(self.project_root)),
                'line': 0,
                'type': 'parse_error',
                'message': f"Failed to parse file: {e}",
                'recommendation': "Check file syntax"
            })
        
        return violations
    
    def validate_directory(self, directory: Path, exclude_patterns: List[str] = None) -> List[Dict[str, Any]]:
        """
        Validate all Python files in a directory.
        
        Args:
            directory: Directory to validate
            exclude_patterns: List of patterns to exclude (e.g., ['test_', '__pycache__'])
        """
        if exclude_patterns is None:
            exclude_patterns = ['test_', '__pycache__', 'archive', 'archived', 'tests']
        
        violations = []
        
        for file_path in directory.rglob('*.py'):
            # Skip excluded patterns
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue
            
            # Skip test files
            if self._is_test_file(file_path):
                continue
            
            file_violations = self.validate_file(file_path)
            violations.extend(file_violations)
        
        return violations
    
    def validate_comprehensive(self, file_path: Path) -> Dict[str, Any]:
        """
        Comprehensive validation: Check both utility usage AND DI Container usage.
        
        This builds on DI Container validation - everything should:
        1. Use DI Container properly (no direct service instantiation)
        2. Use utilities via DI Container (no direct utility calls)
        
        Returns combined violations from both validators.
        """
        # Get utility violations
        utility_violations = self.validate_file(file_path)
        
        # Get DI Container violations
        di_container_violations = self.di_container_validator.validate_file(file_path)
        
        # Combine violations
        all_violations = utility_violations + di_container_violations
        
        # Determine if valid
        is_valid = len(all_violations) == 0
        
        return {
            'file': str(file_path.relative_to(self.project_root)),
            'utility_violations': utility_violations,
            'di_container_violations': di_container_violations,
            'all_violations': all_violations,
            'is_valid': is_valid,
            'utility_count': len(utility_violations),
            'di_container_count': len(di_container_violations),
            'total_count': len(all_violations)
        }
    
    def validate_directory_comprehensive(self, directory: Path, exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """
        Comprehensive validation for a directory: Check both utility usage AND DI Container usage.
        
        Returns summary with violations from both validators.
        """
        # Get utility violations
        utility_violations = self.validate_directory(directory, exclude_patterns)
        
        # Get DI Container violations
        di_container_violations = self.di_container_validator.validate_directory(directory, exclude_patterns)
        
        # Combine and analyze
        all_violations = utility_violations + di_container_violations
        
        # Group by type
        by_type = {}
        for v in all_violations:
            vtype = v['type']
            if vtype not in by_type:
                by_type[vtype] = []
            by_type[vtype].append(v)
        
        return {
            'total_violations': len(all_violations),
            'utility_violations': utility_violations,
            'di_container_violations': di_container_violations,
            'all_violations': all_violations,
            'violations_by_type': by_type,
            'utility_count': len(utility_violations),
            'di_container_count': len(di_container_violations)
        }
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        return 'test' in file_path.name.lower() or 'tests' in str(file_path)
    
    def _matches_forbidden_import(self, line: str, forbidden_import: str) -> bool:
        """Check if line matches forbidden import pattern."""
        line = line.strip()
        
        # Check for import statements
        if line.startswith('import ') and forbidden_import in line:
            return True
        
        if line.startswith('from ') and forbidden_import in line:
            return True
        
        return False
    
    def _is_allowed_pattern(self, line: str) -> bool:
        """Check if line matches an allowed pattern."""
        for pattern in self.ALLOWED_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False
    
    def _get_utility_name(self, import_path: str) -> str:
        """Map import path to utility name."""
        mapping = {
            'logging': 'logger',
            'utilities.logging': 'logger',
            'utilities.health': 'health',
            'utilities.telemetry': 'telemetry',
            'utilities.security': 'security',
            'utilities.tenant': 'tenant',
            'utilities.validation': 'validation',
            'utilities.serialization': 'serialization',
            'utilities.error': 'error_handler',
            'utilities.audit': 'audit',
        }
        return mapping.get(import_path, 'unknown')
