#!/usr/bin/env python3
"""
Simplified Test for Smart City Phase 2 Registration Pattern

Tests that Librarian service properly registers with Curator using Phase 2 pattern.
This test assumes the platform is already running or services are initialized.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
# Also add current working directory
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from typing import Dict, Any, List, Optional


async def test_librarian_registration():
    """Test Librarian service registration with Curator."""
    print("="*80)
    print("Smart City Phase 2 Registration Pattern Validation")
    print("Testing Librarian Service")
    print("="*80)
    
    try:
        # Import services
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        from backend.smart_city.services.librarian.librarian_service import LibrarianService
        
        print("\n🔧 Initializing test environment...")
        
        # Initialize DI Container
        print("   Step 1: Initializing DI Container...")
        di_container = DIContainerService("platform_orchestrated")
        print("   ✅ DI Container initialized")
        
        # Initialize Public Works Foundation (required for Curator)
        print("   Step 2: Initializing Public Works Foundation...")
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        public_works = PublicWorksFoundationService(di_container)
        await public_works.initialize_foundation()
        # Make it available via DI container's get_foundation_service
        di_container._foundation_services = {"PublicWorksFoundationService": public_works}
        print("   ✅ Public Works Foundation initialized")
        
        # Initialize Curator Foundation
        print("   Step 3: Initializing Curator Foundation...")
        curator = CuratorFoundationService(di_container)
        await curator.initialize()
        di_container._foundation_services["CuratorFoundationService"] = curator
        print("   ✅ Curator Foundation initialized")
        
        # Initialize Librarian Service (this will trigger registration)
        print("   Step 4: Initializing Librarian Service...")
        librarian = LibrarianService(di_container)
        await librarian.initialize()
        print("   ✅ Librarian Service initialized")
        
        print("\n" + "="*80)
        print("TEST 1: Service Registration and Discovery")
        print("="*80)
        
        # Test 1: Service Registration
        registered_services = await curator.get_registered_services()
        print(f"\n📋 Registered services: {len(registered_services)}")
        
        librarian_found = False
        for service_id, service_data in registered_services.items():
            service_name = service_data.get("service_name", "")
            if "Librarian" in service_name or "librarian" in service_name.lower():
                librarian_found = True
                print(f"\n✅ Found Librarian service:")
                print(f"   Service ID: {service_id}")
                print(f"   Service Name: {service_name}")
                print(f"   Realm: {service_data.get('realm', 'unknown')}")
                print(f"   Status: {service_data.get('status', 'unknown')}")
                break
        
        if not librarian_found:
            print("\n❌ Librarian service not found in registered services")
            return False
        
        print("\n" + "="*80)
        print("TEST 2: SOA API Discovery")
        print("="*80)
        
        # Test 2: SOA API Discovery
        librarian_capabilities = await curator.capability_registry.get_capabilities_by_service("LibrarianService")
        print(f"\n📋 Librarian capabilities: {len(librarian_capabilities)}")
        
        if not librarian_capabilities:
            print("\n❌ No capabilities found for LibrarianService")
            return False
        
        soa_apis_found = []
        for capability in librarian_capabilities:
            contracts = capability.contracts or {}
            if "soa_api" in contracts:
                soa_api = contracts["soa_api"]
                soa_apis_found.append({
                    "capability": capability.capability_name,
                    "api_name": soa_api.get("api_name", "unknown"),
                    "endpoint": soa_api.get("endpoint", "unknown"),
                    "method": soa_api.get("method", "unknown")
                })
                print(f"\n✅ SOA API: {soa_api.get('api_name')}")
                print(f"   Endpoint: {soa_api.get('endpoint')}")
                print(f"   Method: {soa_api.get('method')}")
        
        if not soa_apis_found:
            print("\n❌ No SOA APIs found")
            return False
        
        print(f"\n✅ Found {len(soa_apis_found)} SOA APIs")
        
        print("\n" + "="*80)
        print("TEST 3: MCP Tool Discovery")
        print("="*80)
        
        # Test 3: MCP Tool Discovery
        mcp_tools_found = []
        for capability in librarian_capabilities:
            contracts = capability.contracts or {}
            if "mcp_tool" in contracts:
                mcp_tool = contracts["mcp_tool"]
                mcp_tools_found.append({
                    "capability": capability.capability_name,
                    "tool_name": mcp_tool.get("tool_name", "unknown"),
                    "mcp_server": mcp_tool.get("mcp_server", "unknown")
                })
                print(f"\n✅ MCP Tool: {mcp_tool.get('tool_name')}")
                print(f"   Capability: {capability.capability_name}")
                print(f"   MCP Server: {mcp_tool.get('mcp_server')}")
        
        if not mcp_tools_found:
            print("\n❌ No MCP tools found")
            return False
        
        print(f"\n✅ Found {len(mcp_tools_found)} MCP tools")
        
        print("\n" + "="*80)
        print("TEST 4: Capability Registration Validation")
        print("="*80)
        
        # Test 4: Validate capabilities
        valid_capabilities = 0
        for capability in librarian_capabilities:
            print(f"\n📦 Capability: {capability.capability_name}")
            print(f"   Protocol: {capability.protocol_name}")
            print(f"   Description: {capability.description}")
            
            contracts = capability.contracts or {}
            has_soa = "soa_api" in contracts
            has_mcp = "mcp_tool" in contracts
            has_rest = "rest_api" in contracts
            has_semantic = capability.semantic_mapping is not None
            
            print(f"   Contracts: SOA={has_soa}, MCP={has_mcp}, REST={has_rest}")
            print(f"   Semantic Mapping: {has_semantic}")
            
            if has_rest:
                print(f"   ⚠️ Warning: Smart City service has REST API (should be SOA + MCP only)")
            if has_semantic:
                print(f"   ⚠️ Warning: Smart City service has semantic mapping (should be None)")
            
            if has_soa or has_mcp:
                valid_capabilities += 1
                print(f"   ✅ Valid capability")
        
        print(f"\n✅ {valid_capabilities} valid capabilities found")
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"\n✅ Service Registration: {'PASS' if librarian_found else 'FAIL'}")
        print(f"✅ SOA API Discovery: {'PASS' if soa_apis_found else 'FAIL'} ({len(soa_apis_found)} APIs)")
        print(f"✅ MCP Tool Discovery: {'PASS' if mcp_tools_found else 'FAIL'} ({len(mcp_tools_found)} tools)")
        print(f"✅ Capability Registration: {'PASS' if valid_capabilities > 0 else 'FAIL'} ({valid_capabilities} capabilities)")
        
        all_passed = librarian_found and soa_apis_found and mcp_tools_found and valid_capabilities > 0
        
        if all_passed:
            print("\n🎉 ALL TESTS PASSED - Phase 2 pattern is working correctly!")
            print("   Ready to migrate remaining Smart City services.")
        else:
            print("\n❌ SOME TESTS FAILED - Review issues above.")
        
        print("="*80 + "\n")
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_librarian_registration())
    sys.exit(0 if success else 1)

