#!/usr/bin/env python3
"""
Layer 0: Platform Startup Validator Tests

Tests that use the Platform Startup Validator to verify platform startup worked correctly.

WHAT: Validate platform startup using validator
HOW: Use Platform Startup Validator to check platform health and readiness
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

# Add tests directory to path for validator import
tests_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, tests_root)

from tests.fixtures.platform_startup_validator import PlatformStartupValidator


class TestPlatformStartupValidator:
    """Test platform startup validator."""
    
    @pytest.fixture
    def validator(self):
        """Create Platform Startup Validator instance."""
        return PlatformStartupValidator(base_url="http://localhost:8000", timeout=5)
    
    def test_validator_initializes(self, validator):
        """Test that validator can be initialized."""
        assert validator is not None
        assert validator.base_url == "http://localhost:8000"
        assert validator.timeout == 5
        assert hasattr(validator, 'validate_platform_startup')
        assert hasattr(validator, 'validate_foundation_health')
        assert hasattr(validator, 'validate_all_foundations')
        assert hasattr(validator, 'validate_platform_readiness')
    
    @pytest.mark.asyncio
    async def test_validator_has_validate_platform_startup_method(self, validator):
        """Test that validator has validate_platform_startup method."""
        assert callable(validator.validate_platform_startup)
        
        # Should return validation results (even if platform not running)
        result = await validator.validate_platform_startup()
        
        assert result is not None
        assert 'is_valid' in result
        assert 'checks' in result
        assert 'violations' in result
        assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_validator_has_validate_foundation_health_method(self, validator):
        """Test that validator has validate_foundation_health method."""
        assert callable(validator.validate_foundation_health)
        
        # Should return validation results (even if platform not running)
        result = await validator.validate_foundation_health("public_works_foundation")
        
        assert result is not None
        assert 'foundation_name' in result
        assert 'is_valid' in result
        assert 'checks' in result
        assert 'violations' in result
        assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_validator_has_validate_all_foundations_method(self, validator):
        """Test that validator has validate_all_foundations method."""
        assert callable(validator.validate_all_foundations)
        
        # Should return validation results (even if platform not running)
        result = await validator.validate_all_foundations()
        
        assert result is not None
        assert 'is_valid' in result
        assert 'foundations' in result
        assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_validator_has_validate_platform_readiness_method(self, validator):
        """Test that validator has validate_platform_readiness method."""
        assert callable(validator.validate_platform_readiness)
        
        # Should return validation results (even if platform not running)
        result = await validator.validate_platform_readiness()
        
        assert result is not None
        assert 'is_valid' in result
        assert 'startup_validation' in result
        assert 'foundations_validation' in result
        assert 'all_violations' in result
        assert 'violation_count' in result
        assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_validator_checks_health_endpoint(self, validator):
        """Test that validator checks health endpoint."""
        result = await validator.validate_platform_startup()
        
        assert 'checks' in result
        assert 'health_endpoint_responds' in result['checks']
    
    @pytest.mark.asyncio
    async def test_validator_checks_platform_status(self, validator):
        """Test that validator checks platform status."""
        result = await validator.validate_platform_startup()
        
        assert 'checks' in result
        assert 'platform_status_operational' in result['checks']
    
    @pytest.mark.asyncio
    async def test_validator_checks_foundations_initialized(self, validator):
        """Test that validator checks foundations initialized."""
        result = await validator.validate_platform_startup()
        
        assert 'checks' in result
        assert 'foundations_initialized' in result['checks']
    
    @pytest.mark.asyncio
    async def test_validator_checks_health_checks_work(self, validator):
        """Test that validator checks health checks work."""
        result = await validator.validate_platform_startup()
        
        assert 'checks' in result
        assert 'health_checks_work' in result['checks']
    
    @pytest.mark.asyncio
    async def test_validator_checks_api_routers_registered(self, validator):
        """Test that validator checks API routers registered."""
        result = await validator.validate_platform_startup()
        
        assert 'checks' in result
        assert 'api_routers_registered' in result['checks']
    
    @pytest.mark.asyncio
    async def test_validator_validates_expected_foundations(self, validator):
        """Test that validator validates expected foundations."""
        result = await validator.validate_all_foundations()
        
        assert 'foundations' in result
        assert 'public_works_foundation' in result['foundations']
        assert 'curator_foundation' in result['foundations']
        assert 'communication_foundation' in result['foundations']
        assert 'agentic_foundation' in result['foundations']
    
    @pytest.mark.asyncio
    async def test_validator_returns_violations_when_platform_not_running(self, validator):
        """Test that validator returns violations when platform is not running."""
        result = await validator.validate_platform_startup()
        
        # If platform is not running, should have violations
        if not result['is_valid']:
            assert len(result['violations']) > 0
            # Should have at least one violation type
            violation_types = [v['type'] for v in result['violations']]
            assert len(violation_types) > 0


