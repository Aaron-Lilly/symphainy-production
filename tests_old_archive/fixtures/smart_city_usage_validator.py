#!/usr/bin/env python3
"""
Smart City Usage Validator

Validates that upstream realms (Business Enablement, Journey, Solution) properly use:
1. Smart City SOA APIs (not direct Smart City service access)
2. Platform Gateway for Public Works abstractions (not direct foundation access)
3. DI Container and Utility patterns

BUILDS ON: DI Container Usage Validator, Utility Usage Validator, Foundation Usage Validator

WHAT: Validate Smart City SOA API and Platform Gateway usage patterns
HOW: Check for anti-patterns (direct service access, bypassing SOA APIs, direct foundation access)

Architectural Rules:
1. Upstream realms MUST use Smart City SOA APIs (get_librarian_api(), get_content_steward_api(), etc.)
2. Upstream realms MUST use Platform Gateway for Public Works abstractions (get_abstraction())
3. Upstream realms MUST NOT directly import or instantiate Smart City services
4. Upstream realms MUST NOT directly access Public Works Foundation (use Platform Gateway)
5. All realms MUST use DI Container and Utilities correctly
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
from tests.fixtures.foundation_usage_validator import FoundationUsageValidator


class SmartCityUsageValidator:
    """
    Validates that upstream realms properly use Smart City SOA APIs and Platform Gateway.
    BUILDS ON: DIContainerUsageValidator, UtilityUsageValidator, FoundationUsageValidator
    
    Anti-patterns to catch:
    1. Direct Smart City service imports (should use SOA APIs)
    2. Direct Smart City service instantiation (should use SOA APIs)
    3. Direct Public Works Foundation access (should use Platform Gateway)
    4. Bypassing SOA APIs for Smart City services
    5. Bypassing Platform Gateway for Public Works abstractions
    """
    
    # Forbidden: Direct Smart City service imports (upstream realms should use SOA APIs)
    FORBIDDEN_SMART_CITY_IMPORTS = {
        'from backend.smart_city.services.librarian',
        'from backend.smart_city.services.content_steward',
        'from backend.smart_city.services.data_steward',
        'from backend.smart_city.services.security_guard',
        'from backend.smart_city.services.traffic_cop',
        'from backend.smart_city.services.nurse',
        'from backend.smart_city.services.conductor',
        'from backend.smart_city.services.post_office',
        'from backend.smart_city.services.city_manager',
        'import librarian_service',
        'import content_steward_service',
        'import data_steward_service',
        'import security_guard_service',
        'import traffic_cop_service',
        'import nurse_service',
        'import conductor_service',
        'import post_office_service',
        'import city_manager_service',
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
    
    # Required: Smart City SOA API patterns (correct usage)
    REQUIRED_SMART_CITY_SOA_API_PATTERNS = {
        'get_librarian_api',
        'get_content_steward_api',
        'get_data_steward_api',
        'get_security_guard_api',
        'get_traffic_cop_api',
        'get_nurse_api',
        'get_conductor_api',
        'get_post_office_api',
        'get_city_manager_api',
        'get_smart_city_api',  # Generic method
    }
    
    # Forbidden: Direct Public Works Foundation access (should use Platform Gateway)
    FORBIDDEN_PUBLIC_WORKS_DIRECT_ACCESS = {
        'public_works_foundation.get_abstraction',
        'public_works.get_abstraction',
        'self.public_works_foundation',
        'di_container.public_works_foundation.get_abstraction',
    }
    
    # Required: Platform Gateway patterns (correct usage)
    REQUIRED_PLATFORM_GATEWAY_PATTERNS = {
        'get_abstraction(',
        'platform_gateway.get_abstraction',
        'self.get_abstraction',
        'ctx.get_abstraction',  # RealmContext pattern
    }
    
    # Allowed Public Works abstractions via Platform Gateway (for upstream realms)
    ALLOWED_PLATFORM_GATEWAY_ABSTRACTIONS = {
        'content_metadata',
        'content_schema',
        'content_insights',
        'file_management',
        'llm',
        'document_intelligence',
        'bpmn_processing',
        'sop_processing',
        'sop_enhancement',
        'strategic_planning',
        'financial_analysis',
        'session',  # Journey realm
    }
    
    # Allowed patterns (exceptions)
    ALLOWED_PATTERNS = [
        r'#.*test',  # Test files can import
        r'from.*import.*#.*test',  # Test imports
        r'#.*TYPE_CHECKING',  # Type checking imports
        r'if TYPE_CHECKING:',  # Type checking blocks
        r'#.*validator',  # Validator files can import
    ]
    
    def __init__(self, project_root: Path):
        """Initialize validator."""
        self.project_root = project_root
        self.violations: List[Dict[str, Any]] = []
        
        # Base validators (builds on them)
        self.di_container_validator = DIContainerUsageValidator(project_root)
        self.utility_validator = UtilityUsageValidator(project_root)
        self.foundation_validator = FoundationUsageValidator(project_root)
    
    def _is_smart_city_file(self, file_path: Path) -> bool:
        """Check if file is in Smart City realm."""
        return 'smart_city' in str(file_path) and 'tests' not in str(file_path)
    
    def _is_upstream_realm_file(self, file_path: Path) -> bool:
        """Check if file is in an upstream realm (Business Enablement, Journey, Solution)."""
        return (
            ('business_enablement' in str(file_path) or
             'journey' in str(file_path) or
             'solution' in str(file_path)) and
            'tests' not in str(file_path) and
            'smart_city' not in str(file_path)
        )
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        return 'test' in file_path.name.lower() or 'tests' in str(file_path)
    
    def _is_in_type_checking_block(self, lines: List[str], line_index: int) -> bool:
        """Check if line is inside a TYPE_CHECKING block."""
        in_block = False
        for i in range(line_index + 1):
            line = lines[i].strip()
            if 'if TYPE_CHECKING:' in line or 'if typing.TYPE_CHECKING:' in line:
                in_block = True
            elif in_block and (line.startswith('import ') or line.startswith('from ')):
                continue
            elif in_block and line and not line.startswith('#'):
                # Check if we've left the TYPE_CHECKING block
                if not (line.startswith('import ') or line.startswith('from ') or line.startswith('    ') or line == ''):
                    in_block = False
        return in_block
    
    def _is_in_comment(self, line: str) -> bool:
        """Check if line is a comment."""
        stripped = line.strip()
        return stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''")
    
    def validate_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Validate a single file for Smart City usage patterns.
        
        Returns list of violations found.
        """
        violations = []
        
        # Skip test files, Smart City files, and base files
        if self._is_test_file(file_path) or self._is_smart_city_file(file_path):
            return violations
        
        # Only validate upstream realm files
        if not self._is_upstream_realm_file(file_path):
            return violations
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if self._is_in_comment(line):
                    continue
                
                # Skip TYPE_CHECKING blocks
                if self._is_in_type_checking_block(lines, line_num - 1):
                    continue
                
                # Check for forbidden Smart City service imports
                for forbidden_pattern in self.FORBIDDEN_SMART_CITY_IMPORTS:
                    if forbidden_pattern in line:
                        violations.append({
                            'file': str(file_path.relative_to(self.project_root)),
                            'line': line_num,
                            'type': 'forbidden_smart_city_import',
                            'message': f'Forbidden Smart City service import/instantiation: {forbidden_pattern}',
                            'recommendation': f'Use Smart City SOA APIs instead: await self.get_librarian_api(), await self.get_content_steward_api(), etc.'
                        })
                
                # Check for direct Public Works Foundation access (should use Platform Gateway)
                for forbidden_pattern in self.FORBIDDEN_PUBLIC_WORKS_DIRECT_ACCESS:
                    if forbidden_pattern in line:
                        violations.append({
                            'file': str(file_path.relative_to(self.project_root)),
                            'line': line_num,
                            'type': 'forbidden_public_works_direct_access',
                            'message': f'Forbidden direct Public Works Foundation access: {forbidden_pattern}',
                            'recommendation': 'Use Platform Gateway: self.get_abstraction("abstraction_name") or ctx.get_abstraction("abstraction_name")'
                        })
        
        except Exception as e:
            violations.append({
                'file': str(file_path.relative_to(self.project_root)),
                'line': 0,
                'type': 'validation_error',
                'message': f'Error validating file: {str(e)}',
                'recommendation': 'Check file syntax and permissions'
            })
        
        return violations
    
    def validate_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """Validate all Python files in a directory."""
        all_violations = []
        
        for file_path in directory.rglob('*.py'):
            violations = self.validate_file(file_path)
            all_violations.extend(violations)
        
        return all_violations
    
    def validate_realm(self, realm_name: str) -> Dict[str, Any]:
        """
        Validate a specific realm (business_enablement, journey, solution).
        
        Returns comprehensive validation results including:
        - Smart City usage violations
        - DI Container violations
        - Utility violations
        - Foundation usage violations
        """
        # project_root should already point to symphainy-platform
        realm_path = self.project_root / 'backend' / realm_name
        
        if not realm_path.exists():
            return {
                'realm': realm_name,
                'status': 'error',
                'error': f'Realm directory not found: {realm_path}',
                'violations': []
            }
        
        # Validate Smart City usage patterns
        smart_city_violations = self.validate_directory(realm_path)
        
        # Validate DI Container usage (returns list of violations)
        di_violations = self.di_container_validator.validate_directory(realm_path)
        
        # Validate Utility usage (returns list of violations)
        util_violations = self.utility_validator.validate_directory(realm_path)
        
        # Validate Foundation usage (returns list of violations)
        foundation_violations = self.foundation_validator.validate_directory(realm_path)
        
        # Combine all violations
        all_violations = smart_city_violations + di_violations + util_violations + foundation_violations
        
        return {
            'realm': realm_name,
            'status': 'success',
            'total_violations': len(all_violations),
            'smart_city_violations': len(smart_city_violations),
            'di_container_violations': len(di_violations),
            'utility_violations': len(util_violations),
            'foundation_violations': len(foundation_violations),
            'violations': all_violations,
            'smart_city_violations_detail': smart_city_violations,
            'di_container_violations_detail': di_violations,
            'utility_violations_detail': util_violations,
            'foundation_violations_detail': foundation_violations,
        }
    
    def validate_all_upstream_realms(self) -> Dict[str, Any]:
        """Validate all upstream realms (Business Enablement, Journey, Solution)."""
        realms = ['business_enablement', 'journey', 'solution']
        results = {}
        
        for realm in realms:
            results[realm] = self.validate_realm(realm)
        
        # Calculate totals
        total_violations = sum(r.get('total_violations', 0) for r in results.values())
        total_smart_city = sum(r.get('smart_city_violations', 0) for r in results.values())
        total_di = sum(r.get('di_container_violations', 0) for r in results.values())
        total_util = sum(r.get('utility_violations', 0) for r in results.values())
        total_foundation = sum(r.get('foundation_violations', 0) for r in results.values())
        
        return {
            'status': 'success',
            'realms_validated': realms,
            'total_violations': total_violations,
            'total_smart_city_violations': total_smart_city,
            'total_di_container_violations': total_di,
            'total_utility_violations': total_util,
            'total_foundation_violations': total_foundation,
            'realm_results': results,
        }

