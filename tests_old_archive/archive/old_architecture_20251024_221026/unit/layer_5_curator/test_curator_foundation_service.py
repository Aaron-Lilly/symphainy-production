#!/usr/bin/env python3
"""
Tests for Curator Foundation Service.

Tests the main coordinator service that manages pattern validation,
capability registry, anti-pattern detection, and documentation generation.
"""

import pytest
import pytest_asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.curator_foundation.services import (
    CapabilityRegistryService,
    PatternValidationService,
    AntiPatternDetectionService,
    DocumentationGenerationService
)
from .test_base import CuratorFoundationTestBase


class TestCuratorFoundationService(CuratorFoundationTestBase):
    """Test Curator Foundation Service functionality."""
    
    @pytest.mark.asyncio
    async def test_curator_foundation_initialization(self, curator_foundation):
        """Test curator foundation service initialization."""
        assert curator_foundation is not None
        assert curator_foundation.service_name == "curator_foundation"
        assert curator_foundation.utility_foundation is not None
        assert curator_foundation.public_works_foundation is not None
        
        # Check that micro-services are initialized
        assert curator_foundation.capability_registry_service is not None
        assert curator_foundation.pattern_validation_service is not None
        assert curator_foundation.antipattern_detection_service is not None
        assert curator_foundation.documentation_generation_service is not None
    
    @pytest.mark.asyncio
    async def test_curator_foundation_health_check(self, curator_foundation):
        """Test curator foundation health check."""
        health_status = await curator_foundation.get_coordinator_status()
        
        assert health_status is not None
        assert "service" in health_status
        assert "status" in health_status
        assert "micro_services" in health_status
        assert "timestamp" in health_status
        
        # Check micro-services status
        micro_services = health_status["micro_services"]
        assert "capability_registry" in micro_services
        assert "pattern_validation" in micro_services
        assert "antipattern_detection" in micro_services
        assert "documentation_generation" in micro_services
    
    @pytest.mark.asyncio
    async def test_capability_registry_service_access(self, curator_foundation):
        """Test access to capability registry service."""
        capability_service = curator_foundation.capability_registry_service
        
        assert capability_service is not None
        assert isinstance(capability_service, CapabilityRegistryService)
        assert capability_service.service_name == "capability_registry"
    
    @pytest.mark.asyncio
    async def test_pattern_validation_service_access(self, curator_foundation):
        """Test access to pattern validation service."""
        pattern_service = curator_foundation.pattern_validation_service
        
        assert pattern_service is not None
        assert isinstance(pattern_service, PatternValidationService)
        assert pattern_service.service_name == "pattern_validation"
    
    @pytest.mark.asyncio
    async def test_antipattern_detection_service_access(self, curator_foundation):
        """Test access to anti-pattern detection service."""
        antipattern_service = curator_foundation.antipattern_detection_service
        
        assert antipattern_service is not None
        assert isinstance(antipattern_service, AntiPatternDetectionService)
        assert antipattern_service.service_name == "antipattern_detection"
    
    @pytest.mark.asyncio
    async def test_documentation_generation_service_access(self, curator_foundation):
        """Test access to documentation generation service."""
        doc_service = curator_foundation.documentation_generation_service
        
        assert doc_service is not None
        assert isinstance(doc_service, DocumentationGenerationService)
        assert doc_service.service_name == "documentation_generation"
    
    @pytest.mark.asyncio
    async def test_curator_foundation_with_mock_dependencies(self, mock_utility_foundation, mock_public_works_foundation):
        """Test curator foundation with mock dependencies."""
        curator_service = CuratorFoundationService(mock_utility_foundation, mock_public_works_foundation)
        await curator_service.initialize()
        
        assert curator_service is not None
        assert curator_service.utility_foundation == mock_utility_foundation
        assert curator_service.public_works_foundation == mock_public_works_foundation
        
        # Check that micro-services are still initialized
        assert curator_service.capability_registry_service is not None
        assert curator_service.pattern_validation_service is not None
        assert curator_service.antipattern_detection_service is not None
        assert curator_service.documentation_generation_service is not None
    
    @pytest.mark.asyncio
    async def test_curator_foundation_coordinator_status(self, curator_foundation):
        """Test coordinator status reporting."""
        status = await curator_foundation.get_coordinator_status()
        
        assert status is not None
        assert isinstance(status, dict)
        assert "service" in status
        assert "status" in status
        assert "micro_services" in status
        assert "capabilities" in status
        assert "timestamp" in status
        
        # Verify service name
        assert status["service"] == "curator_foundation"
        
        # Verify micro-services are reported
        micro_services = status["micro_services"]
        assert len(micro_services) == 4
        assert all(service in micro_services for service in [
            "capability_registry", "pattern_validation", 
            "antipattern_detection", "documentation_generation"
        ])
    
    @pytest.mark.asyncio
    async def test_curator_foundation_initialization_without_public_works(self, utility_foundation):
        """Test curator foundation initialization without public works foundation."""
        curator_service = CuratorFoundationService(utility_foundation, None)
        await curator_service.initialize()
        
        assert curator_service is not None
        assert curator_service.utility_foundation == utility_foundation
        assert curator_service.public_works_foundation is None
        
        # Micro-services should still be initialized
        assert curator_service.capability_registry_service is not None
        assert curator_service.pattern_validation_service is not None
        assert curator_service.antipattern_detection_service is not None
        assert curator_service.documentation_generation_service is not None
