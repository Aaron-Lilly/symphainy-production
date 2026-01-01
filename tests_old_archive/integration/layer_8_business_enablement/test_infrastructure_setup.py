#!/usr/bin/env python3
"""
Test Infrastructure Setup and Configuration

Provides fixtures and utilities for test infrastructure (GCS + Supabase)
with proper isolation and cleanup.
"""

import os
import pytest
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class TestInfrastructureConfig:
    """Configuration for test infrastructure."""
    
    def __init__(self):
        # GCS Configuration
        self.gcs_project_id = os.getenv("TEST_GCS_PROJECT_ID") or os.getenv("GCS_PROJECT_ID", "symphainymvp-devbox")
        self.gcs_bucket = os.getenv("TEST_GCS_BUCKET") or os.getenv("GCS_BUCKET_NAME", "symphainy-bucket-2025")
        
        # CRITICAL: Use JSON credentials (Supabase pattern) - no file paths!
        # GOOGLE_APPLICATION_CREDENTIALS is for SSH/VM access (infrastructure), not bucket access
        # Prefer JSON credentials from environment, fallback to reading from file if needed
        self.gcs_credentials_json = os.getenv("TEST_GCS_CREDENTIALS_JSON") or os.getenv("GCS_CREDENTIALS_JSON")
        
        # Fallback: If JSON not set, try to read from file (for backward compatibility in tests)
        if not self.gcs_credentials_json:
            creds_path = os.getenv("TEST_GCS_CREDENTIALS") or os.getenv("GCS_CREDENTIALS_PATH")
            if creds_path:
                # Resolve relative paths to absolute
                if not os.path.isabs(creds_path):
                    project_root = Path(__file__).parent.parent.parent.parent
                    creds_path = str((project_root / creds_path).resolve())
                
                # Read file and convert to JSON string
                if os.path.exists(creds_path):
                    import json
                    with open(creds_path, 'r') as f:
                        creds_data = json.load(f)
                        self.gcs_credentials_json = json.dumps(creds_data, separators=(',', ':'))
        
        self.gcs_test_prefix = "test/"  # All test files under this prefix
        
        # Supabase Configuration
        self.supabase_url = os.getenv("TEST_SUPABASE_URL") or os.getenv("SUPABASE_URL")
        self.supabase_service_key = os.getenv("TEST_SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
        self.test_tenant_id = "test_tenant"  # Isolate test data by tenant
        
        # Feature Flags
        self.infrastructure_enabled = os.getenv("TEST_INFRASTRUCTURE_ENABLED", "false").lower() == "true"
        
    def is_available(self) -> bool:
        """Check if test infrastructure is available."""
        if not self.infrastructure_enabled:
            return False
        
        # Check if credentials are configured
        # GCS: Can use JSON credentials OR application default credentials
        has_gcs = bool(
            self.gcs_credentials_json or 
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or
            self._has_application_default_credentials()
        )
        has_supabase = bool(self.supabase_url and self.supabase_service_key)
        
        return has_gcs and has_supabase
    
    def _has_application_default_credentials(self) -> bool:
        """Check if application default credentials are available."""
        try:
            from google.auth import default
            credentials, project = default()
            return credentials is not None
        except Exception:
            return False
    
    def get_test_file_path(self, filename: str) -> str:
        """Get test file path with prefix for isolation."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{self.gcs_test_prefix}{timestamp}_{filename}"


@pytest.fixture(scope="session")
def test_infrastructure_config() -> TestInfrastructureConfig:
    """Provide test infrastructure configuration."""
    return TestInfrastructureConfig()


@pytest.fixture(scope="session")
def test_infrastructure_available() -> bool:
    """Check if test infrastructure is available."""
    config = TestInfrastructureConfig()
    return config.is_available()


@pytest.fixture(scope="function")
async def file_storage_backend(test_infrastructure_config: TestInfrastructureConfig, 
                               test_infrastructure_available: bool):
    """
    Provide file storage backend (real infrastructure with test isolation).
    
    Yields:
        FileManagementAbstraction instance with test isolation
    """
    if not test_infrastructure_available:
        config = test_infrastructure_config
        missing = []
        
        if not config.infrastructure_enabled:
            missing.append("TEST_INFRASTRUCTURE_ENABLED=true")
        
        if not config.gcs_credentials_json and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and not config._has_application_default_credentials():
            missing.append("TEST_GCS_CREDENTIALS_JSON or GCS_CREDENTIALS_JSON (or application default credentials)")
        
        if not config.supabase_url:
            missing.append("TEST_SUPABASE_URL or SUPABASE_URL")
        
        if not config.supabase_service_key:
            missing.append("TEST_SUPABASE_SERVICE_KEY or SUPABASE_SERVICE_KEY")
        
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test infrastructure not available.\n\n"
            f"Missing configuration:\n"
            + "\n".join([f"  - {m}" for m in missing]) + "\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"To enable test infrastructure:\n"
            f"  1. Set TEST_INFRASTRUCTURE_ENABLED=true\n"
            f"  2. Configure TEST_GCS_CREDENTIALS_JSON or GCS_CREDENTIALS_JSON (Supabase pattern)\n"
            f"  3. Configure TEST_SUPABASE_URL and TEST_SUPABASE_SERVICE_KEY\n\n"
            f"Note: These tests require real GCS and Supabase infrastructure for integration testing."
        )
    
    from foundations.public_works_foundation.infrastructure_adapters.gcs_file_adapter import GCSFileAdapter
    from foundations.public_works_foundation.infrastructure_adapters.supabase_file_management_adapter import SupabaseFileManagementAdapter
    from foundations.public_works_foundation.infrastructure_abstractions.file_management_abstraction_gcs import FileManagementAbstraction
    
    # Initialize adapters with test configuration
    # Use JSON credentials (Supabase pattern) - no file paths!
    gcs_adapter = GCSFileAdapter(
        project_id=test_infrastructure_config.gcs_project_id,
        bucket_name=test_infrastructure_config.gcs_bucket,
        credentials_json=test_infrastructure_config.gcs_credentials_json
    )
    
    supabase_adapter = SupabaseFileManagementAdapter(
        url=test_infrastructure_config.supabase_url,
        service_key=test_infrastructure_config.supabase_service_key
    )
    
    # Create abstraction with test adapters
    file_abstraction = FileManagementAbstraction(
        gcs_adapter=gcs_adapter,
        supabase_adapter=supabase_adapter
    )
    
    yield file_abstraction
    
    # Cleanup: Delete test files after test
    await cleanup_test_files(file_abstraction, test_infrastructure_config)


async def cleanup_test_files(file_abstraction: Any, config: TestInfrastructureConfig):
    """Clean up test files created during test."""
    try:
        # Get list of test files (with test prefix)
        # This would require implementing list_files in the abstraction
        # For now, we'll rely on GCS lifecycle policies or manual cleanup
        
        # Option 1: Use GCS lifecycle policy (recommended)
        # Set lifecycle policy: Delete files with test/ prefix older than 1 day
        
        # Option 2: Manual cleanup (if list_files is available)
        # test_files = await file_abstraction.list_files(prefix=config.gcs_test_prefix)
        # for file in test_files:
        #     await file_abstraction.delete_file(file["uuid"])
        
        pass  # Cleanup handled by lifecycle policy or manual process
    except Exception as e:
        # Don't fail tests on cleanup errors
        print(f"Warning: Failed to cleanup test files: {e}")


@pytest.fixture
def test_file_metadata(test_infrastructure_config: TestInfrastructureConfig) -> Dict[str, Any]:
    """Provide test file metadata with test isolation."""
    return {
        "tenant_id": test_infrastructure_config.test_tenant_id,
        "upload_source": "test",
        "test_run_id": datetime.utcnow().isoformat()
    }

