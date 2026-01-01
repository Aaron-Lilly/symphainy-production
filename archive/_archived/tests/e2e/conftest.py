#!/usr/bin/env python3
"""
E2E Test Configuration and Fixtures

Industry standard pytest configuration for end-to-end testing.

WHAT (Test Config Role): I provide comprehensive E2E test configuration
HOW (Test Config Implementation): I set up pytest fixtures, test data, and environment management
"""

import asyncio
import os
import sys
import pytest
import tempfile
import shutil
from typing import Dict, Any, Generator
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Updated imports for new architecture
from backend.business_enablement.pillars.business_orchestrator.business_orchestrator_service import business_orchestrator_service
from experience.services.experience_manager_service import experience_manager_service
from config.environment_loader import EnvironmentLoader


class E2ETestEnvironment:
    """E2E Test Environment Manager."""
    
    def __init__(self):
        self.temp_dir = None
        self.original_env = None
        self.services = {}
        self.test_data = {}
    
    async def setup(self):
        """Setup test environment."""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp(prefix="symphainy_e2e_test_")
        
        # Backup original environment
        self.original_env = os.environ.copy()
        
        # Set test environment variables
        os.environ.update({
            "SYMPHAINY_ENV": "testing",
            "TEST_MODE": "true",
            "TEST_TEMP_DIR": self.temp_dir,
            "LOG_LEVEL": "WARNING",
            "API_DEBUG": "false",
            "API_RELOAD": "false"
        })
        
        # Initialize test data
        await self._setup_test_data()
        
        print(f"✅ E2E Test Environment setup complete: {self.temp_dir}")
    
    async def teardown(self):
        """Teardown test environment."""
        # Shutdown services
        for service_name, service in self.services.items():
            try:
                if hasattr(service, 'shutdown'):
                    await service.shutdown()
                print(f"✅ {service_name} shutdown")
            except Exception as e:
                print(f"⚠️ {service_name} shutdown error: {e}")
        
        # Restore original environment
        if self.original_env:
            os.environ.clear()
            os.environ.update(self.original_env)
        
        # Cleanup temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"✅ Test environment cleaned up: {self.temp_dir}")
    
    async def _setup_test_data(self):
        """Setup test data files."""
        test_files = {
            "sample.csv": "name,age,city\nJohn,25,New York\nJane,30,Los Angeles\nBob,35,Chicago",
            "sample.json": '{"users": [{"name": "John", "age": 25}, {"name": "Jane", "age": 30}]}',
            "sample.txt": "This is a sample text file for testing.",
            "sample_cobol.txt": "01 CUSTOMER-RECORD.\n   05 CUSTOMER-ID PIC 9(10).\n   05 CUSTOMER-NAME PIC X(50).\n   05 CUSTOMER-BALANCE PIC S9(7)V99."
        }
        
        for filename, content in test_files.items():
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
            self.test_data[filename] = file_path
        
        print(f"✅ Test data files created: {list(test_files.keys())}")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def e2e_environment():
    """E2E test environment fixture."""
    env = E2ETestEnvironment()
    await env.setup()
    yield env
    await env.teardown()


@pytest.fixture(scope="session")
async def business_orchestrator(e2e_environment):
    """Business Orchestrator service fixture."""
    orchestrator = BusinessOrchestratorService()
    await orchestrator.initialize()
    e2e_environment.services["business_orchestrator"] = orchestrator
    yield orchestrator


@pytest.fixture(scope="session")
async def experience_service(e2e_environment):
    """Experience Service fixture."""
    service = ExperienceService()
    await service.initialize()
    e2e_environment.services["experience_service"] = service
    yield service


@pytest.fixture(scope="session")
async def content_pillar_service(business_orchestrator):
    """Content Pillar service fixture."""
    if "content" in business_orchestrator.pillar_services:
        return business_orchestrator.pillar_services["content"]
    else:
        pytest.skip("Content Pillar service not available")


@pytest.fixture(scope="session")
async def content_liaison_agent(business_orchestrator):
    """Content Liaison Agent fixture."""
    if "content" in business_orchestrator.pillar_liaison_agents:
        return business_orchestrator.pillar_liaison_agents["content"]["agent_instance"]
    else:
        pytest.skip("Content Liaison Agent not available")


@pytest.fixture
def test_file_upload_data(e2e_environment):
    """Test file upload data fixture."""
    return {
        "filename": "test_sample.csv",
        "content": e2e_environment.test_data["sample.csv"],
        "content_type": "text/csv",
        "size": os.path.getsize(e2e_environment.test_data["sample.csv"])
    }


@pytest.fixture
def test_user_context():
    """Test user context fixture."""
    return {
        "user_id": "test_user_123",
        "session_id": f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "permissions": ["read", "write", "admin"]
    }


@pytest.fixture
def test_conversation_context():
    """Test conversation context fixture."""
    return {
        "conversation_id": f"test_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "user_id": "test_user_123",
        "session_id": f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }


# Test data fixtures
@pytest.fixture
def sample_csv_file(e2e_environment):
    """Sample CSV file fixture."""
    return e2e_environment.test_data["sample.csv"]


@pytest.fixture
def sample_json_file(e2e_environment):
    """Sample JSON file fixture."""
    return e2e_environment.test_data["sample.json"]


@pytest.fixture
def sample_cobol_file(e2e_environment):
    """Sample COBOL file fixture."""
    return e2e_environment.test_data["sample_cobol.txt"]


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add slow marker to E2E tests
        if "e2e" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # Add integration marker to integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)



