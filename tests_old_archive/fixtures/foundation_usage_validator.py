#!/usr/bin/env python3
"""
Foundation Usage Validator

Validates that realm services properly use foundations according to architectural rules.
BUILDS ON: DI Container Usage Validator, Utility Usage Validator, Public Works Foundation Usage Validator

WHAT: Validate foundation access patterns
HOW: Check for anti-patterns (improper foundation imports, direct access violations)

Architectural Rules:
1. Smart City services CAN directly access Public Works Foundation and Communications Foundation
2. Other realms (Business Enablement, Journey, Solution) MUST use Smart City SOA APIs (not direct foundation access)
3. All realms CAN access Experience Foundation and Agentic Foundation
4. Other realms can access selective Public Works abstractions via Platform Gateway (not direct foundation access)
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import sys

# Add tests to path for import
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.fixtures.di_container_usage_validator import DIContainerUsageValidator
from tests.fixtures.utility_usage_validator import UtilityUsageValidator
from tests.fixtures.public_works_foundation_usage_validator import PublicWorksFoundationUsageValidator


class FoundationUsageValidator:
    """
    Validates that code properly uses foundations according to architectural rules.
    BUILDS ON: DIContainerUsageValidator, UtilityUsageValidator, PublicWorksFoundationUsageValidator
    
    Anti-patterns to catch:
    1. Non-Smart City realms directly importing Public Works Foundation
    2. Non-Smart City realms directly importing Communications Foundation
    3. Direct foundation service instantiation (should use DI Container)
    4. Bypassing Platform Gateway for Public Works abstractions (for non-Smart City realms)
    """
    
    # Foundation services that should NOT be directly imported by non-Smart City realms
    FORBIDDEN_FOUNDATION_IMPORTS_FOR_REALMS = {
        'PublicWorksFoundationService',
        'CommunicationFoundationService',
        'from foundations.public_works_foundation',
        'from foundations.communication_foundation',
        'import public_works_foundation',
        'import communication_foundation',
    }
    
    # Foundation services that all realms CAN access
    ALLOWED_FOUNDATION_IMPORTS = {
        'ExperienceFoundationService',
        'AgenticFoundationService',
        'CuratorFoundationService',
        'from foundations.experience_foundation',
        'from foundations.agentic_foundation',
        'from foundations.curator_foundation',
        'import experience_foundation',
        'import agentic_foundation',
        'import curator_foundation',
    }
    
    # Direct foundation service instantiation patterns (should use DI Container)
    FORBIDDEN_FOUNDATION_INSTANTIATION = {
        'PublicWorksFoundationService(',
        'CommunicationFoundationService(',
        'ExperienceFoundationService(',
        'AgenticFoundationService(',
        'CuratorFoundationService(',
    }
    
    # Smart City SOA API patterns (correct usage for non-Smart City realms)
    SMART_CITY_SOA_API_PATTERNS = {
        'content_steward.',
        'data_steward.',
        'librarian.',
        'security_guard.',
        'traffic_cop.',
        'nurse.',
        'conductor.',
        'post_office.',
        'get_librarian_api',
        'get_content_steward_api',
        'get_data_steward_api',
        'get_security_guard_api',
        'get_traffic_cop_api',
        'get_nurse_api',
        'get_conductor_api',
        'get_post_office_api',
    }
    
    # Platform Gateway patterns (correct usage for Public Works abstractions)
    PLATFORM_GATEWAY_PATTERNS = {
        'get_abstraction(',
        'platform_gateway.get_abstraction',
        'self.get_abstraction',
    }
    
    # Allowed patterns (exceptions)
    ALLOWED_PATTERNS = [
        r'#.*test',  # Test files can import
        r'from.*import.*#.*test',  # Test imports
        r'#.*TYPE_CHECKING',  # Type checking imports
        r'if TYPE_CHECKING:',  # Type checking blocks
    ]
    
    def __init__(self, project_root: Path):
        """Initialize validator."""
        self.project_root = project_root
        self.violations: List[Dict[str, Any]] = []
        
        # Base validators (builds on them)
        self.di_container_validator = DIContainerUsageValidator(project_root)
        self.utility_validator = UtilityUsageValidator(project_root)
        self.public_works_validator = PublicWorksFoundationUsageValidator(project_root)
    
    def _is_smart_city_file(self, file_path: Path) -> bool:
        """Check if file is in Smart City realm."""
        return 'smart_city' in str(file_path) and 'tests' not in str(file_path)
    
    def _is_business_enablement_file(self, file_path: Path) -> bool:
        """Check if file is in Business Enablement realm."""
        return 'business_enablement' in str(file_path) and 'tests' not in str(file_path)
    
    def _is_journey_file(self, file_path: Path) -> bool:
        """Check if file is in Journey realm."""
        return 'journey' in str(file_path) and 'tests' not in str(file_path)
    
    def _is_solution_file(self, file_path: Path) -> bool:
        """Check if file is in Solution realm."""
        return 'solution' in str(file_path) and 'tests' not in str(file_path)
    
    def _is_foundation_file(self, file_path: Path) -> bool:
        """Check if file is in a foundation (foundations can import other foundations)."""
        return 'foundations' in str(file_path) and 'tests' not in str(file_path)
    
    def _is_base_file(self, file_path: Path) -> bool:
        """Check if file is in bases (base classes can have foundation imports for type hints)."""
        return 'bases' in str(file_path) and 'tests' not in str(file_path)
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        return 'test' in file_path.name.lower() or 'tests' in str(file_path)
    
    def _is_in_type_checking_block(self, lines: List[str], line_index: int) -> bool:
        """Check if line is inside a TYPE_CHECKING block."""
        in_type_checking = False
        for i in range(line_index + 1):
            line = lines[i]
            if 'if TYPE_CHECKING:' in line or 'if TYPE_CHECKING' in line:
                in_type_checking = True
            elif in_type_checking:
                # Check if we've exited the TYPE_CHECKING block
                stripped = line.strip()
                if stripped and not (stripped.startswith('    ') or stripped.startswith('\t') or stripped == ''):
                    in_type_checking = False
        return in_type_checking
    
    def validate_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Validate a single file for foundation usage anti-patterns.
        
        Returns list of violations.
        """
        violations = []
        
        # Skip test files
        if self._is_test_file(file_path):
            return violations
        
        # Foundations and bases can import other foundations
        is_foundation = self._is_foundation_file(file_path)
        is_base = self._is_base_file(file_path)
        is_smart_city = self._is_smart_city_file(file_path)
        is_business_enablement = self._is_business_enablement_file(file_path)
        is_journey = self._is_journey_file(file_path)
        is_solution = self._is_solution_file(file_path)
        
        # Determine if this is a non-Smart City realm
        is_non_smart_city_realm = (is_business_enablement or is_journey or is_solution) and not is_smart_city
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Track if we're inside a TYPE_CHECKING block
            in_type_checking = False
            
            # Check for forbidden patterns
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
                
                # Skip comments
                if line.strip().startswith('#'):
                    continue
                
                # Skip lines inside TYPE_CHECKING blocks
                if in_type_checking:
                    continue
                
                # Check 1: Non-Smart City realms importing forbidden foundations
                if is_non_smart_city_realm and not is_foundation and not is_base:
                    # First check if this is an allowed foundation import
                    is_allowed_import = False
                    for allowed_import in self.ALLOWED_FOUNDATION_IMPORTS:
                        if allowed_import in line:
                            is_allowed_import = True
                            break
                    
                    # Only flag if it's a forbidden import (not an allowed one)
                    if not is_allowed_import:
                        for forbidden_import in self.FORBIDDEN_FOUNDATION_IMPORTS_FOR_REALMS:
                            if forbidden_import in line and (line.strip().startswith('from ') or line.strip().startswith('import ')):
                                if not self._is_allowed_pattern(line):
                                    violations.append({
                                        'file': str(file_path.relative_to(self.project_root)),
                                        'line': i,
                                        'type': 'forbidden_foundation_import',
                                        'message': f"Non-Smart City realm importing forbidden foundation: {line.strip()}",
                                        'recommendation': f"Use Smart City SOA APIs instead (e.g., get_librarian_api(), get_content_steward_api())"
                                    })
                
                # Check 2: Direct foundation service instantiation (all realms should use DI Container)
                # Note: This applies to all realms, including Smart City
                if not is_foundation:
                    for forbidden_instantiation in self.FORBIDDEN_FOUNDATION_INSTANTIATION:
                        if forbidden_instantiation in line and not line.strip().startswith('class ') and not self._is_allowed_pattern(line):
                            # Check if this is a type hint or comment
                            if 'TYPE_CHECKING' in line or line.strip().startswith('#'):
                                continue
                            violations.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'type': 'forbidden_foundation_instantiation',
                                'message': f"Forbidden foundation instantiation: {line.strip()}",
                                'recommendation': f"Use DI Container: self.di_container.get_foundation_service('{self._get_foundation_name(forbidden_instantiation)}')"
                            })
                
                # Check 3: Non-Smart City realms directly accessing Public Works Foundation methods
                if is_non_smart_city_realm and not is_foundation and not is_base:
                    # Check for direct Public Works Foundation method calls
                    if 'public_works_foundation.get_' in line or 'public_works_foundation.create_' in line:
                        if not self._is_allowed_pattern(line):
                            violations.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'type': 'forbidden_direct_foundation_access',
                                'message': f"Non-Smart City realm directly accessing Public Works Foundation: {line.strip()}",
                                'recommendation': "Use Platform Gateway: self.get_abstraction('abstraction_name') or Smart City SOA APIs"
                            })
                    
                    # Check for direct Communications Foundation method calls
                    if 'communication_foundation.' in line or 'communications_foundation.' in line:
                        if not self._is_allowed_pattern(line):
                            violations.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'type': 'forbidden_direct_foundation_access',
                                'message': f"Non-Smart City realm directly accessing Communications Foundation: {line.strip()}",
                                'recommendation': "Use Smart City SOA APIs (e.g., get_post_office_api()) instead"
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
        Comprehensive validation: Check foundation usage, DI Container usage, Utility usage, AND Public Works usage.
        
        Returns combined violations from all validators.
        """
        # Get foundation violations
        foundation_violations = self.validate_file(file_path)
        
        # Get DI Container violations
        di_container_violations = self.di_container_validator.validate_file(file_path)
        
        # Get utility violations
        utility_violations = self.utility_validator.validate_file(file_path)
        
        # Get Public Works violations
        public_works_violations = self.public_works_validator.validate_file(file_path)
        
        # Combine violations
        all_violations = foundation_violations + di_container_violations + utility_violations + public_works_violations
        
        # Determine if valid
        is_valid = len(all_violations) == 0
        
        return {
            'file': str(file_path.relative_to(self.project_root)),
            'foundation_violations': foundation_violations,
            'di_container_violations': di_container_violations,
            'utility_violations': utility_violations,
            'public_works_violations': public_works_violations,
            'all_violations': all_violations,
            'is_valid': is_valid,
            'foundation_count': len(foundation_violations),
            'di_container_count': len(di_container_violations),
            'utility_count': len(utility_violations),
            'public_works_count': len(public_works_violations),
            'total_count': len(all_violations)
        }
    
    def validate_directory_comprehensive(self, directory: Path, exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """
        Comprehensive validation for a directory: Check all validators.
        
        Returns summary with violations from all validators.
        """
        # Get violations from all validators
        foundation_violations = self.validate_directory(directory, exclude_patterns)
        di_container_violations = self.di_container_validator.validate_directory(directory, exclude_patterns)
        utility_violations = self.utility_validator.validate_directory(directory, exclude_patterns)
        public_works_violations = self.public_works_validator.validate_directory(directory, exclude_patterns)
        
        # Combine and analyze
        all_violations = foundation_violations + di_container_violations + utility_violations + public_works_violations
        
        # Group by type
        by_type = {}
        for v in all_violations:
            vtype = v['type']
            if vtype not in by_type:
                by_type[vtype] = []
            by_type[vtype].append(v)
        
        return {
            'total_violations': len(all_violations),
            'foundation_violations': foundation_violations,
            'di_container_violations': di_container_violations,
            'utility_violations': utility_violations,
            'public_works_violations': public_works_violations,
            'all_violations': all_violations,
            'violations_by_type': by_type,
            'foundation_count': len(foundation_violations),
            'di_container_count': len(di_container_violations),
            'utility_count': len(utility_violations),
            'public_works_count': len(public_works_violations)
        }
    
    def _is_allowed_pattern(self, line: str) -> bool:
        """Check if line matches an allowed pattern."""
        for pattern in self.ALLOWED_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False
    
    def _get_foundation_name(self, instantiation: str) -> str:
        """Map foundation instantiation to foundation name."""
        mapping = {
            'PublicWorksFoundationService(': 'PublicWorksFoundationService',
            'CommunicationFoundationService(': 'CommunicationFoundationService',
            'ExperienceFoundationService(': 'ExperienceFoundationService',
            'AgenticFoundationService(': 'AgenticFoundationService',
            'CuratorFoundationService(': 'CuratorFoundationService',
        }
        return mapping.get(instantiation, 'unknown')

