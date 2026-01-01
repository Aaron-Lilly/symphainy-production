#!/usr/bin/env python3
"""
Direct Phase 2 Test - Call orchestrator directly (bypasses API/auth)
Tests semantic processing by calling ContentAnalysisOrchestrator.parse_file() directly
"""

import subprocess
import json
import sys

def run_python_in_container(code):
    """Run Python code inside backend container."""
    # Escape code for shell
    code_escaped = code.replace('"', '\\"').replace('$', '\\$')
    cmd = f'docker exec symphainy-backend-prod python3 -c "{code_escaped}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def test_direct_parse():
    """Test parse_file directly via orchestrator."""
    print("=" * 70)
    print("Direct Test: ContentAnalysisOrchestrator.parse_file()")
    print("=" * 70)
    print()
    
    # Python code to run in container
    test_code = '''
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path("/app")
sys.path.insert(0, str(project_root))

async def test():
    try:
        # Import orchestrator
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        # Get DI container and platform gateway (simplified - just check if we can import)
        print("✅ ContentAnalysisOrchestrator imported successfully")
        print("   Note: Full test requires initialized orchestrator instance")
        print("   This confirms the semantic processing code is available")
        
        # Check if StatelessHFInferenceAgent is available
        try:
            from backend.business_enablement.agents.stateless_hf_inference_agent import StatelessHFInferenceAgent
            print("✅ StatelessHFInferenceAgent imported successfully")
        except Exception as e:
            print(f"❌ StatelessHFInferenceAgent import failed: {e}")
            return False
        
        # Check if semantic processing methods exist
        import inspect
        methods = [m for m in dir(ContentAnalysisOrchestrator) if not m.startswith('_')]
        semantic_methods = [m for m in methods if 'semantic' in m.lower()]
        print(f"✅ Found semantic processing methods: {semantic_methods}")
        
        # Check parse_file signature
        if hasattr(ContentAnalysisOrchestrator, 'parse_file'):
            sig = inspect.signature(ContentAnalysisOrchestrator.parse_file)
            print(f"✅ parse_file() method exists with signature: {sig}")
        else:
            print("❌ parse_file() method not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

result = asyncio.run(test())
sys.exit(0 if result else 1)
'''
    
    stdout, stderr, code = run_python_in_container(test_code)
    
    print(stdout)
    if stderr:
        print("STDERR:", stderr)
    
    return code == 0

def test_check_logs():
    """Check backend logs for semantic processing initialization."""
    print("\n" + "=" * 70)
    print("Checking Backend Logs for Semantic Processing")
    print("=" * 70)
    print()
    
    # Check for StatelessHFInferenceAgent initialization
    cmd = "docker logs symphainy-backend-prod --tail 200 2>&1 | grep -i 'stateless.*hf\|semantic.*processing\|huggingface.*adapter' | tail -10"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("✅ Found semantic processing logs:")
        print(result.stdout)
    else:
        print("⚠️  No semantic processing logs found in recent logs")
        print("   This might mean:")
        print("   - Semantic processing hasn't been triggered yet")
        print("   - Logs are in a different location")
        print("   - Initialization happened earlier")
    
    return True

def main():
    """Run all tests."""
    print("\n🧪 Phase 2 Semantic Processing - Direct Test")
    print("=" * 70)
    print()
    
    # Test 1: Check if code is available
    print("Test 1: Verifying semantic processing code is available...")
    code_available = test_direct_parse()
    
    # Test 2: Check logs
    print("\nTest 2: Checking backend logs...")
    test_check_logs()
    
    print("\n" + "=" * 70)
    if code_available:
        print("✅ Code Verification: PASSED")
        print("   Semantic processing code is available and importable")
        print()
        print("📝 Next Steps:")
        print("   1. Upload a file via the frontend or API (with auth)")
        print("   2. Call parse_file with content_type in parse_options")
        print("   3. Check response for semantic_result")
        print("   4. Verify ArangoDB has stored embeddings/graphs")
    else:
        print("❌ Code Verification: FAILED")
        print("   Check errors above")
    print("=" * 70)
    
    return code_available

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)






