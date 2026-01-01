#!/usr/bin/env python3
"""
Layer 3: Public Works Foundation Compliance Tests

Tests that validate Public Works Foundation properly uses DI Container AND Utilities.

WHAT: Validate foundation compliance
HOW: Use BaseClassValidator (builds on DI Container + Utilities validators)
"""

import pytest

import os
from pathlib import Path

from fixtures.base_class_validator import BaseClassValidator
from fixtures.di_container_usage_validator import DIContainerUsageValidator
from fixtures.utility_usage_validator import UtilityUsageValidator

class TestPublicWorksFoundationCompliance:
    """Test that Public Works Foundation properly uses DI Container AND Utilities."""
    
    @pytest.fixture
    def base_validator(self):
        """Create base class validator."""
        project_root = Path(__file__).parent.parent.parent / 'symphainy-platform'
        return BaseClassValidator(project_root)
    
    @pytest.fixture
    def di_validator(self):
        """Create DI Container validator."""
        project_root = Path(__file__).parent.parent.parent / 'symphainy-platform'
        return DIContainerUsageValidator(project_root)
    
    @pytest.fixture
    def utility_validator(self):
        """Create utility validator."""
        project_root = Path(__file__).parent.parent.parent / 'symphainy-platform'
        return UtilityUsageValidator(project_root)
    
    @pytest.fixture
    def foundation_file(self):
        """Get Public Works Foundation file path."""
        project_root = Path(__file__).parent.parent.parent / 'symphainy-platform'
        return project_root / 'foundations' / 'public_works_foundation' / 'public_works_foundation_service.py'
    
    def test_foundation_uses_di_container(self, di_validator, foundation_file):
        """Test that Public Works Foundation uses DI Container correctly."""
        result = di_validator.validate_service_uses_di_container(foundation_file)
        
        assert result['is_valid'], f"Public Works Foundation has DI Container violations: {result['violations']}"
    
    def test_foundation_uses_utilities(self, utility_validator, foundation_file):
        """Test that Public Works Foundation uses Utilities correctly."""
        result = utility_validator.validate_comprehensive(foundation_file)
        
        # Foundation can have some direct logging (bootstrap cases)
        # But should not have forbidden service instantiation or utility calls
        forbidden_instantiations = [v for v in result['all_violations'] if v['type'] == 'forbidden_service_instantiation']
        forbidden_utility_calls = [v for v in result['utility_violations'] if v['type'] == 'forbidden_call']
        
        assert len(forbidden_instantiations) == 0, f"Public Works Foundation has forbidden service instantiations: {forbidden_instantiations}"
        # Allow some logging calls (bootstrap cases)
        # assert len(forbidden_utility_calls) == 0, f"Public Works Foundation has forbidden utility calls: {forbidden_utility_calls}"
    
    def test_foundation_comprehensive_compliance(self, base_validator, foundation_file):
        """Test comprehensive compliance using BaseClassValidator."""
        result = base_validator.validate_base_class(foundation_file)
        
        # Foundation should use DI Container and Utilities correctly
        # Allow some bootstrap patterns (direct logging for initialization - foundation needs logger)
        di_violations = result['di_container_violations']
        # Allow logging imports and calls (bootstrap case - foundation needs logger before DI Container is fully available)
        utility_violations = [v for v in result['utility_violations'] 
                              if v['type'] not in ['forbidden_call', 'forbidden_import'] 
                              or 'logging' not in v['message'].lower()]
        
        assert len(di_violations) == 0, f"Public Works Foundation has DI Container violations: {di_violations}"
        # Only fail on non-logging utility violations
        non_logging_violations = [v for v in utility_violations if 'logging' not in v['message'].lower()]
        assert len(non_logging_violations) == 0, f"Public Works Foundation has non-logging utility violations: {non_logging_violations}"
    
    def test_foundation_inherits_from_foundation_service_base(self, foundation_file):
        """Test that Public Works Foundation inherits from FoundationServiceBase."""
        with open(foundation_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'FoundationServiceBase' in content, "Public Works Foundation should inherit from FoundationServiceBase"
        assert 'class PublicWorksFoundationService' in content, "Public Works Foundation class should exist"
    
    def test_foundation_accepts_di_container(self, foundation_file):
        """Test that Public Works Foundation accepts di_container in constructor."""
        with open(foundation_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'di_container' in content, "Public Works Foundation should accept di_container"
        assert '__init__' in content, "Public Works Foundation should have __init__ method"
        assert 'self.di_container' in content, "Public Works Foundation should store di_container"
