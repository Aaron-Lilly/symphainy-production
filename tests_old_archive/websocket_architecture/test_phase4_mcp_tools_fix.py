#!/usr/bin/env python3
"""
Test Phase 4 & 4.5 MCP Tools Fix

Verifies that Guide Agent and Liaison Agents use MCP tools instead of SOA APIs.
"""

import sys
import os
import asyncio

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

async def test_guide_agent_mcp_tools():
    """Test that Guide Agent uses MCP tools instead of SOA APIs."""
    print("\n" + "="*80)
    print("TEST: Guide Agent MCP Tools Usage")
    print("="*80)
    
    try:
        # Check that Guide Agent doesn't have SOA API client attributes
        guide_agent_path = os.path.join(project_root, "symphainy-platform/backend/business_enablement/agents/guide_cross_domain_agent.py")
        guide_agent_code = open(guide_agent_path).read()
        
        # Verify SOA API references are removed
        has_soa_api_attributes = (
            'self.traffic_cop = None' in guide_agent_code or
            'self.post_office = None' in guide_agent_code or
            'self.conductor = None' in guide_agent_code
        )
        
        has_soa_api_calls = (
            'call_soa_api' in guide_agent_code and
            'traffic_cop.call_soa_api' in guide_agent_code
        )
        
        has_mcp_tools = (
            'execute_role_tool' in guide_agent_code and
            'traffic_cop' in guide_agent_code and
            'create_session' in guide_agent_code
        )
        
        has_get_smart_city_service = '_get_smart_city_service_via_curator' in guide_agent_code
        
        print(f"✅ Guide Agent code analysis:")
        print(f"   - SOA API attributes removed: {not has_soa_api_attributes}")
        print(f"   - SOA API calls removed: {not has_soa_api_calls}")
        print(f"   - MCP tools usage present: {has_mcp_tools}")
        print(f"   - _get_smart_city_service_via_curator removed: {not has_get_smart_city_service}")
        
        if not has_soa_api_attributes and not has_soa_api_calls and has_mcp_tools and not has_get_smart_city_service:
            print("✅ Guide Agent correctly uses MCP tools!")
            return True
        else:
            print("❌ Guide Agent still has SOA API references or missing MCP tools")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Guide Agent: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_liaison_agent_mcp_tools():
    """Test that Liaison Agent Base uses MCP tools instead of SOA APIs."""
    print("\n" + "="*80)
    print("TEST: Liaison Agent Base MCP Tools Usage")
    print("="*80)
    
    try:
        # Read Liaison Agent Base code
        liaison_agent_code = open(
            os.path.join(project_root, "symphainy-platform/backend/business_enablement/protocols/business_liaison_agent_protocol.py")
        ).read()
        
        # Verify SOA API references are removed
        has_soa_api_attributes = (
            'self.traffic_cop = None' in liaison_agent_code or
            'self.post_office = None' in liaison_agent_code or
            'self.conductor = None' in liaison_agent_code
        )
        
        has_soa_api_calls = (
            'call_soa_api' in liaison_agent_code and
            'traffic_cop.call_soa_api' in liaison_agent_code
        )
        
        has_mcp_tools = (
            'execute_role_tool' in liaison_agent_code and
            'traffic_cop' in liaison_agent_code and
            'create_session' in liaison_agent_code
        )
        
        has_get_smart_city_service = '_get_smart_city_service_via_curator' in liaison_agent_code
        
        print(f"✅ Liaison Agent Base code analysis:")
        print(f"   - SOA API attributes removed: {not has_soa_api_attributes}")
        print(f"   - SOA API calls removed: {not has_soa_api_calls}")
        print(f"   - MCP tools usage present: {has_mcp_tools}")
        print(f"   - _get_smart_city_service_via_curator removed: {not has_get_smart_city_service}")
        
        if not has_soa_api_attributes and not has_soa_api_calls and has_mcp_tools and not has_get_smart_city_service:
            print("✅ Liaison Agent Base correctly uses MCP tools!")
            return True
        else:
            print("❌ Liaison Agent Base still has SOA API references or missing MCP tools")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Liaison Agent Base: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_tool_patterns():
    """Test that MCP tool patterns are correctly implemented."""
    print("\n" + "="*80)
    print("TEST: MCP Tool Pattern Verification")
    print("="*80)
    
    try:
        # Read both agent files
        guide_agent_code = open(
            os.path.join(project_root, "symphainy-platform/backend/business_enablement/agents/guide_cross_domain_agent.py")
        ).read()
        
        liaison_agent_code = open(
            os.path.join(project_root, "symphainy-platform/backend/business_enablement/protocols/business_liaison_agent_protocol.py")
        ).read()
        
        # Check for correct MCP tool usage patterns
        patterns_found = {
            "traffic_cop_create_session": (
                'execute_role_tool' in guide_agent_code and
                '"traffic_cop"' in guide_agent_code and
                '"create_session"' in guide_agent_code
            ),
            "post_office_message_sender": (
                'execute_role_tool' in guide_agent_code and
                '"post_office"' in guide_agent_code and
                '"message_sender"' in guide_agent_code
            ),
            "conductor_workflow_orchestrator": (
                'execute_role_tool' in guide_agent_code and
                '"conductor"' in guide_agent_code and
                '"workflow_orchestrator"' in guide_agent_code
            ),
            "liaison_traffic_cop_create_session": (
                'execute_role_tool' in liaison_agent_code and
                '"traffic_cop"' in liaison_agent_code and
                '"create_session"' in liaison_agent_code
            ),
            "liaison_post_office_message_sender": (
                'execute_role_tool' in liaison_agent_code and
                '"post_office"' in liaison_agent_code and
                '"message_sender"' in liaison_agent_code
            )
        }
        
        print(f"✅ MCP Tool Pattern Verification:")
        for pattern_name, found in patterns_found.items():
            status = "✅" if found else "❌"
            print(f"   {status} {pattern_name}: {found}")
        
        all_found = all(patterns_found.values())
        if all_found:
            print("✅ All MCP tool patterns correctly implemented!")
            return True
        else:
            print("❌ Some MCP tool patterns are missing")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MCP tool patterns: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("PHASE 4 & 4.5 MCP TOOLS FIX - TEST SUITE")
    print("="*80)
    
    results = []
    
    # Test 1: Guide Agent MCP Tools
    results.append(await test_guide_agent_mcp_tools())
    
    # Test 2: Liaison Agent Base MCP Tools
    results.append(await test_liaison_agent_mcp_tools())
    
    # Test 3: MCP Tool Patterns
    results.append(await test_mcp_tool_patterns())
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED - Agents correctly use MCP tools!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Please review the output above")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

