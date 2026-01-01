#!/usr/bin/env python3
"""
Layer 3: Experience Foundation Validator Compliance Tests

Tests that validate Experience Foundation passes all validators.

WHAT: Validate validator compliance
HOW: Run DI Container and Utility validators on Experience Foundation
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add tests to path for validators
tests_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
if tests_root not in sys.path:
    sys.path.insert(0, tests_root)

from tests.fixtures.di_container_usage_validator import DIContainerUsageValidator
from tests.fixtures.utility_usage_validator import UtilityUsageValidator


class TestExperienceFoundationValidatorCompliance:
    """Test Experience Foundation validator compliance."""
    
    @pytest.fixture
    def project_root_path(self):
        """Get project root path."""
        return Path(project_root)
    
    @pytest.fixture
    def experience_foundation_dir(self, project_root_path):
        """Get Experience Foundation directory."""
        return project_root_path / 'symphainy-platform' / 'foundations' / 'experience_foundation'
    
    @pytest.fixture
    def di_validator(self, project_root_path):
        """Create DI Container validator."""
        return DIContainerUsageValidator(project_root_path)
    
    @pytest.fixture
    def utility_validator(self, project_root_path):
        """Create Utility validator."""
        return UtilityUsageValidator(project_root_path)
    
    def test_experience_foundation_di_container_compliance(self, di_validator, experience_foundation_dir):
        """Test that Experience Foundation passes DI Container validator."""
        violations = di_validator.validate_directory(experience_foundation_dir, exclude_patterns=['test_', '__pycache__', 'tests'])
        
        assert len(violations) == 0, f"Found DI Container violations: {violations}"
    
    def test_experience_foundation_utility_compliance(self, utility_validator, experience_foundation_dir):
        """Test that Experience Foundation passes Utility validator."""
        violations = utility_validator.validate_directory(experience_foundation_dir, exclude_patterns=['test_', '__pycache__', 'tests'])
        
        assert len(violations) == 0, f"Found Utility violations: {violations}"

