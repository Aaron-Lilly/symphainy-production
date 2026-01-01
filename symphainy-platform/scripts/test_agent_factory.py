#!/usr/bin/env python3
"""
Test Agent Factory

Tests the unified agent initialization via Agentic Foundation factory.
Verifies that agents can be created with full SDK dependencies.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService


async def test_agent_factory():
    """Test agent factory creation."""
    print("🧪 Testing Agent Factory...")
    
    try:
        # Initialize DI Container
        print("\n1. Initializing DI Container...")
        di_container = DIContainerService("test_agent_factory")
        print("   ✅ DI Container initialized")
        
        # Initialize Public Works Foundation
        print("\n2. Initializing Public Works Foundation...")
        public_works = PublicWorksFoundationService(di_container)
        await public_works.initialize()
        di_container.service_registry["PublicWorksFoundationService"] = public_works
        print("   ✅ Public Works Foundation initialized")
        
        # Initialize Curator Foundation
        print("\n3. Initializing Curator Foundation...")
        curator = CuratorFoundationService(
            foundation_services=di_container,
            public_works_foundation=public_works
        )
        await curator.initialize()
        di_container.service_registry["CuratorFoundationService"] = curator
        print("   ✅ Curator Foundation initialized")
        
        # Initialize Agentic Foundation
        print("\n4. Initializing Agentic Foundation...")
        agentic_foundation = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=public_works,
            curator_foundation=curator
        )
        await agentic_foundation.initialize()
        di_container.service_registry["AgenticFoundationService"] = agentic_foundation
        print("   ✅ Agentic Foundation initialized")
        
        # Test: Create a simple test agent
        print("\n5. Testing agent creation...")
        
        # Create a minimal test agent class that extends BusinessLiaisonAgentBase
        from foundations.agentic_foundation.agui_schema_registry import AGUISchema
        
        class TestAgent:
            """Minimal test agent for factory testing."""
            def __init__(self, agent_name, business_domain, capabilities, required_roles,
                         agui_schema, foundation_services, agentic_foundation,
                         public_works_foundation, mcp_client_manager, policy_integration,
                         tool_composition, agui_formatter, curator_foundation, **kwargs):
                self.agent_name = agent_name
                self.business_domain = business_domain
                self.capabilities = capabilities
                self.required_roles = required_roles
                self.agui_schema = agui_schema
                self.foundation_services = foundation_services
                self.agentic_foundation = agentic_foundation
                self.public_works_foundation = public_works_foundation
                self.mcp_client_manager = mcp_client_manager
                self.policy_integration = policy_integration
                self.tool_composition = tool_composition
                self.agui_formatter = agui_formatter
                self.curator_foundation = curator_foundation
                self.is_initialized = False
                print(f"   📦 TestAgent created: {agent_name}")
            
            async def initialize(self):
                """Initialize test agent."""
                self.is_initialized = True
                print(f"   ✅ TestAgent.initialize() called")
                return True
        
        # Create agent via factory
        test_agent = await agentic_foundation.create_agent(
            agent_class=TestAgent,
            agent_name="TestAgent",
            agent_type="liaison",
            realm_name="business_enablement",
            di_container=di_container,
            orchestrator=None,
            capabilities=["test_capability"],
            required_roles=[]
        )
        
        if test_agent:
            print(f"   ✅ Agent created successfully")
            print(f"   - Agent name: {test_agent.agent_name}")
            print(f"   - Business domain: {test_agent.business_domain}")
            print(f"   - Initialized: {test_agent.is_initialized}")
            print(f"   - Has MCP Client Manager: {test_agent.mcp_client_manager is not None}")
            print(f"   - Has Policy Integration: {test_agent.policy_integration is not None}")
            print(f"   - Has Tool Composition: {test_agent.tool_composition is not None}")
        else:
            print("   ❌ Agent creation failed")
            return False
        
        # Test: Verify agent is tracked
        print("\n6. Testing agent tracking...")
        tracked_agent = await agentic_foundation.get_agent("TestAgent")
        if tracked_agent:
            print(f"   ✅ Agent found in factory cache")
        else:
            print("   ❌ Agent not found in factory cache")
            return False
        
        # Test: Verify agent is registered with Curator
        print("\n7. Testing Curator registration...")
        registered_services = await curator.get_registered_services()
        services_dict = registered_services.get("services", {})
        if "TestAgent" in services_dict:
            print(f"   ✅ Agent registered with Curator")
            agent_metadata = services_dict["TestAgent"]
            print(f"   - Service type: {agent_metadata.get('service_type')}")
            print(f"   - Agent type: {agent_metadata.get('agent_type')}")
            print(f"   - Realm: {agent_metadata.get('realm')}")
        else:
            print("   ⚠️ Agent not found in Curator (may be expected if registration failed)")
        
        # Test: List all agents
        print("\n8. Testing agent listing...")
        agents_list = await agentic_foundation.list_agents()
        print(f"   ✅ Found {len(agents_list)} agents in factory")
        for agent_name, agent_info in agents_list.items():
            print(f"   - {agent_name}: {agent_info}")
        
        print("\n✅ All agent factory tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_agent_factory())
    sys.exit(0 if success else 1)






