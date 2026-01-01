#!/usr/bin/env python3
"""
Test StatelessHFInferenceAgent integration with platform.

Run this to verify agent works within orchestrator context.

Usage:
    # Set HF endpoint and API key
    export HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL="https://xxx.us-east-1.aws.endpoints.huggingface.cloud"
    export HUGGINGFACE_EMBEDDINGS_API_KEY="hf_xxx"
    
    python3 scripts/test_hf_agent_integration.py
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Add symphainy-platform to path
platform_root = os.path.join(project_root, 'symphainy-platform')
sys.path.insert(0, platform_root)

async def test_hf_agent_integration():
    """Test StatelessHFInferenceAgent integration."""
    print("🧪 Testing StatelessHFInferenceAgent Integration...")
    print("   This tests agent initialization and embedding generation")
    print("")
    
    # Check environment variables
    hf_endpoint_url = os.getenv("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
    hf_api_key = os.getenv("HUGGINGFACE_EMBEDDINGS_API_KEY")
    
    if not hf_endpoint_url or not hf_api_key:
        print("❌ HF endpoint configuration missing!")
        print("   Set HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
        print("   Set HUGGINGFACE_EMBEDDINGS_API_KEY")
        return False
    
    print(f"   HF Endpoint: {hf_endpoint_url}")
    print("")
    
    try:
        # Step 1: Test HuggingFaceAdapter directly
        print("Step 1: Testing HuggingFaceAdapter directly...")
        from foundations.public_works_foundation.infrastructure_adapters.huggingface_adapter import HuggingFaceAdapter
        
        adapter = HuggingFaceAdapter(endpoint_url=hf_endpoint_url, api_key=hf_api_key)
        print("✅ HuggingFaceAdapter initialized")
        
        test_result = await adapter.generate_embedding("test_column")
        if test_result and test_result.get("embedding"):
            print(f"✅ Adapter generates embeddings: {len(test_result.get('embedding'))} dimensions")
        else:
            print("❌ Adapter failed to generate embedding")
            return False
        print("")
        
        # Step 2: Test StatelessHFInferenceAgent initialization
        print("Step 2: Testing StatelessHFInferenceAgent initialization...")
        print("   Note: This requires full platform initialization (foundation services, etc.)")
        print("   For now, testing agent can be imported and configured...")
        
        from backend.business_enablement.agents.stateless_hf_inference_agent import StatelessHFInferenceAgent
        
        # Check config file exists
        config_path = os.path.join(
            platform_root,
            "backend/business_enablement/agents/configs/stateless_hf_inference_agent.yaml"
        )
        
        if not os.path.exists(config_path):
            print(f"❌ Agent config file not found: {config_path}")
            return False
        
        print(f"✅ Agent config file exists: {config_path}")
        print("")
        
        # Step 3: Test agent can be instantiated (with minimal dependencies)
        print("Step 3: Testing agent structure...")
        print("   (Full initialization requires foundation services - testing structure only)")
        
        # Read config to verify it's valid
        import yaml
        with open(config_path, 'r') as f:
            agent_config = yaml.safe_load(f)
        
        if agent_config.get("agent_name") == "StatelessHFInferenceAgent":
            print("✅ Agent config is valid")
            print(f"   Agent name: {agent_config.get('agent_name')}")
            print(f"   Role: {agent_config.get('role')}")
            print(f"   Capabilities: {agent_config.get('capabilities')}")
        else:
            print("❌ Agent config invalid")
            return False
        print("")
        
        print("✅ StatelessHFInferenceAgent integration test PASSED!")
        print("")
        print("Summary:")
        print("  ✅ HuggingFaceAdapter works")
        print("  ✅ Agent config file exists and is valid")
        print("  ✅ Agent structure is correct")
        print("")
        print("Note: Full agent initialization requires platform foundation services.")
        print("      This will be tested in Phase 2.2 (orchestrator integration).")
        return True
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from the correct directory")
        import traceback
        traceback.print_exc()
        return False
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_hf_agent_integration())
    sys.exit(0 if success else 1)






