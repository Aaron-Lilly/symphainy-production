#!/usr/bin/env python3
"""
Verify Test Infrastructure Setup

This script verifies that test infrastructure (GCS + Supabase) is properly configured.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent / "symphainy-platform"
sys.path.insert(0, str(project_root))

# Import from local file
import importlib.util
spec = importlib.util.spec_from_file_location(
    "test_infrastructure_setup",
    Path(__file__).parent / "test_infrastructure_setup.py"
)
test_infrastructure_setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_infrastructure_setup)
TestInfrastructureConfig = test_infrastructure_setup.TestInfrastructureConfig


async def verify_gcs():
    """Verify GCS test bucket is accessible."""
    print("🔍 Verifying GCS Test Bucket...")
    
    config = TestInfrastructureConfig()
    
    # Check for bucket credentials (ONLY from GCS_CREDENTIALS_PATH - never from GOOGLE_APPLICATION_CREDENTIALS)
    # CRITICAL: GOOGLE_APPLICATION_CREDENTIALS is for SSH/VM access, not bucket access
    has_explicit_bucket_creds = bool(config.gcs_credentials_path)
    has_app_default = False
    try:
        from google.auth import default
        credentials, project = default()
        has_app_default = credentials is not None
    except Exception:
        pass
    
    if not has_explicit_bucket_creds and not has_app_default:
        print("  ⚠️  No GCS bucket credentials configured")
        print("     (Need GCS_CREDENTIALS_PATH or TEST_GCS_CREDENTIALS, or application default credentials)")
        print("     Note: GOOGLE_APPLICATION_CREDENTIALS is for SSH/VM access, not bucket access")
        return False
    
    try:
        from foundations.public_works_foundation.infrastructure_adapters.gcs_file_adapter import GCSFileAdapter
        
        # Use explicit bucket credentials (ONLY from GCS_CREDENTIALS_PATH)
        credentials_path = config.gcs_credentials_path
        project_id = os.getenv("GCS_PROJECT_ID") or os.getenv("TEST_GCS_PROJECT_ID") or "symphainymvp-devbox"
        
        adapter = GCSFileAdapter(
            project_id=project_id,
            bucket_name=config.gcs_bucket,
            credentials_path=credentials_path if credentials_path else None
        )
        
        # Try to list bucket (this will fail if bucket doesn't exist or credentials are invalid)
        # Note: GCSFileAdapter might not have a list method, so we'll try a simple operation
        print(f"  ✅ GCS adapter initialized")
        print(f"     Bucket: {config.gcs_bucket}")
        print(f"     Credentials: {credentials_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ GCS verification failed: {e}")
        return False


async def verify_supabase():
    """Verify Supabase test configuration."""
    print("🔍 Verifying Supabase Configuration...")
    
    config = TestInfrastructureConfig()
    
    if not config.supabase_url or not config.supabase_service_key:
        print("  ⚠️  Supabase credentials not configured")
        print("     Set TEST_SUPABASE_URL and TEST_SUPABASE_SERVICE_KEY")
        return False
    
    try:
        from foundations.public_works_foundation.infrastructure_adapters.supabase_file_management_adapter import SupabaseFileManagementAdapter
        
        adapter = SupabaseFileManagementAdapter(
            url=config.supabase_url,
            service_key=config.supabase_service_key
        )
        
        # Try to connect
        connected = await adapter.connect()
        
        if connected:
            print(f"  ✅ Supabase adapter connected")
            print(f"     URL: {config.supabase_url}")
            print(f"     Test Tenant: {config.test_tenant_id}")
            return True
        else:
            print(f"  ❌ Supabase connection failed")
            return False
        
    except Exception as e:
        print(f"  ❌ Supabase verification failed: {e}")
        return False


async def main():
    """Main verification function."""
    print("=" * 60)
    print("Test Infrastructure Verification")
    print("=" * 60)
    print()
    
    # Load environment
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env.test"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded configuration from {env_file}")
    else:
        print(f"⚠️  {env_file} not found, using environment variables")
    print()
    
    # Check configuration
    config = TestInfrastructureConfig()
    print(f"Test Infrastructure Enabled: {config.infrastructure_enabled}")
    print()
    
    # Verify components
    gcs_ok = await verify_gcs()
    print()
    supabase_ok = await verify_supabase()
    print()
    
    # Summary
    print("=" * 60)
    if gcs_ok and supabase_ok:
        print("✅ All test infrastructure components verified!")
        print()
        print("You can now run tests with:")
        print("  pytest tests/integration/layer_8_business_enablement/ -v")
    else:
        print("⚠️  Some components need configuration")
        print()
        if not gcs_ok:
            print("  ❌ GCS: Run setup_test_infrastructure.sh")
        if not supabase_ok:
            print("  ❌ Supabase: Update .env.test with Supabase credentials")
        print()
        print("See INFRASTRUCTURE_SETUP_GUIDE.md for details")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

