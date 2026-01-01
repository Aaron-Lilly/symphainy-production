#!/usr/bin/env python3
"""
Layer 2: Logging Service Factory Tests

Tests that validate logging service factory works correctly.

WHAT: Validate logging service factory
HOW: Test get_logging_service_factory()
"""

import pytest

import os
from unittest.mock import Mock, patch

from utilities.logging.logging_service_factory import get_logging_service_factory

class TestLoggingServiceFactory:
    """Test logging service factory."""
    
    def test_get_logging_service_factory(self):
        """Test that factory can be retrieved."""
        factory = get_logging_service_factory()
        
        assert factory is not None
    
    def test_create_smart_city_logging_service(self):
        """Test creating Smart City logging service."""
        factory = get_logging_service_factory()
        service = factory.create_logging_service("smart_city", "test_service")
        
        assert service is not None
        assert service.service_name == "test_service"
    
    def test_create_public_works_logging_service(self):
        """Test creating Public Works logging service."""
        factory = get_logging_service_factory()
        # Use correct realm name: public_works_foundation, not public_works
        service = factory.create_logging_service("public_works_foundation", "test_service")
        
        assert service is not None
        assert service.service_name == "test_service"
    
    def test_create_curator_logging_service(self):
        """Test creating Curator logging service."""
        factory = get_logging_service_factory()
        # Use correct realm name: curator_foundation, not curator
        service = factory.create_logging_service("curator_foundation", "test_service")
        
        assert service is not None
        assert service.service_name == "test_service"
