#!/usr/bin/env python3
"""
Test Smart City Phase 2 Registration Pattern

Validates that Smart City services (using Librarian as test case) properly:
1. Register with Curator (service registration and discovery)
2. Register SOA APIs (SOA API discovery)
3. Register MCP tools (MCP tool discovery)
4. Register capabilities with contracts

This ensures the foundation is correct before migrating remaining services.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Any, List, Optional


class Phase2RegistrationValidator:
    """Validator for Phase 2 registration pattern."""
    
    def __init__(self):
        self.curator = None
        self.results = {
            "service_registration": {"passed": False, "details": []},
            "soa_api_discovery": {"passed": False, "details": []},
            "mcp_tool_discovery": {"passed": False, "details": []},
            "capability_registration": {"passed": False, "details": []}
        }
    
    async def initialize(self):
        """Initialize validator, DI Container, Foundations, and Librarian service."""
        try:
            # Import here to avoid circular imports
            from foundations.di_container.di_container_service import DIContainerService
            from backend.smart_city.services.librarian.librarian_service import LibrarianService
            
            print("\n🔧 Initializing test environment...")
            
            # Step 1: Initialize DI Container
            print("   Step 1: Initializing DI Container...")
            di_container = DIContainerService("platform_orchestrated")
            print("   ✅ DI Container initialized")
            
            # Step 2: Initialize Public Works Foundation (required for Curator)
            print("   Step 2: Initializing Public Works Foundation...")
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            public_works = PublicWorksFoundationService(di_container)
            await public_works.initialize_foundation()
            # Store in DI container's infrastructure_services dict (like main.py does)
            di_container.infrastructure_services["public_works_foundation"] = public_works
            di_container.foundation_services["PublicWorksFoundationService"] = public_works
            print("   ✅ Public Works Foundation initialized")
            
            # Step 3: Initialize Curator Foundation
            print("   Step 3: Initializing Curator Foundation...")
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            self.curator = CuratorFoundationService(di_container)
            await self.curator.initialize()
            # Store in DI container's foundation_services dict (like main.py does)
            di_container.foundation_services["CuratorFoundationService"] = self.curator
            print("   ✅ Curator Foundation initialized")
            
            # Step 4: Initialize Librarian Service (this will trigger registration)
            print("   Step 4: Initializing Librarian Service...")
            librarian = LibrarianService(di_container)
            await librarian.initialize()
            # Store in DI container's smart_city_services dict
            if not hasattr(di_container, "smart_city_services"):
                di_container.smart_city_services = {}
            di_container.smart_city_services["LibrarianService"] = librarian
            print("   ✅ Librarian Service initialized and registered")
            
            # Store references
            self.di_container = di_container
            self.librarian = librarian
            
            print("\n✅ Test environment initialized successfully")
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to initialize validator: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_service_registration(self) -> bool:
        """Test 1: Verify service registration and discovery."""
        print("\n" + "="*80)
        print("TEST 1: Service Registration and Discovery")
        print("="*80)
        
        try:
            # Get registered services
            registered_services = await self.curator.get_registered_services()
            
            print(f"\n📋 Registered services: {len(registered_services)}")
            
            # Look for Librarian
            librarian_found = False
            librarian_details = None
            
            for service_id, service_data in registered_services.items():
                service_name = service_data.get("service_name", "")
                realm = service_data.get("realm", "")
                
                if "Librarian" in service_name or "librarian" in service_name.lower():
                    librarian_found = True
                    librarian_details = service_data
                    print(f"\n✅ Found Librarian service:")
                    print(f"   Service ID: {service_id}")
                    print(f"   Service Name: {service_name}")
                    print(f"   Realm: {realm}")
                    print(f"   Status: {service_data.get('status', 'unknown')}")
                    break
            
            if not librarian_found:
                print("\n❌ Librarian service not found in registered services")
                self.results["service_registration"]["details"].append("Librarian service not found")
                return False
            
            # Verify service metadata
            required_fields = ["service_name", "realm", "status"]
            missing_fields = [field for field in required_fields if field not in librarian_details]
            
            if missing_fields:
                print(f"\n⚠️ Missing required fields: {missing_fields}")
                self.results["service_registration"]["details"].append(f"Missing fields: {missing_fields}")
            else:
                print(f"\n✅ All required service metadata present")
            
            self.results["service_registration"]["passed"] = True
            self.results["service_registration"]["details"].append("Librarian service registered successfully")
            return True
            
        except Exception as e:
            print(f"\n❌ Service registration test failed: {e}")
            import traceback
            traceback.print_exc()
            self.results["service_registration"]["details"].append(f"Error: {str(e)}")
            return False
    
    async def test_soa_api_discovery(self) -> bool:
        """Test 2: Verify SOA API discovery."""
        print("\n" + "="*80)
        print("TEST 2: SOA API Discovery")
        print("="*80)
        
        try:
            # Get capabilities for Librarian
            librarian_capabilities = await self.curator.capability_registry.get_capabilities_by_service("LibrarianService")
            
            print(f"\n📋 Librarian capabilities: {len(librarian_capabilities)}")
            
            if not librarian_capabilities:
                print("\n❌ No capabilities found for LibrarianService")
                self.results["soa_api_discovery"]["details"].append("No capabilities found")
                return False
            
            # Check for SOA API contracts
            soa_apis_found = []
            
            for capability in librarian_capabilities:
                capability_name = capability.capability_name
                contracts = capability.contracts or {}
                
                print(f"\n📦 Capability: {capability_name}")
                print(f"   Protocol: {capability.protocol_name}")
                print(f"   Description: {capability.description}")
                
                # Check for SOA API contract
                if "soa_api" in contracts:
                    soa_api = contracts["soa_api"]
                    api_name = soa_api.get("api_name", "unknown")
                    endpoint = soa_api.get("endpoint", "unknown")
                    method = soa_api.get("method", "unknown")
                    
                    soa_apis_found.append({
                        "capability": capability_name,
                        "api_name": api_name,
                        "endpoint": endpoint,
                        "method": method
                    })
                    
                    print(f"   ✅ SOA API: {api_name}")
                    print(f"      Endpoint: {endpoint}")
                    print(f"      Method: {method}")
                else:
                    print(f"   ⚠️ No SOA API contract found")
            
            if not soa_apis_found:
                print("\n❌ No SOA APIs found in Librarian capabilities")
                self.results["soa_api_discovery"]["details"].append("No SOA API contracts found")
                return False
            
            print(f"\n✅ Found {len(soa_apis_found)} SOA APIs:")
            for api in soa_apis_found:
                print(f"   - {api['api_name']} ({api['method']} {api['endpoint']})")
            
            self.results["soa_api_discovery"]["passed"] = True
            self.results["soa_api_discovery"]["details"].append(f"Found {len(soa_apis_found)} SOA APIs")
            return True
            
        except Exception as e:
            print(f"\n❌ SOA API discovery test failed: {e}")
            import traceback
            traceback.print_exc()
            self.results["soa_api_discovery"]["details"].append(f"Error: {str(e)}")
            return False
    
    async def test_mcp_tool_discovery(self) -> bool:
        """Test 3: Verify MCP tool discovery."""
        print("\n" + "="*80)
        print("TEST 3: MCP Tool Discovery")
        print("="*80)
        
        try:
            # Get capabilities for Librarian
            librarian_capabilities = await self.curator.capability_registry.get_capabilities_by_service("LibrarianService")
            
            if not librarian_capabilities:
                print("\n❌ No capabilities found for LibrarianService")
                self.results["mcp_tool_discovery"]["details"].append("No capabilities found")
                return False
            
            # Check for MCP Tool contracts
            mcp_tools_found = []
            
            for capability in librarian_capabilities:
                capability_name = capability.capability_name
                contracts = capability.contracts or {}
                
                # Check for MCP Tool contract
                if "mcp_tool" in contracts:
                    mcp_tool = contracts["mcp_tool"]
                    tool_name = mcp_tool.get("tool_name", "unknown")
                    mcp_server = mcp_tool.get("mcp_server", "unknown")
                    tool_definition = mcp_tool.get("tool_definition", {})
                    
                    mcp_tools_found.append({
                        "capability": capability_name,
                        "tool_name": tool_name,
                        "mcp_server": mcp_server,
                        "description": tool_definition.get("description", "No description")
                    })
                    
                    print(f"\n✅ MCP Tool: {tool_name}")
                    print(f"   Capability: {capability_name}")
                    print(f"   MCP Server: {mcp_server}")
                    print(f"   Description: {tool_definition.get('description', 'No description')}")
            
            if not mcp_tools_found:
                print("\n❌ No MCP tools found in Librarian capabilities")
                self.results["mcp_tool_discovery"]["details"].append("No MCP tool contracts found")
                return False
            
            print(f"\n✅ Found {len(mcp_tools_found)} MCP tools:")
            for tool in mcp_tools_found:
                print(f"   - {tool['tool_name']} (via {tool['mcp_server']})")
            
            self.results["mcp_tool_discovery"]["passed"] = True
            self.results["mcp_tool_discovery"]["details"].append(f"Found {len(mcp_tools_found)} MCP tools")
            return True
            
        except Exception as e:
            print(f"\n❌ MCP tool discovery test failed: {e}")
            import traceback
            traceback.print_exc()
            self.results["mcp_tool_discovery"]["details"].append(f"Error: {str(e)}")
            return False
    
    async def test_capability_registration(self) -> bool:
        """Test 4: Verify capability registration with contracts."""
        print("\n" + "="*80)
        print("TEST 4: Capability Registration with Contracts")
        print("="*80)
        
        try:
            # Get capabilities for Librarian
            librarian_capabilities = await self.curator.capability_registry.get_capabilities_by_service("LibrarianService")
            
            if not librarian_capabilities:
                print("\n❌ No capabilities found for LibrarianService")
                self.results["capability_registration"]["details"].append("No capabilities found")
                return False
            
            print(f"\n📋 Found {len(librarian_capabilities)} capabilities")
            
            # Validate each capability
            valid_capabilities = 0
            invalid_capabilities = []
            
            for capability in librarian_capabilities:
                print(f"\n📦 Validating capability: {capability.capability_name}")
                
                # Check required fields
                required_fields = ["capability_name", "service_name", "protocol_name", "description", "contracts"]
                missing_fields = [field for field in required_fields if not hasattr(capability, field) or getattr(capability, field) is None]
                
                if missing_fields:
                    print(f"   ❌ Missing required fields: {missing_fields}")
                    invalid_capabilities.append({
                        "capability": capability.capability_name,
                        "issue": f"Missing fields: {missing_fields}"
                    })
                    continue
                
                # Check contracts
                contracts = capability.contracts or {}
                if not contracts:
                    print(f"   ❌ No contracts found")
                    invalid_capabilities.append({
                        "capability": capability.capability_name,
                        "issue": "No contracts"
                    })
                    continue
                
                # Check for at least one contract type
                contract_types = ["soa_api", "rest_api", "mcp_tool"]
                has_contract = any(contract_type in contracts for contract_type in contract_types)
                
                if not has_contract:
                    print(f"   ❌ No valid contract types found")
                    invalid_capabilities.append({
                        "capability": capability.capability_name,
                        "issue": "No valid contract types"
                    })
                    continue
                
                # Check for Smart City pattern (should have SOA API or MCP Tool, not REST API)
                has_rest_api = "rest_api" in contracts
                has_soa_api = "soa_api" in contracts
                has_mcp_tool = "mcp_tool" in contracts
                
                print(f"   ✅ Required fields present")
                print(f"   ✅ Contracts present: {list(contracts.keys())}")
                print(f"   ✅ SOA API: {has_soa_api}, MCP Tool: {has_mcp_tool}, REST API: {has_rest_api}")
                
                # Smart City services should NOT have REST API contracts (not user-facing)
                if has_rest_api:
                    print(f"   ⚠️ Warning: Smart City service has REST API contract (should be SOA API + MCP Tool only)")
                
                # Smart City services should NOT have semantic mapping
                if capability.semantic_mapping:
                    print(f"   ⚠️ Warning: Smart City service has semantic mapping (should be None)")
                else:
                    print(f"   ✅ No semantic mapping (correct for Smart City)")
                
                valid_capabilities += 1
            
            if invalid_capabilities:
                print(f"\n❌ {len(invalid_capabilities)} invalid capabilities:")
                for invalid in invalid_capabilities:
                    print(f"   - {invalid['capability']}: {invalid['issue']}")
                self.results["capability_registration"]["details"].append(f"{len(invalid_capabilities)} invalid capabilities")
            
            if valid_capabilities == 0:
                print("\n❌ No valid capabilities found")
                self.results["capability_registration"]["details"].append("No valid capabilities")
                return False
            
            print(f"\n✅ {valid_capabilities} valid capabilities found")
            
            self.results["capability_registration"]["passed"] = valid_capabilities > 0 and len(invalid_capabilities) == 0
            self.results["capability_registration"]["details"].append(f"{valid_capabilities} valid capabilities")
            return self.results["capability_registration"]["passed"]
            
        except Exception as e:
            print(f"\n❌ Capability registration test failed: {e}")
            import traceback
            traceback.print_exc()
            self.results["capability_registration"]["details"].append(f"Error: {str(e)}")
            return False
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result["passed"])
        
        print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed\n")
        
        for test_name, result in self.results.items():
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status} - {test_name.replace('_', ' ').title()}")
            for detail in result["details"]:
                print(f"   • {detail}")
        
        print("\n" + "="*80)
        
        if passed_tests == total_tests:
            print("✅ ALL TESTS PASSED - Phase 2 pattern is working correctly!")
            print("   Ready to migrate remaining Smart City services.")
        else:
            print("❌ SOME TESTS FAILED - Review issues above before proceeding.")
        
        print("="*80 + "\n")


async def main():
    """Run Phase 2 registration validation tests."""
    print("="*80)
    print("Smart City Phase 2 Registration Pattern Validation")
    print("Testing Librarian Service")
    print("="*80)
    
    validator = Phase2RegistrationValidator()
    
    # Initialize
    if not await validator.initialize():
        print("❌ Failed to initialize validator")
        return 1
    
    # Run tests
    test_results = []
    test_results.append(await validator.test_service_registration())
    test_results.append(await validator.test_soa_api_discovery())
    test_results.append(await validator.test_mcp_tool_discovery())
    test_results.append(await validator.test_capability_registration())
    
    # Print summary
    validator.print_summary()
    
    # Return exit code
    return 0 if all(test_results) else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

