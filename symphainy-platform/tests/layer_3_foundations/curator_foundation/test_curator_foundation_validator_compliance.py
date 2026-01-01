#!/usr/bin/env python3
"""
Layer 3: Curator Foundation Validator Compliance Tests

Tests that validate Curator Foundation passes all validators.

WHAT: Validate validator compliance
HOW: Run all validators on Curator Foundation code and verify compliance
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


class TestCuratorFoundationValidatorCompliance:
    """Test Curator Foundation validator compliance."""
    
    @pytest.fixture
    def project_root_path(self):
        """Get project root path."""
        return Path(project_root)
    
    @pytest.fixture
    def curator_foundation_dir(self, project_root_path):
        """Get Curator Foundation directory."""
        return project_root_path / 'symphainy-platform' / 'foundations' / 'curator_foundation'
    
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
    
    def test_curator_foundation_passes_di_container_validator(self, di_validator, curator_foundation_dir):
        """Test that Curator Foundation passes DI Container validator."""
        violations = di_validator.validate_directory(curator_foundation_dir)
        
        assert len(violations) == 0, f"Found {len(violations)} DI Container violations in Curator Foundation"
    
    def test_curator_foundation_passes_utility_validator(self, utility_validator, curator_foundation_dir):
        """Test that Curator Foundation passes Utility validator."""
        violations = utility_validator.validate_directory(curator_foundation_dir)
        
        assert len(violations) == 0, f"Found {len(violations)} Utility violations in Curator Foundation"
    
    def test_curator_foundation_passes_public_works_validator(self, public_works_validator, curator_foundation_dir):
        """Test that Curator Foundation passes Public Works Foundation validator."""
        violations = public_works_validator.validate_directory(curator_foundation_dir)
        
        assert len(violations) == 0, f"Found {len(violations)} Public Works Foundation violations in Curator Foundation"
    
    def test_curator_foundation_passes_all_validators(self, di_validator, utility_validator, public_works_validator, curator_foundation_dir):
        """Test that Curator Foundation passes all validators."""
        di_violations = di_validator.validate_directory(curator_foundation_dir)
        util_violations = utility_validator.validate_directory(curator_foundation_dir)
        public_works_violations = public_works_validator.validate_directory(curator_foundation_dir)
        
        total_violations = len(di_violations) + len(util_violations) + len(public_works_violations)
        
        assert total_violations == 0, f"Found {total_violations} total violations in Curator Foundation"
        assert len(di_violations) == 0, "DI Container validator found violations"
        assert len(util_violations) == 0, "Utility validator found violations"
        assert len(public_works_violations) == 0, "Public Works Foundation validator found violations"


