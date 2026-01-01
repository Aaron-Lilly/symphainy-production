#!/usr/bin/env python3
"""
Layer 2: Logging Service Tests

Tests that validate logging service works correctly.

WHAT: Validate logging service
HOW: Test SmartCityLoggingService
"""

import pytest

import os
import logging
from unittest.mock import Mock, patch

from utilities.logging.logging_service import SmartCityLoggingService

class TestLoggingService:
    """Test logging service."""
    
    @pytest.fixture
    def logging_service(self):
        """Create logging service instance with DEBUG level."""
        return SmartCityLoggingService("test_service", log_level="DEBUG")
    
    def test_logging_service_initialization(self, logging_service):
        """Test that logging service initializes correctly."""
        assert logging_service.service_name == "test_service"
        assert logging_service.logger is not None
        assert logging_service.logger.name == "test_service"
    
    def test_info_logging(self, logging_service, caplog):
        """Test info logging."""
        with caplog.at_level(logging.INFO):
            logging_service.info("Test info message")
        
        assert "Test info message" in caplog.text
        assert "[test_service]" in caplog.text
    
    def test_warning_logging(self, logging_service, caplog):
        """Test warning logging."""
        with caplog.at_level(logging.WARNING):
            logging_service.warning("Test warning message")
        
        assert "Test warning message" in caplog.text
        assert "[test_service]" in caplog.text
    
    def test_error_logging(self, logging_service, caplog):
        """Test error logging."""
        with caplog.at_level(logging.ERROR):
            logging_service.error("Test error message")
        
        assert "Test error message" in caplog.text
        assert "[test_service]" in caplog.text
    
    def test_debug_logging(self, logging_service, caplog):
        """Test debug logging."""
        # Set logger level to DEBUG
        logging_service.logger.setLevel(logging.DEBUG)
        
        with caplog.at_level(logging.DEBUG):
            logging_service.debug("Test debug message")
        
        assert "Test debug message" in caplog.text
    
    def test_critical_logging(self, logging_service, caplog):
        """Test critical logging."""
        with caplog.at_level(logging.CRITICAL):
            logging_service.critical("Test critical message")
        
        assert "Test critical message" in caplog.text
    
    def test_log_service_event(self, logging_service, caplog):
        """Test structured service event logging."""
        with caplog.at_level(logging.INFO):
            logging_service.log_service_event("test_event", {"key": "value"})
        
        assert "Service Event" in caplog.text
        assert "test_event" in caplog.text
        assert "test_service" in caplog.text
    
    def test_log_error_with_context(self, logging_service, caplog):
        """Test error logging with context."""
        error = ValueError("Test error")
        context = {"key": "value"}
        
        with caplog.at_level(logging.ERROR):
            logging_service.log_error_with_context(error, context)
        
        assert "Error with Context" in caplog.text
        assert "ValueError" in caplog.text
        assert "Test error" in caplog.text
