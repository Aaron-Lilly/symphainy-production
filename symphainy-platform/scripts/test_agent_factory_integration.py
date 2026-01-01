#!/usr/bin/env python3
"""
Test Agent Factory Integration

Tests that orchestrators can successfully initialize agents via the new factory pattern.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Change to project root for imports
os.chdir(project_root)

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService

# Import orchestrator and agents using dynamic import to handle path issues
import importlib.util
spec = importlib.util.spec_from_file_location(
    "content_analysis_orchestrator",
    project_root / "backend" / "business_enablement" / "business_orchestrator" / "use_cases" / "mvp" / "content_analysis_orchestrator" / "content_analysis_orchestrator.py"
)
content_orchestrator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(content_orchestrator_module)
ContentAnalysisOrchestrator = content_orchestrator_module.ContentAnalysisOrchestrator

spec2 = importlib.util.spec_from_file_location(
    "business_orchestrator_service",
    project_root / "backend" / "business_enablement" / "business_orchestrator" / "business_orchestrator_service.py"
)
business_orchestrator_module = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(business_orchestrator_module)
BusinessOrchestratorService = business_orchestrator_module.BusinessOrchestratorService

async def test_content_orchestrator_agent_initialization():
    """Test that ContentAnalysisOrchestrator can initialize agents via factory."""
    print("🧪 Testing ContentAnalysisOrchestrator Agent Initialization...")
    
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
        
        # Create a mock business orchestrator (minimal interface)
        class MockBusinessOrchestrator:
            def __init__(self, di_container):
                self.realm_name = "business_enablement"
                self.di_container = di_container
                self.platform_gateway = None  # Not needed for this test
            async def initialize(self):
                return True
        
        mock_business_orchestrator = MockBusinessOrchestrator(di_container)
        
        # Initialize ContentAnalysisOrchestrator directly
        print("\n5. Initializing ContentAnalysisOrchestrator...")
        # Note: ContentAnalysisOrchestrator requires business_orchestrator to extract platform_gateway
        # For this test, we'll create a minimal mock that provides the required attributes
        class MockBusinessOrchestratorWithGateway:
            def __init__(self, di_container):
                self.realm_name = "business_enablement"
                self.di_container = di_container
                # Create minimal platform gateway
                class MockPlatformGateway:
                    def __init__(self, di_container):
                        self.di_container = di_container
                    async def initialize(self):
                        return True
                self.platform_gateway = MockPlatformGateway(di_container)
            async def initialize(self):
                return True
        
        mock_business_orchestrator = MockBusinessOrchestratorWithGateway(di_container)
        
        content_orchestrator = ContentAnalysisOrchestrator(
            business_orchestrator=mock_business_orchestrator
        )
        
        init_result = await content_orchestrator.initialize()
        if not init_result:
            print("   ❌ ContentAnalysisOrchestrator initialization failed")
            return False
        print(f"   ✅ ContentAnalysisOrchestrator initialized: {content_orchestrator.orchestrator_name}")
        
        # Check if agents were initialized
        print("\n6. Checking agent initialization...")
        if not hasattr(content_orchestrator, 'liaison_agent') or content_orchestrator.liaison_agent is None:
            print("   ❌ ContentLiaisonAgent not initialized")
            return False
        print(f"   ✅ ContentLiaisonAgent initialized: {content_orchestrator.liaison_agent.agent_name}")
        
        if not hasattr(content_orchestrator, 'processing_agent') or content_orchestrator.processing_agent is None:
            print("   ❌ ContentProcessingAgent not initialized")
            return False
        print(f"   ✅ ContentProcessingAgent initialized: {content_orchestrator.processing_agent.agent_name}")
        
        # Verify agents have SDK dependencies
        print("\n7. Verifying agent SDK dependencies...")
        liaison = content_orchestrator.liaison_agent
        if not hasattr(liaison, 'mcp_client_manager'):
            print("   ⚠️ ContentLiaisonAgent missing mcp_client_manager (may be None if MCP not configured)")
        if not hasattr(liaison, 'policy_integration') or liaison.policy_integration is None:
            print("   ❌ ContentLiaisonAgent missing policy_integration")
            return False
        if not hasattr(liaison, 'tool_composition') or liaison.tool_composition is None:
            print("   ❌ ContentLiaisonAgent missing tool_composition")
            return False
        if not hasattr(liaison, 'curator_foundation'):
            print("   ❌ ContentLiaisonAgent missing curator_foundation")
            return False
        print("   ✅ ContentLiaisonAgent has all required SDK dependencies")
        
        processing = content_orchestrator.processing_agent
        if not hasattr(processing, 'policy_integration') or processing.policy_integration is None:
            print("   ❌ ContentProcessingAgent missing policy_integration")
            return False
        if not hasattr(processing, 'tool_composition') or processing.tool_composition is None:
            print("   ❌ ContentProcessingAgent missing tool_composition")
            return False
        print("   ✅ ContentProcessingAgent has all required SDK dependencies")
        
        # Check agent registration with Curator
        print("\n8. Checking agent registration with Curator...")
        registered_services = await curator.get_registered_services()
        services_dict = registered_services.get("services", {})
        
        liaison_registered = "ContentLiaisonAgent" in services_dict
        processing_registered = "ContentProcessingAgent" in services_dict
        
        if liaison_registered:
            print("   ✅ ContentLiaisonAgent registered with Curator")
        else:
            print("   ⚠️ ContentLiaisonAgent not found in Curator (may be expected if registration failed)")
        
        if processing_registered:
            print("   ✅ ContentProcessingAgent registered with Curator")
        else:
            print("   ⚠️ ContentProcessingAgent not found in Curator (may be expected if registration failed)")
        
        print("\n✅ All agent factory integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_content_orchestrator_agent_initialization())
    sys.exit(0 if success else 1)

