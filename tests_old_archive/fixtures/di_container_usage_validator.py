#!/usr/bin/env python3
"""
DI Container Usage Validator

Validates that services properly use DI Container (no bypassing, no direct instantiation).

WHAT: Validate DI Container access patterns
HOW: Check for anti-patterns (direct instantiation, bypassing DI Container)
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import re


class DIContainerUsageValidator:
    """
    Validates that code properly uses DI Container.
    
    Anti-patterns to catch:
    1. Direct service instantiation (e.g., `MyService()` instead of `di_container.get_service()`)
    2. Direct foundation instantiation (e.g., `PublicWorksFoundationService()`)
    3. Creating new DI Container instances (e.g., `DIContainerService()`)
    4. Bypassing DI Container for service access
    5. Direct imports of services that should come from DI Container
    """
    
    # Services that should NOT be directly instantiated
    FORBIDDEN_SERVICE_INSTANTIATION = {
        'PublicWorksFoundationService(',
        'CommunicationFoundationService(',
        'CuratorFoundationService(',
        'AgenticFoundationService(',
        'ExperienceFoundationService(',
        'LibrarianService(',
        'ContentStewardService(',
        'DataStewardService(',
        'SecurityGuardService(',
        'TrafficCopService(',
        'NurseService(',
        'ConductorService(',
        'PostOfficeService(',
        'CityManagerService(',
    }
    
    # DI Container patterns that should NOT be used (creating new instances)
    FORBIDDEN_DI_CONTAINER_PATTERNS = {
        'DIContainerService(',
        'DIContainerService(',
        'di_container = DIContainerService',
        'self.di_container = DIContainerService',
    }
    
    # Direct service imports that should use DI Container instead
    # Note: Agentic, Experience, and Curator Foundations are allowed for all realms
    # Public Works and Communication Foundations are only allowed for Smart City realm
    FORBIDDEN_SERVICE_IMPORTS = {
        'from foundations.public_works_foundation',  # Only allowed for Smart City
        'from foundations.communication_foundation',  # Only allowed for Smart City
        'from backend.smart_city.roles.librarian',
        'from backend.smart_city.roles.content_steward',
        'from backend.smart_city.roles.data_steward',
        'from backend.smart_city.roles.security_guard',
    }
    
    # Foundation imports that are allowed for all realms (not forbidden)
    ALLOWED_FOUNDATION_IMPORTS = {
        'from foundations.agentic_foundation',
        'from foundations.experience_foundation',
        'from foundations.curator_foundation',
    }
    
    # Foundation imports that are only allowed for Smart City realm
    SMART_CITY_ONLY_FOUNDATION_IMPORTS = {
        'from foundations.public_works_foundation',
        'from foundations.communication_foundation',
    }
    
    # Allowed patterns (exceptions)
    ALLOWED_PATTERNS = [
        r'#.*test',  # Test files can import
        r'from.*import.*#.*test',  # Test imports
        r'DIContainerService.*#.*fixture',  # Test fixtures
        r'DIContainerService.*#.*mock',  # Mock DI Container
    ]
    
    def __init__(self, project_root: Path):
        """Initialize validator."""
        self.project_root = project_root
        self.violations: List[Dict[str, Any]] = []
    
    def validate_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Validate a single file for DI Container usage anti-patterns.
        
        Returns list of violations.
        """
        violations = []
        
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
                
                # Skip comments and test files
                if self._is_test_file(file_path) or line.strip().startswith('#'):
                    continue
                
                # Skip lines inside TYPE_CHECKING blocks
                if in_type_checking:
                    continue
                
                # Check for forbidden service instantiation
                for forbidden_instantiation in self.FORBIDDEN_SERVICE_INSTANTIATION:
                    if forbidden_instantiation in line and not line.strip().startswith('class ') and not self._is_allowed_pattern(line):
                        violations.append({
                            'file': str(file_path.relative_to(self.project_root)),
                            'line': i,
                            'type': 'forbidden_service_instantiation',
                            'message': f"Forbidden service instantiation: {line.strip()}",
                            'recommendation': f"Use DI Container: self.di_container.get_service('{self._get_service_name(forbidden_instantiation)}')"
                        })
                
                # Check for forbidden DI Container creation
                for forbidden_pattern in self.FORBIDDEN_DI_CONTAINER_PATTERNS:
                    if forbidden_pattern in line and not self._is_allowed_pattern(line):
                        violations.append({
                            'file': str(file_path.relative_to(self.project_root)),
                            'line': i,
                            'type': 'forbidden_di_container_creation',
                            'message': f"Forbidden DI Container creation: {line.strip()}",
                            'recommendation': "Use DI Container passed via constructor: self.di_container"
                        })
                
                # Check for forbidden service imports
                for forbidden_import in self.FORBIDDEN_SERVICE_IMPORTS:
                    if self._matches_forbidden_import(line, forbidden_import):
                        # Allow same-package imports (foundations can import their own components)
                        if self._is_same_package_import(line, file_path):
                            continue
                        # Skip if inside TYPE_CHECKING block
                        if in_type_checking:
                            continue
                        # Check if this is a Smart City-only foundation import
                        if forbidden_import in self.SMART_CITY_ONLY_FOUNDATION_IMPORTS:
                            # Allow if file is in Smart City realm
                            if self._is_smart_city_file(file_path):
                                continue
                        # Check if this is an allowed foundation import (Agentic, Experience, Curator)
                        is_allowed_foundation = False
                        for allowed_import in self.ALLOWED_FOUNDATION_IMPORTS:
                            if allowed_import in line:
                                is_allowed_foundation = True
                                break
                        if is_allowed_foundation:
                            continue
                        if not self._is_allowed_pattern(line):
                            violations.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'type': 'forbidden_service_import',
                                'message': f"Forbidden service import: {line.strip()}",
                                'recommendation': f"Use DI Container: self.di_container.get_service('{self._get_service_name_from_import(forbidden_import)}')"
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
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        return 'test' in file_path.name.lower() or 'tests' in str(file_path)
    
    def _is_smart_city_file(self, file_path: Path) -> bool:
        """Check if file is in Smart City realm."""
        return 'smart_city' in str(file_path) and 'tests' not in str(file_path)
    
    def _is_same_package_import(self, line: str, file_path: Path) -> bool:
        """Check if import is within same package/foundation."""
        if not line.strip().startswith('from '):
            return False
        
        # Extract package from file path
        file_str = str(file_path)
        
        # Extract package from import
        import_part = line.split('from ')[1].split(' import')[0].strip()
        
        # Check if import is within same foundation/package
        # e.g., foundations.public_works_foundation.* importing from foundations.public_works_foundation.*
        if 'foundations.public_works_foundation' in file_str and 'foundations.public_works_foundation' in import_part:
            return True
        if 'foundations.curator_foundation' in file_str and 'foundations.curator_foundation' in import_part:
            return True
        if 'foundations.communication_foundation' in file_str and 'foundations.communication_foundation' in import_part:
            return True
        if 'foundations.agentic_foundation' in file_str and 'foundations.agentic_foundation' in import_part:
            return True
        if 'foundations.experience_foundation' in file_str and 'foundations.experience_foundation' in import_part:
            return True
        
        # Check for same package within a foundation
        # e.g., composition_services importing from composition_services
        file_parts = file_str.split('/')
        import_parts = import_part.split('.')
        
        # Match foundation name
        for i, part in enumerate(file_parts):
            if 'foundation' in part and i + 1 < len(file_parts):
                foundation_name = file_parts[i]
                if foundation_name in import_part:
                    # Check if it's importing from same foundation
                    if any(foundation_name in imp_part for imp_part in import_parts):
                        return True
        
        return False
    
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
    
    def _get_service_name(self, instantiation: str) -> str:
        """Map service instantiation to service name."""
        mapping = {
            'PublicWorksFoundationService(': 'public_works_foundation',
            'CommunicationFoundationService(': 'communication_foundation',
            'CuratorFoundationService(': 'curator_foundation',
            'AgenticFoundationService(': 'agentic_foundation',
            'ExperienceFoundationService(': 'experience_foundation',
            'LibrarianService(': 'librarian',
            'ContentStewardService(': 'content_steward',
            'DataStewardService(': 'data_steward',
            'SecurityGuardService(': 'security_guard',
            'TrafficCopService(': 'traffic_cop',
            'NurseService(': 'nurse',
            'ConductorService(': 'conductor',
            'PostOfficeService(': 'post_office',
            'CityManagerService(': 'city_manager',
        }
        return mapping.get(instantiation, 'unknown')
    
    def _get_service_name_from_import(self, import_path: str) -> str:
        """Map import path to service name."""
        mapping = {
            'from foundations.public_works_foundation': 'public_works_foundation',
            'from foundations.communication_foundation': 'communication_foundation',
            'from foundations.curator_foundation': 'curator_foundation',
            'from foundations.agentic_foundation': 'agentic_foundation',
            'from foundations.experience_foundation': 'experience_foundation',
            'from backend.smart_city.roles.librarian': 'librarian',
            'from backend.smart_city.roles.content_steward': 'content_steward',
            'from backend.smart_city.roles.data_steward': 'data_steward',
            'from backend.smart_city.roles.security_guard': 'security_guard',
        }
        return mapping.get(import_path, 'unknown')
    
    def validate_service_uses_di_container(self, service_path: Path) -> Dict[str, Any]:
        """
        Validate that a service properly uses DI Container.
        
        Checks:
        1. Accepts di_container in constructor
        2. Uses di_container.get_service() instead of direct instantiation
        3. Does not create new DI Container instances
        """
        violations = self.validate_file(service_path)
        
        # Additional check: verify it accepts di_container
        try:
            with open(service_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            accepts_di_container = 'di_container' in content and ('__init__' in content or 'def __init__' in content)
            uses_get_service = 'get_service' in content or 'di_container.get' in content
            
            if not accepts_di_container:
                violations.append({
                    'file': str(service_path.relative_to(self.project_root)),
                    'line': 0,
                    'type': 'missing_di_container',
                    'message': 'Service does not accept di_container in constructor',
                    'recommendation': 'Add di_container parameter to __init__ method'
                })
            
            if not uses_get_service and accepts_di_container:
                violations.append({
                    'file': str(service_path.relative_to(self.project_root)),
                    'line': 0,
                    'type': 'unused_di_container',
                    'message': 'Service accepts di_container but never uses get_service()',
                    'recommendation': 'Use self.di_container.get_service() to access services'
                })
        
        except Exception as e:
            violations.append({
                'file': str(service_path.relative_to(self.project_root)),
                'line': 0,
                'type': 'parse_error',
                'message': f"Failed to validate service: {e}",
                'recommendation': 'Check file syntax'
            })
        
        return {
            'file': str(service_path.relative_to(self.project_root)),
            'violations': violations,
            'is_valid': len(violations) == 0
        }
