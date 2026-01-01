#!/usr/bin/env python3
"""
Public Works Foundation Usage Validator

Validates that services properly use Public Works Foundation (no direct infrastructure access, proper abstraction usage).
BUILDS ON: DI Container Usage Validator, Utility Usage Validator

WHAT: Validate Public Works Foundation access patterns
HOW: Check for anti-patterns (direct adapter access, bypassing abstractions, improper realm access)

Architectural Rules:
1. Smart City services CAN access Public Works abstractions directly
2. Business Enablement/Journey/Solution MUST use Smart City SOA APIs (not direct infrastructure)
3. No direct adapter instantiation (adapters created by Public Works Foundation)
4. Platform Gateway validates realm access for non-Smart City realms
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import re
import sys

# Add tests to path for import
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.fixtures.di_container_usage_validator import DIContainerUsageValidator
from tests.fixtures.utility_usage_validator import UtilityUsageValidator


class PublicWorksFoundationUsageValidator:
    """
    Validates that code properly uses Public Works Foundation.
    BUILDS ON: DIContainerUsageValidator, UtilityUsageValidator
    
    Anti-patterns to catch:
    1. Direct adapter instantiation (e.g., `RedisAdapter()`, `SupabaseAdapter()`)
    2. Business Enablement accessing infrastructure directly (should use Smart City SOA APIs)
    3. Bypassing abstractions (e.g., `adapter.client` instead of `abstraction.method()`)
    4. Direct infrastructure client access (e.g., `redis_client.get()`)
    5. Improper realm access (Business Enablement accessing session/state/auth)
    """
    
    # Adapters that should NOT be directly instantiated
    FORBIDDEN_ADAPTER_INSTANTIATION = {
        'RedisAdapter(',
        'SupabaseAdapter(',
        'ArangoAdapter(',
        'MeilisearchAdapter(',
        'GCSAdapter(',
        'FileStorageAdapter(',
        'CacheAdapter(',
        'MessageQueueAdapter(',
        'EventBusAdapter(',
    }
    
    # Infrastructure clients that should NOT be directly accessed
    FORBIDDEN_INFRASTRUCTURE_CLIENTS = {
        'redis_client',
        'supabase_client',
        'arango_client',
        'meilisearch_client',
        'gcs_client',
        'storage_client',
        'cache_client',
        'mq_client',
        'event_bus_client',
    }
    
    # Direct infrastructure access patterns (should use abstractions)
    FORBIDDEN_DIRECT_ACCESS = {
        'redis.get(',
        'redis.set(',
        'supabase.table(',
        'arango.collection(',
        'gcs.bucket(',
        'storage.bucket(',
    }
    
    # Business Enablement forbidden abstractions (should use Smart City SOA APIs)
    BUSINESS_ENABLEMENT_FORBIDDEN_ABSTRACTIONS = {
        'session',
        'state',
        'auth',
        'authorization',
    }
    
    # Smart City SOA API patterns (correct usage)
    SMART_CITY_SOA_API_PATTERNS = {
        'content_steward.',
        'data_steward.',
        'librarian.',
        'security_guard.',
        'traffic_cop.',
        'nurse.',
        'conductor.',
        'post_office.',
    }
    
    # Allowed patterns (exceptions)
    ALLOWED_PATTERNS = [
        r'#.*test',  # Test files can import
        r'from.*import.*#.*test',  # Test imports
        r'RedisAdapter.*#.*fixture',  # Test fixtures
        r'SupabaseAdapter.*#.*mock',  # Mock adapters
        r'#.*Public Works Foundation',  # Public Works Foundation can create adapters
        r'#.*registry',  # Registries can create adapters
    ]
    
    def __init__(self, project_root: Path):
        """Initialize validator."""
        self.project_root = project_root
        self.violations: List[Dict[str, Any]] = []
        
        # DI Container and Utility validators (builds on them)
        self.di_container_validator = DIContainerUsageValidator(project_root)
        self.utility_validator = UtilityUsageValidator(project_root)
    
    def _is_public_works_foundation_file(self, file_path: Path) -> bool:
        """Check if file is in Public Works Foundation (can create adapters)."""
        return 'public_works_foundation' in str(file_path) and 'tests' not in str(file_path)
    
    def _is_registry_file(self, file_path: Path) -> bool:
        """Check if file is a registry (can create adapters)."""
        return 'registry' in str(file_path) and 'tests' not in str(file_path)
    
    def _is_business_enablement_file(self, file_path: Path) -> bool:
        """Check if file is in Business Enablement realm."""
        return 'business_enablement' in str(file_path) and 'tests' not in str(file_path)
    
    def _is_journey_file(self, file_path: Path) -> bool:
        """Check if file is in Journey realm."""
        return 'journey' in str(file_path) and 'tests' not in str(file_path)
    
    def _is_solution_file(self, file_path: Path) -> bool:
        """Check if file is in Solution realm."""
        return 'solution' in str(file_path) and 'tests' not in str(file_path)
    
    def _is_smart_city_file(self, file_path: Path) -> bool:
        """Check if file is in Smart City realm."""
        return 'smart_city' in str(file_path) and 'tests' not in str(file_path)
    
    def validate_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Validate a single file for Public Works Foundation usage anti-patterns.
        
        Returns list of violations.
        """
        violations = []
        
        # Skip test files
        if self._is_test_file(file_path):
            return violations
        
        # Public Works Foundation and registries can create adapters
        is_public_works = self._is_public_works_foundation_file(file_path)
        is_registry = self._is_registry_file(file_path)
        is_business_enablement = self._is_business_enablement_file(file_path)
        is_journey = self._is_journey_file(file_path)
        is_solution = self._is_solution_file(file_path)
        is_smart_city = self._is_smart_city_file(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check for forbidden patterns
            for i, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue
                
                # Check 1: Forbidden adapter instantiation (unless Public Works Foundation or registry)
                if not is_public_works and not is_registry:
                    for forbidden_adapter in self.FORBIDDEN_ADAPTER_INSTANTIATION:
                        if forbidden_adapter in line and not line.strip().startswith('class ') and not self._is_allowed_pattern(line):
                            violations.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'type': 'forbidden_adapter_instantiation',
                                'message': f"Forbidden adapter instantiation: {line.strip()}",
                                'recommendation': f"Use Public Works Foundation abstraction: self.get_abstraction('{self._get_abstraction_name(forbidden_adapter)}')"
                            })
                
                # Check 2: Forbidden infrastructure client access
                for forbidden_client in self.FORBIDDEN_INFRASTRUCTURE_CLIENTS:
                    if forbidden_client in line and not self._is_allowed_pattern(line):
                        violations.append({
                            'file': str(file_path.relative_to(self.project_root)),
                            'line': i,
                            'type': 'forbidden_infrastructure_client_access',
                            'message': f"Forbidden infrastructure client access: {line.strip()}",
                            'recommendation': f"Use abstraction instead: self.get_abstraction('{self._get_abstraction_name_from_client(forbidden_client)}')"
                        })
                
                # Check 3: Direct infrastructure access
                for forbidden_access in self.FORBIDDEN_DIRECT_ACCESS:
                    if forbidden_access in line and not self._is_allowed_pattern(line):
                        violations.append({
                            'file': str(file_path.relative_to(self.project_root)),
                            'line': i,
                            'type': 'forbidden_direct_infrastructure_access',
                            'message': f"Forbidden direct infrastructure access: {line.strip()}",
                            'recommendation': "Use abstraction method instead"
                        })
                
                # Check 4: Business Enablement/Journey/Solution accessing forbidden abstractions
                if is_business_enablement or is_journey or is_solution:
                    for forbidden_abstraction in self.BUSINESS_ENABLEMENT_FORBIDDEN_ABSTRACTIONS:
                        # Check for direct abstraction access
                        if f'get_abstraction("{forbidden_abstraction}")' in line or f"get_abstraction('{forbidden_abstraction}')" in line:
                            violations.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'type': 'forbidden_abstraction_access',
                                'message': f"Business Enablement/Journey/Solution accessing forbidden abstraction '{forbidden_abstraction}': {line.strip()}",
                                'recommendation': f"Use Smart City SOA API instead (e.g., content_steward, data_steward, etc.)"
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
        Comprehensive validation: Check Public Works Foundation usage, DI Container usage, AND utility usage.
        
        This builds on DI Container and Utility validation - everything should:
        1. Use DI Container properly (no direct service instantiation)
        2. Use utilities via DI Container (no direct utility calls)
        3. Use Public Works Foundation properly (no direct infrastructure access)
        
        Returns combined violations from all validators.
        """
        # Get Public Works Foundation violations
        public_works_violations = self.validate_file(file_path)
        
        # Get DI Container violations
        di_container_violations = self.di_container_validator.validate_file(file_path)
        
        # Get utility violations
        utility_violations = self.utility_validator.validate_file(file_path)
        
        # Combine violations
        all_violations = public_works_violations + di_container_violations + utility_violations
        
        # Determine if valid
        is_valid = len(all_violations) == 0
        
        return {
            'file': str(file_path.relative_to(self.project_root)),
            'public_works_violations': public_works_violations,
            'di_container_violations': di_container_violations,
            'utility_violations': utility_violations,
            'all_violations': all_violations,
            'is_valid': is_valid,
            'public_works_count': len(public_works_violations),
            'di_container_count': len(di_container_violations),
            'utility_count': len(utility_violations),
            'total_count': len(all_violations)
        }
    
    def validate_directory_comprehensive(self, directory: Path, exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """
        Comprehensive validation for a directory: Check all three validators.
        
        Returns summary with violations from all validators.
        """
        # Get violations from all validators
        public_works_violations = self.validate_directory(directory, exclude_patterns)
        di_container_violations = self.di_container_validator.validate_directory(directory, exclude_patterns)
        utility_violations = self.utility_validator.validate_directory(directory, exclude_patterns)
        
        # Combine and analyze
        all_violations = public_works_violations + di_container_violations + utility_violations
        
        # Group by type
        by_type = {}
        for v in all_violations:
            vtype = v['type']
            if vtype not in by_type:
                by_type[vtype] = []
            by_type[vtype].append(v)
        
        return {
            'total_violations': len(all_violations),
            'public_works_violations': public_works_violations,
            'di_container_violations': di_container_violations,
            'utility_violations': utility_violations,
            'all_violations': all_violations,
            'violations_by_type': by_type,
            'public_works_count': len(public_works_violations),
            'di_container_count': len(di_container_violations),
            'utility_count': len(utility_violations)
        }
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        return 'test' in file_path.name.lower() or 'tests' in str(file_path)
    
    def _is_allowed_pattern(self, line: str) -> bool:
        """Check if line matches an allowed pattern."""
        for pattern in self.ALLOWED_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False
    
    def _get_abstraction_name(self, adapter_name: str) -> str:
        """Map adapter name to abstraction name."""
        mapping = {
            'RedisAdapter(': 'cache',
            'SupabaseAdapter(': 'auth',
            'ArangoAdapter(': 'content_metadata',
            'MeilisearchAdapter(': 'content_insights',
            'GCSAdapter(': 'file_management',
            'FileStorageAdapter(': 'file_management',
            'CacheAdapter(': 'cache',
            'MessageQueueAdapter(': 'messaging',
            'EventBusAdapter(': 'event_management',
        }
        return mapping.get(adapter_name, 'unknown')
    
    def _get_abstraction_name_from_client(self, client_name: str) -> str:
        """Map client name to abstraction name."""
        mapping = {
            'redis_client': 'cache',
            'supabase_client': 'auth',
            'arango_client': 'content_metadata',
            'meilisearch_client': 'content_insights',
            'gcs_client': 'file_management',
            'storage_client': 'file_management',
            'cache_client': 'cache',
            'mq_client': 'messaging',
            'event_bus_client': 'event_management',
        }
        return mapping.get(client_name, 'unknown')


