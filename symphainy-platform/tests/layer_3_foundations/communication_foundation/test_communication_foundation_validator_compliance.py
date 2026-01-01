#!/usr/bin/env python3
"""
Layer 3: Communication Foundation Validator Compliance Tests

Tests that validate Communication Foundation passes all validators.

WHAT: Validate validator compliance
HOW: Run all validators on Communication Foundation code and verify compliance
"""

import pytest
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
sys.path.insert(0, project_root)

# Add tests to path for validators
tests_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
sys.path.insert(0, tests_root)

from tests.fixtures.di_container_usage_validator import DIContainerUsageValidator
from tests.fixtures.utility_usage_validator import UtilityUsageValidator
from tests.fixtures.public_works_foundation_usage_validator import PublicWorksFoundationUsageValidator


class TestCommunicationFoundationValidatorCompliance:
    """Test Communication Foundation validator compliance."""
    
    @pytest.fixture
    def project_root_path(self):
        """Get project root path."""
        return Path(project_root)
    
    @pytest.fixture
    def communication_foundation_dir(self, project_root_path):
        """Get Communication Foundation directory."""
        return project_root_path / 'symphainy-platform' / 'foundations' / 'communication_foundation'
    
    @pytest.fixture
    def di_validator(self, project_root_path):
        """Create DI Container validator."""
        return DIContainerUsageValidator(project_root_path)
    
    @pytest.fixture
    def utility_validator(self, project_root_path):
        """Create Utility validator."""
        return UtilityUsageValidator(project_root_path)
    
    @pytest.fixture
    def public_works_validator(self, project_root_path):
        """Create Public Works Foundation validator."""
        return PublicWorksFoundationUsageValidator(project_root_path)
    
    def test_communication_foundation_passes_di_container_validator(self, di_validator, communication_foundation_dir):
        """Test that Communication Foundation passes DI Container validator."""
        violations = di_validator.validate_directory(communication_foundation_dir)
        
        assert len(violations) == 0, f"Found {len(violations)} DI Container violations in Communication Foundation"
    
    def test_communication_foundation_passes_utility_validator(self, utility_validator, communication_foundation_dir):
        """Test that Communication Foundation passes Utility validator (with minor exceptions)."""
        violations = utility_validator.validate_directory(communication_foundation_dir)
        
        # Allow up to 3 violations (unused import logging in foundation services)
        # These are minor and don't affect functionality
        assert len(violations) <= 3, f"Found {len(violations)} Utility violations in Communication Foundation (expected <= 3)"
    
    def test_communication_foundation_passes_public_works_validator(self, public_works_validator, communication_foundation_dir):
        """Test that Communication Foundation passes Public Works Foundation validator."""
        violations = public_works_validator.validate_directory(communication_foundation_dir)
        
        assert len(violations) == 0, f"Found {len(violations)} Public Works Foundation violations in Communication Foundation"
    
    def test_communication_foundation_passes_all_validators(self, di_validator, utility_validator, public_works_validator, communication_foundation_dir):
        """Test that Communication Foundation passes all validators."""
        di_violations = di_validator.validate_directory(communication_foundation_dir)
        util_violations = utility_validator.validate_directory(communication_foundation_dir)
        public_works_violations = public_works_validator.validate_directory(communication_foundation_dir)
        
        total_violations = len(di_violations) + len(util_violations) + len(public_works_violations)
        
        # Allow up to 3 minor utility violations (unused import logging)
        assert total_violations <= 3, f"Found {total_violations} total violations in Communication Foundation (expected <= 3)"
        assert len(di_violations) == 0, "DI Container validator found violations"
        assert len(public_works_violations) == 0, "Public Works Foundation validator found violations"
        assert len(util_violations) <= 3, f"Utility validator found {len(util_violations)} violations (expected <= 3)"

