#!/usr/bin/env python3
"""
Layer 2: Telemetry Reporting Utility Tests

Tests that validate telemetry reporting utility works correctly.

WHAT: Validate telemetry reporting utility
HOW: Test TelemetryReportingUtility
"""

import pytest

import os
from unittest.mock import Mock, patch

from utilities.telemetry_reporting.telemetry_reporting_utility import TelemetryReportingUtility

class TestTelemetryReportingUtility:
    """Test telemetry reporting utility."""
    
    @pytest.fixture
    def telemetry_utility(self):
        """Create telemetry reporting utility instance."""
        return TelemetryReportingUtility("test_service")
    
    def test_telemetry_utility_initialization(self, telemetry_utility):
        """Test that telemetry utility initializes correctly."""
        assert telemetry_utility is not None
        assert telemetry_utility.service_name == "test_service"  # Uses service_name, not realm_name
        assert telemetry_utility.is_bootstrapped is False
    
    def test_bootstrap_telemetry_utility(self, telemetry_utility):
        """Test bootstrapping telemetry utility."""
        mock_di_container = Mock()
        telemetry_utility.bootstrap(mock_di_container)
        
        assert telemetry_utility.is_bootstrapped is True
        assert telemetry_utility.bootstrap_provider == mock_di_container
