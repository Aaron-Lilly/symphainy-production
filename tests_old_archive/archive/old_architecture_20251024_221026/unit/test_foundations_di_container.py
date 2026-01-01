#!/usr/bin/env python3
"""
Unit Tests: Foundations DI Container

Tests the DIContainerService and its integration with all foundation services.
Validates the new pure dependency injection architecture.

WHAT (Test Role): I validate the DI container and foundation services
HOW (Test Implementation): I test DI container initialization, service injection, and utility access
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../symphainy-platform'))

from foundations.di_container.di_container_service import DIContainerService


class TestDIContainerService:
    """Test DIContainerService functionality."""
    
    @pytest.fixture
    def di_container(self):
        """Create a DI container for testing."""
        return DIContainerService("test_service")
    
    def test_di_container_initialization(self, di_container):
        """Test DI container initializes correctly."""
        assert di_container is not None
        assert di_container.service_name == "test_service"
        assert hasattr(di_container, 'get_logger')
        assert hasattr(di_container, 'get_config')
        assert hasattr(di_container, 'get_health')
        assert hasattr(di_container, 'get_telemetry')
        assert hasattr(di_container, 'get_security')
    
    def test_logger_access(self, di_container):
        """Test logger utility access."""
        logger = di_container.get_logger("test_logger")
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'debug')
    
    def test_config_access(self, di_container):
        """Test configuration utility access."""
        config = di_container.get_config()
        assert config is not None
        assert hasattr(config, 'get')
        assert hasattr(config, 'get_string')
        assert hasattr(config, 'get_int')
        assert hasattr(config, 'get_bool')
    
    def test_health_access(self, di_container):
        """Test health utility access."""
        health = di_container.get_health()
        assert health is not None
        assert hasattr(health, 'get_status')
        assert hasattr(health, 'set_status')
        assert hasattr(health, 'register_health_check')
    
    def test_telemetry_access(self, di_container):
        """Test telemetry utility access."""
        telemetry = di_container.get_telemetry()
        assert telemetry is not None
        assert hasattr(telemetry, 'record_metric')
        assert hasattr(telemetry, 'bootstrap')
        assert hasattr(telemetry, 'is_bootstrapped')
    
    def test_security_access(self, di_container):
        """Test security utility access."""
        security = di_container.get_security()
        assert security is not None
        assert hasattr(security, 'bootstrap')
        assert hasattr(security, 'is_bootstrapped')
        assert hasattr(security, 'service_name')
    
    def test_fastapi_app_creation(self, di_container):
        """Test FastAPI app creation."""
        app = di_container.create_fastapi_app("test_app")
        assert app is not None
        assert hasattr(app, 'get')
        assert hasattr(app, 'post')
        assert hasattr(app, 'put')
        assert hasattr(app, 'delete')
