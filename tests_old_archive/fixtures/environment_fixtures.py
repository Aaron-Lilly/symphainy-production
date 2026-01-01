#!/usr/bin/env python3
"""
Environment-Specific Test Fixtures

This module provides fixtures for testing across different environments
(development, staging, production) with proper service discovery and
environment-specific configurations.
"""

import pytest
import httpx
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add platform path for service discovery
platform_path = Path(__file__).parent.parent.parent / "symphainy-platform"
sys.path.insert(0, str(platform_path))

# Add tests path for imports
tests_path = Path(__file__).parent.parent
sys.path.insert(0, str(tests_path))

from environments.production_test_config import ProductionTestConfig, ServiceHealthChecker


@pytest.fixture(scope="session")
def production_config():
    """Production environment configuration."""
    return ProductionTestConfig()


@pytest.fixture(scope="session")
def service_health_checker(production_config):
    """Service health checker for production testing."""
    return ServiceHealthChecker(production_config)


@pytest.fixture(scope="session")
def development_environment(production_config):
    """Setup development environment for testing."""
    return production_config.setup_environment('development')


@pytest.fixture(scope="session")
def staging_environment(production_config):
    """Setup staging environment for testing."""
    return production_config.setup_environment('staging')


@pytest.fixture(scope="session")
def production_environment(production_config):
    """Setup production environment for testing."""
    return production_config.setup_environment('production')


@pytest.fixture(scope="session")
def development_api_client(production_config):
    """HTTP client for development API testing."""
    config = production_config.get_config('development')
    
    async def _get_client():
        async with httpx.AsyncClient(
            base_url=config['base_url'],
            timeout=config['timeout'],
            headers={'User-Agent': 'Symphainy-E2E-Tests/1.0'}
        ) as client:
            return client
    
    return _get_client


@pytest.fixture(scope="session")
def staging_api_client(production_config):
    """HTTP client for staging API testing."""
    config = production_config.get_config('staging')
    
    async def _get_client():
        async with httpx.AsyncClient(
            base_url=config['base_url'],
            timeout=config['timeout'],
            headers={'User-Agent': 'Symphainy-E2E-Tests/1.0'}
        ) as client:
            return client
    
    return _get_client


@pytest.fixture(scope="session")
def production_api_client(production_config):
    """HTTP client for production API testing."""
    config = production_config.get_config('production')
    
    async def _get_client():
        async with httpx.AsyncClient(
            base_url=config['base_url'],
            timeout=config['timeout'],
            headers={'User-Agent': 'Symphainy-E2E-Tests/1.0'}
        ) as client:
            return client
    
    return _get_client


@pytest.fixture(scope="session")
def development_services(production_config, service_health_checker):
    """Development environment services."""
    services = {}
    
    # Initialize services for development
    try:
        from utilities import ConfigurationUtility
        services['config'] = ConfigurationUtility("development_test")
    except ImportError:
        services['config'] = None
    
    try:
        from utilities import HealthManagementUtility
        services['health'] = HealthManagementUtility("development_test")
    except ImportError:
        services['health'] = None
    
    try:
        from utilities import TelemetryReportingUtility
        services['telemetry'] = TelemetryReportingUtility("development_test")
    except ImportError:
        services['telemetry'] = None
    
    return services


@pytest.fixture(scope="session")
def staging_services(production_config, service_health_checker):
    """Staging environment services."""
    services = {}
    
    # Initialize services for staging
    try:
        from utilities import ConfigurationUtility
        services['config'] = ConfigurationUtility("staging_test")
    except ImportError:
        services['config'] = None
    
    try:
        from utilities import HealthManagementUtility
        services['health'] = HealthManagementUtility("staging_test")
    except ImportError:
        services['health'] = None
    
    try:
        from utilities import TelemetryReportingUtility
        services['telemetry'] = TelemetryReportingUtility("staging_test")
    except ImportError:
        services['telemetry'] = None
    
    return services


@pytest.fixture(scope="session")
def production_services(production_config, service_health_checker):
    """Production environment services."""
    services = {}
    
    # Initialize services for production
    try:
        from utilities import ConfigurationUtility
        services['config'] = ConfigurationUtility("production_test")
    except ImportError:
        services['config'] = None
    
    try:
        from utilities import HealthManagementUtility
        services['health'] = HealthManagementUtility("production_test")
    except ImportError:
        services['health'] = None
    
    try:
        from utilities import TelemetryReportingUtility
        services['telemetry'] = TelemetryReportingUtility("production_test")
    except ImportError:
        services['telemetry'] = None
    
    return services


@pytest.fixture(scope="session")
def development_health_check(service_health_checker):
    """Development environment health check."""
    health_results = {}
    
    # Check service health
    services = ['configuration_utility', 'health_management_utility', 'telemetry_reporting_utility']
    for service in services:
        health_results[service] = service_health_checker.check_service_health(service, 'development')
    
    return health_results


@pytest.fixture(scope="session")
def staging_health_check(service_health_checker):
    """Staging environment health check."""
    health_results = {}
    
    # Check service health
    services = ['configuration_utility', 'health_management_utility', 'telemetry_reporting_utility']
    for service in services:
        health_results[service] = service_health_checker.check_service_health(service, 'staging')
    
    return health_results


@pytest.fixture(scope="session")
def production_health_check(service_health_checker):
    """Production environment health check."""
    health_results = {}
    
    # Check service health
    services = ['configuration_utility', 'health_management_utility', 'telemetry_reporting_utility']
    for service in services:
        health_results[service] = service_health_checker.check_service_health(service, 'production')
    
    return health_results


@pytest.fixture(scope="session")
def test_data_path(production_config):
    """Path to test data directory."""
    return production_config.get_test_data_path()


@pytest.fixture(scope="session")
def reports_path(production_config):
    """Path to test reports directory."""
    return production_config.get_reports_path()


@pytest.fixture(scope="session")
def logs_path(production_config):
    """Path to test logs directory."""
    return production_config.get_logs_path()


@pytest.fixture(scope="session")
def mock_backend_services():
    """Mock backend services for testing when real services are not available."""
    return {
        'mock_api_responses': {
            '/health': {'status': 'healthy', 'timestamp': '2025-01-01T00:00:00Z'},
            '/api/content/health': {'status': 'healthy', 'service': 'content'},
            '/api/insights/health': {'status': 'healthy', 'service': 'insights'},
            '/api/operations/health': {'status': 'healthy', 'service': 'operations'},
            '/api/business-outcomes/health': {'status': 'healthy', 'service': 'business-outcomes'}
        },
        'mock_service_health': {
            'configuration_utility': {'status': 'healthy', 'uptime': '100%'},
            'health_management_utility': {'status': 'healthy', 'uptime': '100%'},
            'telemetry_reporting_utility': {'status': 'healthy', 'uptime': '100%'}
        }
    }
