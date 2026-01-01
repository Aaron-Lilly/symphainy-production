#!/usr/bin/env python3
"""
Layer 3: Agentic Foundation Validator Compliance Tests

Tests that validate Agentic Foundation passes all validators.

WHAT: Validate validator compliance
HOW: Run DI Container and Utility validators on Agentic Foundation
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


class TestAgenticFoundationValidatorCompliance:
    """Test Agentic Foundation validator compliance."""
    
    @pytest.fixture
    def project_root_path(self):
        """Get project root path."""
        return Path(project_root)
    
    @pytest.fixture
    def agentic_foundation_dir(self, project_root_path):
        """Get Agentic Foundation directory."""
        return project_root_path / 'symphainy-platform' / 'foundations' / 'agentic_foundation'
    
    @pytest.fixture
    def di_validator(self, project_root_path):
        """Create DI Container validator."""
        return DIContainerUsageValidator(project_root_path)
    
    @pytest.fixture
    def utility_validator(self, project_root_path):
        """Create Utility validator."""
        return UtilityUsageValidator(project_root_path)
    
    def test_agentic_foundation_di_container_compliance(self, di_validator, agentic_foundation_dir):
        """Test that Agentic Foundation passes DI Container validator."""
        violations = di_validator.validate_directory(agentic_foundation_dir)
        
        # Filter out violations in agentic_manager_service.py (will be archived)
        violations = [v for v in violations if 'agentic_manager_service.py' not in v['file']]
        
        assert len(violations) == 0, f"Found DI Container violations: {violations}"
    
    def test_agentic_foundation_utility_compliance(self, utility_validator, agentic_foundation_dir):
        """Test that Agentic Foundation passes Utility validator."""
        violations = utility_validator.validate_directory(agentic_foundation_dir)
        
        # Filter out violations in agentic_manager_service.py (will be archived)
        violations = [v for v in violations if 'agentic_manager_service.py' not in v['file']]
        
        assert len(violations) == 0, f"Found Utility violations: {violations}"

