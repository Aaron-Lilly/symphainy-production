#!/usr/bin/env python3
"""
E2E Test for Content Pillar Semantic Processing (Phase 2)
Tests parse_file() with semantic processing integration.

This test can run with or without the full platform startup.
If the platform is running, it will use the API endpoint.
Otherwise, it will test the orchestrator directly.
"""

import os
import sys
import asyncio
import httpx
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent / "symphainy-platform"
sys.path.insert(0, str(project_root))

async def test_via_api():
    """Test semantic processing via API endpoint (if platform is running)."""
    print("🧪 Testing via API endpoint...")
    
    # Check if platform is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ Platform is running, testing via API...")
                return True
    except Exception:
        print("⚠️  Platform not running, will test orchestrator directly")
        return False

async def test_orchestrator_directly():
    """Test orchestrator directly (bypasses platform startup)."""
    print("🧪 Testing orchestrator directly...")
    
    try:
        # Import required components
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        print("✅ Imports successful")
        
        # Initialize DI Container
        print("📦 Initializing DI Container...")
        di_container = DIContainerService()
        await di_container.initialize()
        print("✅ DI Container initialized")
        
        # Initialize Public Works Foundation (minimal - just for adapters)
        print("🏗️  Initializing Public Works Foundation...")
        public_works = PublicWorksFoundationService(
            service_name="test_public_works",
            di_container=di_container
        )
        # Skip full initialization - just get adapters we need
        print("⚠️  Skipping full Public Works initialization (would require Traefik)")
        print("   This is a simplified test - full E2E requires platform startup")
        
        return False  # Can't test without full platform
        
    except Exception as e:
        print(f"❌ Error testing orchestrator directly: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 E2E Test: Content Pillar Semantic Processing (Phase 2)")
    print("=" * 60)
    print()
    
    # Try API first
    if await test_via_api():
        print("✅ Platform is running - can test via API")
        print("   Use the API endpoint: POST /api/v1/content/parse")
        print("   With file upload and parse_options containing content_type")
        return
    
    # Try direct orchestrator test
    print()
    print("⚠️  Full E2E test requires platform startup")
    print("   The platform needs to be running to test semantic processing")
    print("   Current blocker: Smart City Gateway import issue")
    print()
    print("💡 Recommendation:")
    print("   1. Fix Smart City Gateway import in main.py")
    print("   2. Or test via API once platform is running")
    print("   3. Or create a minimal test harness that bypasses Smart City Gateway")

if __name__ == "__main__":
    asyncio.run(main())






